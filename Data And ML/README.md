# ScamLens - Member 1: Data and Machine Learning Pipeline (v2.1.0)

> **Role:** Member 1 - Data and ML Engineer  
> **Status:** ✅ Production Ready, Calibrated, Benchmarked, and Serialized  
> **Repository Path:** `Data And ML/`

---

## 📑 Table of Contents
1. [Module Overview & Architecture](#1-module-overview--architecture)
2. [Datasets, Provenance & Data Engineering](#2-datasets-provenance--data-engineering)
3. [Text Preprocessing & Multilingual Engineering](#3-text-preprocessing--multilingual-engineering)
4. [28-Feature URL Engineering & Evasion Defense](#4-28-feature-url-engineering--evasion-defense)
5. [Model Training, Calibration & Comparison](#5-model-training-calibration--comparison)
6. [Evaluation Metrics, Holdout Validation & Curves](#6-evaluation-metrics-holdout-validation--curves)
7. [Explainability Engine & Predictor API](#7-explainability-engine--predictor-api)
8. [Autonomous Cyber-Investigation Agent](#8-autonomous-cyber-investigation-agent)
9. [Automated Verification Test Suite](#9-automated-verification-test-suite)
10. [How to Retrain, Test & Integrate](#10-how-to-retrain-test--integrate)

---

## 1. Module Overview & Architecture

The **Data and Machine Learning** module powers ScamLens with two independent machine learning models, an autonomous evidence-gathering investigation agent, and a production-grade inference engine:

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                         ScamLens ML Architecture                               │
└────────────────────────────────────────────────────────────────────────────────┘
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                 ▼
┌─────────────────────────────┐               ┌─────────────────────────────┐
│      Text NLP Engine        │               │   URL Infrastructure Engine │
│ ─────────────────────────── │               │ ─────────────────────────── │
│ • Unicode / Homoglyphs      │               │ • 28 Structural Features    │
│ • Hinglish & Deobfuscation  │               │ • Shortener & Punycode      │
│ • TF-IDF (15k N-Grams)      │               │ • Port & Redirection Defense│
│ • Calibrated Logistic Reg   │               │ • Calibrated Random Forest  │
│ → models/text_model.joblib  │               │ → models/url_model.joblib   │
└─────────────────────────────┘               └─────────────────────────────┘
         │                                                 │
         └────────────────────────┬────────────────────────┘
                                  ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│              Unified Predictor API & Autonomous Agent Orchestrator             │
│ ────────────────────────────────────────────────────────────────────────────── │
│ • [P0] Empty Input Guard: Unknown state with zero false-positives              │
│ • Distinct raw_ml_score vs calibrated risk_score (0-100%)                      │
│ • Explainability: Local token attributions and structural security reasons     │
│ • Uncertainty Bands: Flagging ambiguous borderline classifications             │
│ • Heuristic Fallback: Safe rule-based operation if model files are unavailable │
│ • Autonomous ReAct Agent: Evidence provenance, IOC extraction & deliberation   │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Datasets, Provenance & Data Engineering

### 2.1 Dataset Registry (`data/raw/DATA_SOURCES.md`)
Full provenance, licenses, and download versions are tracked in [DATA_SOURCES.md](file:///C:/Users/murli%20mishra/.gemini/antigravity/scratch/LeanInHack/Data%20And%20ML/data/raw/DATA_SOURCES.md):
- **UCI SMS Spam Collection:** 5,574 messages baseline (Almeida et al., 2011).
- **OpenPhish Live Phishing Threat Feed:** Zero-day malicious campaigns feed with archived snapshots in `data/raw/openphish_snapshot.txt`.
- **Shreya Gopal Benchmark:** 10,000 academic domain records (5,000 legitimate and 5,000 phishing).
- **Curated Indian Cybercrime Corpus (v2.1):** Realistic scam SMS collected from real FIRs and I4C/1930 advisories (Fake KYC, Digital Arrest, Electricity bills, UPI Collect, Job scams, Telecom disconnects).
- **Curated Indian Legitimate Transactional Corpus:** Bank debits/credits, official OTPs, e-commerce, food deliveries (Swiggy, Zomato), railway PNRs (IRCTC), and utility bills.

### 2.2 Pipeline Manifest (`data/processed/pipeline_manifest.json`)
Every dataset generation step is reproducible and recorded with class distribution, timestamps, random seeds (42), and source provenance.

### 2.3 Isolated Holdout Evaluation Sets (`data/holdout/`)
To guarantee **zero train/test data leakage**, we maintain completely untouched holdout sets:
- `data/holdout/holdout_text.csv` (30 unseen messages: 15 scam, 15 ham).
- `data/holdout/holdout_urls.csv` (24 unseen URLs: 12 phishing, 12 legitimate).

---

## 3. Text Preprocessing & Multilingual Engineering (`src/text_preprocessor.py`)

- **Unicode & Homoglyph Normalization:** Decomposes Unicode (NFKD) and maps Cyrillic homoglyphs (`а` → `a`, `е` → `e`, `р` → `p`, etc.) used to bypass conventional spam filters.
- **Zero-Width Character Stripping:** Removes invisible characters (`\u200b`, `\u200c`, `\ufeff`) used for cloaking.
- **Deobfuscation Engine:** Automatically normalizes intentionally spaced or masked fraud terms (`K Y C` → `kyc`, `f r e e` → `free`, `w1n` → `win`, `lo@n` → `loan`, `p!n` → `pin`).
- **Hinglish Scam Triggers:** Detects high-threat Hindi/Hinglish fraud patterns (`"aapka account band ho jayega"`, `"turant sampark kare"`, `"bijli ka connection kat diya jayega"`, `"inaam jeeta hai"`).
- **Entity Normalization:** Replaces dynamic values with semantic markers: `<urlmarker>`, `<phonemarker>`, `<currencymarker>`, `<codemarker>`.
- **Emoji Threat Indicators:** Flags deceptive prize and urgency emojis (`🎉`, `🏆`, `💰`, `🎁`, `💵`, `🚨`).

---

## 4. 28-Feature URL Engineering & Evasion Defense (`src/feature_extraction.py`)

Our 28-dimensional structural vector extracted from any URL defends against modern attacker evasion:

| # | Feature Name | Description | Security Threat Detected |
| :--- | :--- | :--- | :--- |
| 1–3 | `url_length`, `domain_length`, `path_length` | Dimensional lengths | Abnormal length common in phishing kits |
| 4–7 | `num_dots_url`, `num_dots_domain`, `num_hyphens_url`, `num_hyphens_domain` | Punctuation counts | Deep subdomains & brand hyphen spoofing (`sbi-card-verify.top`) |
| 8–12 | `num_at_symbols`, `num_question_marks`, `num_equals`, `num_percent`, `num_slashes` | Delimiters | Credential injection (`@`), URL encoding abuse (`%20`) |
| 13–15 | `num_digits_url`, `num_digits_domain`, `digit_ratio_url` | Numeric frequencies | Random hashes and fake account numbers |
| 16 | `is_https` | SSL encryption | Unencrypted plain HTTP |
| 17 | `is_ip_address` | Direct IPv4/IPv6 host | Host-based server bypassing domain reputation |
| 18 | `num_subdomains` | Subdomain depth | Multi-tier domain spoofing |
| 19 | `has_suspicious_tld` | High-abuse TLDs | `.top`, `.xyz`, `.fit`, `.buzz`, `.site`, `.club`, `.work`, etc. |
| 20 | `has_sensitive_extension` | Dangerous extensions | Unofficial payload downloads (`.apk`, `.exe`, `.bat`, `.scr`) |
| 21 | `sensitive_keyword_count` | Keyword frequency | `kyc`, `upi`, `login`, `verify`, `bank`, `otp`, `challan` |
| 22 | `brand_in_subdomain_or_path` | Impersonation flag | Major brand name inside an unverified domain |
| 23–24 | `domain_entropy`, `url_entropy` | Shannon Entropy | Algorithmic domain generation (DGA) |
| 25 | `is_shortened_url` | Shortener detection | `bit.ly`, `tinyurl.com`, `is.gd`, `cutt.ly`, `rb.gy` |
| 26 | `is_punycode` | IDN Homograph check | Internationalized domain spoofing (`xn--`) |
| 27 | `has_non_standard_port` | Non-standard TCP port | Rogue listener ports (`:8080`, `:8443`, `:4443`) |
| 28 | `has_double_slash_path` | Redirection trick | Path delimiter evasion (`//login.php`) |

---

## 5. Model Training, Calibration & Comparison (`src/train.py`)

### 5.1 Stratified 5-Fold Cross-Validation
- **Text Model:** 5-Fold CV F1: **93.91% (+/- 1.59%)**, ROC-AUC: **0.9914**.
- **URL Model:** 5-Fold CV F1: **99.56% (+/- 0.22%)**, ROC-AUC: **0.9993**.

### 5.2 True Model Calibration (Platt Sigmoid Scaling)
Both models are calibrated using `CalibratedClassifierCV(method='sigmoid', cv=3)` to output true Bayesian posterior probabilities $P(\text{Scam} \mid x)$, preventing overconfident scores in ambiguous zones.

### 5.3 URL Model Architecture Benchmarking
We evaluated three candidate architectures on the identical stratified cross-validation split:

| Model Architecture | 5-Fold CV Accuracy | Precision | Recall | F1-Score | ROC-AUC | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Calibrated Random Forest (180 trees)** | **99.26%** | **99.59%** | **99.59%** | **0.9959** | **0.9993** | **CHOSEN CHAMPION** |
| HistGradientBoosting (GBDT) | 99.21% | 99.66% | 99.59% | 0.9962 | 0.9987 | Strong Alternative |
| Logistic Regression (L2) | 98.76% | 99.30% | 98.82% | 0.9906 | 0.9954 | Linear Baseline |

---

## 6. Evaluation Metrics, Holdout Validation & Curves

### 6.1 Performance Summary

| Metric | Text Scam Model (NLP) | URL Phishing Model | Production Target | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Test Accuracy** | **98.82%** | **99.26%** | > 92.0% | PASS |
| **Test Precision** | **97.56%** | **99.59%** | > 92.0% | PASS |
| **Test Recall** | **97.80%** | **99.59%** | > 90.0% | PASS |
| **Test F1-Score** | **0.9768** | **0.9959** | > 0.90 | PASS |
| **False Positive Rate (FPR)** | **0.84%** | **4.48%** | < 5.0% | PASS |
| **ROC-AUC** | **0.9982** | **0.9995** | > 0.95 | PASS |
| **5-Fold CV F1** | **97.28% (+/- 0.51%)** | **99.56%** | > 90.0% | PASS |

### 6.2 Visual Artifacts Generated in `evaluation/`
1. `evaluation/confusion_matrix_text.png`
2. `evaluation/confusion_matrix_url.png`
3. `evaluation/pr_curve_text.png` (Precision-Recall curve for text model)
4. `evaluation/pr_curve_url.png` (Precision-Recall curve for URL model)
5. `evaluation/calibration_text.png` (Reliability diagram for calibrated probabilities)
6. `evaluation/calibration_url.png` (Reliability diagram for calibrated probabilities)
7. `evaluation/metrics.json` (Structured JSON benchmark dump)
8. `evaluation/results_summary.md` (Detailed Markdown evaluation dossier)

---

## 7. Explainability Engine & Predictor API (`models/predictor.py`)

The unified predictor provides backward-compatible inference for Member 2 (`signals.py`), Member 3 (`app.py`, `scoring.py`), and Member 4 (UI):

### Key Functions
- `predict_text(text: str) -> dict`: Evaluates message text and extracts explainable trigger reasons.
- `predict_url(url: str) -> dict`: Inspects URL infrastructure and highlights structural flags.
- `predict_combined(text: str, url: str) -> dict`: Multi-evidence fusion producing overall risk score, verdict, and action recommendations.
- `get_model_metadata() -> dict`: Returns loaded model versions and training parameters.

### Empty Input Handling ([P0] Fix)
Empty strings or `None` inputs return:
```python
{
    "verdict": "Unknown",
    "status_color": "gray",
    "icon": "❓",
    "risk_score": 0,
    "raw_ml_score": 0.0,
    "is_empty": True,
    "confidence": 0.0,
    "reasons": ["No content provided for analysis."]
}
```

---

## 8. Autonomous Cyber-Investigation Agent (`src/agent.py`)

`ScamInvestigatorAgent` provides multi-tool agentic orchestration:
1. **Observation & Plan:** Ingests multimodal input, checks completeness, extracts embedded IOCs.
2. **Tool Invocations:** Executes NLP model, URL feature extractor, and threat signatures with provenance tracking and schema validation.
3. **Chain-of-Thought Deliberation:** Synthesizes corroborating evidence across vectors.
4. **Grounded Risk Verdict:** Fuses evidence scores based on mathematical weights rather than arbitrary overrides.
5. **Prescriptive Action Plan:** Generates context-aware emergency recommendations and official helpline numbers (1930 / cybercrime.gov.in).

---

## 9. Automated Verification Test Suite (`tests/test_models.py`)

The automated test suite runs 12 comprehensive unit test classes:
1. `test_empty_and_whitespace_inputs`: Verifies empty inputs produce `Unknown` (never `Safe`).
2. `test_extremely_long_input`: Verifies 10k-character inputs are handled without timeouts.
3. `test_numeric_and_symbol_inputs`: Tests inputs with numbers and symbols only.
4. `test_high_threat_scams_strict`: Strict `Scam` verdict assertion for all known Indian attack campaigns.
5. `test_false_positive_stress`: Strict `Safe` verdict assertion for legitimate OTPs, delivery alerts, and bills.
6. `test_hinglish_and_obfuscated_messages`: Validates Hinglish patterns and deobfuscation.
7. `test_multiple_urls_in_message`: Validates multi-URL extraction and prioritizes malicious links over decoy links.
8. `test_url_phishing_strict`: Tests phishing URLs including HTTPS counterexamples.
9. `test_url_legitimate_strict`: Tests authentic domains including HTTP counterexamples.
10. `test_missing_model_files_fallback`: Tests rule-based heuristic fallback mode when model files are absent.
11. `test_agent_investigation_orchestration`: Tests multi-tool ReAct investigation traces.
12. `test_model_metadata`: Tests model versioning inspection API.

**Test Pass Rate:** **12/12 (100.0%)**

---

## 10. How to Retrain, Test & Integrate

### Retrain Models
```bash
cd "Data And ML"
python -u src/train.py
```

### Run ML Unit Test Suite
```bash
cd "Data And ML"
python tests/test_models.py
```

### Run Member 3 Integration Tests
```bash
python "Integration App and Report/tests/test_integration.py"
```
*(Result: 16/16 Passed 100.0%)*
