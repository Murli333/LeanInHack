# ScamLens Dataset Registry & Provenance (Member 1: Data & ML)

This document tracks all external feeds, benchmark repositories, and hand-curated corpora used for training and evaluating ScamLens machine learning models.

---

## 1. External & Benchmark Datasets

### A. UCI SMS Spam Collection
- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/228/sms+spam+collection) (Mirror: `https://raw.githubusercontent.com/justmarkham/DAT8/master/data/sms.tsv`)
- **Version:** 1.0 (Standard benchmark corpus)
- **Download Date:** November 2026
- **License:** Public Domain / Research use (Attribution: Almeida, T.A., Gómez Hidalgo, J.M., Yamakami, A. Contributions to the study of SMS spam filtering, 2011)
- **Format:** Tab-separated text (`label \t text`), 5,574 messages (4,827 ham, 747 spam).
- **Usage:** Serves as the international baseline for standard SMS vocabulary, legitimate short conversational text, and generic commercial spam.

### B. OpenPhish Live Phishing Threat Feed
- **Source:** [OpenPhish Community Feed](https://openphish.com/feed.txt)
- **Version:** Dynamic Live Feed Snapshot (November 2026 snapshot archived in `data/raw/openphish_snapshot.txt`)
- **License:** OpenPhish Free Community Agreement (for security defense and academic research)
- **Format:** Plain text list of active phishing URLs identified in zero-day campaigns.
- **Usage:** Provides recent, active phishing URLs targeting financial institutions, cloud services, and email providers.

### C. Shreya Gopal Phishing Website Benchmark Dataset
- **Source:** [GitHub Repository: Phishing-Website-Detection-by-Machine-Learning-Techniques](https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/5.urldata.csv)
- **Version:** Benchmark 5.urldata.csv (5,000 legitimate and 5,000 phishing domains)
- **Download Date:** November 2026
- **License:** MIT Open Source License
- **Format:** CSV (`Domain, Label`), 10,000 domain records.
- **Usage:** Provides a balanced baseline of global phishing domains vs. legitimate top Alexa domains.

---

## 2. Curated Datasets (Indian Cybercrime & Region-Specific)

### D. Curated Indian Scam Message Corpus
- **Author/Collector:** ScamLens Data Team (Member 1)
- **Version:** 2.0 (Updated November 2026 with recent Indian modus operandi)
- **Source:** Real FIR reports, Indian Cyber Crime Coordination Centre (I4C / 1930) advisories, RBI consumer alerts, Delhi Police advisories, and crowdsourced scam SMS received across India.
- **Categories Covered:**
  1. **Fake KYC / Netbanking Block:** SBI YONO, HDFC card unlock, ICICI PAN link, Paytm wallet KYC.
  2. **Digital Arrest & Law Enforcement Impersonation:** Delhi Police, CBI, Mumbai Airport Narcotics, PMLA summons via Skype/WhatsApp.
  3. **Electricity & Utility Disconnection Threats:** BSES, Tata Power, Discom evening disconnection threats with fraudulent personal numbers.
  4. **UPI Collect / Refund Scams:** Amazon Pay, Google Pay, PhonePe deceptive collect requests with "Enter UPI PIN to receive money".
  5. **Part-time Task & Job Investment Scams:** YouTube likes, Google map ratings, Telegram HR recruiter VIP tasks.
  6. **Speed Post / Customs / Parcel Fee:** India Post address incomplete, FedEx customs clearance fee.
  7. **TRAI SIM Termination:** Telecom regulatory deactivation within 2 hours.
  8. **Government Subsidy / PM Yojana:** Fake PM scholarship, free laptop, solar scheme claims.
  9. **Lapsed Insurance Bonus:** Fake IRDAI / LIC maturity release scams.
  10. **Matrimonial & Foreign Gift Scams:** Custom clearance fee demand for overseas parcels.
  11. **Obfuscated & Hinglish Scams:** Messages with intentional typos (`w1n`, `lo@n`, `K Y C`) and mixed Hindi-English warnings (`aapka account band ho jayega`).

### E. Curated Indian Genuine (Ham) Corpus
- **Author/Collector:** ScamLens Data Team (Member 1)
- **Version:** 2.0 (Updated November 2026)
- **Source:** Authentic transactional SMS from verified Indian senders (DND-registered transactional headers), utility alerts, delivery updates, and common bilingual conversational messages.
- **Categories Covered:**
  - Bank transaction debit/credit alerts (HDFC, SBI, ICICI, Axis).
  - Genuine Bank OTPs (with standard "Never share OTP" disclaimer).
  - Food & Grocery deliveries (Swiggy, Zomato, Blinkit).
  - E-Commerce logistics & OTPs (Amazon, Flipkart, Myntra).
  - Government advisories (Aadhaar update, DigiLocker, Income Tax e-filing receipt).
  - Railway & Flight tickets (IRCTC PNR status, IndiGo web check-in).
  - Utility billing (Tata Power, BSES Delhi bill generation).
  - Healthcare & Education (Max Healthcare appointments, school portal notifications).

---

## 3. Dedicated Holdout Test Dataset

- **Location:** `data/holdout/holdout_text.csv` and `data/holdout/holdout_urls.csv`
- **Purpose:** A completely separate, untouched validation suite containing **never-seen-in-training** scam and ham instances.
- **Leakage Prevention:** Strictly excluded from any TF-IDF vocabulary fitting, training splits, and hyperparameter tuning. Used purely for unbiased final validation.
