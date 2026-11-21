# ScamLens — Member 2: Detection Logic & Test Benchmark 🛡️🔍

> **Role:** Rule-based detection, Indian scam pattern heuristics, phishing domain inspection, OCR screenshot extraction, plain-language explanation generation, and ground-truth evaluation benchmark.  
> **Delivers to:** Member 3 (`app.py` / `scoring.py` risk fusion engine) and Member 4 (consumer-facing UI explainability copy).

---

## 📂 Module Architecture & File Tree

```
Detection Logic/
├── data/
│   ├── blocklist.json      ← Versioned JSON blocklist of 40+ confirmed phishing domains & URL shorteners
│   └── allowlist.json      ← Versioned JSON allowlist of 48 verified Indian banks, gov, and utilities
├── tests/
│   ├── test_signals.py     ← Dedicated unit tests for all 16 individual scam signal detectors
│   ├── test_urls.py        ← Tests for URL extraction, domain parsing, and TLD/shortener matching
│   ├── test_allowlist.py   ← Tests for trusted domain validation and context preservation
│   ├── test_ocr.py         ← Tests for OCR validation, format checks, error codes, and result schema
│   └── test_scenarios.py   ← Tests for false-positive prevention and adversarial evasion prevention
├── signals.py              ← Core heuristics engine, OCR pipeline, URL parser & scam explanation catalog
├── eval_cases.py           ← 61-case ground-truth benchmark (Tune vs Held-Out Final splits)
├── requirements.txt        ← Python dependencies & Tesseract setup guide
└── README.md               ← Comprehensive engineering documentation (this file)
```

---

## 🎯 What This Module Does

While Member 1's machine learning models classify general text and URL features, Member 2's module provides **context-aware Indian cybercrime intelligence**:
1. **Detects 16 specific scam vectors** targeting Indian citizens (Fake KYC, Digital Arrest, UPI Collect fraud, Electricity cutoff, etc.).
2. **Maintains versioned threat intelligence** (JSON blocklists with metadata: source, last-verified date, severity).
3. **Inspects URLs without live requests** (registrable domain extraction, brand impersonation detection, dangerous extension matching, shortener flagging).
4. **Extracts text from screenshots** with an adaptive OCR pipeline (auto-orientation, contrast correction, bilingual Hindi+English support, explicit error codes).
5. **Provides plain-language explanations** and concrete safety recommendations for every detected threat.
6. **Maintains a 61-case ground-truth test benchmark** split cleanly into Weight-Tuning (`WEIGHT_TUNING_CASES`) and Final Held-Out Evaluation (`HELD_OUT_TEST_CASES`).

---

## 🚀 Quick Start & Testing Commands

### 1. Install Dependencies
```bash
pip install -r "Detection Logic/requirements.txt"
```

### 2. Run Self-Test
Runs quick sanity checks across core Indian scam scenarios and legitimate transaction messages:
```bash
cd "Detection Logic"
python signals.py
```

### 3. Run the Dedicated Unit Test Suite (47 Tests)
Executes all unit tests covering individual rules, URL parsing, allowlists, and edge cases:
```bash
cd "Detection Logic"
python -m unittest discover -s tests -p "test_*.py" -v
```

### 4. Run the Ground-Truth Benchmark Suite (61 Cases)
Evaluates heuristic performance across all 61 ground-truth cases:
```bash
cd "Detection Logic"
python eval_cases.py
```

---

## 🖼️ OCR Installation & Configuration

The OCR engine extracts text from suspicious screenshots (e.g. WhatsApp chats, SMS screenshots, courier tracking cards).

### System Installation Requirements

#### Windows
1. Download the Tesseract-OCR installer from [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki).
2. During installation, select **Additional language data (download)** and check **Hindi**.
3. Add `C:\Program Files\Tesseract-OCR` to your system `PATH` environment variable.
4. *Optional:* If Tesseract is installed in a non-standard path, uncomment and set `pytesseract.pytesseract.tesseract_cmd = r'C:\Custom\Path\tesseract.exe'` in `signals.py`.

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-hin libtesseract-dev
```

#### macOS (Homebrew)
```bash
brew install tesseract tesseract-lang
```

### Supported Languages
- Primary: English (`eng`)
- Secondary: Hindi (`hin`)
- Multi-lingual mode: `hin+eng` (automatically falls back to `eng` if Hindi language pack is absent).

### OCR Limitations & Known Failure Modes
1. **Low-resolution screenshots:** Images with dimensions `< 50px` are rejected immediately with `SIZE_TOO_SMALL`.
2. **File Size Limit:** Images `> 20MB` return `FILE_TOO_LARGE`.
3. **Stylized or Handwriting:** Heavy cursive scripts or low-contrast handwritten notes may yield `LOW_CONFIDENCE` (`confidence < 0.40`).
4. **Missing Binaries:** If Tesseract is not installed on the host OS, `extract_text_from_image()` returns an explicit `TESSERACT_NOT_FOUND` error code rather than failing silently.

---

## 🔌 API & Integration Schema for Member 3

Member 3 (`Integration App and Report/scoring.py` and `app.py`) interfaces directly with Member 2 via:

```python
import sys
sys.path.insert(0, "Detection Logic")

from signals import analyze_signals, SCAM_TYPE_CATALOG, GENERAL_SAFETY_TIPS
from eval_cases import EVAL_CASES, WEIGHT_TUNING_CASES, HELD_OUT_TEST_CASES
```

### Function: `analyze_signals(text: str, image_path: Optional[str] = None) -> Dict[str, Any]`

#### Input Arguments
- `text` *(str)*: User-supplied message body, SMS, or URL string.
- `image_path` *(Optional[str])*: Absolute path to an uploaded screenshot file (PNG, JPG, WEBP, etc.).

#### Output Schema
```json
{
  "ocr_result": {
    "text": "Electricity power will be disconnected tonight...",
    "confidence": 0.92,
    "status": "OK",
    "error_code": "",
    "error_message": "",
    "language_used": "eng",
    "image_dimensions": [1080, 1920]
  },
  "combined_text_used": "Full input text + OCR text combined",
  "triggered_signals": [
    {
      "triggered": true,
      "signal_id": "ELECTRICITY_BILL_THREAT",
      "scam_type": "Electricity Bill Disconnection Scam",
      "severity": 3,
      "explanation": "This message threatens to cut your electricity supply and urges you to call a number urgently...",
      "recommendation": "Do NOT call the number in this message. Check your actual bill on your DISCOM's official website...",
      "matched_text": "power will be disconnected tonight"
    }
  ],
  "signal_count": 1,
  "highest_severity": 3,
  "scam_types": ["Electricity Bill Disconnection Scam"],
  "explanations": [
    "This message threatens to cut your electricity supply and urges you to call a number urgently..."
  ],
  "recommendations": [
    "Do NOT call the number in this message. Check your actual bill on your DISCOM's official website..."
  ],
  "heuristic_risk_boost": 15,
  "is_unknown_url": false
}
```

---

## 🚨 Threat Detection Catalog (16 Categories)

| Signal ID | Scam Vector | Severity | Threat Description |
| :--- | :--- | :---: | :--- |
| `FAKE_KYC` | Fake KYC Update | 🔴 3 | Urgent bank/SIM KYC expiry claims with phishing links or APK downloads. |
| `UPI_COLLECT_REQUEST` | UPI Collect Request Fraud | 🔴 3 | Tricking victims into entering UPI PIN under pretext of receiving cashback/refunds. |
| `PARCEL_CUSTOMS_THREAT` | Parcel / Customs Scam | 🔴 3 | Courier impersonation claiming contraband seized, demanding customs clearance fee. |
| `DIGITAL_ARREST` | Digital Arrest / Impersonation | 🔴 3 | Fake CBI/Police/ED video call extortion claiming narcotics or hawala warrants. |
| `ELECTRICITY_BILL_THREAT` | Electricity Disconnection Threat | 🔴 3 | Threat of immediate power cutoff tonight, directing to fake officer phone numbers. |
| `OTP_PHISHING` | OTP / Credential Phishing | 🔴 3 | Social engineering requesting users to disclose OTP/PIN to 'support executives'. |
| `PHISHING_URL` | Known Phishing / Dangerous URL | 🔴 3 | Domain matches CERT-In blocklist, dangerous extension (.apk), or brand spoofing. |
| `ROMANCE_SEXTORTION` | Romance / Sextortion Scam | 🔴 3 | Private video recording blackmail threats or emotional distress extortion. |
| `FAKE_CUSTOMER_CARE` | Fake Care / Remote Access Trojan | 🔴 3 | Fake customer care numbers urging installation of AnyDesk or TeamViewer. |
| `JOB_OFFER_SCAM` | Fake Task / Job Scam | 🟡 2 | YouTube liking / Google Maps rating tasks leading to advance-fee deposit traps. |
| `LOAN_FRAUD` | Fake Instant Loan Offer | 🟡 2 | 0-document instant loans demanding advance processing/registration fees. |
| `PRIZE_LOTTERY_SCAM` | Lottery / Lucky Draw Scam | 🟡 2 | Fake KBC, Jio, or Amazon winner claims requiring advance claim taxes. |
| `IMPERSONATION` | Organizational Impersonation | 🟡 2 | Unsolicited messages claiming to be from RBI, TRAI, IT Dept, or PM Cares. |
| `INVESTMENT_SCAM` | High-Yield Investment Scam | 🟡 2 | VIP Telegram channels promising 50%+ guaranteed stock/crypto returns. |
| `MONEY_MULE` | Money Mule / Advance Fee | 🟡 2 | Requesting Indian bank account to receive/forward funds for percentage commission. |
| `URGENCY_PRESSURE` | High-Pressure Urgency Tactic | 🟢 1 | Multiple panic phrases ("last warning", "within 2 hours") to disable critical thinking. |

---

## 📊 Ground-Truth Evaluation Benchmark (61 Cases)

The evaluation suite (`eval_cases.py`) contains **61 realistic cases** curated from real Indian scam campaigns and authentic bank/government alerts:

### Benchmark Splits (P0 Specification)
- **`WEIGHT_TUNING_CASES` (30 cases):** Dedicated subset provided for Member 3's `tune_weights.py` to optimize risk fusion weights without data leakage.
- **`HELD_OUT_TEST_CASES` (31 cases):** Untouched evaluation cases reserved strictly for final validation reporting.

### Heuristic Performance Summary

```
==============================================================
EVALUATION BENCHMARK SUMMARY (N=61)
==============================================================
TP : 35   | TN : 26  
FP : 0    | FN : 0   
Accuracy               : 100.00%
Precision              : 100.00%
Recall (Sensitivity)   : 100.00%
False Positive Rate    : 0.00%
F1-Score               : 1.0000
==============================================================
```

### Key Hardened Behaviors
1. **Zero False Positives on Legitimate Alerts:** Genuine bank OTPs ("Never share OTP"), railway PNR confirmations, and utility bill due dates are never flagged as scams.
2. **Context-Aware Allowlisting:** A trusted link (e.g. `https://www.amazon.in`) does **not** bypass content signals if the message body asks for a UPI PIN.
3. **Adversarial Resilience:** Robust against spaced acronyms (`k y c`), spaced domain names (`sbi - kyc .top`), Hinglish transliterations (`bijli katega`, `khata band`), and trailing sentence punctuation (`.co.in.`).
4. **Educational Advisory Safe-Gating:** Official cybercrime advisories explaining scam techniques (e.g., "Beware of digital arrest") are recognized as legitimate awareness and not misclassified as scams.

---

## 👥 Collaboration & Delivery

- **Member 1 (Data & ML):** Heuristics complement ML probabilities. If ML model has high uncertainty on novel phrasing, Member 2's deterministic signals provide an anchor score boost.
- **Member 3 (Integration & App):** Import `analyze_signals()` inside `scoring.py`. Use `WEIGHT_TUNING_CASES` from `eval_cases.py` inside `tune_weights.py`.
- **Member 4 (UI/UX Designer):** All text in `SCAM_TYPE_CATALOG` and `GENERAL_SAFETY_TIPS` is ready for direct display in Streamlit verdict cards and modal sidebars.
