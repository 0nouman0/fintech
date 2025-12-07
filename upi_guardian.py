import cv2
from qreader import QReader
import time

# Initialize QReader
qreader = QReader()

# Mock Blocklist
UPI_BLOCKLIST = [
    "scammer@upi",
    "fake.lottery@okicici",
    "urgent.kyc@paytm"
]

def decode_qr_code(image_path: str) -> str:
    """
    Decodes a QR code image and returns the data (UPI string).
    """
    try:
        # Read the image
        img = cv2.imread(image_path)
        if img is None:
            return None
            
        # Detect and decode
        decoded_text = qreader.detect_and_decode(image=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        if decoded_text and len(decoded_text) > 0:
            return decoded_text[0] # Return first QR code found
        return None
    except Exception as e:
        print(f"Error decoding QR: {e}")
        return None

def parse_upi_string(upi_string: str) -> dict:
    """
    Parses a UPI string (upi://pay?...) to extract VPA and other details.
    """
    if not upi_string or not upi_string.startswith("upi://pay"):
        return None
        
    details = {}
    params = upi_string.split("?")[1].split("&")
    for param in params:
        if "=" in param:
            key, value = param.split("=", 1)
            details[key] = value
            
    return details

def verify_vpa_mock_api(vpa: str) -> dict:
    """
    Simulates a Bank API call to verify a VPA.
    """
    # Simulate network latency
    # time.sleep(0.5) 
    
    if vpa in UPI_BLOCKLIST:
        return {
            "status": "BLOCKED",
            "risk_level": "SCAM",
            "name": "Flagged Fraudster",
            "message": "This UPI ID has been reported for fraud."
        }
    
    if "shop" in vpa or "merchant" in vpa:
        return {
            "status": "VERIFIED",
            "risk_level": "SAFE",
            "name": "Verified Merchant",
            "message": "Safe to pay."
        }
        
    return {
        "status": "UNKNOWN",
        "risk_level": "CAUTION",
        "name": "Unknown User",
        "message": "Verify the name before paying."
    }

def scan_and_verify_upi(image_path: str) -> dict:
    """
    Orchestrates the UPI scanning and verification process.
    """
    upi_string = decode_qr_code(image_path)
    
    if not upi_string:
        return {"error": "No QR code found or could not decode."}
        
    details = parse_upi_string(upi_string)
    if not details or "pa" not in details: # 'pa' is the parameter for Payee Address (VPA)
        return {"error": "Invalid UPI QR code."}
        
    vpa = details["pa"]
    verification = verify_vpa_mock_api(vpa)
    
    return {
        "upi_string": upi_string,
        "extracted_details": details,
        "verification_result": verification
    }
