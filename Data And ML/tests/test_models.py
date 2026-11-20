"""
Verification & Test Suite for ScamLens ML Models
Tests inference engine, accuracy on diverse test cases, and ensures
output formats align with Member 2, Member 3, and Member 4.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
if MODELS_DIR not in sys.path:
    sys.path.insert(0, MODELS_DIR)

from predictor import ScamLensPredictor


def run_tests():
    print("="*60)
    print(">>> RUNNING SCAMLENS ML VERIFICATION TEST SUITE")
    print("="*60)
    
    predictor = ScamLensPredictor(models_dir=MODELS_DIR)
    
    # 1. Text Scam Test Cases
    test_scams = [
        ("Dear SBI user, your YONO account is locked due to pending KYC update. Click http://sbi-kyc-verify.top/sbi.apk to update immediately.", "Scam"),
        ("Urgent: Electricity power will be disconnected at 9:30 PM from power office because your previous month bill was not updated. Please immediately contact our electricity officer 9876543210.", "Scam"),
        ("Delhi Police Cyber Cell: A parcel in your name containing illegal narcotics has been seized at Mumbai airport. Digital arrest warrant issued. Contact CBI Officer on Skype.", "Scam"),
        ("Dear Customer, you received UPI collect request of Rs 4999 from Amazon Pay. Enter your UPI PIN to receive money in your bank account.", "Scam"),
        ("Congratulations! You have been selected for part-time work from home. Earn Rs 2500-5000 daily by liking YouTube videos. Contact on Telegram @work_hr", "Scam"),
    ]
    
    test_legit = [
        ("Dear Customer, 849201 is your one time password (OTP) for SBI Internet Banking login. Valid for 3 mins. Never share OTP with anyone.", "Safe"),
        ("Dear Customer, your Swiggy order from Biryani Blues is out for delivery. Delivery partner Ravi will reach you shortly.", "Safe"),
        ("Your PNR 2451982301 for Train 12301 NDLS RAJDHANI is confirmed. Coach B3 Berth 42. Check PNR status at www.irctc.co.in.", "Safe"),
        ("Dear Consumer, your Tata Power DDL electricity bill for CA No 60012345678 of Rs 2140 is due on 25-Nov. Pay via official portal.", "Safe"),
        ("Hi Priya, are we meeting at Starbucks Connaught Place at 5 PM today? Let me know if you are running late.", "Safe"),
    ]
    
    print("\n--- 1. Evaluating Text Scam Cases ---")
    scam_passed = 0
    for text, expected in test_scams:
        res = predictor.predict_text(text)
        is_correct = (res["verdict"] in ["Scam", "Suspicious"])
        if is_correct:
            scam_passed += 1
        status = "PASS" if is_correct else "FAIL"
        print(f"[{status}] Score: {res['risk_score']}% | Verdict: {res['verdict']} | Text: {text[:60]}...")
        if res["reasons"]:
            print(f"       -> Explanation: {res['reasons'][0]}")

    print("\n--- 2. Evaluating Text Legitimate Cases ---")
    legit_passed = 0
    for text, expected in test_legit:
        res = predictor.predict_text(text)
        is_correct = (res["verdict"] == "Safe")
        if is_correct:
            legit_passed += 1
        status = "PASS" if is_correct else "FAIL"
        print(f"[{status}] Score: {res['risk_score']}% | Verdict: {res['verdict']} | Text: {text[:60]}...")

    # 2. URL Test Cases
    test_urls = [
        ("http://sbi-kyc-verify.top/sbi.apk", "Scam"),
        ("http://192.168.1.104/secure-bank-login/", "Scam"),
        ("http://hdfc-card-unlock.xyz/verify", "Scam"),
        ("https://www.onlinesbi.sbi/", "Safe"),
        ("https://netbanking.hdfcbank.com/netbanking/", "Safe"),
        ("https://cybercrime.gov.in/", "Safe"),
    ]
    
    print("\n--- 3. Evaluating URL Test Cases ---")
    url_passed = 0
    for url, expected in test_urls:
        res = predictor.predict_url(url)
        if expected == "Scam":
            is_correct = (res["verdict"] in ["Scam", "Suspicious"])
        else:
            is_correct = (res["verdict"] == "Safe")
            
        if is_correct:
            url_passed += 1
        status = "PASS" if is_correct else "FAIL"
        print(f"[{status}] Score: {res['risk_score']}% | Verdict: {res['verdict']} | URL: {url}")
        if res["reasons"]:
            print(f"       -> Explanation: {res['reasons'][0]}")

    # 3. Combined Multimodal Test
    print("\n--- 4. Evaluating Combined Multimodal Inference ---")
    combined_sample_text = "Dear customer, your electricity will be disconnected tonight. Update bill immediately: http://electricity-bill-disconnection-alert.fit/pay"
    comb_res = predictor.predict_combined(text=combined_sample_text)
    print(f"Verdict: {comb_res['verdict']} ({comb_res['icon']}) | Total Risk Score: {comb_res['risk_score']}%")
    print("Why we think this:")
    for reason in comb_res["reasons"]:
        print(f"  • {reason}")
    print("Safety Tips:")
    for tip in comb_res["safety_tips"]:
        print(f"  - {tip}")

    print("\n" + "="*60)
    total_tests = len(test_scams) + len(test_legit) + len(test_urls)
    total_passed = scam_passed + legit_passed + url_passed
    print(f"SUMMARY: {total_passed}/{total_tests} Tests Passed ({(total_passed/total_tests)*100:.1f}%)")
    print("="*60)
    assert total_passed == total_tests, "Test suite did not achieve 100% test pass rate!"
    print("[SUCCESS] All Verification Tests Passed Flawlessly!")


if __name__ == "__main__":
    run_tests()
