# ScamLens 🛡️🔍

> **AI-Powered Digital Fraud & Scam Intelligence Platform**  
> Multimodal scam analysis across messages, URLs, screenshots, voice recordings, and QR codes.

---

## 🚀 Team Architecture & Modules

```
LeanInHack/
├── Data And ML/             # [Member 1: Data & Machine Learning]
│   ├── data/                # Processed and benchmark datasets
│   ├── models/              # text_model.joblib, url_model.joblib, predictor.py
│   ├── evaluation/          # Confusion matrices, benchmarks, results_summary.md
│   ├── src/                 # Text & URL preprocessing, feature extraction, train.py
│   ├── tests/               # 16-case verification test suite
│   └── README.md            # Detailed ML integration guide & API contracts
│
├── Detection Logic/         # [Member 2: Scam Rules & Test Set]
│   ├── signals.py           # Indian scam rules (Fake KYC, UPI, Digital Arrest, Bills)
│   └── eval_cases.py        # 30-40 ground-truth evaluation cases
│
├── App/                     # [Member 3: Streamlit Application & Integration]
│   ├── app.py               # Streamlit application UI & analyze() logic
│   └── scoring.py           # Combined risk weighting logic
│
└── Design/                  # [Member 4: UI/UX & Documentation]
    ├── assets/              # Icons, badges, wireframe designs
    └── presentation/        # Slide deck & final project report
```

---

## ⚡ Quick Start for Member 1 (Data & ML)

Check `Data And ML/README.md` for instructions on running models, tests, and using the `ScamLensPredictor` API.
