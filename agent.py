import os
import json
import google.genai as genai
from google.genai import types
from dotenv import load_dotenv
from tools import rule_based_risk_analyzer
from spam_detector import analyze_call_transcript
from upi_guardian import scan_and_verify_upi
from PIL import Image
from gtts import gTTS
import uuid

load_dotenv()

class FinancialSafetyNet:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
        self.client = genai.Client(api_key=api_key)
        # Using gemini-flash-latest as it is available and likely has better quota
        self.model_name = "gemini-flash-latest" 

        self.system_instruction = """
You are the "Financial Safety Net Agent" for India.
Your goal is to protect users from financial risks (UPI scams, Loan traps, Insurance exclusions).

INPUT: Text, Image (Screenshot/PDF), or Audio (Call Recording).
OUTPUT: JSON ONLY.

CRITICAL PRIVACY RULE:
If the user input asks for or mentions sharing sensitive personal documents like **Aadhaar Card, PAN Card, Voter ID, Driving License, Passport, OTP, or CVV**, you MUST:
1. Mark risk_level as "SUSPICIOUS" or "SCAM".
2. Warn the user NEVER to share these details over unverified channels (WhatsApp, Phone, Unknown Links).
3. Explain that banks/officials never ask for these photos/details via informal chats.

Follow these steps:
1. Analyze the input to identify the category (UPI, Loan, Insurance, Unknown, Spam Call).
2. Assess the risk level (SAFE, SUSPICIOUS, SCAM, CONFUSING).
3. Extract key financial terms (Interest rate, fees, tenure, exclusions) OR Transcript (if audio).
4. Provide simple advice in common language.

Use the provided tools/context to enhance your reasoning.
Always output valid JSON matching the schema provided in the user prompt.
"""

    def generate_audio_advice(self, text: str, output_dir: str = "static/audio"):
        """
        Generates an audio file from the advice text using gTTS.
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            filename = f"advice_{uuid.uuid4().hex}.mp3"
            filepath = os.path.join(output_dir, filename)
            
            tts = gTTS(text=text, lang='en', tld='co.in') # Indian English accent
            tts.save(filepath)
            
            return filename
        except Exception as e:
            print(f"TTS Generation failed: {e}")
            return None

    def analyze(self, text_input: str = None, image_path: str = None, audio_path: str = None, category_hint: str = "unknown"):
        """
        Main analysis function.
        """
        
        # 1. Rule-Based Pre-analysis (if text is available)
        rule_based_result = {}
        if text_input:
            rule_based_result = rule_based_risk_analyzer(text_input, category_hint)
            
            # Check for spam patterns if it looks like a transcript
            if category_hint == "spam_check" or "call" in text_input.lower():
                spam_result = analyze_call_transcript(text_input)
                # Merge results (prioritize high risk)
                if spam_result["score"] > rule_based_result.get("score", 0):
                    rule_based_result = spam_result
                    category_hint = "spam_call"

        # 2. UPI Guardian Check (if image is QR)
        upi_result = {}
        if image_path and category_hint == "upi_qr":
             upi_result = scan_and_verify_upi(image_path)
             if "error" not in upi_result:
                 # Construct a text description for Gemini
                 text_input = f"UPI QR Code detected. VPA: {upi_result['extracted_details'].get('pa')}. Verification Status: {upi_result['verification_result']['status']}."
                 rule_based_result = {"risk_level": upi_result['verification_result']['risk_level'], "reasons": [upi_result['verification_result']['message']]}

        # 3. Gemini Analysis
        prompt_parts = []
        
        if text_input:
            prompt_parts.append(f"User Input Text: {text_input}")
            
        if image_path:
            try:
                image = Image.open(image_path)
                prompt_parts.append(image)
            except Exception as e:
                return {"error": f"Failed to load image: {e}"}

        if audio_path:
            try:
                # Read audio file as bytes
                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()
                prompt_parts.append(types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3")) # Assuming mp3 for now
                prompt_parts.append("Please transcribe this audio and analyze it for spam/scam risks.")
            except Exception as e:
                return {"error": f"Failed to load audio: {e}"}

        prompt_parts.append(f"Rule-Based Analysis Result: {json.dumps(rule_based_result)}")
        prompt_parts.append(f"UPI Verification Result: {json.dumps(upi_result)}")

        # Define the JSON schema for structured output
        schema = {
            "type": "OBJECT",
            "properties": {
                "risk_level": {"type": "STRING", "enum": ["SAFE", "SUSPICIOUS", "SCAM", "CONFUSING"]},
                "score": {"type": "INTEGER"},
                "category": {"type": "STRING", "enum": ["upi", "loan", "insurance", "spam_call", "unknown"]},
                "reasons": {"type": "ARRAY", "items": {"type": "STRING"}},
                "advice": {"type": "STRING"},
                "transcript": {"type": "STRING", "nullable": True},
                "extracted_details": {
                    "type": "OBJECT",
                    "properties": {
                        "interest_rate": {"type": "STRING", "nullable": True},
                        "fees": {"type": "STRING", "nullable": True},
                        "tenure": {"type": "STRING", "nullable": True},
                        "exclusions": {"type": "STRING", "nullable": True},
                        "other_key_points": {"type": "ARRAY", "items": {"type": "STRING"}}
                    }
                }
            },
            "required": ["risk_level", "score", "category", "reasons", "advice", "extracted_details"]
        }

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt_parts,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    response_mime_type="application/json",
                    response_schema=schema
                )
            )
            
            result = json.loads(response.text)
            
            # Post-Analysis: Apply strict rules to the transcript if available
            # This ensures that even if Gemini misses the context, our keyword list catches it.
            if result.get("transcript"):
                transcript_text = result["transcript"]
                strict_check = rule_based_risk_analyzer(transcript_text, category_hint="spam_call")
                
                if strict_check["score"] > result["score"]:
                    result["risk_level"] = strict_check["risk_level"]
                    result["score"] = strict_check["score"]
                    result["reasons"].extend(strict_check["reasons"])
                    result["advice"] += " " + " ".join([r for r in strict_check["reasons"] if "sensitive" in r.lower()])

            # Generate Audio Advice
            if "advice" in result:
                audio_file = self.generate_audio_advice(result["advice"])
                if audio_file:
                    result["audio_advice_url"] = f"/static/audio/{audio_file}"
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                return {
                    "error": "Quota Exceeded. Please try again later or switch to a different model.",
                    "details": "The AI model is currently busy or you have hit your rate limit."
                }
            return {"error": f"Gemini Analysis Failed: {e}"}
