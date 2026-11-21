"""
Unit tests for URL extraction, domain matching, and blocklist validation (signals.py).
"""

import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_DETECTION_DIR = os.path.dirname(_HERE)
if _DETECTION_DIR not in sys.path:
    sys.path.insert(0, _DETECTION_DIR)

import signals


class TestURLExtractionAndMatching(unittest.TestCase):

    def test_extract_standard_https_url(self):
        text = "Visit https://www.onlinesbi.sbi/portal to log in."
        urls = signals._extract_urls(text)
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0], "https://www.onlinesbi.sbi/portal")

    def test_strip_trailing_sentence_punctuation(self):
        text = "Check your train status at https://www.irctc.co.in."
        urls = signals._extract_urls(text)
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0], "https://www.irctc.co.in")
        self.assertFalse(urls[0].endswith("."))

    def test_strip_trailing_comma_exclamation_question(self):
        for text in [
            "Go to http://sbi-kyc-verify.top/update,",
            "Beware of http://sbi-kyc-verify.top/update!",
            "Did you visit http://sbi-kyc-verify.top/update?",
        ]:
            urls = signals._extract_urls(text)
            self.assertEqual(len(urls), 1)
            self.assertEqual(urls[0], "http://sbi-kyc-verify.top/update")

    def test_deobfuscate_spaced_dots_and_hyphens(self):
        text = "Visit sbi - kyc .top for urgent update"
        urls = signals._extract_urls(text)
        self.assertIn("sbi-kyc.top", urls)

    def test_url_parser_robustness(self):
        # Empty string
        raw, scheme, domain, path = signals._parse_url("")
        self.assertEqual(domain, "")

        # Scheme-less URL
        raw, scheme, domain, path = signals._parse_url("sbi-kyc-verify.top/update.apk")
        self.assertEqual(domain, "sbi-kyc-verify.top")

        # URL with port and query
        raw, scheme, domain, path = signals._parse_url("http://sbi-kyc.top:8080/test?user=123")
        self.assertEqual(domain, "sbi-kyc.top")

    def test_registrable_domain_co_in(self):
        self.assertEqual(signals._registrable_domain("secure.netbanking.sbi.co.in"), "sbi.co.in")
        self.assertEqual(signals._registrable_domain("www.irctc.co.in"), "irctc.co.in")
        self.assertEqual(signals._registrable_domain("login.hdfcbank.com"), "hdfcbank.com")
        self.assertEqual(signals._registrable_domain("sub.sbi-kyc-verify.top"), "sbi-kyc-verify.top")

    def test_blocklist_matching_direct_and_subdomain(self):
        # Direct domain
        self.assertIsNotNone(signals._is_blocklisted("sbi-kyc-verify.top"))
        # Subdomain
        self.assertIsNotNone(signals._is_blocklisted("login.sbi-kyc-verify.top"))
        # Non-blocklisted domain
        self.assertIsNone(signals._is_blocklisted("example-unknown-domain.com"))

    def test_url_shortener_identification(self):
        self.assertTrue(signals._is_shortener("bit.ly"))
        self.assertTrue(signals._is_shortener("tinyurl.com"))
        self.assertTrue(signals._is_shortener("t.me"))
        self.assertFalse(signals._is_shortener("google.com"))

    def test_phishing_url_signal_triggers_on_blocklist(self):
        res = signals.signal_phishing_url("Check http://sbi-kyc-verify.top/sbi.apk")
        self.assertTrue(res["triggered"])
        self.assertEqual(res["scam_type"], "Known Phishing URL")

    def test_phishing_url_signal_triggers_on_shortener(self):
        res = signals.signal_phishing_url("Click https://bit.ly/cashback-offer now")
        self.assertTrue(res["triggered"])
        self.assertEqual(res["scam_type"], "Shortened / Opaque URL")

    def test_phishing_url_signal_triggers_on_suspicious_tld(self):
        res = signals.signal_phishing_url("Check out http://cheap-tickets.xyz/sale")
        self.assertTrue(res["triggered"])
        self.assertIn("High-Risk Domain Extension", res["scam_type"])


if __name__ == "__main__":
    unittest.main()
