"""
ScamLens - eval_cases.py
Member 2: Detection Logic & Test Set

Ground-truth evaluation benchmark: 35 cases (18 scam, 17 genuine).
Used by Member 3 to tune the final scoring weights in app.py.

Each case is a dict with:
  - id (str): Unique case identifier
  - text (str): The input message / URL string
  - image_path (str | None): Path to screenshot (if applicable)
  - expected_verdict (str): "Scam" | "Suspicious" | "Safe"
  - expected_scam_types (List[str]): Expected scam categories triggered
  - notes (str): Brief explanation of why this is or isn't a scam
"""

EVAL_CASES = [

    # =========================================================
    # SECTION A: SCAM CASES (18 cases)
    # =========================================================

    {
        "id": "SCAM_001",
        "text": (
            "Dear SBI Customer, your account has been temporarily suspended due to incomplete KYC. "
            "To restore access, click here immediately: http://sbi-kyc-verify.top/sbi-update.apk "
            "Failure to update within 24 hours will result in permanent account closure."
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["Fake KYC Update", "Malicious File Download Link", "High-Pressure Urgency Tactic"],
        "notes": (
            "Classic SBI KYC scam: combines urgency, blocklisted domain, APK download link. "
            "Real SBI never sends APK links via SMS."
        ),
    },

    {
        "id": "SCAM_002",
        "text": (
            "URGENT: Your electricity power will be disconnected TONIGHT at 9:30 PM due to unpaid bills. "
            "To avoid disconnection, immediately contact our electricity officer at 8800XXXXXX. "
            "Do not ignore this final notice."
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["Electricity Bill Disconnection Scam", "High-Pressure Urgency Tactic"],
        "notes": (
            "Electricity disconnection scam with fake 'officer' contact. "
            "No real DISCOM threatens disconnection via SMS at a specific hour."
        ),
    },

    {
        "id": "SCAM_003",
        "text": (
            "Dear Customer, you have received a UPI collect request of Rs. 4,999 from Amazon Pay Rewards. "
            "Enter your UPI PIN to receive the cashback amount in your bank account immediately. "
            "Offer valid for 10 minutes only."
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["UPI Collect Request Fraud", "High-Pressure Urgency Tactic"],
        "notes": (
            "UPI collect request fraud. Victim enters PIN thinking they receive money, "
            "but actually approves a debit. Amazon never sends money via collect requests."
        ),
    },

    {
        "id": "SCAM_004",
        "text": (
            "Delhi Police Cyber Cell: A parcel registered in your name containing illegal narcotics "
            "(2.4 kg) has been intercepted at IGI Airport. An arrest warrant has been issued against you. "
            "You are under digital arrest. Contact CBI Officer Sharma immediately on Skype: cbiofficer_sharma. "
            "Do not leave home or face immediate physical arrest."
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["Digital Arrest / Agency Impersonation", "Parcel / Customs Scam"],
        "notes": (
            "Combined digital arrest + parcel scam. CBI and police never arrest people via "
            "Skype or place them under 'digital arrest'."
        ),
    },

    {
        "id": "SCAM_005",
        "text": (
            "Congratulations! You have been selected for a part-time work from home opportunity. "
            "Earn Rs 2500 to Rs 5000 daily by completing simple tasks — liking YouTube videos "
            "and rating Google Maps locations. No experience required. "
            "Join now on Telegram: @daily_task_earn2024"
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["Fake Job / Task Scam"],
        "notes": (
            "Classic advance-fee task scam on Telegram. After small payments to build trust, "
            "users are asked to deposit large amounts for 'high-value tasks'."
        ),
    },

    {
        "id": "SCAM_006",
        "text": (
            "ALERT from HDFC Bank: Your HDFC account has been BLOCKED due to suspicious activity. "
            "To unblock your account and avoid permanent suspension, verify your details at: "
            "http://hdfc-netbanking.site/verify-account "
            "This link expires in 2 hours."
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["Fake KYC Update", "Suspicious URL (High-Risk Domain)", "High-Pressure Urgency Tactic"],
        "notes": (
            "HDFC phishing with fake .site domain. Urgency and account block threat are "
            "hallmarks of phishing social engineering."
        ),
    },

    {
        "id": "SCAM_007",
        "text": (
            "Dear Customer, your FedEx parcel (Tracking: FX8829301IN) is on hold at customs. "
            "A customs clearance fee of Rs 1,750 is due. Pay immediately to avoid return and legal action. "
            "Pay here: http://fedex-india-customs.xyz/pay"
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["Parcel / Customs Scam", "Known Phishing URL"],
        "notes": (
            "FedEx impersonation with fake customs fee demand. FedEx never collects "
            "customs fees via unofficial payment links."
        ),
    },

    {
        "id": "SCAM_008",
        "text": (
            "Income Tax Department Notice: Unauthorized transaction detected using your PAN card. "
            "An FIR has been filed against you. Failure to respond within 2 hours will lead to arrest. "
            "Contact IT Officer Verma immediately: +91-98XXX-XXXXX"
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["Digital Arrest / Agency Impersonation", "High-Pressure Urgency Tactic"],
        "notes": (
            "Income Tax Department impersonation with arrest threat. Real IT department "
            "sends official written notices, not threatening SMS/calls."
        ),
    },

    {
        "id": "SCAM_009",
        "text": (
            "Congratulations! Your mobile number has won Rs 25,00,000 in the KBC Jio Lucky Draw 2024. "
            "Your winning number is 7482. To claim your prize, call KBC Lottery Manager at 8899XXXXXX "
            "and pay a Rs 2,100 processing fee."
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["Lottery / Prize Scam"],
        "notes": (
            "Fake KBC lottery. KBC does not operate SMS lotteries. The request for a "
            "'processing fee' is the definitive scam indicator."
        ),
    },

    {
        "id": "SCAM_010",
        "text": (
            "Your TRAI has detected that your mobile number is involved in illegal money transactions. "
            "Your SIM will be deactivated in 2 hours. To prevent deactivation, please verify your "
            "Aadhaar by clicking: http://trai-sim-verify.xyz/aadhaar"
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["Organizational Impersonation", "Suspicious URL (High-Risk Domain)"],
        "notes": (
            "TRAI impersonation with Aadhaar phishing URL. TRAI never deactivates SIMs "
            "via SMS and does not operate verification portals at unofficial domains."
        ),
    },

    {
        "id": "SCAM_011",
        "text": (
            "Quick Loan Offer! Get instant personal loan of Rs 5,00,000 without any documents. "
            "No CIBIL check. Approval in 5 minutes. 0% interest for first 3 months. "
            "Apply now — WhatsApp us at 9876XXXXXX or click: http://instant-loan-india.top/apply"
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["Fake Loan Offer", "Suspicious URL (High-Risk Domain)"],
        "notes": (
            "Fake instant loan with no-document, 0% interest claim. These collect advance "
            "fees or install malicious loan apps that blackmail victims."
        ),
    },

    {
        "id": "SCAM_012",
        "text": (
            "Dear Paytm User: Your Paytm KYC has expired. To continue using Paytm wallet "
            "and UPI services, re-verify your KYC now. Download the official Paytm verification "
            "app here: http://paytm-kyc-update.xyz/paytm-kyc.apk"
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["Fake KYC Update", "Malicious File Download Link", "Known Phishing URL"],
        "notes": (
            "Paytm KYC scam with APK download from blocklisted domain. Paytm KYC is only "
            "done in the official Paytm app from Play Store."
        ),
    },

    {
        "id": "SCAM_013",
        "text": (
            "Microsoft Technical Support: We have detected a virus on your computer that is stealing "
            "your banking information. Call our certified technician immediately at 1800-XXXXXX "
            "to remove the threat. Do not shut down your computer. Act NOW to protect your data."
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["Organizational Impersonation", "High-Pressure Urgency Tactic"],
        "notes": (
            "Tech support scam impersonating Microsoft. Microsoft never proactively calls "
            "about viruses. Victim is usually led to install remote access software."
        ),
    },

    {
        "id": "SCAM_014",
        "text": (
            "Dear Customer, you have received a PhonePe cashback of Rs 500. "
            "To collect your cashback, scan the QR code or enter your UPI PIN at the payment screen. "
            "PIN entry is mandatory to process the credit to your account."
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["UPI Collect Request Fraud", "OTP / PIN Phishing"],
        "notes": (
            "PhonePe cashback fraud using PIN phishing variant. No UPI platform requires "
            "PIN entry to receive money."
        ),
    },

    {
        "id": "SCAM_015",
        "text": (
            "Narcotics Control Bureau: Your Aadhaar card has been used to book a parcel "
            "containing 3.2 kg of MDMA drugs currently held at Mumbai Customs. "
            "An arrest notice has been issued. To verify your identity and avoid arrest, "
            "share your personal details and photo ID with Officer Rajan at rajan_ncb@gmail.com"
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["Digital Arrest / Agency Impersonation", "Parcel / Customs Scam"],
        "notes": (
            "NCB/customs impersonation. Government agencies never communicate arrest "
            "notices via email/WhatsApp and never use gmail.com addresses."
        ),
    },

    {
        "id": "SCAM_016",
        "text": (
            "FREE RECHARGE OFFER! Jio is offering 365-day unlimited free recharge for selected users. "
            "You have been selected! Claim your free recharge at: http://jio-free-recharge.xyz/claim "
            "Share this with 10 friends to activate. Offer ends tonight!"
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["Suspicious URL (High-Risk Domain)", "Lottery / Prize Scam"],
        "notes": (
            "Fake Jio offer to harvest personal data or spread the scam virally. "
            "Jio does not offer free recharges via SMS links."
        ),
    },

    {
        "id": "SCAM_017",
        "text": (
            "PM Cares Fund: The Government of India is distributing financial relief of Rs 15,000 "
            "to eligible citizens. Your Aadhaar has been verified as eligible. "
            "To receive funds, provide your bank account number, Aadhaar, and date of birth "
            "to Officer Priya at: 9876543210"
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["Organizational Impersonation"],
        "notes": (
            "PM Cares Fund impersonation to harvest banking and Aadhaar data. "
            "Government relief funds are disbursed through official DBT channels, never via SMS."
        ),
    },

    {
        "id": "SCAM_018",
        "text": (
            "Enforcement Directorate Notice: Your bank account ending 4821 has been linked to "
            "hawala transactions worth Rs 2.3 crore. You are required to stay at home and remain "
            "on this call under digital arrest until further instructions. "
            "Transfer Rs 50,000 as security deposit to avoid FIR registration."
        ),
        "image_path": None,
        "expected_verdict": "Scam",
        "expected_scam_types": ["Digital Arrest / Agency Impersonation", "High-Pressure Urgency Tactic"],
        "notes": (
            "Enforcement Directorate digital arrest scam demanding money to avoid FIR. "
            "ED never operates this way — this is a textbook digital arrest fraud."
        ),
    },


    # =========================================================
    # SECTION B: GENUINE / SAFE CASES (17 cases)
    # =========================================================

    {
        "id": "SAFE_001",
        "text": (
            "849201 is your SBI One Time Password (OTP) for transaction of Rs 2,500.00 at HDFC "
            "on 20-11-2024. Valid for 5 minutes. NEVER share your OTP with anyone. "
            "SBI never asks for OTP. If not done by you, call 1800-11-2211."
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Genuine SBI OTP SMS. Contains the classic 'NEVER share OTP' warning. "
            "ScamLens should detect this as safe and not flag the OTP mention."
        ),
    },

    {
        "id": "SAFE_002",
        "text": (
            "Dear Consumer, your BSES Rajdhani electricity bill for CA No. 60012345678 "
            "of Rs 2,140 for the period Oct-Nov 2024 is due on 25-Nov-2024. "
            "Pay via official portal at bsesdelhi.com or visit your nearest payment center."
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Official BSES electricity bill notification. References official website, "
            "contains CA number, and gives a reasonable payment deadline. No threat of immediate cutoff."
        ),
    },

    {
        "id": "SAFE_003",
        "text": (
            "Your Swiggy order #SW-2298821 from The Yellow Chilli, Koramangala is out for delivery. "
            "Delivery partner Ramesh will reach you in approximately 15 minutes. "
            "Track your order at swiggy.com/track/2298821"
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Genuine Swiggy delivery notification. No suspicious elements — "
            "references swiggy.com directly with an order tracking link."
        ),
    },

    {
        "id": "SAFE_004",
        "text": (
            "Your PNR 2451982301 for Train 12301 HOWRAH RAJDHANI EXP from NDLS on 22-Nov-2024 "
            "is Confirmed. Coach B3, Berth 42 (Lower). Check PNR status at www.irctc.co.in. "
            "Have a safe journey!"
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Legitimate IRCTC booking confirmation. References irctc.co.in directly. "
            "Specific berth and PNR details indicate a real booking."
        ),
    },

    {
        "id": "SAFE_005",
        "text": (
            "Hi Priya! Are we still meeting at Starbucks, Connaught Place at 5:30 PM today? "
            "Let me know if you're running late — I'll grab us a table. 😊"
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Personal, casual message. No financial, urgency, or threat indicators. "
            "ScamLens should return a low risk score."
        ),
    },

    {
        "id": "SAFE_006",
        "text": (
            "INR 15,000.00 credited to your HDFC Bank account XX4821 on 20-Nov-2024 "
            "by NEFT from Infosys BPM Ltd. Available Balance: INR 48,230.50. "
            "If not done by you, call 1800-258-3838."
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Genuine HDFC bank credit alert. Contains account details, credit amount, "
            "and official helpline. No link, no urgency, no request for personal details."
        ),
    },

    {
        "id": "SAFE_007",
        "text": (
            "Your Amazon.in order #402-8129831-2918734 for 'boAt Airdopes 141 (True Wireless Earbuds)' "
            "has been shipped. Expected delivery: 22 Nov 2024. "
            "Track your package at amazon.in/orders"
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Genuine Amazon shipment notification. Contains specific order ID, product name, "
            "and links to amazon.in — a trusted domain."
        ),
    },

    {
        "id": "SAFE_008",
        "text": (
            "Your appointment at AIIMS OPD (Dr. Meera Kapoor, Cardiology) is confirmed for "
            "23-Nov-2024 at 10:30 AM. Please carry your Aadhaar card and previous medical records. "
            "Contact: 011-26588500 for queries."
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Hospital appointment confirmation. No suspicious elements, no link, "
            "no financial request. Official phone number format."
        ),
    },

    {
        "id": "SAFE_009",
        "text": (
            "Paytm: Rs 500.00 paid to Sharma General Store (UPI: sharmashop@paytm) on 20-Nov-24 "
            "12:34 PM. UPI Ref: 421889293847. If not done by you, call 0120-4770770 immediately."
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Genuine Paytm UPI transaction confirmation. Contains UPI reference number, "
            "merchant UPI ID, official Paytm helpline number. No suspicious indicators."
        ),
    },

    {
        "id": "SAFE_010",
        "text": (
            "Your Ola ride is confirmed! Driver Suresh K is on the way in a Maruti Swift Dzire "
            "(DL 7C AB 1234). ETA: 4 minutes. Ride fare estimate: Rs 180. "
            "Track your ride on the Ola app."
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Genuine Ola ride confirmation. Contains driver details, vehicle number, "
            "and fare estimate. Standard cab booking notification."
        ),
    },

    {
        "id": "SAFE_011",
        "text": (
            "Your ITR for FY 2023-24 has been successfully e-verified on 20-Nov-2024. "
            "Acknowledgement number: 325498765432. Processing time: up to 60 days. "
            "Track status at incometax.gov.in/iec/foservices"
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Genuine IT department ITR e-verification notification. References official "
            "incometax.gov.in domain. No demand for money or personal details."
        ),
    },

    {
        "id": "SAFE_012",
        "text": (
            "Dear Rahul, your salary of Rs 68,500 has been credited to your account ending 4321 "
            "on 20-Nov-2024. Balance: Rs 1,24,340. — ICICI Bank. "
            "SMS HELP to 9222208888 or visit icicibank.com for assistance."
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Genuine ICICI Bank salary credit notification. Contains specific account "
            "ending, amount, and official website reference. No suspicious patterns."
        ),
    },

    {
        "id": "SAFE_013",
        "text": (
            "Hi! This is Zomato. Your order from Domino's Pizza (₹520) is on its way. "
            "Delivery partner Ajay is 1.2 km away. Track live at zomato.com/order/tracking"
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Legitimate Zomato delivery tracking message. References zomato.com, "
            "contains specific order amount and delivery partner. Standard food delivery notification."
        ),
    },

    {
        "id": "SAFE_014",
        "text": (
            "Dear Customer, your Tata Power DDL bill for Account No. 1004567890 "
            "for November 2024 is Rs 3,250. Due Date: 10-Dec-2024. "
            "Pay online at tatapower-ddl.com or visit nearest collection center."
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Genuine Tata Power electricity bill notification. References official "
            "tatapower-ddl.com, gives a future due date (not tonight), and no officer contact."
        ),
    },

    {
        "id": "SAFE_015",
        "text": (
            "Your DigiLocker document 'Driving Licence' has been successfully fetched from "
            "Ministry of Road Transport. Access your documents at digilocker.gov.in. "
            "If you didn't request this, change your DigiLocker password at once."
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Legitimate DigiLocker notification. References digilocker.gov.in — "
            "an official government domain. Standard document fetch alert."
        ),
    },

    {
        "id": "SAFE_016",
        "text": (
            "Your Flipkart order for 'Samsung Galaxy Buds2 (Graphite)' worth Rs 4,999 "
            "has been successfully placed. Order ID: OD-28819291031. "
            "Expected delivery by 24-Nov-2024. Track at flipkart.com/account/orders."
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Genuine Flipkart order confirmation. Contains specific product name, "
            "order ID, and links to flipkart.com. No suspicious elements."
        ),
    },

    {
        "id": "SAFE_017",
        "text": (
            "RBL Bank: Your credit card ending 8821 has been charged Rs 1,299 at NETFLIX.COM "
            "on 20-Nov-24. Available credit limit: Rs 48,701. "
            "Dispute at rblbank.com or call 022-61156300."
        ),
        "image_path": None,
        "expected_verdict": "Safe",
        "expected_scam_types": [],
        "notes": (
            "Genuine RBL Bank credit card transaction alert. Contains specific amounts, "
            "last 4 digits, and official RBL Bank dispute helpline. Standard bank SMS."
        ),
    },

]


# =========================================================
# EVALUATION RUNNER
# =========================================================

def run_evaluation(predictor=None, signal_analyzer=None, verbose: bool = True) -> dict:
    """
    Runs all eval cases through the signals analyzer (and optionally ML predictor).

    Args:
        predictor: Optional ScamLensPredictor instance from Member 1's models/predictor.py
        signal_analyzer: Optional analyze_signals function from signals.py
        verbose: Print detailed results to stdout

    Returns:
        A dict with overall accuracy, precision, recall, false_positive_rate,
        per-case results, and confusion matrix counts.
    """
    results = []
    tp = fp = tn = fn = 0

    for case in EVAL_CASES:
        text = case["text"]
        expected = case["expected_verdict"]

        # Run signal analysis
        signal_result = {"signal_count": 0, "scam_types": [], "heuristic_risk_boost": 0}
        if signal_analyzer:
            signal_result = signal_analyzer(text, case.get("image_path"))

        # Run ML prediction
        ml_result = {"verdict": "Unknown", "risk_score": 0, "reasons": []}
        if predictor:
            ml_result = predictor.predict_combined(text=text)

        # Determine actual verdict (combined)
        if predictor:
            actual_verdict = ml_result["verdict"]
        else:
            # Heuristic-only verdict
            boost = signal_result.get("heuristic_risk_boost", 0)
            if boost >= 25:
                actual_verdict = "Scam"
            elif boost >= 10:
                actual_verdict = "Suspicious"
            else:
                actual_verdict = "Safe"

        # Compute confusion matrix
        is_scam_expected = expected in ("Scam", "Suspicious")
        is_scam_actual = actual_verdict in ("Scam", "Suspicious")

        if is_scam_expected and is_scam_actual:
            tp += 1
        elif not is_scam_expected and not is_scam_actual:
            tn += 1
        elif not is_scam_expected and is_scam_actual:
            fp += 1
        elif is_scam_expected and not is_scam_actual:
            fn += 1

        result = {
            "id": case["id"],
            "expected": expected,
            "actual": actual_verdict,
            "correct": (is_scam_expected == is_scam_actual),
            "risk_score": ml_result.get("risk_score", signal_result.get("heuristic_risk_boost", 0)),
            "signals_triggered": signal_result.get("scam_types", []),
            "ml_reasons": ml_result.get("reasons", []),
            "notes": case["notes"],
        }
        results.append(result)

        if verbose:
            status = "✅ PASS" if result["correct"] else "❌ FAIL"
            print(f"[{status}] {case['id']} | Expected: {expected:10s} | "
                  f"Got: {actual_verdict:10s} | Score: {result['risk_score']:3d}% | "
                  f"Signals: {result['signals_triggered']}")

    # Metrics
    total = len(EVAL_CASES)
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

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
        print("\n" + "=" * 60)
        print("EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Total Cases  : {total}")
        print(f"TP           : {tp}  |  TN: {tn}")
        print(f"FP           : {fp}  |  FN: {fn}")
        print(f"Accuracy     : {accuracy:.2%}")
        print(f"Precision    : {precision:.2%}")
        print(f"Recall       : {recall:.2%}")
        print(f"F1 Score     : {f1:.4f}")
        print(f"False Pos.   : {fpr:.2%}")

    return summary


if __name__ == "__main__":
    import sys
    import os

    # Try to import signals and predictor for a full run
    try:
        from signals import analyze_signals
        print("[✓] Loaded signals.py")
    except ImportError:
        analyze_signals = None
        print("[!] signals.py not found — running heuristic-only evaluation")

    try:
        # Adjust path to Member 1's models directory
        REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        MODELS_DIR = os.path.join(REPO_ROOT, "Data And ML", "models")
        sys.path.insert(0, MODELS_DIR)
        from predictor import ScamLensPredictor
        predictor = ScamLensPredictor(models_dir=MODELS_DIR)
        print("[✓] Loaded ML Predictor from Data And ML/models/")
    except Exception as e:
        predictor = None
        print(f"[!] ML Predictor not loaded ({e}) — running heuristic-only evaluation")

    print("\n" + "=" * 60)
    print(">>> SCAMLENS EVAL BENCHMARK — Member 2 Test Set")
    print("=" * 60 + "\n")

    summary = run_evaluation(predictor=predictor, signal_analyzer=analyze_signals, verbose=True)
