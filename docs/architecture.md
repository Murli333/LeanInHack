# ScamLens System Architecture & Data Flow

## 1. High-Level Architecture

ScamLens is an AI-powered cybersecurity platform that protects consumers from digital financial scams and phishing campaigns across India.

```
                    ┌────────────────────────┐
                    │   User Inputs          │
                    │   (SMS, URL, Image)    │
                    └───────────┬────────────┘
                                │
               ┌────────────────┴────────────────┐
               ▼                                 ▼
   ┌───────────────────────┐         ┌───────────────────────┐
   │ Mobile PWA Frontend   │         │ Streamlit Web Console │
   │ (frontend/index.html) │         │ (Integration App/)    │
   └───────────┬───────────┘         └───────────┬───────────┘
               │                                 │
               └────────────────┬────────────────┘
                                │
                                ▼
               ┌─────────────────────────────────┐
               │  FastAPI Backend Service Layer  │
               │  (backend/main.py:8000)         │
               └────────────────┬────────────────┘
                                │
                                ▼
               ┌─────────────────────────────────┐
               │ Centralized Scoring Engine      │
               │ (scoring.py: analyze())         │
               └────────────────┬────────────────┘
                                │
      ┌─────────────────────────┼─────────────────────────┐
      ▼                         ▼                         ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────────┐
│ Member 1: ML  │       │ Member 2:     │       │ External Threat   │
│ Text Classifier│      │ Heuristic     │       │ Intelligence      │
│ & 28-feat URL │       │ Rules & OCR   │       │ (OpenPhish, I4C)  │
│ (predictor.py)│       │ (signals.py)  │       │                   │
└───────┬───────┘       └───────┬───────┘       └─────────┬─────────┘
        │                       │                         │
        └───────────────────────┼─────────────────────────┘
                                ▼
               ┌─────────────────────────────────┐
               │ Explainable Risk Assessment     │
               │ • Verdict: Safe/Suspicious/Scam │
               │ • Risk Score: 0 - 100%          │
               │ • Plain-Language "Why" Reasons  │
               │ • Actionable Safety Guidance    │
               │ • 1930 & Cybercrime.gov.in Links│
               └─────────────────────────────────┘
```

## 2. Key Components

1. **`Data And ML/` (Member 1):**
   - Trained TF-IDF + Calibrated Logistic Regression text model (`text_model.joblib`).
   - 28-feature Calibrated Random Forest URL model (`url_model.joblib`).
   - Unified inference API (`predictor.py`) and autonomous investigation agent (`agent.py`).
2. **`Detection Logic/` (Member 2):**
   - Heuristic scam pattern regex engines covering 12 Indian attack vectors.
   - Phishing blocklist and trusted allowlist lookup.
   - Screenshot OCR extraction via Tesseract.
3. **`Integration App and Report/` (Member 3):**
   - Unified `analyze()` function fusing ML probabilities and heuristic signals.
   - Streamlit interactive web application.
4. **`frontend/` (Member 4 & Cross-Platform):**
   - Responsive mobile-first PWA and desktop web console.
5. **`backend/`:**
   - Production FastAPI microservice exposing REST endpoints.
