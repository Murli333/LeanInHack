# ScamLens — Member 3: Integration Benchmark Report

**Selected Profile:** Balanced Hybrid  
**Weights:** text_ml=0.35, heuristics=0.35, url_ml=0.15, url_rule=0.15

## Performance Summary (35 Ground-Truth Cases)

| Metric | Value |
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

## Detailed Results Log

| ID | Expected | Predicted | Score | Status | Text Preview |
| :--- | :---: | :---: | :---: | :---: | :--- |
| SCAM_001 | Scam | Scam | 98% | PASS (TP) | `Dear SBI Customer, your account has been temporarily suspend...` |
| SCAM_002 | Scam | Scam | 83% | PASS (TP) | `URGENT: Your electricity power will be disconnected TONIGHT ...` |
| SCAM_003 | Scam | Scam | 96% | PASS (TP) | `Dear Customer, you have received a UPI collect request of Rs...` |
| SCAM_004 | Scam | Scam | 87% | PASS (TP) | `Delhi Police Cyber Cell: A parcel registered in your name co...` |
| SCAM_005 | Scam | Scam | 71% | PASS (TP) | `Congratulations! You have been selected for a part-time work...` |
| SCAM_006 | Scam | Scam | 98% | PASS (TP) | `ALERT from HDFC Bank: Your HDFC account has been BLOCKED due...` |
| SCAM_007 | Scam | Scam | 98% | PASS (TP) | `Dear Customer, your FedEx parcel (Tracking: FX8829301IN) is ...` |
| SCAM_008 | Scam | Scam | 85% | PASS (TP) | `Income Tax Department Notice: Unauthorized transaction detec...` |
| SCAM_009 | Scam | Scam | 73% | PASS (TP) | `Congratulations! Your mobile number has won Rs 25,00,000 in ...` |
| SCAM_010 | Scam | Scam | 78% | PASS (TP) | `Your TRAI has detected that your mobile number is involved i...` |
| SCAM_011 | Scam | Scam | 71% | PASS (TP) | `Quick Loan Offer! Get instant personal loan of Rs 5,00,000 w...` |
| SCAM_012 | Scam | Scam | 98% | PASS (TP) | `Dear Paytm User: Your Paytm KYC has expired. To continue usi...` |
| SCAM_013 | Scam | Suspicious | 66% | PASS (TP) | `Microsoft Technical Support: We have detected a virus on you...` |
| SCAM_014 | Scam | Scam | 94% | PASS (TP) | `Dear Customer, you have received a PhonePe cashback of Rs 50...` |
| SCAM_015 | Scam | Scam | 92% | PASS (TP) | `Narcotics Control Bureau: Your Aadhaar card has been used to...` |
| SCAM_016 | Scam | Scam | 75% | PASS (TP) | `FREE RECHARGE OFFER! Jio is offering 365-day unlimited free ...` |
| SCAM_017 | Scam | Suspicious | 68% | PASS (TP) | `PM Cares Fund: The Government of India is distributing finan...` |
| SCAM_018 | Scam | Scam | 86% | PASS (TP) | `Enforcement Directorate Notice: Your bank account ending 482...` |
| SAFE_001 | Safe | Safe | 15% | PASS (TN) | `849201 is your SBI One Time Password (OTP) for transaction o...` |
| SAFE_002 | Safe | Safe | 25% | PASS (TN) | `Dear Consumer, your BSES Rajdhani electricity bill for CA No...` |
| SAFE_003 | Safe | Safe | 15% | PASS (TN) | `Your Swiggy order #SW-2298821 from The Yellow Chilli, Korama...` |
| SAFE_004 | Safe | Safe | 8% | PASS (TN) | `Your PNR 2451982301 for Train 12301 HOWRAH RAJDHANI EXP from...` |
| SAFE_005 | Safe | Safe | 2% | PASS (TN) | `Hi Priya! Are we still meeting at Starbucks, Connaught Place...` |
| SAFE_006 | Safe | Safe | 15% | PASS (TN) | `INR 15,000.00 credited to your HDFC Bank account XX4821 on 2...` |
| SAFE_007 | Safe | Safe | 25% | PASS (TN) | `Your Amazon.in order #402-8129831-2918734 for 'boAt Airdopes...` |
| SAFE_008 | Safe | Safe | 25% | PASS (TN) | `Your appointment at AIIMS OPD (Dr. Meera Kapoor, Cardiology)...` |
| SAFE_009 | Safe | Safe | 25% | PASS (TN) | `Paytm: Rs 500.00 paid to Sharma General Store (UPI: sharmash...` |
| SAFE_010 | Safe | Safe | 25% | PASS (TN) | `Your Ola ride is confirmed! Driver Suresh K is on the way in...` |
| SAFE_011 | Safe | Safe | 25% | PASS (TN) | `Your ITR for FY 2023-24 has been successfully e-verified on ...` |
| SAFE_012 | Safe | Safe | 15% | PASS (TN) | `Dear Rahul, your salary of Rs 68,500 has been credited to yo...` |
| SAFE_013 | Safe | Safe | 25% | PASS (TN) | `Hi! This is Zomato. Your order from Domino's Pizza (₹520) is...` |
| SAFE_014 | Safe | Safe | 25% | PASS (TN) | `Dear Customer, your Tata Power DDL bill for Account No. 1004...` |
| SAFE_015 | Safe | Safe | 25% | PASS (TN) | `Your DigiLocker document 'Driving Licence' has been successf...` |
| SAFE_016 | Safe | Safe | 25% | PASS (TN) | `Your Flipkart order for 'Samsung Galaxy Buds2 (Graphite)' wo...` |
| SAFE_017 | Safe | Safe | 25% | PASS (TN) | `RBL Bank: Your credit card ending 8821 has been charged Rs 1...` |
