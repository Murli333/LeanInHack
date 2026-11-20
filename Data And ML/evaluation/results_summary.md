# ScamLens ML Model Evaluation Results (Member 1)

This report contains the benchmark metrics, validation performance, and confusion matrices for the two trained machine learning models powering **ScamLens**.

---

## 1. Performance Overview

| Metric | Text Scam Model (`text_model.joblib`) | URL Phishing Model (`url_model.joblib`) | Target / Industry Benchmark | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Accuracy** | **99.33%** | **99.50%** | > 90.0% | PASS |
| **Precision** | **96.30%** | **99.86%** | > 92.0% | PASS |
| **Recall** | **98.48%** | **99.59%** | > 90.0% | PASS |
| **F1-Score** | **0.9738** | **0.9973** | > 0.90 | PASS |
| **False Positive Rate (FPR)** | **0.55%** | **1.61%** | < 3.0% | PASS |
| **ROC-AUC** | **0.9996** | **0.9998** | > 0.95 | PASS |

> [!NOTE]
> A critical constraint in scam detection is maintaining a **low False Positive Rate (FPR)** so genuine transactional OTPs, electricity alerts, and delivery messages are not mistakenly flagged. Both models achieve an FPR under 2.5%, making them safe for live consumer deployment.

---

## 2. Confusion Matrices

### Text Scam Model Confusion Matrix
- **True Negatives (Genuine Ham correctly cleared):** 903
- **False Positives (Genuine mistakenly flagged):** 5
- **False Negatives (Scams missed):** 2
- **True Positives (Scams correctly caught):** 130

*Confusion Matrix Asset:* `evaluation/confusion_matrix_text.png`

### URL Phishing Model Confusion Matrix
- **True Negatives (Legitimate URLs cleared):** 61
- **False Positives (Safe URLs flagged as phishing):** 1
- **False Negatives (Phishing URLs missed):** 3
- **True Positives (Phishing URLs detected):** 730

*Confusion Matrix Asset:* `evaluation/confusion_matrix_url.png`

---

## 3. Top Explanatory Signals for Detection Logic (Member 2) & UI (Member 4)

### Top Text Scam Keywords Identified by Model:
`reply`, `free`, `call`, `text`, `call phonemarker`, `txt`, `to codemarker`, `urlmarker`, `codemarker`, `phonemarker`

### Top URL Structural Indicators:
- **`is_https`** (Importance: 61.2%)
- **`domain_length`** (Importance: 11.4%)
- **`domain_entropy`** (Importance: 5.6%)
- **`url_length`** (Importance: 5.5%)
- **`url_entropy`** (Importance: 2.9%)

---

## 4. Hand-off Checklist for Teammates

- **Models Serialized:**
  - `models/text_model.joblib`
  - `models/url_model.joblib`
- **Inference Wrapper:** `models/predictor.py` provides clean `predict_text()`, `predict_url()`, and `predict_combined()` functions.
- **Charts Generated:**
  - `evaluation/confusion_matrix_text.png`
  - `evaluation/confusion_matrix_url.png`
