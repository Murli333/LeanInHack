# ScamLens 🛡️🔍
### *AI-Powered Digital Fraud Detection & Explainable Cybersecurity Assistant*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4%2B-orange.svg)](https://scikit-learn.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red.svg)](https://streamlit.io/)
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
    │  - Unicode Homoglyphs & Hinglish Deobfuscation      │
    │  - Text Normalization (markers, entities, emojis)   │
    │  - OCR Text Extraction (for uploaded screenshots)   │
    │  - URL Lexical & Structural Parser (28 features)    │
    └─────────────────────────┬───────────────────────────┘
                              │
                              ▼
    ┌─────────────────────────────────────────────────────┐
    │  ScamLens Dual-Core ML Inference Engine (v2.1)      │
    │                                                     │
    │  ┌───────────────────────┐ ┌──────────────────────┐ │
    │  │ Text Scam Classifier  │ │ URL Phishing Engine  │ │
    │  │ (TF-IDF + Calibrated  │ │ (28-Feature Ensemble │ │
    │  │  Logistic Regression) │ │  Random Forest)      │ │
    │  │ Accuracy: 99.04%      │ │ Accuracy: 99.26%     │ │
    │  │ FPR: 0.55%            │ │ FPR: 4.48%           │ │
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
    │  (Member 3: analyze() function in scoring.py)       │
    │  - Computes Unified Risk Score (0 - 100%)           │
    │  - Generates Plain-Language "Why We Think This"     │
    │  - Attaches Context-Aware Safety Recommendations    │
    └─────────────────────────┬───────────────────────────┘
                              │
                              ▼
    ┌─────────────────────────────────────────────────────┐
    │  Streamlit Consumer-Facing UI                       │
    │  (Member 3 & 4: Mobile-First, Accessible)           │
    │  - ✅ Safe State (0 - 39% | Calm Green)             │
    │  - ⚠️ Suspicious State (40 - 69% | Amber Caution)   │
    │  - 🚨 Scam State (70 - 100% | Urgent Red)           │
    └─────────────────────────────────────────────────────┘
```

---

## 👥 Team Ownership & Project Structure

```
LeanInHack/
│
├── Data And ML/                        # [Member 1: Data & Machine Learning] ✅
│   ├── data/                           # Raw & cleaned datasets (UCI SMS, OpenPhish, Curated)
│   ├── models/                         # text_model.joblib, url_model.joblib, predictor.py
│   ├── evaluation/                     # Confusion matrices, benchmark JSON, results_summary.md
│   ├── src/                            # Preprocessing, 24-feature extractor, train.py
│   ├── tests/                          # 16-case verification test suite
│   ├── requirements.txt                # Python ML dependencies
│   └── README.md                       # Deep-dive ML engineering documentation
│
├── Detection Logic/                    # [Member 2: Scam Rules & Test Set] ✅
│   ├── signals.py                      # 12 Indian scam signal types, blocklist, allowlist, OCR
│   ├── eval_cases.py                   # 35 ground-truth evaluation cases (18 scam, 17 genuine)
│   ├── requirements.txt                # pytesseract, Pillow, scikit-learn
│   └── README.md                       # API docs, signal catalog, integration guide
│
├── Integration App and Report/         # [Member 3: Integration, App & Report] ✅
│   ├── app.py                          # Streamlit application UI with one-click demo pills
│   ├── scoring.py                      # Weighted risk-fusion engine + analyze() API
│   ├── tune_weights.py                 # Grid-search weight tuning & benchmark suite
│   ├── FINAL_PROJECT_REPORT.md         # Comprehensive project submission report
│   ├── requirements.txt                # Streamlit & integration dependencies
│   ├── README.md                       # Member 3 detailed documentation
│   ├── tests/
│   │   └── test_integration.py         # 16 end-to-end integration tests (100% pass)
│   └── evaluation/
│       └── benchmark_results.md        # Benchmark evaluation results log
│
└── Design/                             # [Member 4: UI/UX & Documentation]
    ├── assets/                         # Icons, badges, wireframe designs
    └── presentation/                   # Slide deck & final project report diagrams
```

### Team Responsibilities:
- **Member 1 (Data & ML):** Builds, trains, tunes, and evaluates the Text Scam Classifier and URL Phishing Model. Delivers `.joblib` models, confusion matrices, evaluation metrics, and the unified `ScamLensPredictor` API.
- **Member 2 (Detection Logic & Test Set):** Builds the heuristic scam signal engine (`signals.py`) covering 12 Indian scam types, a 35-domain phishing blocklist, OCR screenshot extraction, and a 35-case ground-truth benchmark (`eval_cases.py`). Provides plain-language explanations and recommendations for all scam categories, and exports `SCAM_TYPE_CATALOG` and `GENERAL_SAFETY_TIPS`.
- **Member 3 (Integration, App & Report):** Builds the Streamlit web application, integrates the ML models and rule-based signals into the `analyze()` pipeline, tunes weights, runs end-to-end integration tests, and compiles the project report.
- **Member 4 (UI/UX Designer):** Designs the mobile-first accessible interface (Safe/Suspicious/Scam cards, 0–100% risk meter, plain-language reason lists, error states) and creates the slide deck visuals.

---

## 🔬 Member 1: Completed ML Deliverables & Performance

| Model | Algorithm | Accuracy | Precision | Recall | F1-Score | False Positive Rate (FPR) | ROC-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Text Scam Classifier** | TF-IDF (1-2 N-grams) + Calibrated Logistic Regression | **99.33%** | **96.30%** | **98.48%** | **0.9738** | **0.55%** | **0.9996** |
| **URL Phishing Classifier** | 24 Structural/Lexical Features + Random Forest Ensemble | **99.50%** | **99.86%** | **99.59%** | **0.9973** | **1.61%** | **0.9998** |

### Why Low False Positive Rate (FPR) is Critical:
In fraud intelligence, a high false positive rate destroys user trust—blocking a genuine banking OTP or a train PNR confirmation causes immediate panic. ScamLens achieves an **FPR under 1.6%**, safely filtering genuine transactional alerts while catching subtle scam patterns.

---

## 🕵️ Member 2: Completed Detection Logic Deliverables

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

---

## ⚡ Member 3: Integration, App & Tuned Benchmark

### Integrated System Benchmark Results:

| Metric | Value | Target Benchmark | Verdict |
| :--- | :---: | :---: | :---: |
| **Accuracy** | **100.0%** | > 92.0% | ✅ **Passed** |
| **Precision** | **100.0%** | > 95.0% | ✅ **Passed** |
| **Recall (Sensitivity)** | **100.0%** | > 90.0% | ✅ **Passed** |
| **False Positive Rate (FPR)** | **0.0%** | < 2.0% | ✅ **Passed** |
| **F1-Score** | **1.0000** | > 0.90 | ✅ **Passed** |

---

## 💻 Quick Start & Running the Platform

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

pip install -r "Integration App and Report/requirements.txt"
```

### 3. Launch the Streamlit Consumer App
```bash
cd "Integration App and Report"
streamlit run app.py
```
*Opens automatically at `http://localhost:8501`.*

### 4. Run All Test Suites
```bash
# Member 1 — ML model test suite (16 tests)
python "Data And ML/tests/test_models.py"

# Member 3 — Integration test suite (16 tests)
python "Integration App and Report/tests/test_integration.py"

# Member 3 — Weight tuning and evaluation benchmarks
python "Integration App and Report/tune_weights.py"
```

---

## 🔗 Quick API Usage

### Combined Multimodal Analysis (Member 3 `scoring.py`):
```python
import sys
sys.path.insert(0, "Integration App and Report")
from scoring import analyze

res = analyze(
    message_text="Electricity power will be disconnected at 9:30 PM. Call officer at 9876543210.",
    url="http://electricity-bill-disconnection-alert.fit/pay"
)

print(res["verdict"])      # 'Scam'
print(res["risk_score"])   # 95
print(res["status_color"]) # 'red'
print(res["icon"])         # '🚨'
print(res["reasons"])      # Plain-language explanation bullet points
print(res["safety_tips"])  # Actionable emergency tips
```

---

## 📜 License & Compliance
Built for the **LeanInHack** Hackathon. Educational & Cybersecurity research purposes. All scam phone numbers and test indicators use synthetic dummy records or known neutralized scam campaign patterns.
