# ScamLens — Member 3: Benchmark & Weight-Tuning Report

> [!WARNING]
> **Small Sample Size Advisory:** Dataset currently consists of 35 curated ground-truth cases. Results are indicative; evaluate on a larger, continuous benchmark before production deployment.

**Selected Weight Profile:** `Balanced Hybrid`  
**Active Weights:** `text_ml=0.35`, `heuristics=0.35`, `url_ml=0.15`, `url_rule=0.15`, `unknown_url_score=60`

## 1. Dataset Partitioning (Stratified, Fixed Seed=42)

| Split | Sample Count | Scam Cases | Safe Cases | Purpose |
| :--- | :---: | :---: | :---: | :--- |
| **Tune Split** | 21 | 11 | 10 | Primary parameter tuning |
| **Validation Split** | 7 | 4 | 3 | Model selection & hyperparameter check |
| **Test Split (Holdout)** | 7 | 3 | 4 | Untouched final generalization evaluation |
| **Total** | 35 | 18 | 17 | Full benchmark dataset |

## 2. Generalization Performance on Untouched Test Split

| Evaluation Modality | Evaluated Cases | Accuracy | Precision | Recall | FPR | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Combined Multimodal** | 7 | **100.0%** | **100.0%** | **100.0%** | 0.0% | **1.0** |
| **Text-Only (URLs Stripped)** | 7 | **100.0%** | **100.0%** | **100.0%** | 0.0% | **1.0** |
| **URL-Only Evaluation** | 2 | **100.0%** | **100.0%** | **100.0%** | 0.0% | **1.0** |

## 3. Full Benchmark Dataset Performance (35 Cases)

| Metric | Full Dataset Value |
| :--- | :---: |
| Total Cases | 35 |
| Accuracy | **100.0%** |
| Precision | **100.0%** |
| Recall | **100.0%** |
| False Positive Rate (FPR) | **0.0%** |
| F1-Score | **1.0** |
| True Positives (TP) | 18 |
| True Negatives (TN) | 17 |
| False Positives (FP) | 0 |
| False Negatives (FN) | 0 |

## 4. Per-Case Test Split Log

| Case ID | Ground Truth | Predicted | Risk Index | Match | Text Excerpt |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `SAFE_004` | Safe | Safe | 2 | PASS (TN) | Your PNR 2451982301 for Train 12301 HOWRAH RAJDHANI EXP from... |
| `SCAM_004` | Scam | Scam | 87 | PASS (TP) | Delhi Police Cyber Cell: A parcel registered in your name co... |
| `SAFE_014` | Safe | Safe | 25 | PASS (TN) | Dear Customer, your Tata Power DDL bill for Account No. 1004... |
| `SAFE_008` | Safe | Safe | 25 | PASS (TN) | Your appointment at AIIMS OPD (Dr. Meera Kapoor, Cardiology)... |
| `SCAM_009` | Scam | Scam | 73 | PASS (TP) | Congratulations! Your mobile number has won Rs 25,00,000 in ... |
| `SCAM_001` | Scam | Scam | 98 | PASS (TP) | Dear SBI Customer, your account has been temporarily suspend... |
| `SAFE_007` | Safe | Safe | 25 | PASS (TN) | Your Amazon.in order #402-8129831-2918734 for 'boAt Airdopes... |
