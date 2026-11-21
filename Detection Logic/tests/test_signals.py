"""
Unit tests for ScamLens individual scam signals (Member 2: signals.py).
Tests all 16 scam detectors with authentic Indian scam patterns.
"""

import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_DETECTION_DIR = os.path.dirname(_HERE)
if _DETECTION_DIR not in sys.path:
    sys.path.insert(0, _DETECTION_DIR)

import signals


class TestIndividualSignals(unittest.TestCase):
    """Tests each signal function in isolation."""

    def test_signal_fake_kyc_triggers_on_urgent_bank_sms(self):
        msg = "Dear SBI user, your YONO account is suspended. Update KYC at http://sbi-kyc-verify.top immediately."
        res = signals.signal_fake_kyc(msg)
        self.assertTrue(res["triggered"])
        self.assertEqual(res["signal_id"], "FAKE_KYC")
        self.assertEqual(res["severity"], 3)

    def test_signal_fake_kyc_triggers_on_hinglish(self):
        msg = "Aapka HDFC khata band ho jayega kyonki KYC update nahi hai. Abhi link par click karke update karein."
        res = signals.signal_fake_kyc(msg)
        self.assertTrue(res["triggered"])

    def test_signal_fake_kyc_does_not_trigger_on_branch_visit(self):
        msg = "Dear Customer, please visit your nearest SBI home branch with original Aadhaar to update re-KYC before 31-Dec."
        res = signals.signal_fake_kyc(msg)
        self.assertFalse(res["triggered"])

    def test_signal_upi_collect_request(self):
        msg = "You have received UPI collect request of Rs 4,999 from Amazon. Enter UPI PIN to receive cashback."
        res = signals.signal_upi_collect_request(msg)
        self.assertTrue(res["triggered"])
        self.assertEqual(res["signal_id"], "UPI_COLLECT_REQUEST")
        self.assertEqual(res["severity"], 3)

    def test_signal_parcel_customs_threat(self):
        msg = "FedEx Customs Notice: Illegal contraband seized in your package at Mumbai airport. Customs clearance fee Rs 1,500 due."
        res = signals.signal_parcel_customs_threat(msg)
        self.assertTrue(res["triggered"])
        self.assertEqual(res["signal_id"], "PARCEL_CUSTOMS_THREAT")

    def test_signal_digital_arrest(self):
        msg = "Delhi Police Cyber Cell: Digital arrest warrant issued against you for narcotics trafficking. Connect on Skype."
        res = signals.signal_digital_arrest(msg)
        self.assertTrue(res["triggered"])
        self.assertEqual(res["signal_id"], "DIGITAL_ARREST")

    def test_signal_digital_arrest_bypasses_advisory(self):
        msg = "Advisory from Delhi Police: Real police never arrests online or places anyone under digital arrest. Stay vigilant."
        res = signals.signal_digital_arrest(msg)
        self.assertFalse(res["triggered"])

    def test_signal_job_offer_scam(self):
        msg = "Earn Rs 3000 daily part time work from home by liking YouTube videos. Join Telegram @easy_earn."
        res = signals.signal_job_offer_scam(msg)
        self.assertTrue(res["triggered"])
        self.assertEqual(res["signal_id"], "JOB_OFFER_SCAM")

    def test_signal_electricity_bill_threat(self):
        msg = "Electricity power will be disconnected TONIGHT at 9:30 PM due to unpaid bill. Call electricity officer 9876543210 immediately."
        res = signals.signal_electricity_bill_threat(msg)
        self.assertTrue(res["triggered"])
        self.assertEqual(res["signal_id"], "ELECTRICITY_BILL_THREAT")

    def test_signal_electricity_bill_bypasses_genuine_bill(self):
        msg = "Dear Consumer, your BSES electricity bill for CA No 60012345678 of Rs 2,140 is due on 25-Nov. Pay via official portal."
        res = signals.signal_electricity_bill_threat(msg)
        self.assertFalse(res["triggered"])

    def test_signal_otp_phishing(self):
        msg = "Bank verification agent needs your 6-digit OTP to unblock debit card. Share OTP on call."
        res = signals.signal_otp_phishing(msg)
        self.assertTrue(res["triggered"])
        self.assertEqual(res["signal_id"], "OTP_PHISHING")

    def test_signal_otp_phishing_bypasses_legitimate_otp(self):
        msg = "849201 is your OTP for transaction of Rs 500. NEVER share your OTP with anyone. Bank never asks for OTP."
        res = signals.signal_otp_phishing(msg)
        self.assertFalse(res["triggered"])

    def test_signal_loan_fraud(self):
        msg = "Instant loan of Rs 5 Lakh without CIBIL check and zero documents. 0% interest rate. WhatsApp 9876543210."
        res = signals.signal_loan_fraud(msg)
        self.assertTrue(res["triggered"])
        self.assertEqual(res["signal_id"], "LOAN_FRAUD")

    def test_signal_lottery_prize_scam(self):
        msg = "Congratulations! Your mobile number won Rs 25,00,000 in KBC Lucky Draw 2024. Pay Rs 2100 registration fee to claim."
        res = signals.signal_prize_lottery_scam(msg)
        self.assertTrue(res["triggered"])
        self.assertEqual(res["signal_id"], "PRIZE_LOTTERY_SCAM")

    def test_signal_investment_scam(self):
        msg = "Guaranteed stock market returns of 50% monthly profit. Join our VIP Telegram channel for sure shot tips."
        res = signals.signal_investment_scam(msg)
        self.assertTrue(res["triggered"])
        self.assertEqual(res["signal_id"], "INVESTMENT_SCAM")

    def test_signal_romance_sextortion(self):
        msg = "I recorded our private video call. Transfer Rs 10,000 immediately or I will make video viral."
        res = signals.signal_romance_sextortion(msg)
        self.assertTrue(res["triggered"])
        self.assertEqual(res["signal_id"], "ROMANCE_SEXTORTION")

    def test_signal_fake_customer_care(self):
        msg = "Refund department: Install AnyDesk app from Play Store and share the 9-digit code to receive refund."
        res = signals.signal_fake_customer_care(msg)
        self.assertTrue(res["triggered"])
        self.assertEqual(res["signal_id"], "FAKE_CUSTOMER_CARE")

    def test_signal_money_mule(self):
        msg = "We need an Indian bank account to receive company funds of Rs 25 Lakhs. Keep 10% commission and forward the rest."
        res = signals.signal_money_mule(msg)
        self.assertTrue(res["triggered"])
        self.assertEqual(res["signal_id"], "MONEY_MULE")


if __name__ == "__main__":
    unittest.main()
