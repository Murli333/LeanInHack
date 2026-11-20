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
    │  (Member 3: analyze() function in scoring.py)      │
    │  - Computes Unified Risk Score (0 - 100%)          │
    │  - Generates Plain-Language "Why We Think This"    │
    │  - Attaches Context-Aware Safety Recommendations   │
    └─────────────────────────┬───────────────────────────┘
                              │
                              ▼
    ┌─────────────────────────────────────────────────────┐
    │  Streamlit Consumer-Facing UI                       │
    │  (Member 3: app.py — Mobile-First, Accessible)     │
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
│   ├── data/                           # Raw & cleaned datasets
│   ├── models/                         # text_model.joblib, url_model.joblib, predictor.py
│   ├── evaluation/                     # Confusion matrices, benchmarks, results_summary.md
│   ├── src/                            # Preprocessing, 24-feature extractor, train.py
│   ├── tests/                          # 16-case verification test suite
│   ├── requirements.txt
│   └── README.md
│
├── Detection Logic/                    # [Member 2: Scam Rules & Test Set] ✅
│   ├── signals.py                      # 12 Indian scam signal types + blocklist + OCR
│   └── eval_cases.py                   # 36 ground-truth evaluation cases
│
├── Integration App and Report/         # [Member 3: Integration, App & Report] ✅
│   ├── app.py                          # Streamlit application UI
│   ├── scoring.py                      # Weighted risk-fusion engine + analyze() API
│   ├── tune_weights.py                 # Grid-search weight tuning & benchmarks
│   ├── requirements.txt
│   ├── README.md                       # Member 3 detailed documentation
│   ├── tests/
│   │   └── test_integration.py         # 16 end-to-end integration tests
│   └── evaluation/
│       └── benchmark_results.md        # Auto-generated benchmark report
│
└── Design/                             # [Member 4: UI/UX & Documentation]
    ├── assets/                         # Icons, badges, wireframe designs
    └── presentation/                   # Slide deck & final project report
```

### Team Responsibilities:
- **Member 1 (Data & ML):** Builds, trains, tunes, and evaluates the Text Scam Classifier and URL Phishing Model. Delivers `.joblib` models, confusion matrices, evaluation metrics, and the unified `ScamLensPredictor` API.
- **Member 2 (Detection Logic & Test Set):** Builds the heuristic scam signal engine (`signals.py`) covering 12 Indian scam types, a 35-domain phishing blocklist, OCR screenshot extraction, and a 36-case ground-truth benchmark (`eval_cases.py`).
- **Member 3 (Integration, App & Report):** Builds the Streamlit web application, integrates the ML models and rule-based signals into the `analyze()` pipeline, tunes weights, runs end-to-end tests, and compiles the final report.
- **Member 4 (UI/UX Designer):** Designs the mobile-first accessible interface (Safe/Suspicious/Scam cards, 0–100% risk meter, plain-language reason lists, error states) and creates the slide deck visuals.

---

## 🔬 Model Performance Summary

| Model | Accuracy | Precision | Recall | F1-Score | FPR | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Text Scam Classifier** | **99.33%** | **96.30%** | **98.48%** | **0.9738** | **0.55%** | **0.9996** |
| **URL Phishing Classifier** | **99.50%** | **99.86%** | **99.59%** | **0.9973** | **1.61%** | **0.9998** |

### Integrated System (Member 3 — 36-Case Benchmark):

| Metric | Value |
| :--- | :---: |
| Accuracy | **100.0%** |
| Precision | **100.0%** |
| Recall | **100.0%** |
| False Positive Rate | **0.0%** |
| F1-Score | **1.0** |

---

## 💻 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/Murli333/LeanInHack.git
cd LeanInHack
pip install -r "Integration App and Report/requirements.txt"
```

### 2. Run the Streamlit App
```bash
cd "Integration App and Report"
streamlit run app.py
```

### 3. Run All Tests
```bash
# Member 1 — ML model tests
cd "Data And ML"
python tests/test_models.py

# Member 3 — Integration tests
cd "../Integration App and Report"
python tests/test_integration.py

# Member 3 — Weight tuning benchmarks
python tune_weights.py
```

---

## 🔗 Quick API Usage

### From `scoring.py` (Member 3):
```python
from scoring import analyze

result = analyze(
    message_text="Your electricity will be disconnected tonight. Call 9876543210.",
    url="http://electricity-bill-disconnection-alert.fit/pay"
)

print(result["verdict"])      # "Scam"
print(result["risk_score"])   # 95
print(result["icon"])         # "🚨"
print(result["reasons"])      # ["Threatens immediate power disconnection...", ...]
print(result["safety_tips"])  # ["⚠️ Do NOT click any links...", ...]
```

### From `predictor.py` (Member 1):
```python
from models.predictor import ScamLensPredictor

predictor = ScamLensPredictor()
res = predictor.predict_text("Dear SBI user, update KYC immediately...")
print(res["verdict"], res["risk_score"])
```

---

## 🕵️ Scam Signal Coverage

| Signal | Scam Type | Severity |
|--------|-----------|----------|
| `fake_kyc` | Fake KYC / Account Suspension | 🔴 High |
| `upi_collect` | UPI Collect Request Fraud | 🔴 High |
| `parcel_customs` | Parcel / Customs Extortion | 🔴 High |
| `digital_arrest` | Digital Arrest / Agency Impersonation | 🔴 High |
| `job_scam` | Fake Part-Time Job / Task Scam | 🟡 Medium |
| `electricity_bill` | Electricity Bill Disconnection Threat | 🔴 High |
| `urgency` | High-Pressure Urgency Tactics | 🟢 Low |
| `malicious_apk` | APK / Remote Access App Download | 🔴 High |

---

## 📜 License & Compliance
Built for the **LeanInHack** Hackathon. Educational & Cybersecurity research purposes. All scam phone numbers and test indicators use synthetic dummy records or known neutralized scam campaign patterns.
