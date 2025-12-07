import re

def rule_based_risk_analyzer(text: str, category: str = "unknown") -> dict:
    """
    Analyzes text for specific risk indicators based on category.
    Returns a dictionary with risk_level, score, and reasons.
    """
    text = text.lower()
    reasons = []
    score = 0
    
    # UPI Fraud Indicators
    if category == "upi" or "upi" in text or "paytm" in text or "gpay" in text or "phonepe" in text:
        if "pin" in text and ("receive" in text or "get" in text or "won" in text):
            reasons.append("Asks for UPI PIN to receive money (High Risk)")
            score += 90
        if "kyc" in text and ("update" in text or "expire" in text or "block" in text):
            reasons.append("Urgent KYC update request (Common Phishing)")
            score += 80
        if re.search(r"bit\.ly|tinyurl", text):
            reasons.append("Contains suspicious shortened link")
            score += 60
        if "lottery" in text or "winner" in text:
            reasons.append("Lottery/Prize claim (Common Scam)")
            score += 85

    # Loan Risk Indicators
    if category == "loan" or "loan" in text or "credit" in text:
        # Check for high interest rates (simple regex, can be improved)
        interest_match = re.search(r"(\d{1,2})%", text)
        if interest_match:
            rate = int(interest_match.group(1))
            if rate > 24:
                reasons.append(f"Very high interest rate detected: {rate}%")
                score += 70
        
        if "processing fee" in text and ("advance" in text or "before" in text):
            reasons.append("Demands advance processing fee (Illegal/Scam)")
            score += 95
        
        if "no cibil" in text or "no documents" in text:
            reasons.append("Too good to be true (No CIBIL/Docs check)")
            score += 50

    # Insurance Risk Indicators
    if category == "insurance" or "policy" in text:
        if "waiting period" in text:
            reasons.append("Contains waiting period clause")
            score += 20
        if "exclusion" in text or "not cover" in text:
            reasons.append("Contains exclusion clauses")
            score += 30
        if "pre-existing" in text:
            reasons.append("Mentions pre-existing disease limitations")
            score += 25

    # Sensitive Data Indicators (Privacy Protection)
    sensitive_keywords = ["aadhaar", "pan card", "voter id", "driving license", "passport", "otp", "cvv", "password"]
    for keyword in sensitive_keywords:
        if keyword in text:
            if "send" in text or "share" in text or "upload" in text or "photo" in text or "verify" in text:
                reasons.append(f"Requests sharing of sensitive document/info: {keyword.upper()} (High Privacy Risk)")
                score += 85
            else:
                reasons.append(f"Mentions sensitive document: {keyword.upper()}")
                score += 10

    # Determine Risk Level
    if score >= 80:
        risk_level = "SCAM"
    elif score >= 50:
        risk_level = "SUSPICIOUS"
    elif score >= 20:
        risk_level = "CONFUSING"
    else:
        risk_level = "SAFE"

    return {
        "risk_level": risk_level,
        "score": min(score, 100),
        "reasons": reasons
    }
