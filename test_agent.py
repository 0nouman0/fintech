import unittest
from tools import rule_based_risk_analyzer
from spam_detector import check_spam_number, analyze_call_transcript
from upi_guardian import parse_upi_string, verify_vpa_mock_api

class TestFinancialSafetyNet(unittest.TestCase):

    def test_upi_scam_rule(self):
        text = "Enter your UPI PIN to receive Rs. 500 cashback immediately."
        result = rule_based_risk_analyzer(text, "upi")
        self.assertEqual(result["risk_level"], "SCAM")
        self.assertIn("Asks for UPI PIN to receive money (High Risk)", result["reasons"])

    def test_loan_scam_rule(self):
        text = "Instant loan approved. Pay processing fee of Rs. 1999 in advance."
        result = rule_based_risk_analyzer(text, "loan")
        self.assertEqual(result["risk_level"], "SCAM")
        self.assertIn("Demands advance processing fee (Illegal/Scam)", result["reasons"])

    def test_spam_number_check(self):
        result = check_spam_number("9876543210")
        self.assertEqual(result["risk"], "SCAM")
        self.assertEqual(result["tag"], "Fake Loan Agent")

    def test_spam_transcript(self):
        text = "I am calling from CBI police station. You are under digital arrest."
        result = analyze_call_transcript(text)
        self.assertEqual(result["risk_level"], "SCAM")
        self.assertIn("Impersonating Law Enforcement (Digital Arrest Scam)", result["reasons"])

    def test_upi_parsing(self):
        upi_string = "upi://pay?pa=merchant@okicici&pn=Shop&am=100"
        details = parse_upi_string(upi_string)
        self.assertEqual(details["pa"], "merchant@okicici")

    def test_upi_mock_api(self):
        result = verify_vpa_mock_api("scammer@upi")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["risk_level"], "SCAM")

if __name__ == '__main__':
    unittest.main()
