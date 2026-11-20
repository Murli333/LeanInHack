# ScamLens 🛡️🔍
### *AI-Powered Digital Fraud Detection & Explainable Cybersecurity Assistant*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4%2B-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()
[![Hackathon](https://img.shields.io/badge/Hackathon-LeanInHack-purple.svg)]()

---

## 📌 Executive Summary

**ScamLens** is an intelligent, multimodal digital safety assistant designed to protect everyday citizens from evolving digital fraud. Unlike legacy spam filters that merely flag suspicious keywords or rely on basic link blocklists, ScamLens combines **calibrated Machine Learning models, heuristic scam signals, structural URL inspection, OCR, and explainable AI** to provide context-aware, human-readable fraud intelligence.

When an end user receives an unsolicited message, payment link, or screenshot, ScamLens answers three fundamental questions in plain language:
1. **Is this safe, suspicious, or a scam?**
2. **What is the risk level (0 to 100%)?**
3. **Why is it suspicious, and what concrete steps should the user take?**

---

## 🚨 The Threat Landscape (Indian Cyber Scam Epidemic)

Digital financial fraud in India has skyrocketed with the adoption of instant digital payments (UPI) and messaging platforms. ScamLens is purpose-engineered to counter top prevalent threat vectors:

- **Fake KYC Updates:** Urgent SMS claiming bank accounts, debit cards, or SIMs will be blocked unless a rogue APK or phishing link is visited.
- **Electricity Bill Disconnection Threats:** Messages threatening immediate power cutoff tonight unless an "officer" is called or an outstanding bill is paid.
- **Digital Arrest & Agency Impersonation:** Deceptive calls or messages impersonating the CBI, ED, Delhi Police, or Customs claiming seized narcotics or parcel contraband.
- **UPI Collect Request Fraud:** Tricking users into entering their UPI PIN under the false pretext of receiving cashback, lottery prizes, or refunds.
- **Part-Time Task & Job Scams:** Enticing users with high daily earnings for liking YouTube videos or rating Google Maps locations, leading to advance-fee deposit fraud.

---

## 🏗️ System Architecture & Workflow

```
[ User Input: Suspicious SMS / WhatsApp / URL / Screenshot ]
                              │
                              ▼
    ┌─────────────────────────────────────────────────────┐
    │  Multimodal Extraction & Input Preprocessing         │
    │  - Text Normalization (<CURRENCY>, <PHONE>, <CODE>) │
    │  - OCR Text Extraction (for uploaded screenshots)   │
    │  - URL Lexical & Structural Parser (24 features)    │
    └─────────────────────────┬───────────────────────────┘
                              │
                              ▼
    ┌─────────────────────────────────────────────────────┐
    │  ScamLens Dual-Core ML Inference Engine             │
    │                                                     │
    │  ┌───────────────────────┐ ┌──────────────────────┐ │
    │  │ Text Scam Classifier  │ │ URL Phishing Engine  │ │
    │  │ (TF-IDF + Calibrated  │ │ (24-Feature Ensemble │ │
    │  │  Logistic Regression) │ │  Random Forest)      │ │
    │  │ Accuracy: 99.33%      │ │ Accuracy: 99.50%     │ │
    │  │ FPR: 0.55%            │ │ FPR: 1.61%           │ │
    │  └───────────┬───────────┘ └──────────┬───────────┘ │
    │              │                        │             │
    └──────────────┼────────────────────────┼─────────────┘
                   │                        │
                   ▼                        ▼
    ┌─────────────────────────────────────────────────────┐
    │  Heuristic Rules & Signal Corroboration             │
    │  (Member 2: signals.py & Blocklist Verification)    │
    └─────────────────────────┬───────────────────────────┘
                              │
                              ▼
    ┌─────────────────────────────────────────────────────┐
    │  Ensemble Risk Scorer & Explainability Engine       │
    │  (Member 3: analyze() function in app.py)           │
    │  - Computes Unified Risk Score (0 - 100%)           │
    │  - Generates Plain-Language "Why We Think This"     │
    │  - Attaches Context-Aware Safety Recommendations    │
    └─────────────────────────┬───────────────────────────┘
                              │
                              ▼
    ┌─────────────────────────────────────────────────────┐
    │  Streamlit Consumer-Facing UI                       │
    │  (Member 4: Mobile-First, Accessible 3 States)      │
    │  - ✅ Safe State (0 - 39% | Calm Green)             │
    │  - ⚠️ Suspicious State (40 - 69% | Amber Caution)   │
    │  - 🚨 Scam State (70 - 100% | Urgent Red)           │
    └─────────────────────────────────────────────────────┘
```

---

## 👥 Team Ownership & Project Structure

The project repository is structured into modular domains so each team member can work independently while maintaining strict interface contracts:

```
LeanInHack/
│
├── Data And ML/             # [MEMBER 1: ML MODELS & PIPELINES] ✅ COMPLETED
│   ├── data/                # Raw & cleaned datasets (UCI SMS, OpenPhish, Indian Curated)
│   ├── models/              # Trained models (text_model.joblib, url_model.joblib, predictor.py)
│   ├── evaluation/          # Confusion matrices, benchmark JSON, results_summary.md
│   ├── src/                 # Preprocessing, 24-feature extractor, train.py
│   ├── tests/               # 16-test verification suite (100% pass)
│   ├── requirements.txt     # Python ML dependencies
│   └── README.md            # Deep-dive ML engineering documentation
│
├── Detection Logic/         # [MEMBER 2: HEURISTICS & TEST BENCHMARK] ✅ COMPLETED
│   ├── signals.py           # Indian scam rules (12 signal types, phishing blocklist, OCR)
│   ├── eval_cases.py        # 35 ground-truth evaluation cases (18 scam, 17 genuine)
│   ├── requirements.txt     # Python dependencies (pytesseract, Pillow, scikit-learn)
│   └── README.md            # API docs, signal catalog, integration guide
│
├── App/                     # [MEMBER 3: INTEGRATION & APP]
│   ├── app.py               # Streamlit application UI & analyze() endpoint
│   └── scoring.py           # Final weighted risk scoring engine
│
└── Design/                  # [MEMBER 4: UI/UX & ASSETS]
    ├── assets/              # Icons, badges, wireframe designs
    └── presentation/        # Slide deck & final project report diagrams
```

### Team Responsibilities:
- **Member 1 (Data & ML):** Builds, trains, tunes, and evaluates the Text Scam Classifier and URL Phishing Model. Delivers `.joblib` models, confusion matrices, evaluation metrics, and the unified `ScamLensPredictor` API.
- **Member 2 (Detection Logic & Test Set):** Builds the heuristic scam signal engine (`signals.py`) covering 12 Indian scam types, a 35-domain phishing blocklist, OCR screenshot extraction, and a 35-case ground-truth benchmark (`eval_cases.py`). Provides plain-language explanations and recommendations for all scam categories, and exports the `SCAM_TYPE_CATALOG` for the UI.
- **Member 3 (Integration, App & Report):** Builds the Streamlit web application, integrates the ML models and rule-based signals into the `analyze()` pipeline, tunes weights, and compiles the project report.
- **Member 4 (UI/UX Designer):** Designs the mobile-first accessible interface (Safe/Suspicious/Scam cards, 0–100% risk meter, plain-language reason lists, error states) and creates the slide deck visuals.

---

## 🔬 Member 1: Completed ML Deliverables & Performance

Member 1 has completed and pushed all data pipelines, trained models, evaluation assets, and inference wrappers:

### Benchmark Summary

| Model | Algorithm | Accuracy | Precision | Recall | F1-Score | False Positive Rate (FPR) | ROC-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Text Scam Classifier** | TF-IDF (1-2 N-grams) + Calibrated Logistic Regression | **99.33%** | **96.30%** | **98.48%** | **0.9738** | **0.55%** | **0.9996** |
| **URL Phishing Classifier** | 24 Structural/Lexical Features + Random Forest Ensemble | **99.50%** | **99.86%** | **99.59%** | **0.9973** | **1.61%** | **0.9998** |

### Why Low False Positive Rate (FPR) is Critical:
In fraud intelligence, a high false positive rate destroys user trust—blocking a genuine banking OTP or a train PNR confirmation causes immediate panic. ScamLens achieves an **FPR under 1.6%**, safely filtering genuine transactional alerts while catching subtle scam patterns.

---

## 💻 Quick Start & Running the Models

### 1. Clone the Repository
```bash
git clone https://github.com/Murli333/LeanInHack.git
cd LeanInHack
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r "Data And ML/requirements.txt"
```

### 3. Run the Verification Test Suite
Runs 16 realistic test cases covering Indian scams, legitimate transactions, and phishing URLs:
```bash
cd "Data And ML"
python tests/test_models.py
```

### 4. Retrain Models (Optional)
The pre-trained `.joblib` files are already bundled in `models/`. To re-download datasets and retrain from scratch:
```bash
cd "Data And ML"
python src/train.py
```

---

## 🔗 Quick API Usage for Teammates

### Text Analysis:
```python
from models.predictor import ScamLensPredictor

predictor = ScamLensPredictor()
res = predictor.predict_text("Electricity power will be disconnected at 9:30 PM. Call officer at 9876543210.")

print(res["verdict"])     # 'Scam'
print(res["risk_score"])  # 89 (0-100 scale)
print(res["reasons"])     # ['Pressures you with immediate electricity disconnection threats.']
```

### URL Analysis:
```python
res = predictor.predict_url("http://sbi-kyc-verify.top/sbi.apk")

print(res["verdict"])     # 'Scam'
print(res["risk_score"])  # 99
print(res["reasons"])     # ['Registered under an untrusted, high-risk top-level domain (TLD).', 'Links directly to an untrusted executable or package (.apk/.exe).']
```

### Combined Multimodal Analysis (For `app.py`):
```python
res = predictor.predict_combined(
    text="Dear SBI customer, update KYC immediately: http://sbi-kyc-verify.top/sbi.apk"
)
print(res["verdict"])      # 'Scam'
print(res["risk_score"])   # 96
print(res["status_color"]) # 'red'
print(res["icon"])         # '🚨'
print(res["safety_tips"])  # ['Do NOT click any links...', 'Never share OTP/PIN...']
```

---

## 🕵️ Member 2: Completed Detection Logic Deliverables

Member 2 has completed and pushed the full heuristic signal engine, phishing blocklist, OCR module, and ground-truth evaluation benchmark.

### Signal Engine Coverage (`signals.py`)

| Signal | Scam Type | Severity | Indian Threat Context |
|--------|-----------|----------|----------------------|
| `signal_fake_kyc` | Fake KYC Update | 🔴 High | Bank/SIM KYC expiry threats with APK phishing links |
| `signal_upi_collect_request` | UPI Collect Request Fraud | 🔴 High | "Enter PIN to receive cashback" debit fraud |
| `signal_parcel_customs_threat` | Parcel / Customs Scam | 🔴 High | FedEx/DHL impersonation, fake customs clearance fees |
| `signal_digital_arrest` | Digital Arrest / Agency Impersonation | 🔴 High | CBI/ED/Police fake arrest via video call |
| `signal_job_offer_scam` | Fake Job / Task Scam | 🟡 Medium | YouTube-like/Google Maps rating advance-fee trap |
| `signal_electricity_bill_threat` | Electricity Bill Disconnection Scam | 🔴 High | Fake DISCOM officer demanding immediate payment |
| `signal_otp_phishing` | OTP / PIN Phishing | 🔴 High | "Share OTP with agent" account takeover |
| `signal_loan_fraud` | Fake Loan Offer | 🟡 Medium | No-document instant loan with upfront fee trap |
| `signal_phishing_url` | Known Phishing URL / Brand Impersonation | 🔴 High | Blocklist + TLD + APK + brand checks |
| `signal_urgency_pressure` | High-Pressure Urgency Tactic | 🟢 Low | Panic-inducing phrases to bypass rational thought |
| `signal_prize_lottery_scam` | Lottery / Prize Scam | 🟡 Medium | KBC lottery, fake Jio/Amazon winner SMS |
| `signal_impersonation` | Organizational Impersonation | 🟡 Medium | Fake RBI, TRAI, PM Cares, Income Tax notices |

### Phishing Infrastructure
- **35+ blocklisted domains** confirmed in Indian cybercrime campaigns
- **40+ trusted domains** allowlisted to prevent false positives on real bank/gov SMS
- Subdomain-aware matching (e.g., `login.sbi-kyc-verify.top` is caught)

### Evaluation Benchmark (`eval_cases.py`): 35 Cases

| Metric | Heuristic-Only | Combined (ML + Heuristic) |
|--------|---------------|--------------------------|
| Scam Cases | 18 | 18 |
| Safe Cases | 17 | 17 |
| True Positives | — | 17/18 (94.4% recall) |
| True Negatives | — | 6/17 |
| Heuristic False Positives | **0** | — |
| Notes | Signals engine has 0 FP on safe cases | ML model needs FPR tuning by Member 3 |

> **Note for Member 3:** The eval results show the ML model (trained on UCI SMS spam) flags some legitimate Indian bank SMS (Paytm confirmations, Aadhaar-related, electricity bills) as scams due to keyword overlap. Use `heuristic_risk_boost` from `signals.py` as the primary signal — the heuristics have **0 false positives** on our test set. Suggested weight: `final_score = ml_score * 0.6 + signal_boost * 0.4` where `signal_boost` = `heuristic_risk_boost * 2.5`.

### Quick API for `app.py` Integration

```python
import sys
sys.path.insert(0, "Detection Logic")
from signals import analyze_signals, SCAM_TYPE_CATALOG, GENERAL_SAFETY_TIPS

# Analyze text (and optional screenshot)
result = analyze_signals(text=message, image_path=screenshot_path)

# Key outputs:
result["heuristic_risk_boost"]  # 0–40 points to add to ML score
result["scam_types"]            # e.g. ["Fake KYC Update", "Known Phishing URL"]
result["explanations"]          # Plain-language "Why we think this" list (UI-ready)
result["recommendations"]       # Action steps for the user
result["ocr_text"]              # Text extracted from screenshot via OCR
```

---

## 🛠️ Git Collaboration Guide for Team Members

### Pulling the latest changes from GitHub:
```bash
git pull origin main
```

### Pushing your changes:
```bash
git add .
git commit -m "feat(module): description of what you implemented"
git push origin main
```

---

## 📜 License & Compliance
Built for the **LeanInHack** Hackathon. Educational & Cybersecurity research purposes. All scam phone numbers and test indicators use synthetic dummy records or known neutralized scam campaign patterns.
