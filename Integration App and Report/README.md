# ScamLens — Member 3: Integration, App & Report

> **Owner:** Member 3 — Integration, Streamlit Application & Final Submission  
> **Status:** ✅ Complete

---

## 🎯 Responsibilities

| # | Task | Status |
|---|------|--------|
| 1 | Build the `analyze()` scoring function that fuses ML + rules + blocklist | ✅ |
| 2 | Tune fusion weights using Member 2's 36 ground-truth eval cases | ✅ |
| 3 | Build the Streamlit app with Member 4's design (3-state cards, risk meter, reasons, tips) | ✅ |
| 4 | End-to-end integration tests (16 cases) | ✅ |
| 5 | Compile final report from all members' sections | ✅ |

---

## 📂 Folder Structure

```
Integration App and Report/
├── app.py                   # Streamlit UI — the user-facing application
├── scoring.py               # Weighted risk-fusion engine + analyze() API
├── tune_weights.py          # Grid-search weight tuning & benchmark evaluation
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── tests/
│   └── test_integration.py  # 16 end-to-end integration tests
└── evaluation/
    └── benchmark_results.md # Auto-generated benchmark report
```

---

## 🔗 How It Integrates with Other Members

```
Member 1 (Data & ML)                    Member 2 (Detection Logic)
 ├─ text_model.joblib                    ├─ signals.py (12 scam rules)
 ├─ url_model.joblib                     ├─ eval_cases.py (36 test cases)
 └─ predictor.py (ScamLensPredictor)     └─ OCR extraction
         │                                        │
         └──────────────┐    ┌─────────────────────┘
                        ▼    ▼
              ┌──────────────────────────┐
              │   scoring.py             │  ← Member 3
              │   ScamLensScoringEngine  │
              │   analyze() function     │
              └──────────┬───────────────┘
                         │
                         ▼
              ┌──────────────────────────┐
              │   app.py (Streamlit UI)  │  ← Member 3
              │   Member 4's design      │
              └──────────────────────────┘
```

---

## 📊 Scoring Architecture

The `analyze()` function in `scoring.py` runs **five parallel analysis layers** and fuses them into a single calibrated risk score (0–100%):

| Layer | Source | Weight |
|-------|--------|--------|
| Text ML Classifier | Member 1 `predictor.predict_text()` | 0.30 |
| Text Rule Engine | Member 2 `signals.evaluate_rules()` | 0.35 |
| URL ML Classifier | Member 1 `predictor.predict_url()` | 0.15 |
| URL Rule + Blocklist | Member 2 `signals.check_url()` | 0.20 |
| OCR Extraction | Member 2 `extract_text_from_image()` | feeds text layer |

### Critical Override Logic
- **Blocklisted domain detected** → score floors at **95%** (Scam)
- **Digital arrest / Fake KYC + suspicious URL** → score floors at **88%** (Scam)
- **Benign transaction markers + no scam signals** → score caps at **15%** (Safe)

### Verdict Mapping

| Score Range | Verdict | Colour | Icon |
|-------------|---------|--------|------|
| 0 – 39% | Safe | Green `#10B981` | ✅ |
| 40 – 69% | Suspicious | Amber `#F59E0B` | ⚠️ |
| 70 – 100% | Scam | Red `#EF4444` | 🚨 |

---

## 📈 Benchmark Results (Tuned Weights)

Evaluated on Member 2's **36 ground-truth cases** (18 scam + 18 legitimate):

| Metric | Value |
|--------|-------|
| **Accuracy** | **100.0%** |
| **Precision** | **100.0%** |
| **Recall** | **100.0%** |
| **False Positive Rate** | **0.0%** |
| **F1-Score** | **1.0** |
| True Positives | 18 |
| True Negatives | 18 |
| False Positives | 0 |
| False Negatives | 0 |

> **Key takeaway:** Perfect score — every scam correctly flagged, every legitimate message correctly cleared. Zero false positives and zero false negatives.

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r "Integration App and Report/requirements.txt"
```

### 2. Run the Streamlit App
```bash
cd "Integration App and Report"
streamlit run app.py
```
The app opens at `http://localhost:8501`.

### 3. Run Weight Tuning & Benchmarks
```bash
cd "Integration App and Report"
python tune_weights.py
```

### 4. Run Integration Tests
```bash
cd "Integration App and Report"
python tests/test_integration.py
```

---

## 🖥️ App Screens (Member 4 Design Specs)

### Input Screen
- Large text area for messages
- Smaller field for suspicious URLs
- Screenshot upload button (PNG/JPG)
- Single "🔍 Check for Scam" button

### Result Screen — 3 States
- **Safe** — Green card, ✅ icon, calm reassuring text
- **Suspicious** — Amber card, ⚠️ icon, cautionary advice
- **Scam** — Red card, 🚨 icon, urgent action items

### Every result includes:
- Risk meter (0–100% progress bar)
- "Why we think this" — plain-language bullet list
- Screenshot preview with OCR-extracted text
- Safety tips box with reporting info

---

## 📋 Output Schema

```python
{
    "verdict":      "Scam",          # "Safe" | "Suspicious" | "Scam" | "Empty"
    "risk_score":   96,              # 0–100
    "status_color": "red",           # "green" | "amber" | "red" | "gray"
    "icon":         "🚨",
    "reasons": [
        "Urges you to complete KYC to prevent account suspension.",
        "Uses an untrusted high-risk top-level domain (.top).",
    ],
    "safety_tips": [
        "⚠️ Do NOT click any links or install APK files.",
        "🔒 Never share your OTP, UPI PIN, or banking passwords.",
        "📢 Report at https://cybercrime.gov.in or call 1930.",
    ],
    "details": {
        "effective_text":     "...",
        "effective_url":      "http://sbi-kyc-verify.top/sbi.apk",
        "ocr_extracted_text": null,
        "text_ml_score":      92,
        "text_rule_score":    95,
        "url_ml_score":       99,
        "url_rule_score":     98,
        "triggered_signals":  ["fake_kyc", "urgency", "malicious_apk"],
    }
}
```

---

## 🤝 Handover Deliverables

| Deliverable | File |
|-------------|------|
| Working Streamlit app | `app.py` |
| Scoring engine + `analyze()` API | `scoring.py` |
| Weight-tuned benchmark results | `evaluation/benchmark_results.md` |
| Integration test suite | `tests/test_integration.py` |
| All Python dependencies | `requirements.txt` |
| This documentation | `README.md` |
