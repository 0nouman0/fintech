import argparse
import json
import os
from agent import FinancialSafetyNet
from spam_detector import check_spam_number

def main():
    parser = argparse.ArgumentParser(description="Financial Safety Net Agent")
    parser.add_argument("--text", type=str, help="Text content to analyze")
    parser.add_argument("--image", type=str, help="Path to image file (Screenshot/PDF/QR)")
    parser.add_argument("--type", type=str, default="unknown", help="Category hint: upi, loan, insurance, spam_check, upi_qr")
    parser.add_argument("--check-number", type=str, help="Check a phone number for spam")
    
    args = parser.parse_args()
    
    # Simple Spam Number Check
    if args.check_number:
        result = check_spam_number(args.check_number)
        print(json.dumps(result, indent=2))
        return

    # Agent Analysis
    if not args.text and not args.image:
        print("Error: Please provide --text or --image input.")
        return

    try:
        agent = FinancialSafetyNet()
        result = agent.analyze(text_input=args.text, image_path=args.image, category_hint=args.type)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
