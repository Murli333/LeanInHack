# ScamLens — Member 3: Integration Benchmark Report

**Selected Profile:** Balanced Hybrid  
**Weights:** text_ml=0.3, text_rule=0.35, url_ml=0.15, url_rule=0.2

## Performance Summary

| Metric | Value |
| :--- | :---: |
| Total Cases | 36 |
| Accuracy | **100.0%** |
| Precision | **100.0%** |
| Recall | **100.0%** |
| FPR | **0.0%** |
| F1-Score | **1.0** |
| TP | 18 |
| TN | 18 |
| FP | 0 |
| FN | 0 |

## Detailed Results

| ID | Category | Truth | Predicted | Score | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| SCAM-01 | Fake KYC | Scam | Scam | 99% | PASS (TP) |
| SCAM-02 | Fake KYC | Scam | Scam | 95% | PASS (TP) |
| SCAM-03 | Fake KYC | Scam | Scam | 74% | PASS (TP) |
| SCAM-04 | Electricity Bill Threat | Scam | Scam | 87% | PASS (TP) |
| SCAM-05 | Electricity Bill Threat | Scam | Scam | 95% | PASS (TP) |
| SCAM-06 | Electricity Bill Threat | Scam | Suspicious | 66% | PASS (TP) |
| SCAM-07 | UPI Collect Fraud | Scam | Scam | 80% | PASS (TP) |
| SCAM-08 | UPI Collect Fraud | Scam | Scam | 87% | PASS (TP) |
| SCAM-09 | UPI Collect Fraud | Scam | Scam | 76% | PASS (TP) |
| SCAM-10 | Digital Arrest | Scam | Scam | 86% | PASS (TP) |
| SCAM-11 | Digital Arrest | Scam | Scam | 83% | PASS (TP) |
| SCAM-12 | Digital Arrest | Scam | Scam | 71% | PASS (TP) |
| SCAM-13 | Customs Extortion | Scam | Scam | 95% | PASS (TP) |
| SCAM-14 | Customs Extortion | Scam | Suspicious | 58% | PASS (TP) |
| SCAM-15 | Job Scam | Scam | Scam | 82% | PASS (TP) |
| SCAM-16 | Job Scam | Scam | Suspicious | 49% | PASS (TP) |
| SCAM-17 | Phishing URL | Scam | Scam | 94% | PASS (TP) |
| SCAM-18 | Phishing URL | Scam | Scam | 98% | PASS (TP) |
| LEGIT-01 | Bank OTP Alert | Safe | Safe | 8% | PASS (TN) |
| LEGIT-02 | Bank OTP Alert | Safe | Safe | 32% | PASS (TN) |
| LEGIT-03 | Bank Transaction Alert | Safe | Safe | 15% | PASS (TN) |
| LEGIT-04 | Bank Transaction Alert | Safe | Safe | 15% | PASS (TN) |
| LEGIT-05 | E-Commerce Delivery | Safe | Safe | 8% | PASS (TN) |
| LEGIT-06 | E-Commerce Delivery | Safe | Safe | 33% | PASS (TN) |
| LEGIT-07 | E-Commerce Delivery | Safe | Safe | 15% | PASS (TN) |
| LEGIT-08 | Courier Tracking | Safe | Safe | 37% | PASS (TN) |
| LEGIT-09 | Travel / Railway | Safe | Safe | 9% | PASS (TN) |
| LEGIT-10 | Travel / Flight | Safe | Safe | 21% | PASS (TN) |
| LEGIT-11 | Legitimate Utility | Safe | Safe | 25% | PASS (TN) |
| LEGIT-12 | Telecom Alert | Safe | Safe | 33% | PASS (TN) |
| LEGIT-13 | Official Portal | Safe | Safe | 35% | PASS (TN) |
| LEGIT-14 | Official Portal | Safe | Safe | 33% | PASS (TN) |
| LEGIT-15 | Personal Message | Safe | Safe | 9% | PASS (TN) |
| LEGIT-16 | Work Chat | Safe | Safe | 19% | PASS (TN) |
| LEGIT-17 | Legitimate URL | Safe | Safe | 6% | PASS (TN) |
| LEGIT-18 | Legitimate URL | Safe | Safe | 6% | PASS (TN) |
