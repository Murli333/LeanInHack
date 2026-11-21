"""
Unit tests for trusted domain allowlist validation (signals.py).
Tests official bank/government domain matching and context preservation.
"""

import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_DETECTION_DIR = os.path.dirname(_HERE)
if _DETECTION_DIR not in sys.path:
    sys.path.insert(0, _DETECTION_DIR)

import signals


class TestAllowlistValidation(unittest.TestCase):

    def test_official_bank_domains_are_trusted(self):
        self.assertTrue(signals._is_trusted("sbi.co.in"))
        self.assertTrue(signals._is_trusted("www.onlinesbi.sbi"))
        self.assertTrue(signals._is_trusted("hdfcbank.com"))
        self.assertTrue(signals._is_trusted("icicibank.com"))
        self.assertTrue(signals._is_trusted("axisbank.com"))
        self.assertTrue(signals._is_trusted("kotak.com"))

    def test_official_government_domains_are_trusted(self):
        self.assertTrue(signals._is_trusted("cybercrime.gov.in"))
        self.assertTrue(signals._is_trusted("uidai.gov.in"))
        self.assertTrue(signals._is_trusted("incometax.gov.in"))
        self.assertTrue(signals._is_trusted("digilocker.gov.in"))
        self.assertTrue(signals._is_trusted("irctc.co.in"))

    def test_subdomains_of_trusted_are_trusted(self):
        self.assertTrue(signals._is_trusted("netbanking.hdfcbank.com"))
        self.assertTrue(signals._is_trusted("retail.onlinesbi.sbi"))
        self.assertTrue(signals._is_trusted("foservices.incometax.gov.in"))

    def test_lookalikes_are_NOT_trusted(self):
        self.assertFalse(signals._is_trusted("sbi-kyc-verify.top"))
        self.assertFalse(signals._is_trusted("hdfc-netbanking.site"))
        self.assertFalse(signals._is_trusted("irctc-booking.xyz"))
        self.assertFalse(signals._is_trusted("onlinesbi.com.fakeportal.ru"))

    def test_trusted_domain_skips_phishing_url_signal(self):
        res = signals.signal_phishing_url("Check PNR at https://www.irctc.co.in/nget")
        self.assertFalse(res["triggered"])

    def test_trusted_domain_does_not_suppress_content_signals(self):
        # Even if a trusted domain is linked, an urgent threat or PIN request must still trigger!
        msg = "Enter your UPI PIN to claim ₹2,000 cashback from Amazon: https://www.amazon.in"
        res = signals.analyze_signals(msg)
        self.assertGreater(res["signal_count"], 0)
        self.assertIn("UPI Collect Request Fraud", res["scam_types"])


if __name__ == "__main__":
    unittest.main()
