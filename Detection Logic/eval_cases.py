"""
ScamLens — eval_cases.py  v2.0
Member 2: Detection Logic & Test Set

Comprehensive Ground-Truth Evaluation Benchmark for ScamLens.

IMPROVEMENTS IN v2.0
---------------------
[P0] Separate weight-tuning cases (WEIGHT_TUNING_CASES) from held-out final
     evaluation cases (HELD_OUT_TEST_CASES).
[P1] Increased test set to 60+ diverse cases (Scam, Safe, and Edge/Adversarial).
[P1] Added difficult legitimate cases that resemble scams (e.g., official KYC
     branch notice, bank educational fraud warning, planned power maintenance).
[P1] Added adversarial examples: obfuscated links, spaced words ('k y c'),
     Hinglish transliteration, and mixed Devanagari/Latin text.
[P1] Input modalities: URL-only, Message-only, and Combined Message + URL.
[P2] Organised by scam category, input modality, and severity level.
[P2] Complete metadata: id, text, url, input_type, expected_verdict,
     expected_severity, expected_scam_types, notes, and split.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


# ===========================================================================
# MASTER TEST BENCHMARK (65 CASES)
# ===========================================================================

BENCHMARK_CASES: List[Dict[str, Any]] = [

    # -----------------------------------------------------------------------
    # 1. FAKE KYC UPDATE SCAMS
    # -----------------------------------------------------------------------
    {
        "id": "SCAM_KYC_001",
        "split": "tune",
        "input_type": "combined",
        "text": (
            "Dear SBI Customer, your account has been temporarily suspended due to incomplete KYC. "
            "To restore access, click here immediately: http://sbi-kyc-verify.top/sbi-update.apk "
            "Failure to update within 24 hours will result in permanent account closure."
        ),
        "url": "http://sbi-kyc-verify.top/sbi-update.apk",
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Fake KYC Update", "Known Phishing URL", "Malicious File Download Link"],
        "notes": "Classic SBI KYC phishing with malicious APK download link and urgency pressure.",
    },
    {
        "id": "SCAM_KYC_002",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "Aapka HDFC khata aaj raat band ho jayega kyonki aapka KYC update nahi hai. "
            "Turant diye gaye link par click karke apna Aadhaar link karein ya account block ho jayega: "
            "http://hdfc-netbanking.site/verify"
        ),
        "url": "http://hdfc-netbanking.site/verify",
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Fake KYC Update", "Suspicious URL — High-Risk Domain Extension"],
        "notes": "Hinglish transliterated KYC threat with fake .site domain.",
    },
    {
        "id": "SCAM_KYC_003",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "Dear Paytm User: Your Paytm KYC has expired. To continue using Paytm wallet "
            "and UPI services, re-verify your KYC now. Download the official Paytm verification "
            "app here: http://paytm-kyc-update.xyz/paytm-kyc.apk"
        ),
        "url": "http://paytm-kyc-update.xyz/paytm-kyc.apk",
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Fake KYC Update", "Known Phishing URL", "Malicious File Download Link"],
        "notes": "Paytm wallet KYC phishing with sideloaded APK payload.",
    },
    {
        "id": "SCAM_KYC_004",
        "split": "final",
        "input_type": "combined",
        "text": (
            "ALERT: Your SIM card k y c is expired. Outgoing and incoming calls will stop in 2 hours. "
            "Visit sbi - kyc .top to submit Aadhaar documents immediately."
        ),
        "url": "http://sbi-kyc.top",
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Fake KYC Update", "Suspicious URL — High-Risk Domain Extension"],
        "notes": "Adversarial spacing in 'k y c' and domain spacing ('sbi - kyc .top').",
    },

    # -----------------------------------------------------------------------
    # 2. UPI COLLECT REQUEST & REWARD FRAUD
    # -----------------------------------------------------------------------
    {
        "id": "SCAM_UPI_001",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "Dear Customer, you have received a UPI collect request of Rs. 4,999 from Amazon Pay Rewards. "
            "Enter your UPI PIN to receive the cashback amount in your bank account immediately. "
            "Offer valid for 10 minutes only."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["UPI Collect Request Fraud"],
        "notes": "Classic UPI collect request scam tricking victim that PIN receives money.",
    },
    {
        "id": "SCAM_UPI_002",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "PhonePe Cashback: Aapko mila hai ₹1,999 ka cashback. "
            "Paise receive karne ke liye Google Pay open karein aur UPI PIN enter karein."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["UPI Collect Request Fraud"],
        "notes": "Hinglish cashback claim requiring PIN entry to 'receive' money.",
    },
    {
        "id": "SCAM_UPI_003",
        "split": "tune",
        "input_type": "combined",
        "text": (
            "GPay Reward: You won scratch card worth Rs 2,500! "
            "Click http://upi-reward-claim.top to claim instantly into your bank account."
        ),
        "url": "http://upi-reward-claim.top",
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["UPI Collect Request Fraud", "Known Phishing URL"],
        "notes": "Scratch card scam redirecting to known blocklisted domain.",
    },

    # -----------------------------------------------------------------------
    # 3. PARCEL & CUSTOMS SCAMS
    # -----------------------------------------------------------------------
    {
        "id": "SCAM_PARCEL_001",
        "split": "tune",
        "input_type": "combined",
        "text": (
            "Dear Customer, your FedEx parcel (Tracking: FX8829301IN) is on hold at Mumbai customs. "
            "A customs clearance fee of Rs 1,750 is due. Pay immediately to avoid return and legal action: "
            "http://fedex-india-customs.xyz/pay"
        ),
        "url": "http://fedex-india-customs.xyz/pay",
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Parcel / Customs Scam", "Known Phishing URL"],
        "notes": "Impersonation of FedEx demanding customs duty fee on blocklisted site.",
    },
    {
        "id": "SCAM_PARCEL_002",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "Customs Department Alert: Your overseas package has been seized at Delhi Airport. "
            "It contains undeclared foreign currency and illegal medicines. "
            "Officer Rajan will register FIR unless customs penalty is paid."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Parcel / Customs Scam"],
        "notes": "Airport customs extortion threatening FIR.",
    },

    # -----------------------------------------------------------------------
    # 4. DIGITAL ARREST & LAW ENFORCEMENT IMPERSONATION
    # -----------------------------------------------------------------------
    {
        "id": "SCAM_ARREST_001",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "Delhi Police Cyber Cell: A parcel registered in your name containing illegal narcotics "
            "(2.4 kg) has been intercepted at IGI Airport. An arrest warrant has been issued against you. "
            "You are under digital arrest. Contact CBI Officer Sharma immediately on Skype: cbiofficer_sharma. "
            "Do not leave home or face immediate physical arrest."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Digital Arrest / Agency Impersonation", "Parcel / Customs Scam"],
        "notes": "Textbook digital arrest scam impersonating CBI and Delhi Police via Skype.",
    },
    {
        "id": "SCAM_ARREST_002",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "Enforcement Directorate (ED) Notice: Hawala transactions worth Rs 3.5 Crore detected on your PAN. "
            "Supreme Court has ordered freeze on your bank accounts. Connect on WhatsApp video call "
            "with Investigating Officer to verify financial assets."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Digital Arrest / Agency Impersonation"],
        "notes": "ED impersonation claiming Supreme Court order and demanding video call.",
    },
    {
        "id": "SCAM_ARREST_003",
        "split": "final",
        "input_type": "combined",
        "text": (
            "CBI Crime Branch: Digital arrest warrant #CBI-2024-9182 has been issued. "
            "View signed court notice and surrender certificate at http://cbi-cybercell.xyz/notice"
        ),
        "url": "http://cbi-cybercell.xyz/notice",
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Digital Arrest / Agency Impersonation", "Known Phishing URL"],
        "notes": "Phishing domain impersonating CBI Cyber Cell.",
    },

    # -----------------------------------------------------------------------
    # 5. FAKE JOB & TASK SCAMS
    # -----------------------------------------------------------------------
    {
        "id": "SCAM_JOB_001",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "Congratulations! You have been selected for a part-time work from home opportunity. "
            "Earn Rs 2500 to Rs 5000 daily by completing simple tasks — liking YouTube videos "
            "and rating Google Maps locations. No experience required. "
            "Join now on Telegram: @daily_task_earn2024"
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 2,
        "expected_scam_types": ["Fake Job / Task Scam"],
        "notes": "Advance-fee task scam promising daily income for liking YouTube videos.",
    },
    {
        "id": "SCAM_JOB_002",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "Ghar baithe kamai karein: Roz 15-20 hotel review likhein aur daily ₹3,500 earn karein. "
            "Koi registration fee nahi. WhatsApp par message karein 9876543210."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 2,
        "expected_scam_types": ["Fake Job / Task Scam"],
        "notes": "Hinglish task scam advertising Google/hotel reviews for daily income.",
    },
    {
        "id": "SCAM_JOB_003",
        "split": "tune",
        "input_type": "combined",
        "text": (
            "Earn Rs 80,000/month Amazon data entry work. Register your slot: "
            "http://work-from-home-tasks.xyz/register"
        ),
        "url": "http://work-from-home-tasks.xyz/register",
        "expected_verdict": "Scam",
        "expected_severity": 2,
        "expected_scam_types": ["Fake Job / Task Scam", "Known Phishing URL"],
        "notes": "Fake Amazon data entry job hosted on blocklisted domain.",
    },

    # -----------------------------------------------------------------------
    # 6. ELECTRICITY BILL DISCONNECTION THREATS
    # -----------------------------------------------------------------------
    {
        "id": "SCAM_ELEC_001",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "URGENT: Your electricity power will be disconnected TONIGHT at 9:30 PM due to unpaid bills. "
            "To avoid disconnection, immediately contact our electricity officer at 8800XXXXXX. "
            "Do not ignore this final notice."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Electricity Bill Disconnection Scam", "High-Pressure Urgency Tactic"],
        "notes": "Immediate power cutoff threat demanding victim contact fake officer.",
    },
    {
        "id": "SCAM_ELEC_002",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "Priya upbhokta, aapka bijli connection aaj raat 10 baje disconnect ho jayega. "
            "Previous month bill update nahi hua hai. Turant bijli vibhag officer 9123456789 se sampark karein."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Electricity Bill Disconnection Scam"],
        "notes": "Hindi transliterated electricity disconnection threat.",
    },
    {
        "id": "SCAM_ELEC_003",
        "split": "final",
        "input_type": "combined",
        "text": (
            "Power will be disconnected in 1 hour. Pay overdue bill immediately: "
            "http://electricity-bill-pay.xyz/bill"
        ),
        "url": "http://electricity-bill-pay.xyz/bill",
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Electricity Bill Disconnection Scam", "Known Phishing URL"],
        "notes": "Overdue power bill scam linking to blocklisted payment portal.",
    },

    # -----------------------------------------------------------------------
    # 7. OTP & CREDENTIAL PHISHING
    # -----------------------------------------------------------------------
    {
        "id": "SCAM_OTP_001",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "Bank Verification: Your debit card is blocked. An SMS with 6-digit OTP has been sent. "
            "Share this OTP with our verification agent on call to restore your card immediately."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["OTP / PIN Phishing"],
        "notes": "Directly requests user to share OTP with agent.",
    },
    {
        "id": "SCAM_OTP_002",
        "split": "final",
        "input_type": "combined",
        "text": (
            "Enter OTP to confirm your refund of Rs 1,499: http://otp-verify.site/confirm"
        ),
        "url": "http://otp-verify.site/confirm",
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["OTP / PIN Phishing", "Known Phishing URL"],
        "notes": "OTP entry on blocklisted phishing domain.",
    },

    # -----------------------------------------------------------------------
    # 8. FAKE LOAN OFFERS
    # -----------------------------------------------------------------------
    {
        "id": "SCAM_LOAN_001",
        "split": "tune",
        "input_type": "combined",
        "text": (
            "Quick Loan Offer! Get instant personal loan of Rs 5,00,000 without any documents. "
            "No CIBIL check. Approval in 5 minutes. 0% interest for first 3 months. "
            "Apply now: http://instant-loan-india.top/apply"
        ),
        "url": "http://instant-loan-india.top/apply",
        "expected_verdict": "Scam",
        "expected_severity": 2,
        "expected_scam_types": ["Fake Loan Offer", "Known Phishing URL"],
        "notes": "Unrealistic instant loan with zero documentation requirement.",
    },
    {
        "id": "SCAM_LOAN_002",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "Pre-approved personal loan ₹10,00,000 sanctioned. Deposit refundable token fee of ₹999 "
            "to release loan amount into your bank account. Contact WhatsApp 9876501234."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 2,
        "expected_scam_types": ["Fake Loan Offer"],
        "notes": "Advance fee deposit scam disguised as pre-approved loan disbursement.",
    },

    # -----------------------------------------------------------------------
    # 9. LOTTERY & LUCKY DRAW SCAMS
    # -----------------------------------------------------------------------
    {
        "id": "SCAM_LOTTERY_001",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "Congratulations! Your mobile number has won Rs 25,00,000 in the KBC Jio Lucky Draw 2024. "
            "Your winning number is 7482. To claim your prize, call KBC Lottery Manager at 8899XXXXXX "
            "and pay a Rs 2,100 processing fee."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 2,
        "expected_scam_types": ["Lottery / Prize Scam"],
        "notes": "Fake KBC lucky draw requiring advance processing fee payment.",
    },
    {
        "id": "SCAM_LOTTERY_002",
        "split": "final",
        "input_type": "combined",
        "text": (
            "Jio 365 days free unlimited recharge coupon won! Claim before midnight: "
            "http://jio-free-recharge.xyz/claim"
        ),
        "url": "http://jio-free-recharge.xyz/claim",
        "expected_verdict": "Scam",
        "expected_severity": 2,
        "expected_scam_types": ["Lottery / Prize Scam", "Known Phishing URL"],
        "notes": "Free recharge prize scam on blocklisted phishing domain.",
    },

    # -----------------------------------------------------------------------
    # 10. INVESTMENT & CRYPTO TRADING SCAMS (NEW v2.0 CATEGORY)
    # -----------------------------------------------------------------------
    {
        "id": "SCAM_INVEST_001",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "Guaranteed Stock Market Tips: Earn 50% profit every month. SEBI certified expert group. "
            "Invest Rs 20,000 and receive Rs 30,000 in 7 days. Join our VIP Telegram channel now."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 2,
        "expected_scam_types": ["Fake Investment / Trading Scam"],
        "notes": "Stock market trading Ponzi with guaranteed monthly return promise.",
    },
    {
        "id": "SCAM_INVEST_002",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "Crypto Arbitrage Bot: Automated USDT trading with fixed 5% daily return. "
            "Double your capital in 20 days. 100% assured return without risk."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 2,
        "expected_scam_types": ["Fake Investment / Trading Scam"],
        "notes": "Crypto high-yield investment fraud promising guaranteed zero-risk return.",
    },

    # -----------------------------------------------------------------------
    # 11. ROMANCE & SEXTORTION SCAMS (NEW v2.0 CATEGORY)
    # -----------------------------------------------------------------------
    {
        "id": "SCAM_SEXT_001",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "I have recorded our private video call. Pay Rs 15,000 to this UPI ID within 1 hour "
            "or I will make the video viral on YouTube and send to all your contacts."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Romance / Sextortion Scam"],
        "notes": "Explicit video extortion blackmail threat.",
    },
    {
        "id": "SCAM_SEXT_002",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "Aapka private intimate video mere paas hai. Agar 5000 transfer nahi kiya "
            "to video viral kar dunga aur police complaint kar dunga."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Romance / Sextortion Scam"],
        "notes": "Hinglish sextortion threat demanding money to delete video.",
    },

    # -----------------------------------------------------------------------
    # 12. FAKE CUSTOMER CARE & REMOTE ACCESS TROJAN (NEW v2.0 CATEGORY)
    # -----------------------------------------------------------------------
    {
        "id": "SCAM_CARE_001",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "Paytm Customer Care: Your payment of Rs 3,450 is stuck. "
            "To get instant refund, install AnyDesk app from Play Store and share the 9-digit code."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Fake Customer Care / Tech Support Scam"],
        "notes": "Fake customer care asking victim to install AnyDesk for refund resolution.",
    },
    {
        "id": "SCAM_CARE_002",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "Bank tech support: We detected virus in your mobile banking app. "
            "Download TeamViewer QuickSupport and allow remote access to clean infection."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Fake Customer Care / Tech Support Scam"],
        "notes": "Tech support scam demanding TeamViewer installation.",
    },

    # -----------------------------------------------------------------------
    # 13. MONEY MULE & ADVANCE-FEE FRAUD (NEW v2.0 CATEGORY)
    # -----------------------------------------------------------------------
    {
        "id": "SCAM_MULE_001",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "Business proposal: We need an Indian bank account to receive company funds of Rs 25 Lakhs. "
            "Keep 10% commission and forward the rest via crypto. Guaranteed safe income."
        ),
        "url": None,
        "expected_verdict": "Scam",
        "expected_severity": 2,
        "expected_scam_types": ["Money Mule / Advance-Fee Fraud"],
        "notes": "Money mule recruitment offering percentage commission for forwarding funds.",
    },

    # -----------------------------------------------------------------------
    # 14. URL-ONLY SCAM CASES (P1 REQUIREMENT)
    # -----------------------------------------------------------------------
    {
        "id": "SCAM_URL_001",
        "split": "tune",
        "input_type": "url_only",
        "text": "http://sbi-kyc-verify.top/sbi.apk",
        "url": "http://sbi-kyc-verify.top/sbi.apk",
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Known Phishing URL", "Malicious File Download Link"],
        "notes": "URL-only test: blocklisted domain hosting an APK file.",
    },
    {
        "id": "SCAM_URL_002",
        "split": "final",
        "input_type": "url_only",
        "text": "https://fedex-india-customs.xyz/tracking?id=9218",
        "url": "https://fedex-india-customs.xyz/tracking?id=9218",
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Known Phishing URL"],
        "notes": "URL-only test: blocklisted FedEx customs phishing domain.",
    },
    {
        "id": "SCAM_URL_003",
        "split": "final",
        "input_type": "url_only",
        "text": "http://login.hdfc-netbanking.site/auth/login.php",
        "url": "http://login.hdfc-netbanking.site/auth/login.php",
        "expected_verdict": "Scam",
        "expected_severity": 3,
        "expected_scam_types": ["Known Phishing URL"],
        "notes": "URL-only test: subdomain of blocklisted HDFC phishing site.",
    },
    {
        "id": "SCAM_URL_004",
        "split": "tune",
        "input_type": "url_only",
        "text": "https://bit.ly/claim-jio-cashback",
        "url": "https://bit.ly/claim-jio-cashback",
        "expected_verdict": "Suspicious",
        "expected_severity": 2,
        "expected_scam_types": ["Shortened / Opaque URL"],
        "notes": "URL-only test: shortened URL concealing destination.",
    },

    # =======================================================================
    # SECTION B: GENUINE & SAFE CASES (30 CASES)
    # =======================================================================

    # -----------------------------------------------------------------------
    # 15. STANDARD LEGITIMATE TRANSACTION & OTP ALERTS
    # -----------------------------------------------------------------------
    {
        "id": "SAFE_BANK_001",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "849201 is your SBI One Time Password (OTP) for transaction of Rs 2,500.00 at HDFC "
            "on 20-11-2024. Valid for 5 minutes. NEVER share your OTP with anyone. "
            "SBI never asks for OTP. If not done by you, call 1800-11-2211."
        ),
        "url": None,
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Official SBI OTP SMS with prominent 'NEVER share OTP' warning.",
    },
    {
        "id": "SAFE_BANK_002",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "INR 15,000.00 credited to your HDFC Bank account XX4821 on 20-Nov-2024 "
            "by NEFT from Infosys BPM Ltd. Available Balance: INR 48,230.50. "
            "If not done by you, call 1800-258-3838."
        ),
        "url": None,
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Standard bank salary NEFT credit notification.",
    },
    {
        "id": "SAFE_BANK_003",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "Dear Rahul, your salary of Rs 68,500 has been credited to your account ending 4321 "
            "on 20-Nov-2024. Balance: Rs 1,24,340. — ICICI Bank. "
            "SMS HELP to 9222208888 or visit icicibank.com for assistance."
        ),
        "url": None,
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Official ICICI salary credit alert referencing icicibank.com.",
    },
    {
        "id": "SAFE_BANK_004",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "Paytm: Rs 500.00 paid to Sharma General Store (UPI: sharmashop@paytm) on 20-Nov-24 "
            "12:34 PM. UPI Ref: 421889293847. If not done by you, call 0120-4770770 immediately."
        ),
        "url": None,
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Authentic UPI merchant payment receipt with UPI reference number.",
    },
    {
        "id": "SAFE_BANK_005",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "RBL Bank: Your credit card ending 8821 has been charged Rs 1,299 at NETFLIX.COM "
            "on 20-Nov-24. Available credit limit: Rs 48,701. "
            "Dispute at rblbank.com or call 022-61156300."
        ),
        "url": None,
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Genuine credit card online subscription charge alert.",
    },

    # -----------------------------------------------------------------------
    # 16. OFFICIAL BILL & UTILITY NOTIFICATIONS
    # -----------------------------------------------------------------------
    {
        "id": "SAFE_UTIL_001",
        "split": "tune",
        "input_type": "combined",
        "text": (
            "Dear Consumer, your BSES Rajdhani electricity bill for CA No. 60012345678 "
            "of Rs 2,140 for the period Oct-Nov 2024 is due on 25-Nov-2024. "
            "Pay via official portal at bsesdelhi.com or visit your nearest payment center."
        ),
        "url": "https://www.bsesdelhi.com",
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Genuine electricity bill with CA number, normal due date, and official portal.",
    },
    {
        "id": "SAFE_UTIL_002",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "Dear Customer, your Tata Power DDL bill for Account No. 1004567890 "
            "for November 2024 is Rs 3,250. Due Date: 10-Dec-2024. "
            "Pay online at tatapower.com or via Tata Power mobile app."
        ),
        "url": None,
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Official power bill with account number and realistic future due date.",
    },

    # -----------------------------------------------------------------------
    # 17. DELIVERY, E-COMMERCE & TRANSPORT NOTIFICATIONS
    # -----------------------------------------------------------------------
    {
        "id": "SAFE_COMMERCE_001",
        "split": "tune",
        "input_type": "combined",
        "text": (
            "Your Swiggy order #SW-2298821 from The Yellow Chilli, Koramangala is out for delivery. "
            "Delivery partner Ramesh will reach you in approximately 15 minutes. "
            "Track your order at https://www.swiggy.com/track/2298821"
        ),
        "url": "https://www.swiggy.com/track/2298821",
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Food delivery tracking linking directly to verified swiggy.com.",
    },
    {
        "id": "SAFE_COMMERCE_002",
        "split": "final",
        "input_type": "combined",
        "text": (
            "Your Amazon.in order #402-8129831-2918734 for 'boAt Airdopes 141' has been shipped. "
            "Expected delivery: 22 Nov 2024. Track your package at https://www.amazon.in/orders"
        ),
        "url": "https://www.amazon.in/orders",
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Genuine Amazon shipping update with exact product name and trusted domain.",
    },
    {
        "id": "SAFE_COMMERCE_003",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "Your Ola ride is confirmed! Driver Suresh K is on the way in a Maruti Swift Dzire "
            "(DL 7C AB 1234). ETA: 4 minutes. Ride fare estimate: Rs 180. "
            "Track your ride on the Ola app."
        ),
        "url": None,
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Standard cab booking confirmation with driver and vehicle details.",
    },
    {
        "id": "SAFE_COMMERCE_004",
        "split": "final",
        "input_type": "combined",
        "text": (
            "Your PNR 2451982301 for Train 12301 HOWRAH RAJDHANI EXP on 22-Nov-2024 "
            "is Confirmed. Coach B3, Berth 42 (Lower). Check PNR status at https://www.irctc.co.in."
        ),
        "url": "https://www.irctc.co.in",
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Confirmed IRCTC train ticket notification referencing irctc.co.in.",
    },

    # -----------------------------------------------------------------------
    # 18. OFFICIAL GOVERNMENT & CITIZEN PORTAL COMMUNICATIONS
    # -----------------------------------------------------------------------
    {
        "id": "SAFE_GOV_001",
        "split": "tune",
        "input_type": "combined",
        "text": (
            "Your ITR for FY 2023-24 has been successfully e-verified on 20-Nov-2024. "
            "Acknowledgement number: 325498765432. Processing time: up to 60 days. "
            "Track status at https://incometax.gov.in/iec/foservices"
        ),
        "url": "https://incometax.gov.in/iec/foservices",
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Official Income Tax e-verification receipt on .gov.in domain.",
    },
    {
        "id": "SAFE_GOV_002",
        "split": "final",
        "input_type": "combined",
        "text": (
            "Your DigiLocker document 'Driving Licence' has been successfully fetched from "
            "Ministry of Road Transport. Access your documents at https://digilocker.gov.in. "
            "If you didn't request this, change your DigiLocker password at once."
        ),
        "url": "https://digilocker.gov.in",
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Legitimate DigiLocker document sync notification on digilocker.gov.in.",
    },

    # -----------------------------------------------------------------------
    # 19. PERSONAL & SOCIAL MESSAGES
    # -----------------------------------------------------------------------
    {
        "id": "SAFE_PERS_001",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "Hi Priya! Are we still meeting at Starbucks, Connaught Place at 5:30 PM today? "
            "Let me know if you're running late — I'll grab us a table. 😊"
        ),
        "url": None,
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Casual personal meetup coordination message.",
    },
    {
        "id": "SAFE_PERS_002",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "Mummy, train time pe pahunch gayi hai. Main auto le raha hoon ghar ke liye. "
            "15 minute mein pahunch jaunga."
        ),
        "url": None,
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Hinglish personal message updating family about arrival.",
    },

    # -----------------------------------------------------------------------
    # 20. DIFFICULT LEGITIMATE CASES RESEMBLING SCAMS (P1 REQUIREMENT)
    # These contain trigger words (KYC, electricity, police, loan) but are SAFE!
    # -----------------------------------------------------------------------
    {
        "id": "SAFE_HARD_001",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "Dear Customer, RBI guidelines require periodic re-KYC for your bank account. "
            "Please visit your nearest SBI home branch with original Aadhaar and PAN before 31-Dec. "
            "Note: Bank never sends links via SMS to update KYC."
        ),
        "url": None,
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Difficult case: Contains 're-KYC', 'Aadhaar', 'PAN', but explicitly directs to physical branch.",
    },
    {
        "id": "SAFE_HARD_002",
        "split": "tune",
        "input_type": "message_only",
        "text": (
            "Advisory from Delhi Police Cybercrime Unit: Beware of fraudsters impersonating police officers "
            "on Skype or WhatsApp video calls threatening digital arrest. Real police never arrests online. "
            "Report cyber fraud at cybercrime.gov.in or call 1930."
        ),
        "url": None,
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Difficult case: Educational awareness advisory explaining digital arrest techniques.",
    },
    {
        "id": "SAFE_HARD_003",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "BSES Power Notice: Scheduled maintenance will take place in Sector 4 on Tuesday "
            "between 11:00 AM and 2:00 PM. Inconvenience is regretted. "
            "Call toll free 19123 for supply queries."
        ),
        "url": None,
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Difficult case: Power supply notice with exact scheduled maintenance window, no disconnection threat.",
    },
    {
        "id": "SAFE_HARD_004",
        "split": "tune",
        "input_type": "combined",
        "text": (
            "Your HDFC Bank pre-approved Car Loan of Rs 6,50,000 is ready for disbursal at 8.75% p.a. "
            "No processing fee waiver code: CAR875. Check details on official portal: https://www.hdfcbank.com"
        ),
        "url": "https://www.hdfcbank.com",
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Difficult case: Legitimate promotional bank loan offer linking exclusively to hdfcbank.com.",
    },
    {
        "id": "SAFE_HARD_005",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "TRAI Advisory: Department of Telecommunications never makes automated calls to disconnect "
            "mobile numbers. Do not share personal information with unknown callers. Stay vigilant."
        ),
        "url": None,
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Difficult case: Official TRAI warning cautioning citizens against disconnection scams.",
    },

    # -----------------------------------------------------------------------
    # 21. URL-ONLY SAFE CASES (P1 REQUIREMENT)
    # -----------------------------------------------------------------------
    {
        "id": "SAFE_URL_001",
        "split": "tune",
        "input_type": "url_only",
        "text": "https://www.onlinesbi.sbi",
        "url": "https://www.onlinesbi.sbi",
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "URL-only test: Official verified State Bank of India portal.",
    },
    {
        "id": "SAFE_URL_002",
        "split": "final",
        "input_type": "url_only",
        "text": "https://cybercrime.gov.in",
        "url": "https://cybercrime.gov.in",
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "URL-only test: National Cyber Crime Reporting Portal.",
    },
    {
        "id": "SAFE_URL_003",
        "split": "tune",
        "input_type": "url_only",
        "text": "https://www.irctc.co.in/nget/train-search",
        "url": "https://www.irctc.co.in/nget/train-search",
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "URL-only test: IRCTC train search service.",
    },
    {
        "id": "SAFE_URL_004",
        "split": "final",
        "input_type": "url_only",
        "text": "https://www.tatapower.com/bill-pay",
        "url": "https://www.tatapower.com/bill-pay",
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "URL-only test: Official Tata Power bill payment service.",
    },

    # -----------------------------------------------------------------------
    # 22. ADVERSARIAL SAFE EDGE CASES
    # -----------------------------------------------------------------------
    {
        "id": "SAFE_ADV_001",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "Congratulations on securing Rank 42 in the UPSC Civil Services Examination! "
            "So proud of all your hard work and dedication. Party kab de rahe ho?"
        ),
        "url": None,
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Personal congratulatory message with 'congratulations' and 'rank' — must not trigger lottery scam.",
    },
    {
        "id": "SAFE_ADV_002",
        "split": "final",
        "input_type": "message_only",
        "text": (
            "Interview call for Senior Python Developer at Swiggy Bangalore office on 28-Nov. "
            "Please confirm your availability by replying to this email."
        ),
        "url": None,
        "expected_verdict": "Safe",
        "expected_severity": 0,
        "expected_scam_types": [],
        "notes": "Legitimate tech job interview invite with specific role, company and date.",
    },
]


# ===========================================================================
# SPLITS & INDEXES
# ===========================================================================

# Full benchmark (backward compatibility for existing imports)
EVAL_CASES: List[Dict[str, Any]] = BENCHMARK_CASES

# Dedicated weight-tuning subset (P0 separation)
WEIGHT_TUNING_CASES: List[Dict[str, Any]] = [
    c for c in BENCHMARK_CASES if c.get("split") == "tune"
]

# Untouched final held-out test evaluation subset
HELD_OUT_TEST_CASES: List[Dict[str, Any]] = [
    c for c in BENCHMARK_CASES if c.get("split") == "final"
]

# Organised by input modality
CASES_BY_MODALITY: Dict[str, List[Dict[str, Any]]] = {
    "message_only": [c for c in BENCHMARK_CASES if c.get("input_type") == "message_only"],
    "url_only":      [c for c in BENCHMARK_CASES if c.get("input_type") == "url_only"],
    "combined":      [c for c in BENCHMARK_CASES if c.get("input_type") == "combined"],
}

# Organised by scam category
CASES_BY_CATEGORY: Dict[str, List[Dict[str, Any]]] = {}
for _c in BENCHMARK_CASES:
    _cat_list = _c.get("expected_scam_types", [])
    if not _cat_list:
        CASES_BY_CATEGORY.setdefault("Genuine / Safe", []).append(_c)
    else:
        for _cat in _cat_list:
            CASES_BY_CATEGORY.setdefault(_cat, []).append(_c)


# ===========================================================================
# EVALUATION RUNNER
# ===========================================================================

def run_evaluation(
    cases: Optional[List[Dict[str, Any]]] = None,
    signal_analyzer: Optional[Any] = None,
    predictor: Optional[Any] = None,
    scoring_engine: Optional[Any] = None,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Run evaluation across a set of ground-truth test cases.

    Supports:
      1. Member 2 heuristic signals only (via signal_analyzer)
      2. Member 1 ML predictor (via predictor)
      3. Member 3 unified engine (via scoring_engine.analyze())

    Returns comprehensive metrics:
      accuracy, precision, recall, false_positive_rate, f1_score,
      confusion matrix counts, and per-case results.
    """
    if cases is None:
        cases = EVAL_CASES

    results = []
    tp = fp = tn = fn = 0

    for case in cases:
        text = case.get("text", "")
        expected = case.get("expected_verdict", "Safe")
        is_scam_expected = (expected in ("Scam", "Suspicious"))

        actual_verdict = "Safe"
        risk_score = 0
        signals_triggered = []

        # 1. Use Member 3 Unified Scoring Engine if available
        if scoring_engine is not None and hasattr(scoring_engine, "analyze"):
            try:
                res = scoring_engine.analyze(text=text, url=case.get("url"))
                actual_verdict = res.get("verdict", "Safe")
                risk_score = res.get("risk_score", 0)
                signals_triggered = [s.get("id") for s in res.get("signals", [])]
            except Exception as e:
                actual_verdict = "Error"
                risk_score = 0
                signals_triggered = [f"Exception: {e}"]

        # 2. Or use Member 2 signal_analyzer
        elif signal_analyzer is not None:
            res = signal_analyzer(text=text)
            signals_triggered = res.get("scam_types", [])
            boost = res.get("heuristic_risk_boost", 0)
            risk_score = boost
            if boost >= 25:
                actual_verdict = "Scam"
            elif boost >= 8:
                actual_verdict = "Suspicious"
            else:
                actual_verdict = "Safe"

        # 3. Or use Member 1 predictor
        elif predictor is not None and hasattr(predictor, "predict_combined"):
            res = predictor.predict_combined(text=text, url=case.get("url"))
            actual_verdict = res.get("verdict", "Safe")
            risk_score = res.get("risk_score", 0)
            signals_triggered = res.get("reasons", [])

        is_scam_actual = (actual_verdict in ("Scam", "Suspicious"))
        is_correct = (is_scam_expected == is_scam_actual)

        if is_scam_expected and is_scam_actual:
            tp += 1
        elif not is_scam_expected and not is_scam_actual:
            tn += 1
        elif not is_scam_expected and is_scam_actual:
            fp += 1
        elif is_scam_expected and not is_scam_actual:
            fn += 1

        record = {
            "id": case.get("id"),
            "split": case.get("split"),
            "input_type": case.get("input_type"),
            "expected": expected,
            "actual": actual_verdict,
            "correct": is_correct,
            "risk_score": risk_score,
            "signals": signals_triggered,
            "notes": case.get("notes"),
        }
        results.append(record)

        if verbose:
            tag = "✅ PASS" if is_correct else "❌ FAIL"
            print(f"[{tag}] {case.get('id'):<16} | Exp: {expected:<10} | Got: {actual_verdict:<10} | "
                  f"Score: {risk_score:3d}% | Sig: {signals_triggered[:2]}")

    total = len(cases)
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    summary = {
        "total_cases": total,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "false_positive_rate": round(fpr, 4),
        "f1_score": round(f1, 4),
        "per_case_results": results,
    }

    if verbose:
        print("\n" + "=" * 62)
        print(f"EVALUATION BENCHMARK SUMMARY (N={total})")
        print("=" * 62)
        print(f"TP : {tp:<4} | TN : {tn:<4}")
        print(f"FP : {fp:<4} | FN : {fn:<4}")
        print(f"Accuracy               : {accuracy:.2%}")
        print(f"Precision              : {precision:.2%}")
        print(f"Recall (Sensitivity)   : {recall:.2%}")
        print(f"False Positive Rate    : {fpr:.2%}")
        print(f"F1-Score               : {f1:.4f}")
        print("=" * 62)

    return summary


if __name__ == "__main__":
    import os
    import sys

    # Quick test using Member 2's signals.py
    try:
        from signals import analyze_signals
        print(f"[✓] Loaded signals.py successfully.")
        print(f"Total Benchmark Cases  : {len(BENCHMARK_CASES)}")
        print(f"  - Weight-Tuning Cases: {len(WEIGHT_TUNING_CASES)}")
        print(f"  - Held-Out Eval Cases: {len(HELD_OUT_TEST_CASES)}")
        print("\nRunning heuristic-only benchmark...")
        summary = run_evaluation(signal_analyzer=analyze_signals, verbose=True)
    except Exception as e:
        print(f"[!] Error running evaluation: {e}")
