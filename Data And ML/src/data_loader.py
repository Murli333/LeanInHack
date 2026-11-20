"""
Data Loader & Dataset Generator for ScamLens
Downloads standard benchmark datasets and augments them with realistic
Indian scam patterns (KYC, UPI, Digital Arrest, Electricity, Job Frauds)
and legitimate transactional communications.
"""
import os
import csv
import io
import requests
import pandas as pd
from typing import Tuple

# Augmentation: Real Indian Scam Messages (High Threat)
INDIAN_SCAM_SAMPLES = [
    ("spam", "Dear SBI user, your YONO account is locked due to pending KYC update. Click http://sbi-kyc-verify.top/sbi.apk to update immediately."),
    ("spam", "Urgent: Electricity power will be disconnected at 9:30 PM from power office because your previous month bill was not updated. Please immediately contact our electricity officer 9876543210."),
    ("spam", "Electricity Department Alert: Dear consumer, your bill Rs 1450 is unpaid. Power supply will be disconnected tonight. Call officer at 8912345678 immediately."),
    ("spam", "Dear Customer, your HDFC bank debit card is blocked. Kindly click http://hdfc-card-unlock.xyz/verify to unblock your card and update PAN card."),
    ("spam", "Income Tax Department: Refund of Rs 15,490 approved. Please submit your bank account details and OTP at http://incometax-refund-portal.site/claim"),
    ("spam", "Delhi Police Cyber Cell: A parcel in your name containing illegal narcotics has been seized at Mumbai airport. Digital arrest warrant issued. Contact CBI Officer on Skype/WhatsApp 9871203948 immediately."),
    ("spam", "Congratulations! You have been selected for part-time work from home. Earn Rs 2500-5000 daily by liking YouTube videos and Google reviews. Contact on Telegram @work_hr_india"),
    ("spam", "Dear Customer, you received UPI collect request of Rs 4999 from Amazon Pay. Enter your UPI PIN to receive money in your bank account."),
    ("spam", "Paytm KYC Alert: Your wallet is on hold. Complete video KYC now or account will be permanently blocked. Click http://paytm-kyc-kyc.top/update"),
    ("spam", "Dear Customer, your ICICI reward points worth Rs 9,850 are expiring today. Redeem in cash directly to your bank account: http://icici-points-reward.link/redeem"),
    ("spam", "Pre-approved Personal Loan of Rs 5,00,000 at 1% interest rate without CIBIL score. Download APK to claim: http://instant-cash-loan.top/loan.apk"),
    ("spam", "FedEx Express: Your parcel #FX-9821 cannot be delivered due to unpaid customs fee of Rs 480. Pay now or package will be returned: http://fedex-customs-india.xyz"),
    ("spam", "TRAI Alert: Your mobile SIM number will be disconnected within 2 hours due to illegal activity and Aadhaar mismatch. Call customer executive 9823411122."),
    ("spam", "Dear user, you have won Rs 25,00,000 in KBC Kaun Banega Crorepati lucky draw. To claim prize money WhatsApp Rana Pratap Singh at 7890123456."),
    ("spam", "Speed Post Alert: Your address is incomplete. Package delivery suspended. Update your address and pay Rs 25 redelivery fee: http://indiapost-update.xyz/login"),
    ("spam", "Airtel 5G SIM upgrade: Switch your 4G SIM to 5G free with 84 days recharge. Click http://airtel-5g-upgrade.site and enter your OTP to activate."),
    ("spam", "Dear Customer, PAN card verification failed for Bank account. To avoid freeze, click http://pancard-kyc-update.work and upload front and back photo."),
    ("spam", "CBI Notice: An arrest warrant has been issued against you under PMLA Act. Report immediately to virtual court room link: http://cbi-investigation.top/court"),
    ("spam", "You have a pending traffic challan of Rs 1000 on vehicle DL01AB1234. Pay within 24 hours to avoid court summons: http://echallan-parivahan-pay.xyz/bill"),
    ("spam", "Work from Home Amazon Part Time: Earn Rs 3000 to Rs 8000 daily with simple review tasks. WhatsApp us at +919811223344 right now for joining bonus.")
]

# Augmentation: Real Indian Legitimate Messages (Ham - Transactional & Informational)
INDIAN_HAM_SAMPLES = [
    ("ham", "Dear Customer, your Swiggy order from Biryani Blues is out for delivery. Delivery partner Ravi will reach you shortly. Track in Swiggy app."),
    ("ham", "OTP for your Zomato order is 4821. Please share with the delivery partner upon arrival. Do not share with anyone else."),
    ("ham", "Dear Customer, Rs 1,250.00 debited from HDFC Bank A/C ending 4589 on 18-NOV-26 towards UPI-Merchant. Bal: Rs 42,310.20."),
    ("ham", "Your PNR 2451982301 for Train 12301 NDLS RAJDHANI is confirmed. Coach B3 Berth 42. Check PNR status at www.irctc.co.in."),
    ("ham", "Dear Consumer, your Tata Power DDL electricity bill for CA No 60012345678 of Rs 2140 is due on 25-Nov. Pay via official portal or BBPS."),
    ("ham", "Dear Customer, 849201 is your one time password (OTP) for SBI Internet Banking login. Valid for 3 mins. Never share OTP with anyone."),
    ("ham", "Your Flipkart order containing boAt headphones has been delivered. Thank you for shopping with us! Rate your delivery experience."),
    ("ham", "Aadhaar OTP for authentication is 912048. Generated at 14:22 hrs. Valid for 10 minutes. Unique Identification Authority of India."),
    ("ham", "Dear Customer, your monthly statement for ICICI Bank Credit Card ending 1004 is generated. Total amount due: Rs 8,420. Due date: 05-Dec."),
    ("ham", "Hi Priya, are we meeting at Starbucks Connaught Place at 5 PM today? Let me know if you are running late."),
    ("ham", "Dear user, your recharge of Rs 299 for Airtel number 9810234567 was successful. Data: 1.5GB/day, Unlimited Calls for 28 days."),
    ("ham", "Uber: Your driver Ramesh is arriving in a white Dzire (DL1ZAA1234). PIN for trip is 7291."),
    ("ham", "Your appointment with Dr. Sharma at Apollo Clinic is confirmed for tomorrow at 11:30 AM. Please arrive 10 minutes early."),
    ("ham", "Dear Parent, school fees for term 2 have been published on student portal. Kindly clear by 30th November. DPS RK Puram."),
    ("ham", "Dear Customer, your Amazon package will be delivered today by 8 PM. OTP for delivery is 3910. Deliver to secure location if unavailable."),
    ("ham", "Dear SBI customer, Rs 5,000.00 credited to your A/C ending 3821 via NEFT from ABC Corp. Available Bal: Rs 58,190.00."),
    ("ham", "Dear Axis Bank Customer, your OTP for transaction of Rs 450.00 at Myntra is 639102. Valid for 5 minutes. Do not disclose to anyone."),
    ("ham", "BSES Yamuna Power: Dear Consumer, your electricity bill of Rs 3,410 for CA 100234567 has been generated. Due date 28-Nov-2026. Pay online to avail rebate."),
    ("ham", "Your Indigo flight 6E-204 from DEL to BLR is on schedule. Web check-in is now open. Boarding gate opens at 18:15 hrs."),
    ("ham", "Dear Customer, transaction alert: INR 350.00 spent on ICICI Bank Card XX4019 on 19-Nov-26 at CAFE COFFEE DAY. Avail limit: INR 85,000.")
]

# Curated Phishing URLs
CURATED_PHISHING_URLS = [
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
    "http://netflix-account-suspended-billing.click/update",
    "http://appleid-security-verification-login.site/confirm",
    "http://amazon-gift-card-wheel.vip/spin",
    "http://google-drive-shared-doc-login.work/file.html",
    "http://yono-sbi-reward.online/login.html",
    "http://bank-of-baroda-kyc.stream/kyc",
    "http://punjab-national-bank-pan-update.vip/pan",
    "http://axis-bank-netbanking-login.monster/secure",
    "http://bhim-upi-cashback-offer.bid/scratch",
    "http://free-recharge-jio-5g.club/claim",
    "http://whatsapp-pink-edition-download.xyz/whatsapp.apk",
    "http://courier-customs-clearance-tax.rest/payment"
]

# Legitimate Trusted URLs
CURATED_LEGITIMATE_URLS = [
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
    "https://www.google.com/search?q=cybersecurity",
    "https://github.com/scikit-learn/scikit-learn",
    "https://en.wikipedia.org/wiki/Phishing",
    "https://stackoverflow.com/questions",
    "https://www.microsoft.com/en-in",
    "https://www.apple.com/in/",
    "https://timesofindia.indiatimes.com/news",
    "https://indianexpress.com/section/india/",
    "https://www.tatapower.com/customer-services/",
    "https://www.bsesdelhi.com/web/brpl/home",
    "https://www.delhipolice.nic.in/",
    "https://www.rbi.org.in/",
    "https://echallan.parivahan.gov.in/"
]


def load_sms_dataset(data_dir: str = "data") -> pd.DataFrame:
    """
    Downloads UCI SMS dataset and merges with Indian scam & ham corpus.
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
    try:
        if not os.path.exists(raw_path):
            print(f"[*] Downloading UCI SMS dataset from {uci_url}...")
            resp = requests.get(uci_url, timeout=10)
            if resp.status_code == 200:
                with open(raw_path, "w", encoding="utf-8") as f:
                    f.write(resp.text)
                print(f"[+] Downloaded raw SMS dataset ({len(resp.text)} bytes).")

        if os.path.exists(raw_path):
            df_uci = pd.read_csv(raw_path, sep="\t", header=None, names=["label", "text"], quoting=csv.QUOTE_NONE, encoding="utf-8", on_bad_lines='skip')
            for _, row in df_uci.iterrows():
                lbl = str(row["label"]).strip().lower()
                txt = str(row["text"]).strip()
                if lbl in ["ham", "spam"] and txt:
                    records.append({"label": lbl, "text": txt, "is_scam": 1 if lbl == "spam" else 0})
            print(f"[+] Loaded {len(records)} messages from UCI dataset.")
    except Exception as e:
        print(f"[!] Warning: Failed to fetch online UCI dataset ({e}). Building from curated seed.")

    # 2. Augment with Indian scam cases (repeat 12x to establish solid pattern recognition)
    for _ in range(12):
        for lbl, msg in INDIAN_SCAM_SAMPLES:
            records.append({"label": lbl, "text": msg, "is_scam": 1})

    # 3. Augment with legitimate Indian transactional & conversational messages (repeat 15x)
    for _ in range(15):
        for lbl, msg in INDIAN_HAM_SAMPLES:
            records.append({"label": lbl, "text": msg, "is_scam": 0})

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
    url_records = []

    # 1. Fetch live OpenPhish feed
    try:
        print("[*] Fetching live phishing feed from OpenPhish...")
        op_resp = requests.get("https://openphish.com/feed.txt", timeout=8)
        if op_resp.status_code == 200:
            op_urls = [line.strip() for line in op_resp.text.split("\n") if line.strip() and line.startswith("http")]
            for u in op_urls[:500]:
                url_records.append({"url": u, "is_phishing": 1})
            print(f"[+] Added {len(op_urls[:500])} URLs from OpenPhish feed.")
    except Exception as e:
        print(f"[!] OpenPhish fetch notice: {e}")

    # 2. Add curated phishing URLs
    for u in CURATED_PHISHING_URLS:
        url_records.append({"url": u, "is_phishing": 1})
    for domain in ["sbi-card-reward.xyz", "hdfc-net-banking.top", "paytm-cash-bonus.site", "electricity-disconnection-bill.fit"]:
        for path in ["/login", "/verify", "/update.php", "/app.apk", "/collect-upi"]:
            url_records.append({"url": f"http://{domain}{path}", "is_phishing": 1})

    # 3. Add legitimate URLs
    for u in CURATED_LEGITIMATE_URLS:
        url_records.append({"url": u, "is_phishing": 0})
    for domain in ["google.com", "microsoft.com", "github.com", "wikipedia.org", "flipkart.com", "amazon.in"]:
        for path in ["/about", "/help", "/privacy", "/terms", "/search?q=test", "/products/catalog"]:
            url_records.append({"url": f"https://www.{domain}{path}", "is_phishing": 0})

    # 4. Fetch additional public legitimate/phishing sample dataset if available
    raw_url_file = os.path.join(raw_dir, "benchmark_urldata.csv")
    try:
        repo_url = "https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/5.urldata.csv"
        if not os.path.exists(raw_url_file):
            print(f"[*] Downloading domain samples from {repo_url}...")
            resp = requests.get(repo_url, timeout=12)
            if resp.status_code == 200:
                with open(raw_url_file, "w", encoding="utf-8") as f:
                    f.write(resp.text)
                print(f"[+] Cached raw benchmark URL dataset.")

        if os.path.exists(raw_url_file):
            df_ext = pd.read_csv(raw_url_file)
            if "Domain" in df_ext.columns and "Label" in df_ext.columns:
                for _, r in df_ext.iterrows():
                    domain = str(r["Domain"]).strip()
                    label = int(r["Label"]) # 1 is phishing, 0 is safe
                    if domain:
                        scheme = "http://" if label == 1 else "https://"
                        url_records.append({"url": scheme + domain, "is_phishing": label})
                print(f"[+] Integrated {len(df_ext)} benchmark domains from research dataset.")
    except Exception as e:
        print(f"[!] Benchmark domain fetch notice: {e}")

    df_urls = pd.DataFrame(url_records).drop_duplicates(subset=["url"]).reset_index(drop=True)
    df_urls.to_csv(cleaned_path, index=False, encoding="utf-8")
    print(f"[+] Total URL Dataset: {len(df_urls)} URLs ({df_urls['is_phishing'].sum()} phishing, {len(df_urls) - df_urls['is_phishing'].sum()} legitimate).")
    print(f"[+] Saved cleaned URL dataset to {cleaned_path}")
    return df_urls


if __name__ == "__main__":
    print("=== ScamLens Data Loader ===")
    df_sms = load_sms_dataset()
    df_url = load_url_dataset()
    print("=== Data Preparation Completed Successfully ===")
