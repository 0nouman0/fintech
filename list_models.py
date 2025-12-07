import os
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found.")
else:
    client = genai.Client(api_key=api_key)
    try:
        # The SDK method to list models might vary, checking standard approach
        # For google-genai SDK (v1.0+), it's often client.models.list()
        for model in client.models.list():
            print(model.name)
    except Exception as e:
        print(f"Error listing models: {e}")
