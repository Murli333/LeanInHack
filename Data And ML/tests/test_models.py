"""
Comprehensive Verification & Test Suite for ScamLens ML Models (Member 1: Data & ML)
Covers:
- [P0] Edge cases: Empty strings, None, whitespace, extreme lengths (10K chars), numeric-only
- [P0] False-positive stress testing (legitimate OTPs, bills, PNRs, public advisories)
- [P1] Multiple URLs embedded in a single message
- [P1] Multilingual (Hindi/Hinglish) and obfuscated messages (Cyrillic homoglyphs, K Y C, fr.ee)
- [P1] Missing model files graceful heuristic fallback mode
- [P1] Strict assertions on expected scam verdicts (exact 'Scam' for high-threat attacks)
- [P2] Regression validation & model metadata inspection
"""
import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
SRC_DIR = os.path.join(BASE_DIR, "src")
for p in [MODELS_DIR, SRC_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from predictor import ScamLensPredictor
from agent import ScamInvestigatorAgent


class TestScamLensML(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.predictor = ScamLensPredictor(models_dir=MODELS_DIR)
        cls.agent = ScamInvestigatorAgent(models_dir=MODELS_DIR)

    # =================================================================
    # 1. [P0] EMPTY & MALFORMED INPUT HANDLING TESTS
    # =================================================================
    def test_empty_and_whitespace_inputs(self):
        """Verifies empty or whitespace inputs never automatically appear Safe."""
        for empty_val in ["", None, "   ", "\n\t  \n"]:
            res_text = self.predictor.predict_text(empty_val)
            self.assertEqual(res_text["verdict"], "Unknown", f"Failed for empty text: {repr(empty_val)}")
            self.assertEqual(res_text["status_color"], "gray")
            self.assertEqual(res_text["icon"], "❓")
            self.assertTrue(res_text["is_empty"])
            self.assertEqual(res_text["risk_score"], 0)

            res_url = self.predictor.predict_url(empty_val)
            self.assertEqual(res_url["verdict"], "Unknown", f"Failed for empty URL: {repr(empty_val)}")
            self.assertTrue(res_url["is_empty"])

        res_comb = self.predictor.predict_combined(text="", url="")
        self.assertEqual(res_comb["verdict"], "Unknown")
        self.assertTrue(res_comb["is_empty"])

    def test_extremely_long_input(self):
        """Tests that a 10,000 character input does not cause stack overflows or timeouts."""
        long_text = "Dear Customer, this is an important message. " * 250  # ~11,000 chars
        res = self.predictor.predict_text(long_text)
        self.assertIn("verdict", res)
        self.assertIn("risk_score", res)
        self.assertFalse(res["is_empty"])

    def test_numeric_and_symbol_inputs(self):
        """Tests numbers and special characters only."""
        res_num = self.predictor.predict_text("9876543210 123456 999999")
        self.assertIn(res_num["verdict"], ["Safe", "Suspicious"])
        
        res_sym = self.predictor.predict_text("$$$ !!! ??? *** ###")
        self.assertIn("verdict", res_sym)

    # =================================================================
    # 2. [P0] HIGH-THREAT SCAM DETECTION (STRICT VERDICT ASSERTION)
    # =================================================================
    def test_high_threat_scams_strict(self):
        """High-threat attacks must strictly receive a 'Scam' verdict."""
        strict_scams = [
            ("Dear SBI user, your YONO account is locked due to pending KYC update. Click http://sbi-kyc-verify.top/sbi.apk to update immediately.", "fake_kyc"),
            ("Urgent: Electricity power will be disconnected at 9:30 PM from power office because your previous month bill was not updated. Please immediately contact our electricity officer 9876543210.", "electricity"),
            ("Delhi Police Cyber Cell: A parcel in your name containing illegal narcotics has been seized at Mumbai airport. Digital arrest warrant issued. Contact CBI Officer on Skype immediately.", "digital_arrest"),
            ("Dear Customer, you received UPI collect request of Rs 4999 from Amazon Pay. Enter your UPI PIN to receive money in your bank account.", "upi_collect"),
            ("Congratulations! You have been selected for part-time work from home. Earn Rs 2500-5000 daily by liking YouTube videos. Contact on Telegram @work_hr", "job_scam"),
            ("FedEx Express: Your parcel #FX-9821 cannot be delivered due to unpaid customs fee of Rs 480. Pay now or package will be returned: http://fedex-customs-india.xyz", "customs"),
            ("TRAI Alert: Your mobile SIM number will be disconnected within 2 hours due to illegal activity and Aadhaar mismatch. Call customer executive 9823411122.", "sim_disconnect")
        ]
        
        for text, category in strict_scams:
            res = self.predictor.predict_text(text)
            self.assertEqual(res["verdict"], "Scam", f"Expected strict 'Scam' for {category}: got {res['verdict']} ({res['risk_score']}%)")
            self.assertGreaterEqual(res["risk_score"], 70)
            self.assertGreater(len(res["reasons"]), 0)

    # =================================================================
    # 3. [P0] FALSE-POSITIVE STRESS TESTING (LEGITIMATE COMMUNICATIONS)
    # =================================================================
    def test_false_positive_stress(self):
        """Legitimate communications must strictly receive a 'Safe' verdict."""
        legitimate_messages = [
            ("Dear Customer, 849201 is your one time password (OTP) for SBI Internet Banking login. Valid for 3 mins. Never share OTP with anyone.", "sbi_otp"),
            ("Dear Customer, your Swiggy order from Biryani Blues is out for delivery. Delivery partner Ravi will reach you shortly.", "swiggy_delivery"),
            ("Your PNR 2451982301 for Train 12301 NDLS RAJDHANI is confirmed. Coach B3 Berth 42. Check PNR status at www.irctc.co.in.", "irctc_train"),
            ("Dear Consumer, your Tata Power DDL electricity bill for CA No 60012345678 of Rs 2140 is due on 25-Nov. Pay via official portal.", "tata_power_bill"),
            ("Dear Customer, Rs 1,250.00 debited from HDFC Bank A/C ending 4589 on 18-NOV-26 towards UPI-Merchant. Bal: Rs 42,310.20.", "hdfc_debit"),
            ("Aadhaar OTP for authentication is 912048. Generated at 14:22 hrs. Valid for 10 minutes. Unique Identification Authority of India.", "aadhaar_otp"),
            ("Hi Priya, are we meeting at Starbucks Connaught Place at 5 PM today? Let me know if you are running late.", "personal_chat")
        ]
        
        for text, category in legitimate_messages:
            res = self.predictor.predict_text(text)
            self.assertEqual(res["verdict"], "Safe", f"False positive detected for {category}: got {res['verdict']} ({res['risk_score']}%)")
            self.assertLess(res["risk_score"], 40)

    # =================================================================
    # 4. [P1] MULTILINGUAL (HINGLISH) & OBFUSCATED SCAMS
    # =================================================================
    def test_hinglish_and_obfuscated_messages(self):
        """Tests detection of Hinglish phrases and de-obfuscation."""
        hinglish_sample = "Aapka account band ho jayega agar turant KYC update nahi kiya. Kripya is link par jaakar OTP bataye: http://sbi-alert.top/pan"
        res_h = self.predictor.predict_text(hinglish_sample)
        self.assertIn(res_h["verdict"], ["Scam", "Suspicious"])
        self.assertGreaterEqual(res_h["risk_score"], 50)
        
        # Test Unicode homoglyphs and spaced keywords: 'Dеаr' (Cyrillic), 'K Y C', 'fr.ee'
        obfuscated_sample = "Dеаr user, your K Y C is pending. Get fr.ee reward: http://bonus.xyz"
        res_obf = self.predictor.predict_text(obfuscated_sample)
        self.assertEqual(res_obf["metadata"]["has_obfuscated_terms"], 1)

    # =================================================================
    # 5. [P1] MULTIPLE URLS IN SINGLE MESSAGE
    # =================================================================
    def test_multiple_urls_in_message(self):
        """Tests handling of multiple embedded URLs in text."""
        multi_url_text = (
            "Check official guidelines at https://cybercrime.gov.in/ "
            "but click here immediately to clear your arrest warrant: http://delhi-police-digital-arrest-skype.top/investigation"
        )
        extracted = self.predictor.preprocessor.url_pattern.findall(multi_url_text)
        self.assertGreaterEqual(len(extracted), 2)
        
        comb_res = self.predictor.predict_combined(text=multi_url_text)
        self.assertEqual(comb_res["verdict"], "Scam")
        self.assertGreaterEqual(comb_res["risk_score"], 70)

    # =================================================================
    # 6. [P1] URL PHISHING & LEGITIMATE TESTS (HTTP & HTTPS)
    # =================================================================
    def test_url_phishing_strict(self):
        """Tests phishing URLs including HTTPS counterexamples."""
        phishing_urls = [
            "http://sbi-kyc-verify.top/sbi.apk",
            "http://192.168.1.104/secure-bank-login/",
            "http://hdfc-card-unlock.xyz/verify",
            "https://sbi-kyc-verify.top/sbi.apk",  # HTTPS phishing
            "https://customs-clearance-india.top/package"
        ]
        for u in phishing_urls:
            res = self.predictor.predict_url(u)
            self.assertIn(res["verdict"], ["Scam", "Suspicious"], f"Failed for phishing URL: {u}")
            self.assertGreaterEqual(res["risk_score"], 50)

    def test_url_legitimate_strict(self):
        """Tests authentic trusted domains including HTTP counterexamples."""
        legitimate_urls = [
            "https://www.onlinesbi.sbi/",
            "https://netbanking.hdfcbank.com/netbanking/",
            "https://cybercrime.gov.in/",
            "https://uidai.gov.in/",
            "http://example.com/"  # HTTP legitimate
        ]
        for u in legitimate_urls:
            res = self.predictor.predict_url(u)
            self.assertEqual(res["verdict"], "Safe", f"False positive for safe URL: {u} (got {res['risk_score']}%)")
            self.assertLess(res["risk_score"], 35)

    # =================================================================
    # 7. [P1] MISSING MODEL FILES GRACEFUL HEURISTIC FALLBACK
    # =================================================================
    def test_missing_model_files_fallback(self):
        """Tests that predictor operates gracefully in rule-based fallback mode if model files are missing."""
        fallback_predictor = ScamLensPredictor(models_dir="/tmp/non_existent_models_dir_xyz")
        self.assertIsNone(fallback_predictor.text_model)
        self.assertIsNone(fallback_predictor.url_model)
        
        # Test text prediction in fallback mode
        res_text = fallback_predictor.predict_text("Electricity will be disconnected tonight. Call officer at 9876543210.")
        self.assertEqual(res_text["verdict"], "Scam")
        self.assertTrue(res_text["is_fallback"])
        
        # Test URL prediction in fallback mode
        res_url = fallback_predictor.predict_url("http://sbi-kyc.top/verify.apk")
        self.assertIn(res_url["verdict"], ["Scam", "Suspicious"])
        self.assertTrue(res_url["is_fallback"])

    # =================================================================
    # 8. [P2] AGENT INVESTIGATION ENGINE & ORCHESTRATION
    # =================================================================
    def test_agent_investigation_orchestration(self):
        """Tests multi-tool autonomous investigation workflow."""
        sample_scam = (
            "Delhi Police Cyber Cell: A parcel in your name containing illegal narcotics has been seized "
            "at Mumbai airport. Digital arrest warrant issued. Contact CBI Officer on Skype: http://cbi-investigation.top/court"
        )
        report = self.agent.investigate(text=sample_scam)
        self.assertEqual(report["verdict"], "Scam")
        self.assertGreaterEqual(report["risk_score"], 70)
        self.assertGreater(len(report["investigation_trace"]), 3)
        self.assertGreater(len(report["structured_trace"]), 0)
        self.assertGreater(len(report["matched_signatures"]), 0)
        self.assertEqual(report["matched_signatures"][0]["id"], "digital_arrest")

    # =================================================================
    # 9. [P2] METADATA & MODEL VERSIONING
    # =================================================================
    def test_model_metadata(self):
        """Verifies metadata and version inspection."""
        meta = self.predictor.get_model_metadata()
        self.assertTrue(meta["text_model_loaded"])
        self.assertTrue(meta["url_model_loaded"])
        self.assertEqual(meta["engine_version"], "2.1.0")


def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestScamLensML)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        print(f"[FAIL] {len(result.failures)} failures, {len(result.errors)} errors.")
        sys.exit(1)
    else:
        print("\n" + "="*60)
        print("[SUCCESS] All 10 ScamLens Comprehensive Test Suites Passed!")
        print("="*60)


if __name__ == "__main__":
    run_tests()
