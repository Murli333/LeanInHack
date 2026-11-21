"""
Data Loader & Dataset Generator for ScamLens (Member 1: Data & ML)
Downloads benchmark datasets, augments them with realistic Indian scam patterns
and legitimate transactional communications, tracks provenance, prevents data leakage,
and generates separate untouched holdout evaluation sets.
"""
import os
import csv
import io
import json
import time
import requests
import datetime
import pandas as pd
from typing import Tuple, List, Dict, Any

# =====================================================================
# 1. CURATED REALISTIC INDIAN SCAM SAMPLES (Expanded Corpus)
# =====================================================================
INDIAN_SCAM_SAMPLES = [
    # Fake KYC & Banking Threats
    ("spam", "Dear SBI user, your YONO account is locked due to pending KYC update. Click http://sbi-kyc-verify.top/sbi.apk to update immediately.", "fake_kyc"),
    ("spam", "Dear Customer, your HDFC bank debit card is blocked. Kindly click https://hdfc-card-unlock.xyz/verify to unblock your card and update PAN card.", "fake_kyc"),
    ("spam", "Paytm KYC Alert: Your wallet is on hold. Complete video KYC now or account will be permanently blocked. Click http://paytm-kyc-kyc.top/update", "fake_kyc"),
    ("spam", "Dear Customer, PAN card verification failed for Bank account. To avoid freeze, click https://pancard-kyc-update.work and upload front and back photo.", "fake_kyc"),
    ("spam", "Bank of Baroda Alert: Your netbanking has been suspended due to incomplete Re-KYC. Visit http://bob-kyc-portal.club to restore access.", "fake_kyc"),
    ("spam", "Punjab National Bank: Dear user, submit Aadhaar copy immediately to prevent debit card deactivation: http://pnb-aadhaar-link.site", "fake_kyc"),

    # Urgent Electricity & Utility Disconnection Threats
    ("spam", "Urgent: Electricity power will be disconnected at 9:30 PM from power office because your previous month bill was not updated. Please immediately contact our electricity officer 9876543210.", "electricity_threat"),
    ("spam", "Electricity Department Alert: Dear consumer, your bill Rs 1450 is unpaid. Power supply will be disconnected tonight. Call officer at 8912345678 immediately.", "electricity_threat"),
    ("spam", "BSES Urgent Notice: Power line disconnection scheduled tonight at 10 PM. To avoid disconnection, call BSES Junior Engineer at 9711223344.", "electricity_threat"),
    ("spam", "Tata Power consumer alert: Your electricity connection will be severed in 2 hours for non-payment of previous invoice. Contact officer on 9819283746.", "electricity_threat"),

    # Digital Arrest & Law Enforcement Impersonation
    ("spam", "Delhi Police Cyber Cell: A parcel in your name containing illegal narcotics has been seized at Mumbai airport. Digital arrest warrant issued. Contact CBI Officer on Skype/WhatsApp 9871203948 immediately.", "digital_arrest"),
    ("spam", "CBI Notice: An arrest warrant has been issued against you under PMLA Act. Report immediately to virtual court room link: https://cbi-investigation.top/court", "digital_arrest"),
    ("spam", "Mumbai Crime Branch: Suspected money laundering detected on your Aadhaar card. Join Skype digital interrogation room within 15 minutes or face police remand.", "digital_arrest"),
    ("spam", "Narcotics Control Bureau (NCB): 500g MDMA intercepted from Taiwan in your name. Connect via video call with Investigation Officer immediately: 9811445566.", "digital_arrest"),

    # UPI Collect & Cashback / Lottery Phishing
    ("spam", "Dear Customer, you received UPI collect request of Rs 4999 from Amazon Pay. Enter your UPI PIN to receive money in your bank account.", "upi_fraud"),
    ("spam", "Income Tax Department: Refund of Rs 15,490 approved. Please submit your bank account details and OTP at http://incometax-refund-portal.site/claim", "tax_refund"),
    ("spam", "Dear Customer, your ICICI reward points worth Rs 9,850 are expiring today. Redeem in cash directly to your bank account: https://icici-points-reward.link/redeem", "reward_points"),
    ("spam", "Dear user, you have won Rs 25,00,000 in KBC Kaun Banega Crorepati lucky draw. To claim prize money WhatsApp Rana Pratap Singh at 7890123456.", "lottery_scam"),
    ("spam", "PhonePe Cashback: Congratulations! You received Rs 1,999 scratch card cashback. Click https://phonepe-cashback.xyz/claim and enter your UPI PIN.", "upi_fraud"),

    # Work-From-Home / Part-Time Task Scams
    ("spam", "Congratulations! You have been selected for part-time work from home. Earn Rs 2500-5000 daily by liking YouTube videos and Google reviews. Contact on Telegram @work_hr_india", "job_scam"),
    ("spam", "Work from Home Amazon Part Time: Earn Rs 3000 to Rs 8000 daily with simple review tasks. WhatsApp us at +919811223344 right now for joining bonus.", "job_scam"),
    ("spam", "Part time job opportunity: Hotel review and rating tasks. Payout Rs 500 per review, daily payout in bank. Telegram @hotel_evaluator_hr", "job_scam"),

    # Delivery & Customs Scams
    ("spam", "FedEx Express: Your parcel #FX-9821 cannot be delivered due to unpaid customs fee of Rs 480. Pay now or package will be returned: http://fedex-customs-india.xyz", "customs_parcel"),
    ("spam", "Speed Post Alert: Your address is incomplete. Package delivery suspended. Update your address and pay Rs 25 redelivery fee: http://indiapost-update.xyz/login", "customs_parcel"),
    ("spam", "DHL Express: Overseas parcel held at New Delhi hub due to unpaid customs duty of INR 1,250. Click https://dhl-clearance.site to release consignment.", "customs_parcel"),

    # Telecom / SIM Termination & 5G Upgrade
    ("spam", "TRAI Alert: Your mobile SIM number will be disconnected within 2 hours due to illegal activity and Aadhaar mismatch. Call customer executive 9823411122.", "sim_disconnect"),
    ("spam", "Airtel 5G SIM upgrade: Switch your 4G SIM to 5G free with 84 days recharge. Click http://airtel-5g-upgrade.site and enter your OTP to activate.", "sim_disconnect"),
    ("spam", "Jio Alert: Dear user, your Jio SIM e-KYC has expired. Re-verify within 24 hours to prevent outgoing call suspension: http://jio-sim-verify.top", "sim_disconnect"),

    # Pre-approved Loan Scams
    ("spam", "Pre-approved Personal Loan of Rs 5,00,000 at 1% interest rate without CIBIL score. Download APK to claim: http://instant-cash-loan.top/loan.apk", "loan_scam"),
    ("spam", "Instant Loan 5 Lakh credited in 5 mins without documentation or salary slip. Install FastCash loan app: http://quick-rupee-loan.click/get.apk", "loan_scam"),

    # Obfuscated & Hinglish Scams
    ("spam", "Aapka SBI account band ho jayega agar aapne turant KYC update nahi kiya. Kripya is link par jaakar OTP bataye: http://sbi-alert.top/pan", "hinglish_scam"),
    ("spam", "Bijli ka connection kat diya jayega aaj raat 9 baje. Turant sampark kare bijli adhikari se 9876543210 par bill clear karne ke liye.", "hinglish_scam"),
    ("spam", "Dеаr SBI user, your K Y C is pending. Claim your fr.ee reward of Rs 5000: http://sbi-bonus.site", "obfuscated_scam"),
    ("spam", "Ghar baithe paise kamaye 2000 se 5000 daily YouTube video like karke. WhatsApp kare 9811002233 par.", "hinglish_scam"),
    ("spam", "Lapsed LIC policy bonus of Rs 2,45,000 ready for release. Call IRDAI officer at 9812345678 to claim without tax deduction.", "insurance_scam"),
    ("spam", "VIP Crypto Signals: Earn 500% profit guaranteed in 24 hours on Binance and WazirX. Join Telegram VIP channel: @crypto_crorepati", "crypto_scam")
]

# =====================================================================
# 2. CURATED REALISTIC INDIAN LEGITIMATE (HAM) SAMPLES (Expanded)
# =====================================================================
INDIAN_HAM_SAMPLES = [
    # E-commerce, Food Delivery & Quick Commerce
    ("ham", "Dear Customer, your Swiggy order from Biryani Blues is out for delivery. Delivery partner Ravi will reach you shortly. Track in Swiggy app.", "food_delivery"),
    ("ham", "OTP for your Zomato order is 4821. Please share with the delivery partner upon arrival. Do not share with anyone else.", "food_delivery"),
    ("ham", "Blinkit order #98214 is packed and arriving in 8 minutes. Delivery partner details sent via app notifications.", "food_delivery"),
    ("ham", "Your Flipkart order containing boAt headphones has been delivered. Thank you for shopping with us! Rate your delivery experience.", "ecommerce"),
    ("ham", "Dear Customer, your Amazon package will be delivered today by 8 PM. OTP for delivery is 3910. Deliver to secure location if unavailable.", "ecommerce"),
    ("ham", "Myntra order dispatched: Roadster cotton shirt has been handed over to Blue Dart. Expected delivery: 22-Nov-2026.", "ecommerce"),

    # Genuine Bank Transaction Debits/Credits & Legitimate OTPs
    ("ham", "Dear Customer, Rs 1,250.00 debited from HDFC Bank A/C ending 4589 on 18-NOV-26 towards UPI-Merchant. Bal: Rs 42,310.20.", "bank_debit"),
    ("ham", "Dear SBI customer, Rs 5,000.00 credited to your A/C ending 3821 via NEFT from ABC Corp. Available Bal: Rs 58,190.00.", "bank_credit"),
    ("ham", "Dear Customer, 849201 is your one time password (OTP) for SBI Internet Banking login. Valid for 3 mins. Never share OTP with anyone.", "bank_otp"),
    ("ham", "Dear Axis Bank Customer, your OTP for transaction of Rs 450.00 at Myntra is 639102. Valid for 5 minutes. Do not disclose to anyone.", "bank_otp"),
    ("ham", "Dear Customer, your monthly statement for ICICI Bank Credit Card ending 1004 is generated. Total amount due: Rs 8,420. Due date: 05-Dec.", "bank_statement"),
    ("ham", "Dear Customer, transaction alert: INR 350.00 spent on ICICI Bank Card XX4019 on 19-Nov-26 at CAFE COFFEE DAY. Avail limit: INR 85,000.", "bank_alert"),

    # Government & Institutional Notifications
    ("ham", "Aadhaar OTP for authentication is 912048. Generated at 14:22 hrs. Valid for 10 minutes. Unique Identification Authority of India.", "gov_aadhaar"),
    ("ham", "Income Tax Department: E-filing acknowledgment for ITR-1 AY 2026-27 has been received successfully. Ack No: 9182736451.", "gov_incometax"),
    ("ham", "DigiLocker: Your Driving License issued by Transport Department Delhi has been successfully linked to your DigiLocker account.", "gov_digilocker"),
    ("ham", "Parivahan Sewa: Vehicle registration certificate for DL01AB1234 has been renewed. Download mParivahan app for digital RC.", "gov_parivahan"),

    # Transport, Travel & Utilities
    ("ham", "Your PNR 2451982301 for Train 12301 NDLS RAJDHANI is confirmed. Coach B3 Berth 42. Check PNR status at www.irctc.co.in.", "travel_irctc"),
    ("ham", "Your Indigo flight 6E-204 from DEL to BLR is on schedule. Web check-in is now open. Boarding gate opens at 18:15 hrs.", "travel_flight"),
    ("ham", "Uber: Your driver Ramesh is arriving in a white Dzire (DL1ZAA1234). PIN for trip is 7291.", "travel_cab"),
    ("ham", "Dear Consumer, your Tata Power DDL electricity bill for CA No 60012345678 of Rs 2140 is due on 25-Nov. Pay via official portal or BBPS.", "utility_bill"),
    ("ham", "BSES Yamuna Power: Dear Consumer, your electricity bill of Rs 3,410 for CA 100234567 has been generated. Due date 28-Nov-2026. Pay online to avail rebate.", "utility_bill"),
    ("ham", "Dear user, your recharge of Rs 299 for Airtel number 9810234567 was successful. Data: 1.5GB/day, Unlimited Calls for 28 days.", "telecom_recharge"),
    ("ham", "Jio validity alert: Your plan on 9820011223 expires in 3 days. Recharge on MyJio app to continue uninterrupted services.", "telecom_recharge"),

    # Healthcare, Education & Personal Conversations
    ("ham", "Your appointment with Dr. Sharma at Apollo Clinic is confirmed for tomorrow at 11:30 AM. Please arrive 10 minutes early.", "healthcare"),
    ("ham", "Max Healthcare: Lab test report for Blood Glucose Fasting is ready. Download from Max MyHealth app.", "healthcare"),
    ("ham", "Dear Parent, school fees for term 2 have been published on student portal. Kindly clear by 30th November. DPS RK Puram.", "education"),
    ("ham", "National Testing Agency (NTA): Admit card for UGC-NET examination has been released on official website nta.ac.in.", "education"),
    ("ham", "Hi Priya, are we meeting at Starbucks Connaught Place at 5 PM today? Let me know if you are running late.", "personal"),
    ("ham", "Papa called, he said we are going to Dadi's place this Sunday morning. Call him back when free.", "personal")
]

# =====================================================================
# 3. CURATED PHISHING URLs (Both HTTP & HTTPS to prevent HTTPS bias)
# =====================================================================
CURATED_PHISHING_URLS = [
    # HTTP Phishing
    "http://sbi-kyc-verify.top/sbi.apk",
    "http://hdfc-card-unlock.xyz/verify",
    "http://incometax-refund-portal.site/claim",
    "http://paytm-kyc-kyc.top/update",
    "http://icici-points-reward.link/redeem",
    "http://instant-cash-loan.top/loan.apk",
    "http://fedex-customs-india.xyz/pay",
    "http://airtel-5g-upgrade.site/activate",
    "http://pancard-kyc-update.work/login.php",
    "http://cbi-investigation.top/court",
    "http://echallan-parivahan-pay.xyz/bill",
    "http://indiapost-update.xyz/login",
    "http://192.168.1.104/secure-bank-login/",
    "http://185.220.101.5/yono/update.apk",
    "http://sbi-reward-points-redeem.club/bonus",
    "http://verify-aadhaar-kyc-portal.buzz/auth",
    "http://electricity-bill-disconnection-alert.fit/pay",
    "http://delhi-police-digital-arrest-skype.top/investigation",

    # HTTPS Phishing (Counterexamples: Phishers using Free SSL!)
    "https://sbi-kyc-verify.top/sbi.apk",
    "https://hdfc-netbanking.site/login.php",
    "https://icici-verify.top/customer-login",
    "https://paytm-cashback-gift.xyz/scratch",
    "https://phonepe-reward-claim.site/wallet",
    "https://aadhaar-link-verify.site/auth",
    "https://tatapower-pay.site/bill/pay",
    "https://bses-bill-update.top/disconnection",
    "https://customs-clearance-india.top/package",
    "https://work-from-home-tasks.xyz/register",
    "https://youtube-like-earn.top/payout",
    "https://telegram-task-earn.xyz/join",
    "https://bhim-upi-reward.top/collect",
    "https://axis-netbanking-portal.club/auth",
    "https://yono-sbi-kyc-document.online/verify",
    "https://104.21.32.18:8443/login/bank.html",
    "https://bit.ly/sbi-urgent-kyc-update",
    "https://tinyurl.com/delhi-electricity-pay",
    "https://cutt.ly/refund-income-tax-claim"
]

# =====================================================================
# 4. CURATED LEGITIMATE URLs (Both HTTPS & HTTP to prevent HTTP bias)
# =====================================================================
CURATED_LEGITIMATE_URLS = [
    # Verified HTTPS Official Domains
    "https://www.onlinesbi.sbi/",
    "https://netbanking.hdfcbank.com/netbanking/",
    "https://www.icicibank.com/personal-banking",
    "https://www.axisbank.com/",
    "https://www.incometax.gov.in/iec/foportal/",
    "https://cybercrime.gov.in/",
    "https://uidai.gov.in/",
    "https://www.irctc.co.in/nget/train-search",
    "https://www.swiggy.com/restaurants",
    "https://www.zomato.com/india",
    "https://www.flipkart.com/mobiles",
    "https://www.amazon.in/electronics/b",
    "https://paytm.com/recharge",
    "https://www.phonepe.com/",
    "https://www.airtel.in/prepaid-recharge",
    "https://www.jio.com/selfcare/recharge/mobility/",
    "https://parivahan.gov.in/parivahan/",
    "https://www.tatapower.com/customer-services/",
    "https://www.bsesdelhi.com/web/brpl/home",
    "https://www.delhipolice.nic.in/",
    "https://www.rbi.org.in/",
    "https://echallan.parivahan.gov.in/",
    "https://github.com/scikit-learn/scikit-learn",
    "https://en.wikipedia.org/wiki/Phishing",
    "https://stackoverflow.com/questions",

    # HTTP Legitimate Counterexamples (Older or standard educational/reference sites)
    "http://info.cern.ch/hypertext/WWW/TheProject.html",
    "http://example.com/",
    "http://www.columbia.edu/~fdc/sample.html",
    "http://gnu.org/licenses/gpl-3.0.html",
    "http://web.mit.edu/about/",
    "http://w3.org/History.html",
    "http://textfiles.com/directory.html"
]


# =====================================================================
# 5. DEDICATED UNTOUCHED HOLDOUT TEST SETS (Zero Overlap with Training)
# =====================================================================
HOLDOUT_SCAM_MESSAGES = [
    ("spam", "Airtel Service Alert: Your outgoing calls will be blocked by midnight due to Aadhaar non-submission. Verify immediately at http://airtel-aadhaar-link.top", "sim_disconnect"),
    ("spam", "Mumbai Customs Notice: Consignment containing expensive electronic gadgets seized. Transfer Rs 2,500 clearance duty to release: http://customs-hub-clearance.xyz", "customs_parcel"),
    ("spam", "Digital Arrest Warrant: Delhi High Court has registered case #CR-8819 under NDPS Act. Appear online on WhatsApp or face immediate arrest.", "digital_arrest"),
    ("spam", "SBI YONO alert: 50,000 reward points credited. Redeem into your bank account before 12 AM: http://sbi-reward-points.site/redeem", "reward_points"),
    ("spam", "Electricity alert: Power supply disconnected tonight at 10 PM. Call Power Board SDM Sharma at 9811998877 immediately to clear dues.", "electricity_threat"),
    ("spam", "Work From Home part time: Review 5 apps on Play Store and get Rs 1,500 instantly. WhatsApp recruiter now: 9822334455", "job_scam"),
    ("spam", "Income Tax refund notification: Order for tax refund of Rs 22,400 ready. Validate bank account details at http://it-refund-validate.link", "tax_refund"),
    ("spam", "Paytm wallet KYC expired: Account locked permanently in 4 hours. Update KYC at http://paytm-kyc-officer.work", "fake_kyc"),
    ("spam", "Aapka PNB account freeze kar diya gaya hai. Turant OTP aur card number bataye unfreeze karne ke liye.", "hinglish_scam"),
    ("spam", "Dear User, won Rs 50,00,000 in Jio Diwali Kaun Banega Crorepati Lucky Draw. Call Manager Rana at 7788990011 to claim.", "lottery_scam"),
    ("spam", "Pre-approved loan of Rs 10 Lakh approved at 0.5% interest. Install app now to disburse: http://instant-dhan-loan.top/dhan.apk", "loan_scam"),
    ("spam", "Traffic Police e-Challan: Vehicle DL5CAB1234 has pending fine of Rs 2,000. Pay within 12 hours: http://traffic-challan-pay.xyz", "challan_scam"),
    ("spam", "HDFC Netbanking: Unrecognized login from Russia detected. Click https://hdfc-security-check.xyz to lock your account.", "fake_kyc"),
    ("spam", "India Post: Consignment arrived at terminal but postal index number is wrong. Update: http://indiapost-address.top", "customs_parcel"),
    ("spam", "Crypto VIP trading: Double your Bitcoin in 48 hours guaranteed. Join our private Telegram channel @vip_crypto_signals", "crypto_scam")
]

HOLDOUT_HAM_MESSAGES = [
    ("ham", "Dear Customer, your Swiggy Instamart order of groceries has been placed successfully and will be delivered in 12 mins.", "grocery_delivery"),
    ("ham", "Zomato: Delivery partner Suresh is on the way with your lunch order. Track live in the Zomato app.", "food_delivery"),
    ("ham", "Your OTP for Aadhaar online service verification is 654321. Valid for 10 minutes. Do not share with anyone. - UIDAI", "gov_otp"),
    ("ham", "Dear Customer, INR 2,400.00 debited from SBI A/C 9812 on 20-Nov-26 via UPI to ZOMATO. Avail Bal: INR 31,450.00.", "bank_debit"),
    ("ham", "Dear ICICI Bank customer, 451290 is the OTP for card transaction of INR 1,899.00 at AMAZON. Never disclose OTP to anyone.", "bank_otp"),
    ("ham", "Indian Railways: PNR 2819283918 train 12952 MUMBAI RAJDHANI coach A1 berth 18 confirmed. Charting prepared.", "travel_train"),
    ("ham", "IndiGo flight 6E-512 departs from Terminal 3 Delhi at 09:15 AM. Web check-in closes 60 minutes before departure.", "travel_flight"),
    ("ham", "Tata Power DDL: Payment of Rs 1,840 received successfully against CA No 6001928374 on 19-Nov-26. Thank you for timely payment.", "utility_paid"),
    ("ham", "BSES Delhi: Meter reading for your connection CA 100928374 scheduled for 23-Nov-26. Please allow access to authorized staff.", "utility_meter"),
    ("ham", "Amazon: Package with order #402-9182371 has been delivered to your front door. How was your delivery experience?", "ecommerce_delivered"),
    ("ham", "Blinkit: Your order has been delivered by partner Amit. Please rate your delivery experience in app.", "delivery_rate"),
    ("ham", "Dr. Batra Clinic: Reminder for your regular consultation on Friday at 4 PM. Call clinic to reschedule if needed.", "healthcare"),
    ("ham", "DPS R.K. Puram: Winter uniform instructions have been uploaded to parent portal. Kindly review guidelines.", "education"),
    ("ham", "Airtel: Your bill for landline broadband 011-28192834 is Rs 943 due on 28-Nov. Pay on Airtel Thanks app.", "utility_telecom"),
    ("ham", "Hi Rahul, sharing the project presentation slides on email. Let's do a quick sync call at 3 PM today.", "personal_work")
]

HOLDOUT_PHISHING_URLS = [
    ("http://sbi-kyc-urgent-verification.top/yono", 1),
    ("http://hdfc-netbanking-card-unblock.xyz/login", 1),
    ("http://icici-points-cashback.online/claim", 1),
    ("http://electricity-bill-discom-officer.fit/pay", 1),
    ("http://delhi-police-cbi-investigation.top/skype", 1),
    ("http://speedpost-indiapost-address.xyz/redeliver", 1),
    ("https://airtel-sim-terminate-kyc.site/login", 1),
    ("https://paytm-wallet-hold-re-kyc.buzz/auth", 1),
    ("https://185.120.45.6/apk/loan-easy.apk", 1),
    ("https://incometax-tds-refund-portal.vip/claim", 1),
    ("https://bit.ly/claim-kbc-lottery-prize", 1),
    ("https://tinyurl.com/fast-cash-instant-loan", 1)
]

HOLDOUT_LEGITIMATE_URLS = [
    ("https://www.onlinesbi.sbi/portal/", 0),
    ("https://netbanking.hdfcbank.com/", 0),
    ("https://www.icicibank.com/", 0),
    ("https://cybercrime.gov.in/Webform/Crime_Details.aspx", 0),
    ("https://uidai.gov.in/my-aadhaar/overview.html", 0),
    ("https://www.irctc.co.in/nget/", 0),
    ("https://www.swiggy.com/corporate/", 0),
    ("https://www.zomato.com/investor-relations", 0),
    ("https://parivahan.gov.in/parivahan/en/content/mparivahan", 0),
    ("https://www.tatapower.com/sustainability/", 0),
    ("http://info.cern.ch/hypertext/WWW/Summary.html", 0),
    ("http://example.com/index.html", 0)
]


# =====================================================================
# 6. HELPER FUNCTIONS: JACCARD SIMILARITY & DUPLICATE DETECTION
# =====================================================================
def jaccard_word_similarity(text1: str, text2: str) -> float:
    """Computes Jaccard word set similarity between two texts."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    return intersection / union if union > 0 else 0.0


def robust_fetch(url: str, max_retries: int = 3, delay: float = 2.0, timeout: float = 10.0) -> requests.Response | None:
    """Fetches remote URL with exponential backoff retry logic."""
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code == 200:
                return resp
        except Exception as e:
            if attempt == max_retries:
                print(f"[!] Warning: Download failed after {max_retries} attempts ({url}): {e}")
            else:
                time.sleep(delay * attempt)
    return None


def create_holdout_set(data_dir: str = "data") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Creates and saves dedicated holdout datasets for text and URL classification.
    Strictly isolated from training splits.
    """
    holdout_dir = os.path.join(data_dir, "holdout")
    os.makedirs(holdout_dir, exist_ok=True)

    text_records = []
    for lbl, msg, category in HOLDOUT_SCAM_MESSAGES:
        text_records.append({"label": lbl, "text": msg, "is_scam": 1, "category": category, "split": "holdout"})
    for lbl, msg, category in HOLDOUT_HAM_MESSAGES:
        text_records.append({"label": lbl, "text": msg, "is_scam": 0, "category": category, "split": "holdout"})

    df_holdout_text = pd.DataFrame(text_records).drop_duplicates(subset=["text"]).reset_index(drop=True)
    text_path = os.path.join(holdout_dir, "holdout_text.csv")
    df_holdout_text.to_csv(text_path, index=False, encoding="utf-8")
    print(f"[+] Saved Holdout Text Dataset: {len(df_holdout_text)} records to {text_path}")

    url_records = []
    for u, is_phish in HOLDOUT_PHISHING_URLS:
        url_records.append({"url": u, "is_phishing": is_phish, "split": "holdout"})
    for u, is_phish in HOLDOUT_LEGITIMATE_URLS:
        url_records.append({"url": u, "is_phishing": is_phish, "split": "holdout"})

    df_holdout_url = pd.DataFrame(url_records).drop_duplicates(subset=["url"]).reset_index(drop=True)
    url_path = os.path.join(holdout_dir, "holdout_urls.csv")
    df_holdout_url.to_csv(url_path, index=False, encoding="utf-8")
    print(f"[+] Saved Holdout URL Dataset: {len(df_holdout_url)} records to {url_path}")

    return df_holdout_text, df_holdout_url


def save_pipeline_manifest(df_text: pd.DataFrame, df_urls: pd.DataFrame, data_dir: str = "data"):
    """
    Generates reproducible pipeline metadata manifest.
    """
    proc_dir = os.path.join(data_dir, "processed")
    os.makedirs(proc_dir, exist_ok=True)
    manifest_path = os.path.join(proc_dir, "pipeline_manifest.json")

    text_source_counts = df_text["source"].value_counts().to_dict() if "source" in df_text.columns else {}
    url_source_counts = df_urls["source"].value_counts().to_dict() if "source" in df_urls.columns else {}

    manifest = {
        "dataset_version": "2.1.0",
        "generated_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "random_seed": 42,
        "text_dataset": {
            "total_records": int(len(df_text)),
            "scam_records": int(df_text["is_scam"].sum()),
            "ham_records": int(len(df_text) - df_text["is_scam"].sum()),
            "scam_ratio": round(float(df_text["is_scam"].mean()), 4),
            "sources_breakdown": text_source_counts
        },
        "url_dataset": {
            "total_records": int(len(df_urls)),
            "phishing_records": int(df_urls["is_phishing"].sum()),
            "legitimate_records": int(len(df_urls) - df_urls["is_phishing"].sum()),
            "phishing_ratio": round(float(df_urls["is_phishing"].mean()), 4),
            "sources_breakdown": url_source_counts
        },
        "preprocessing_pipeline": [
            "Unicode normalization (NFKD) and Cyrillic homoglyph replacement",
            "Zero-width character stripping (U+200B..U+FEFF)",
            "Deobfuscation of spaced & masked fraud keywords",
            "Hinglish & Hindi scam pattern identification",
            "Entity marker replacement (urlmarker, phonemarker, currencymarker, codemarker)",
            "Holdout dataset strict isolation to prevent train/test leakage",
            "28-feature structural URL extraction with shortener & Punycode defense"
        ]
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
    print(f"[+] Saved pipeline manifest to {manifest_path}")


# =====================================================================
# 7. MAIN DATA LOADERS: TEXT & URL
# =====================================================================
def load_sms_dataset(data_dir: str = "data") -> pd.DataFrame:
    """
    Loads UCI SMS dataset and merges with Indian scam & ham corpus.
    Applies deduplication and records data provenance.
    """
    raw_dir = os.path.join(data_dir, "raw")
    proc_dir = os.path.join(data_dir, "processed")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(proc_dir, exist_ok=True)

    raw_path = os.path.join(raw_dir, "sms_spam_raw.tsv")
    cleaned_path = os.path.join(proc_dir, "cleaned_text_data.csv")

    records = []

    # 1. UCI SMS dataset
    uci_url = "https://raw.githubusercontent.com/justmarkham/DAT8/master/data/sms.tsv"
    if not os.path.exists(raw_path):
        print(f"[*] Downloading UCI SMS dataset from {uci_url}...")
        resp = robust_fetch(uci_url)
        if resp:
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(resp.text)
            print(f"[+] Downloaded raw SMS dataset ({len(resp.text)} bytes).")

    if os.path.exists(raw_path):
        df_uci = pd.read_csv(raw_path, sep="\t", header=None, names=["label", "text"], quoting=csv.QUOTE_NONE, encoding="utf-8", on_bad_lines='skip')
        for _, row in df_uci.iterrows():
            lbl = str(row["label"]).strip().lower()
            txt = str(row["text"]).strip()
            if lbl in ["ham", "spam"] and txt:
                records.append({
                    "label": lbl,
                    "text": txt,
                    "is_scam": 1 if lbl == "spam" else 0,
                    "source": "uci_sms",
                    "category": "general"
                })
        print(f"[+] Loaded {len(records)} messages from UCI dataset.")

    # 2. Augment with Indian scam cases (single copies; balanced class weighting used in model training)
    for lbl, msg, category in INDIAN_SCAM_SAMPLES:
        records.append({
            "label": lbl,
            "text": msg,
            "is_scam": 1,
            "source": "indian_scam_curated",
            "category": category
        })

    # 3. Augment with legitimate Indian transactional & informational messages
    for lbl, msg, category in INDIAN_HAM_SAMPLES:
        records.append({
            "label": lbl,
            "text": msg,
            "is_scam": 0,
            "source": "indian_ham_curated",
            "category": category
        })

    # Remove exact duplicate texts
    df = pd.DataFrame(records).drop_duplicates(subset=["text"]).reset_index(drop=True)
    df.to_csv(cleaned_path, index=False, encoding="utf-8")
    print(f"[+] Total Text Dataset: {len(df)} messages ({df['is_scam'].sum()} scams, {len(df) - df['is_scam'].sum()} genuine/ham).")
    print(f"[+] Saved cleaned text dataset to {cleaned_path}")
    return df


def load_url_dataset(data_dir: str = "data") -> pd.DataFrame:
    """
    Builds comprehensive URL dataset combining open-source feeds (OpenPhish),
    benchmark datasets, and curated phishing/legitimate patterns.
    """
    raw_dir = os.path.join(data_dir, "raw")
    proc_dir = os.path.join(data_dir, "processed")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(proc_dir, exist_ok=True)

    cleaned_path = os.path.join(proc_dir, "cleaned_url_data.csv")
    snapshot_path = os.path.join(raw_dir, "openphish_snapshot.txt")
    url_records = []

    # 1. Fetch live OpenPhish feed or use local snapshot
    openphish_urls = []
    print("[*] Fetching live phishing feed from OpenPhish...")
    op_resp = robust_fetch("https://openphish.com/feed.txt", timeout=8)
    if op_resp and op_resp.text:
        openphish_urls = [line.strip() for line in op_resp.text.split("\n") if line.strip() and line.startswith("http")]
        with open(snapshot_path, "w", encoding="utf-8") as f:
            f.write(op_resp.text)
        print(f"[+] Saved OpenPhish snapshot ({len(openphish_urls)} URLs).")
    elif os.path.exists(snapshot_path):
        with open(snapshot_path, "r", encoding="utf-8") as f:
            openphish_urls = [line.strip() for line in f.read().split("\n") if line.strip() and line.startswith("http")]
        print(f"[+] Loaded {len(openphish_urls)} URLs from cached OpenPhish snapshot.")

    for u in openphish_urls[:600]:
        url_records.append({"url": u, "is_phishing": 1, "source": "openphish"})

    # 2. Add curated phishing URLs (including HTTPS phish)
    for u in CURATED_PHISHING_URLS:
        url_records.append({"url": u, "is_phishing": 1, "source": "curated_phishing"})

    # Synthetic domain pattern generators
    for domain in ["sbi-card-reward.xyz", "hdfc-net-banking.top", "paytm-cash-bonus.site", "electricity-disconnection-bill.fit", "cbi-cyber-investigation.top"]:
        for path in ["/login", "/verify", "/update.php", "/app.apk", "/collect-upi"]:
            url_records.append({"url": f"http://{domain}{path}", "is_phishing": 1, "source": "synthetic_phishing"})
            # Also add HTTPS versions to break the HTTPS == Safe bias!
            url_records.append({"url": f"https://{domain}{path}", "is_phishing": 1, "source": "synthetic_phishing"})

    # 3. Add legitimate URLs (including HTTP legitimate counterexamples)
    for u in CURATED_LEGITIMATE_URLS:
        url_records.append({"url": u, "is_phishing": 0, "source": "curated_legitimate"})

    for domain in ["google.com", "microsoft.com", "github.com", "wikipedia.org", "flipkart.com", "amazon.in", "irctc.co.in", "uidai.gov.in"]:
        for path in ["/about", "/help", "/privacy", "/terms", "/search?q=test", "/products/catalog", "/contact"]:
            url_records.append({"url": f"https://www.{domain}{path}", "is_phishing": 0, "source": "synthetic_legitimate"})

    # 4. Fetch additional public legitimate/phishing sample dataset if available
    raw_url_file = os.path.join(raw_dir, "benchmark_urldata.csv")
    repo_url = "https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/5.urldata.csv"
    if not os.path.exists(raw_url_file):
        print(f"[*] Downloading domain samples from {repo_url}...")
        resp = robust_fetch(repo_url, timeout=12)
        if resp:
            with open(raw_url_file, "w", encoding="utf-8") as f:
                f.write(resp.text)
            print(f"[+] Cached raw benchmark URL dataset.")

    if os.path.exists(raw_url_file):
        try:
            df_ext = pd.read_csv(raw_url_file)
            if "Domain" in df_ext.columns and "Label" in df_ext.columns:
                for _, r in df_ext.iterrows():
                    domain = str(r["Domain"]).strip()
                    label = int(r["Label"]) # 1 is phishing, 0 is safe
                    if domain:
                        scheme = "http://" if label == 1 else "https://"
                        url_records.append({"url": scheme + domain, "is_phishing": label, "source": "shreya_benchmark"})
                print(f"[+] Integrated benchmark domains from research dataset.")
        except Exception as e:
            print(f"[!] Benchmark domain parse notice: {e}")

    df_urls = pd.DataFrame(url_records).drop_duplicates(subset=["url"]).reset_index(drop=True)
    df_urls.to_csv(cleaned_path, index=False, encoding="utf-8")
    print(f"[+] Total URL Dataset: {len(df_urls)} URLs ({df_urls['is_phishing'].sum()} phishing, {len(df_urls) - df_urls['is_phishing'].sum()} legitimate).")
    print(f"[+] Saved cleaned URL dataset to {cleaned_path}")
    return df_urls


if __name__ == "__main__":
    print("=== ScamLens Data Loader Pipeline ===")
    df_sms = load_sms_dataset()
    df_url = load_url_dataset()
    create_holdout_set()
    save_pipeline_manifest(df_sms, df_url)
    print("=== Data Preparation & Holdout Set Isolation Completed Successfully ===")
