# ScamLens — Member 2: Detection Logic & Test Set 🕵️

> **Role:** Heuristic Scam Signal Engine + OCR + Ground-Truth Evaluation Benchmark  
> **Delivers to:** Member 3 (`app.py` scoring integration) and Member 4 (UI explanation text)

---

## 📂 Module Contents

```
Detection Logic/
├── signals.py        ← Heuristic rule engine + OCR + scam signal catalog
├── eval_cases.py     ← 35 ground-truth test cases (18 scam, 17 genuine)
├── requirements.txt  ← Python dependencies (OCR + ML)
└── README.md         ← This file
```

---

## 🎯 What This Module Does

This module acts as the **intelligence layer** between Member 1's ML models and Member 3's app.  
It answers: *"Does this message match known Indian scam patterns?"*

### Core Responsibilities

| Task | File | Status |
|------|------|--------|
| Fake KYC signal detection | `signals.py` | ✅ |
| UPI collect request detection | `signals.py` | ✅ |
| Digital arrest / agency impersonation | `signals.py` | ✅ |
| Parcel / customs threat detection | `signals.py` | ✅ |
| Job scam / task scam detection | `signals.py` | ✅ |
| Electricity bill threat detection | `signals.py` | ✅ |
| OTP / PIN phishing detection | `signals.py` | ✅ |
| Loan fraud detection | `signals.py` | ✅ |
| URL phishing blocklist check | `signals.py` | ✅ |
| Urgency pressure tactic detection | `signals.py` | ✅ |
| Lottery / prize scam detection | `signals.py` | ✅ |
| Organizational impersonation | `signals.py` | ✅ |
| Screenshot OCR text extraction | `signals.py` | ✅ |
| 35-case evaluation benchmark | `eval_cases.py` | ✅ |
| Plain-language UI explanations | `signals.py` (SCAM_TYPE_CATALOG) | ✅ |

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r "Detection Logic/requirements.txt"
```

> **OCR setup (optional — only needed for screenshot analysis):**
> - Windows: Download Tesseract from https://github.com/UB-Mannheim/tesseract/wiki
> - Linux: `sudo apt-get install tesseract-ocr`
> - macOS: `brew install tesseract`

### 2. Run Signal Detection (Standalone)
```bash
cd "Detection Logic"
python signals.py
```

### 3. Run Evaluation Benchmark
```bash
cd "Detection Logic"
python eval_cases.py
```

---

## 🔌 API for Member 3 (Integration)

### Import and use in `app.py`:

```python
import sys
sys.path.insert(0, "Detection Logic")

from signals import analyze_signals, SCAM_TYPE_CATALOG, GENERAL_SAFETY_TIPS

# Analyze a text message
result = analyze_signals(
    text="Dear SBI user, your KYC is pending. Click http://sbi-kyc.top to update.",
    image_path=None   # Pass path to screenshot image for OCR
)

print(result["signal_count"])          # Number of signals triggered
print(result["scam_types"])            # ["Fake KYC Update", "Known Phishing URL"]
print(result["explanations"])          # Plain-language "why we think this" list
print(result["recommendations"])       # What the user should do
print(result["heuristic_risk_boost"])  # Score to add to ML model output (0–40)
print(result["ocr_text"])             # Text extracted from screenshot (if provided)
```

### Combined with Member 1's ML Predictor:
```python
from predictor import ScamLensPredictor
from signals import analyze_signals

predictor = ScamLensPredictor()
ml_result = predictor.predict_combined(text=message)

signal_result = analyze_signals(text=message)

# Combine scores (suggested weights — tune in app.py):
final_score = min(100, ml_result["risk_score"] + signal_result["heuristic_risk_boost"])
```

### Screenshot OCR:
```python
from signals import analyze_signals

result = analyze_signals(
    text="",   # or any additional typed text
    image_path="/path/to/screenshot.png"
)
print(result["ocr_text"])     # What was read from the image
print(result["scam_types"])   # Signals detected in the extracted text
```

---

## 📊 Signal Architecture

Each signal function in `signals.py` follows this contract:

```python
def signal_fake_kyc(text: str) -> dict:
    """
    Returns:
      {
        "triggered": True | False,
        "signal_id": "FAKE_KYC",
        "scam_type": "Fake KYC Update",
        "severity": 3,          # 1=low, 2=medium, 3=high
        "explanation": "...",   # Plain-language reason for UI
        "recommendation": "...", # What the user should do
      }
    """
```

### Severity Scale

| Level | Meaning | Risk Boost Added |
|-------|---------|-----------------|
| 3 (High) | Near-certain fraud indicator | +15 points |
| 2 (Medium) | Strong suspicious signal | +8 points |
| 1 (Low) | Soft indicator / supporting signal | +3 points |

> **Total heuristic boost is capped at +40** to preserve ML model's primary control of the final score.

---

## 🧪 Evaluation Cases Overview

`eval_cases.py` contains **35 carefully crafted test messages**:

| Category | Count | Notes |
|----------|-------|-------|
| 🚨 Scam cases | 18 | Cover all 10 scam types |
| ✅ Safe / Genuine cases | 17 | Real bank SMS, delivery, OTP alerts |

### Scam Coverage in Test Set

| Scam Type | Cases |
|-----------|-------|
| Fake KYC Update | SCAM_001, SCAM_006, SCAM_012 |
| UPI Collect Request | SCAM_003, SCAM_014 |
| Digital Arrest | SCAM_004, SCAM_008, SCAM_018 |
| Parcel / Customs | SCAM_007, SCAM_015 |
| Job / Task Scam | SCAM_005 |
| Electricity Bill Threat | SCAM_002 |
| Lottery / Prize Scam | SCAM_009, SCAM_016 |
| Fake Loan Offer | SCAM_011 |
| Organizational Impersonation | SCAM_010, SCAM_013, SCAM_017 |
| Digital Arrest + Parcel (combined) | SCAM_015, SCAM_018 |

---

## 🗂️ Phishing Blocklist

`signals.py` includes `PHISHING_BLOCKLIST` — a curated set of **35+ known malicious domains** confirmed in Indian scam campaigns, including:

- Fake KYC portals (sbi-kyc-verify.top, hdfc-netbanking.site)
- Fake electricity payment portals
- Parcel/customs scam domains
- Job scam recruitment sites
- Digital arrest / agency impersonation domains

Combined with `TRUSTED_DOMAINS` (40+ verified Indian banks, gov, and e-commerce sites) for allowlisting.

---

## 🖼️ OCR Module

`signals.py` → `extract_text_from_image(image_path)`:

- Uses **Tesseract-OCR** via `pytesseract`
- Automatically upscales small images for better accuracy
- Configured for English + (optionally) Hindi text
- Integrates with `analyze_signals()` — text extracted from screenshots is analyzed alongside typed text
- Graceful error handling: returns `[OCR ERROR] ...` string if Tesseract is missing

---

## 📋 Scam Type Catalog (For Member 4 — UI Text)

`signals.py` exports `SCAM_TYPE_CATALOG` — a dictionary of **15 scam types** with:
- `icon` — emoji icon for display
- `short_description` — one-line UI card label
- `full_explanation` — multi-sentence "why this is a scam" text
- `user_advice` — what to do in plain language
- `report_at` — where to report (cybercrime.gov.in, 1930)

Also exports `GENERAL_SAFETY_TIPS` — 8 universal safety tips for display in the UI's safety tips box.

---

## 🔄 Interface Contracts with Other Members

### → Member 1 (Data & ML)
- Uses `predictor.py` → `ScamLensPredictor` for `predict_combined()`
- `eval_cases.py` loads models from `../Data And ML/models/`

### → Member 3 (Integration & App)
- **Delivers:** `analyze_signals(text, image_path)` function
- **Delivers:** `SCAM_TYPE_CATALOG` and `GENERAL_SAFETY_TIPS` for UI
- **Delivers:** `heuristic_risk_boost` to combine with ML scores
- **Delivers:** `eval_cases.EVAL_CASES` list for weight tuning in `scoring.py`

### → Member 4 (UI/UX Designer)
- **Delivers:** `explanation` and `recommendation` strings per signal (verbatim UI copy)
- **Delivers:** `SCAM_TYPE_CATALOG` with icons, short and full descriptions, user advice
- **Delivers:** `GENERAL_SAFETY_TIPS` for the safety tips box

---

## 📝 Notes for Teammates

1. **Member 3:** Tune the `heuristic_risk_boost` weight by running `eval_cases.py` with the final models. Suggested starting weight: `final_score = min(100, ml_score * 0.7 + signal_boost * 0.3)` — adjust based on eval results.

2. **Member 4:** Every `explanation` and `recommendation` string in `signals.py` is written in plain, non-technical language and is ready to use as on-screen text. The `SCAM_TYPE_CATALOG` is the reference for the "Why we think this" section.

3. **OCR:** Tesseract must be installed on the deployment machine. If running on Streamlit Cloud, add it to `packages.txt`: `tesseract-ocr`.

---

*Member 2 — ScamLens Hackathon Project | LeanInHack 2024*
