"""
ScamLens - Member 2: Comprehensive Evaluation Test Cases
36 Realistic Ground-Truth Test Cases (18 Scams, 18 Legitimate)
Focusing on Modern Indian Digital Fraud Patterns and Authentic Communications.
Used by Member 3 to tune weights, benchmark accuracy, precision, recall, and false positive rates.
"""

EVALUATION_CASES = [
    # =========================================================================
    # SCAM TEST CASES (18 Cases across major Indian Fraud vectors)
    # =========================================================================
    
    # --- Fake KYC & Account Suspension ---
    {
        "id": "SCAM-01",
        "category": "Fake KYC",
        "input_type": "text_url",
        "text": "Dear SBI Customer, your YONO account has been suspended due to pending KYC document update. Please visit http://sbi-kyc-verify.top/sbi.apk immediately to complete verification.",
        "url": "http://sbi-kyc-verify.top/sbi.apk",
        "ground_truth": "Scam",
        "expected_signals": ["fake_kyc", "urgency", "malicious_apk"]
    },
    {
        "id": "SCAM-02",
        "category": "Fake KYC",
        "input_type": "text",
        "text": "Dear HDFC user, your netbanking will be deactivated within 24 hours due to non-submission of PAN card. Update now at http://hdfc-card-unlock.xyz/verify or call 9811223344.",
        "url": "http://hdfc-card-unlock.xyz/verify",
        "ground_truth": "Scam",
        "expected_signals": ["fake_kyc", "urgency"]
    },
    {
        "id": "SCAM-03",
        "category": "Fake KYC",
        "input_type": "text",
        "text": "Your Paytm KYC is expired. Your wallet balance has been put on hold. Download our quick support app to complete biometric verification.",
        "url": None,
        "ground_truth": "Scam",
        "expected_signals": ["fake_kyc", "malicious_apk"]
    },

    # --- Electricity & Utility Threats ---
    {
        "id": "SCAM-04",
        "category": "Electricity Bill Threat",
        "input_type": "text",
        "text": "Urgent: Electricity power will be disconnected at 9:30 PM from power office because your previous month bill was not updated. Please immediately contact our electricity officer 9876543210.",
        "url": None,
        "ground_truth": "Scam",
        "expected_signals": ["electricity_bill", "urgency"]
    },
    {
        "id": "SCAM-05",
        "category": "Electricity Bill Threat",
        "input_type": "text_url",
        "text": "Dear Consumer, your BSES power connection will be cut off tonight due to unpaid arrears. Pay immediately to avoid black-out: http://electricity-bill-disconnection-alert.fit/pay",
        "url": "http://electricity-bill-disconnection-alert.fit/pay",
        "ground_truth": "Scam",
        "expected_signals": ["electricity_bill", "urgency", "phishing_domain"]
    },
    {
        "id": "SCAM-06",
        "category": "Electricity Bill Threat",
        "input_type": "text",
        "text": "Bijli vibhag notice: Your meter is disconnected. Call executive Sharma at 9988776655 to verify payment receipt immediately.",
        "url": None,
        "ground_truth": "Scam",
        "expected_signals": ["electricity_bill", "urgency"]
    },

    # --- UPI Collect & PIN Fraud ---
    {
        "id": "SCAM-07",
        "category": "UPI Collect Fraud",
        "input_type": "text",
        "text": "Dear Customer, you received UPI collect request of Rs 4999 from Amazon Pay. Enter your UPI PIN to receive money in your bank account.",
        "url": None,
        "ground_truth": "Scam",
        "expected_signals": ["upi_collect"]
    },
    {
        "id": "SCAM-08",
        "category": "UPI Collect Fraud",
        "input_type": "text_url",
        "text": "Congratulations! You won a Diwali cashback reward of Rs 2500 on PhonePe. Click here to claim into bank account: http://phonepe-cashback-reward.xyz/claim",
        "url": "http://phonepe-cashback-reward.xyz/claim",
        "ground_truth": "Scam",
        "expected_signals": ["upi_collect", "phishing_domain"]
    },
    {
        "id": "SCAM-09",
        "category": "UPI Collect Fraud",
        "input_type": "text",
        "text": "I have sent you 5000 advance on OLX for your sofa. Check your GPay and enter your UPI PIN to accept the payment.",
        "url": None,
        "ground_truth": "Scam",
        "expected_signals": ["upi_collect"]
    },

    # --- Digital Arrest & Law Enforcement Extortion ---
    {
        "id": "SCAM-10",
        "category": "Digital Arrest",
        "input_type": "text",
        "text": "Delhi Police Cyber Cell: A parcel in your name containing illegal narcotics and fake passports has been seized at Mumbai airport. Digital arrest warrant issued. Contact CBI Officer on Skype immediately.",
        "url": None,
        "ground_truth": "Scam",
        "expected_signals": ["digital_arrest", "parcel_customs", "urgency"]
    },
    {
        "id": "SCAM-11",
        "category": "Digital Arrest",
        "input_type": "text",
        "text": "Supreme Court of India Notice: FIR No 402/2026 registered under PMLA against your Aadhaar. Connect to our investigation room immediately or facing immediate detention.",
        "url": None,
        "ground_truth": "Scam",
        "expected_signals": ["digital_arrest", "urgency"]
    },
    {
        "id": "SCAM-12",
        "category": "Digital Arrest",
        "input_type": "text",
        "text": "Enforcement Directorate Warning: Your bank account is linked to a 20 Crore money laundering case. Transfer your liquid funds to RBI verification account to prove innocence.",
        "url": None,
        "ground_truth": "Scam",
        "expected_signals": ["digital_arrest"]
    },

    # --- Parcel & Customs Extortion ---
    {
        "id": "SCAM-13",
        "category": "Customs Extortion",
        "input_type": "text_url",
        "text": "FedEx Courier Alert: Your international package #FDX98213 is held at Delhi Customs due to unpaid clearance fee of Rs 3,450. Pay duty now: http://fedex-customs-clearance.top/pay",
        "url": "http://fedex-customs-clearance.top/pay",
        "ground_truth": "Scam",
        "expected_signals": ["parcel_customs", "phishing_domain"]
    },
    {
        "id": "SCAM-14",
        "category": "Customs Extortion",
        "input_type": "text",
        "text": "India Post: Consignment arrived from UK with valuable electronics. Pay release charge of Rs 1800 within 2 hours or parcel will be confiscated.",
        "url": None,
        "ground_truth": "Scam",
        "expected_signals": ["parcel_customs", "urgency"]
    },

    # --- Part-time Job & Task Scams ---
    {
        "id": "SCAM-15",
        "category": "Job Scam",
        "input_type": "text",
        "text": "Congratulations! You have been selected for part-time work from home. Earn Rs 2500-5000 daily by liking YouTube videos and rating hotels. Contact on Telegram @work_hr",
        "url": None,
        "ground_truth": "Scam",
        "expected_signals": ["job_scam"]
    },
    {
        "id": "SCAM-16",
        "category": "Job Scam",
        "input_type": "text",
        "text": "Amazon hiring online part-time assistants. No experience required. Salary 3000 Rs per day paid instantly. Join our Telegram VIP group: t.me/amazon_task_india",
        "url": "http://t.me/amazon_task_india",
        "ground_truth": "Scam",
        "expected_signals": ["job_scam"]
    },

    # --- Phishing URL Only ---
    {
        "id": "SCAM-17",
        "category": "Phishing URL",
        "input_type": "url",
        "text": None,
        "url": "http://192.168.1.104/secure-bank-login/",
        "ground_truth": "Scam",
        "expected_signals": ["ip_address_host"]
    },
    {
        "id": "SCAM-18",
        "category": "Phishing URL",
        "input_type": "url",
        "text": None,
        "url": "http://yonosbi-login.online/download.apk",
        "ground_truth": "Scam",
        "expected_signals": ["phishing_domain", "malicious_apk"]
    },

    # =========================================================================
    # LEGITIMATE TEST CASES (18 Cases across Authentic Communications)
    # =========================================================================
    
    # --- Bank OTP Alerts ---
    {
        "id": "LEGIT-01",
        "category": "Bank OTP Alert",
        "input_type": "text",
        "text": "Dear Customer, 849201 is your one time password (OTP) for SBI Internet Banking login. Valid for 3 mins. Never share OTP with anyone.",
        "url": None,
        "ground_truth": "Safe",
        "expected_signals": []
    },
    {
        "id": "LEGIT-02",
        "category": "Bank OTP Alert",
        "input_type": "text",
        "text": "452890 is your Secret OTP for HDFC Bank card ending 8021 for Rs. 1420.00 at Zomato. Do not share OTP with anyone to avoid fraud.",
        "url": None,
        "ground_truth": "Safe",
        "expected_signals": []
    },
    {
        "id": "LEGIT-03",
        "category": "Bank Transaction Alert",
        "input_type": "text",
        "text": "Dear Customer, your A/C ending 4502 is debited by Rs 1500.00 on 20-Nov-26 via UPI. Avail Bal: Rs 42,390.12. If not done by you, call 18002584455.",
        "url": None,
        "ground_truth": "Safe",
        "expected_signals": []
    },
    {
        "id": "LEGIT-04",
        "category": "Bank Transaction Alert",
        "input_type": "text",
        "text": "A/C *8912 credited with INR 75,000.00 on 01-Nov-26 by NEFT-SALARY. Net available balance INR 1,12,400.50. ICICI Bank.",
        "url": None,
        "ground_truth": "Safe",
        "expected_signals": []
    },

    # --- Genuine Delivery & E-Commerce Alerts ---
    {
        "id": "LEGIT-05",
        "category": "E-Commerce Delivery",
        "input_type": "text",
        "text": "Dear Customer, your Swiggy order from Biryani Blues is out for delivery. Delivery partner Ravi will reach you shortly with your food.",
        "url": None,
        "ground_truth": "Safe",
        "expected_signals": []
    },
    {
        "id": "LEGIT-06",
        "category": "E-Commerce Delivery",
        "input_type": "text",
        "text": "Your Amazon package containing boAt Headphones is arriving today by 8 PM. Share OTP 6192 with the delivery associate at the time of delivery.",
        "url": None,
        "ground_truth": "Safe",
        "expected_signals": []
    },
    {
        "id": "LEGIT-07",
        "category": "E-Commerce Delivery",
        "input_type": "text",
        "text": "Your Flipkart package has been delivered. Thank you for shopping with us! Rate your delivery experience on the Flipkart app.",
        "url": None,
        "ground_truth": "Safe",
        "expected_signals": []
    },
    {
        "id": "LEGIT-08",
        "category": "Courier Tracking",
        "input_type": "text_url",
        "text": "Blue Dart Express shipment #48291048201 has been dispatched from Mumbai Hub. Track live status at https://www.bluedart.com",
        "url": "https://www.bluedart.com",
        "ground_truth": "Safe",
        "expected_signals": []
    },

    # --- Travel & Utility Legitimate Alerts ---
    {
        "id": "LEGIT-09",
        "category": "Travel / Railway",
        "input_type": "text_url",
        "text": "Your PNR 2451982301 for Train 12301 NDLS RAJDHANI is confirmed. Coach B3 Berth 42. Check PNR status at https://www.irctc.co.in.",
        "url": "https://www.irctc.co.in",
        "ground_truth": "Safe",
        "expected_signals": []
    },
    {
        "id": "LEGIT-10",
        "category": "Travel / Flight",
        "input_type": "text",
        "text": "IndiGo 6E-204 from DEL to BLR is on time. Web check-in is now open. Boarding gate opens at 18:20 at Terminal 3.",
        "url": None,
        "ground_truth": "Safe",
        "expected_signals": []
    },
    {
        "id": "LEGIT-11",
        "category": "Legitimate Utility",
        "input_type": "text_url",
        "text": "Dear Consumer, your Tata Power DDL electricity bill for CA No 60012345678 of Rs 2140 is due on 25-Nov. Pay via official portal https://www.tatapower.com.",
        "url": "https://www.tatapower.com",
        "ground_truth": "Safe",
        "expected_signals": []
    },
    {
        "id": "LEGIT-12",
        "category": "Telecom Alert",
        "input_type": "text",
        "text": "You have used 100% of your daily high-speed data limit. Your speed is throttled to 64 Kbps until midnight. Recharge on MyJio app.",
        "url": None,
        "ground_truth": "Safe",
        "expected_signals": []
    },

    # --- Official Government Portals ---
    {
        "id": "LEGIT-13",
        "category": "Official Portal",
        "input_type": "text_url",
        "text": "National Cyber Crime Reporting Portal: Report cybercrimes, financial frauds and women safety issues at https://cybercrime.gov.in or call 1930.",
        "url": "https://cybercrime.gov.in",
        "ground_truth": "Safe",
        "expected_signals": []
    },
    {
        "id": "LEGIT-14",
        "category": "Official Portal",
        "input_type": "text_url",
        "text": "Income Tax Department: E-filing of ITR for AY 2026-27 is open. File your taxes securely on the official portal https://incometax.gov.in.",
        "url": "https://incometax.gov.in",
        "ground_truth": "Safe",
        "expected_signals": []
    },

    # --- Conversational & Informal Texts ---
    {
        "id": "LEGIT-15",
        "category": "Personal Message",
        "input_type": "text",
        "text": "Hi Priya, are we meeting at Starbucks Connaught Place at 5 PM today? Let me know if you are running late.",
        "url": None,
        "ground_truth": "Safe",
        "expected_signals": []
    },
    {
        "id": "LEGIT-16",
        "category": "Work Chat",
        "input_type": "text",
        "text": "Hey team, the Sprint Review meeting is scheduled for tomorrow at 11 AM IST on Google Meet. Please update your Jira boards before the call.",
        "url": None,
        "ground_truth": "Safe",
        "expected_signals": []
    },

    # --- Legitimate URLs Only ---
    {
        "id": "LEGIT-17",
        "category": "Legitimate URL",
        "input_type": "url",
        "text": None,
        "url": "https://www.onlinesbi.sbi/",
        "ground_truth": "Safe",
        "expected_signals": []
    },
    {
        "id": "LEGIT-18",
        "category": "Legitimate URL",
        "input_type": "url",
        "text": None,
        "url": "https://netbanking.hdfcbank.com/netbanking/",
        "ground_truth": "Safe",
        "expected_signals": []
    }
]


def get_cases_summary():
    """Returns metadata summary of the evaluation cases."""
    scam_count = sum(1 for c in EVALUATION_CASES if c["ground_truth"] == "Scam")
    legit_count = sum(1 for c in EVALUATION_CASES if c["ground_truth"] == "Safe")
    categories = set(c["category"] for c in EVALUATION_CASES)
    return {
        "total": len(EVALUATION_CASES),
        "scam": scam_count,
        "legitimate": legit_count,
        "categories": list(categories)
    }


if __name__ == "__main__":
    summary = get_cases_summary()
    print(f"Total test cases: {summary['total']} (Scams: {summary['scam']}, Legitimate: {summary['legitimate']})")
    print("Categories covered:", ", ".join(summary["categories"]))
