import random

# Mock Spam Database
SPAM_DB = {
    "9876543210": {"risk": "SCAM", "reports": 500, "tag": "Fake Loan Agent"},
    "9988776655": {"risk": "SUSPICIOUS", "reports": 120, "tag": "Telemarketer"},
    "1234567890": {"risk": "SAFE", "reports": 0, "tag": "Verified Business"},
}

def check_spam_number(phone_number: str) -> dict:
    """
    Checks a phone number against the mock spam database.
    """
    # Clean number
    phone_number = phone_number.replace("+91", "").strip()
    
    if phone_number in SPAM_DB:
        return SPAM_DB[phone_number]
    
    # Simulate random unknown number check
    # In a real app, this would query a live API like Truecaller
    return {"risk": "UNKNOWN", "reports": 0, "tag": "Unknown Number"}

def analyze_call_transcript(transcript: str, gemini_client=None) -> dict:
    """
    Analyzes a call transcript for scam patterns.
    Uses Gemini if client is provided, otherwise simple keywords.
    """
    risk_score = 0
    reasons = []
    
    transcript_lower = transcript.lower()
    
    if "otp" in transcript_lower and "share" in transcript_lower:
        risk_score += 90
        reasons.append("Caller asked for OTP sharing")
        
    if "police" in transcript_lower or "cbi" in transcript_lower:
        risk_score += 80
        reasons.append("Impersonating Law Enforcement (Digital Arrest Scam)")
        
    if "refund" in transcript_lower and "click" in transcript_lower:
        risk_score += 70
        reasons.append("Refund scam pattern detected")

    if risk_score >= 80:
        risk_level = "SCAM"
    elif risk_score >= 50:
        risk_level = "SUSPICIOUS"
    else:
        risk_level = "SAFE"
        
    return {
        "risk_level": risk_level,
        "score": risk_score,
        "reasons": reasons
    }
