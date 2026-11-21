"""
Unit tests for false-positive and false-negative prevention scenarios (signals.py).
"""

import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_DETECTION_DIR = os.path.dirname(_HERE)
if _DETECTION_DIR not in sys.path:
    sys.path.insert(0, _DETECTION_DIR)

import signals


class TestFalsePositiveAndNegativeScenarios(unittest.TestCase):

    def test_fp_prevention_on_train_pnr_with_period(self):
        msg = "Your PNR 2451982301 for Train 12301 is Confirmed. Check status at https://www.irctc.co.in."
        res = signals.analyze_signals(msg)
        self.assertEqual(res["signal_count"], 0)
        self.assertEqual(res["heuristic_risk_boost"], 0)

    def test_fp_prevention_on_scheduled_maintenance(self):
        msg = "BSES Power Notice: Scheduled maintenance will take place in Sector 4 on Tuesday between 11 AM and 2 PM."
        res = signals.analyze_signals(msg)
        self.assertEqual(res["signal_count"], 0)

    def test_fp_prevention_on_personal_congratulations(self):
        msg = "Congratulations on your new job at Google! So proud of you. Let's celebrate tonight."
        res = signals.analyze_signals(msg)
        self.assertEqual(res["signal_count"], 0)

    def test_fp_prevention_on_rbi_advisory(self):
        msg = "RBI Advisory: Beware of unauthorized loan apps offering instant loans without documentation."
        res = signals.analyze_signals(msg)
        self.assertEqual(res["signal_count"], 0)

    def test_fn_prevention_on_spaced_acronym_k_y_c(self):
        msg = "Your account k y c is expired. Update immediately: sbi - kyc .top"
        res = signals.analyze_signals(msg)
        self.assertGreaterEqual(res["signal_count"], 1)
        self.assertTrue("Fake KYC Update" in res["scam_types"] or "Known Phishing URL" in res["scam_types"])

    def test_fn_prevention_on_hindi_bijli_katega(self):
        msg = "Priya consumer, aapka bijli connection aaj raat katega. Abhi contact karein bijli officer se."
        res = signals.analyze_signals(msg)
        self.assertGreaterEqual(res["signal_count"], 1)
        self.assertIn("Electricity Bill Disconnection Scam", res["scam_types"])

    def test_fn_prevention_on_hinglish_pin_dalo(self):
        msg = "Cashback receive karne ke liye Google Pay mein UPI PIN daalo turant."
        res = signals.analyze_signals(msg)
        self.assertGreaterEqual(res["signal_count"], 1)
        self.assertIn("UPI Collect Request Fraud", res["scam_types"])


if __name__ == "__main__":
    unittest.main()
