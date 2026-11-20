# ScamLens - Member 1: Data and Machine Learning

Welcome to the **Data and Machine Learning** core of **ScamLens**. This module provides trained, calibrated AI models and an explainable inference engine for detecting digital scams across messages and suspicious URLs.

---

## 🎯 Deliverables Summary (Member 1 Hand-Off)

| Deliverable | Location | Description |
| :--- | :--- | :--- |
| **Text Scam Classifier** | `models/text_model.joblib` | Serialized NLP pipeline (TF-IDF + Calibrated Classifier) for SMS & messages. |
| **URL Phishing Classifier** | `models/url_model.joblib` | Serialized Random Forest model trained on 24 structural & lexical features. |
| **Unified Inference Engine** | `models/predictor.py` | Clean Python API (`ScamLensPredictor`) for Member 2 & 3 with explainability. |
| **Evaluation Metrics & Report** | `evaluation/results_summary.md` | Formal results table (Precision, Recall, FPR, ROC-AUC). |
| **Confusion Matrix Charts** | `evaluation/confusion_matrix_*.png` | High-resolution confusion matrices for project report & presentation slides. |
| **Automated Verification Suite** | `tests/test_models.py` | 16 end-to-end integration test cases covering real-world Indian scams & legitimate alerts. |

---

## 📊 Model Performance & Benchmarks

Both models have been trained on real-world datasets augmented with modern Indian scam patterns (Fake KYC, UPI Collect, Digital Arrest, Electricity bill threats, Part-time job scams) and legitimate transactional templates:

| Metric | Text Scam Model | URL Phishing Model | Target Benchmark | Verdict |
| :--- | :---: | :---: | :---: | :---: |
| **Accuracy** | **99.33%** | **99.50%** | > 90.0% | ✅ **Passed** |
| **Precision** | **96.30%** | **99.86%** | > 92.0% | ✅ **Passed** |
| **Recall** | **98.48%** | **99.59%** | > 90.0% | ✅ **Passed** |
| **F1-Score** | **0.9738** | **0.9973** | > 0.90 | ✅ **Passed** |
| **False Positive Rate (FPR)** | **0.55%** | **1.61%** | < 3.0% | ✅ **Passed** |
| **ROC-AUC** | **0.9996** | **0.9998** | > 0.95 | ✅ **Passed** |

> **Why False Positive Rate Matters:** In consumer fraud detection, mistakenly blocking genuine bank OTPs, delivery updates, or utility receipts causes user frustration. ScamLens maintains a False Positive Rate under **1.6%**, safely distinguishing authentic transactional alerts from scams.

---

## 🤝 Alignment with Teammates

### 1. For Member 2: Detection Logic and Test Set (`signals.py` & `eval_cases.py`)
- You can query `models/predictor.py` directly inside your evaluation script to benchmark against your 30-40 test cases:
```python
from models.predictor import ScamLensPredictor

predictor = ScamLensPredictor()
res = predictor.predict_text("Your electricity will be disconnected tonight. Call officer at 9876543210.")

print(res["verdict"])        # 'Scam'
print(res["risk_score"])     # 89 (0-100 scale)
print(res["reasons"])        # ['Pressures you with immediate electricity disconnection threats.']
print(res["detected_keywords"]) # ['electricity', 'disconnected', 'bill']
```
- Member 2 can use `res["risk_score"]` and `res["detected_keywords"]` to reinforce rule-based weights in `signals.py`.

---

### 2. For Member 3: Integration and Streamlit App (`app.py` & `analyze()`)
- In `app.py`, simply instantiate `ScamLensPredictor`:
```python
from models.predictor import ScamLensPredictor

# Initialize once on app startup
predictor = ScamLensPredictor()

def analyze(message_text: str = None, url: str = None):
    # Predicts text, URL, or combined multimodal input
    result = predictor.predict_combined(text=message_text, url=url)
    return result
```
- Output returned by `analyze()` directly contains:
```python
{
    "verdict": "Scam",           # "Safe" | "Suspicious" | "Scam"
    "status_color": "red",       # "green" | "amber" | "red"
    "icon": "🚨",                 # "✅" | "⚠️" | "🚨"
    "risk_score": 96,            # 0 to 100 integer
    "reasons": [                 # "Why we think this" bullet list
        "Pressures you with immediate electricity disconnection threats.",
        "Registered under an untrusted, high-risk top-level domain (.fit)."
    ],
    "safety_tips": [             # Actionable guidance for user
        "Never share your OTP, UPI PIN, or bank passwords with anyone.",
        "Report fraud at cybercrime.gov.in or call 1930."
    ]
}
```

---

### 3. For Member 4: UI/UX Designer
- **3 Color & Verdict States:**
  - `Safe` (Risk 0 - 39%): Reassuring green (`#10B981`), `✅`
  - `Suspicious` (Risk 40 - 69%): Amber caution (`#F59E0B`), `⚠️`
  - `Scam` (Risk 70 - 100%): Urgent red (`#EF4444`), `🚨`
- **Risk Meter:** Integer `risk_score` from `0` to `100` ready to bind to Streamlit progress bars or gauges.
- **Why We Think This:** A human-readable list of explanation strings without technical jargon.
- **Charts for Slides:** Use `evaluation/confusion_matrix_text.png` and `evaluation/confusion_matrix_url.png` in the project presentation slides and architecture diagram.

---

## 🛠️ How to Run & Verify

1. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run training pipeline (optional, models are pre-trained):**
   ```bash
   python src/train.py
   ```

3. **Run automated verification tests:**
   ```bash
   python tests/test_models.py
   ```
