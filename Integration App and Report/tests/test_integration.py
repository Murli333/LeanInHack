"""
ScamLens — Member 3: End-to-End Integration Tests
===================================================
Verifies that the full pipeline (ML + rules + scoring + analyze())
produces correct verdicts for hand-picked representative cases.

Usage:
    cd "Integration App and Report"
    python tests/test_integration.py
"""

import os
import sys

_THIS_DIR  = os.path.dirname(os.path.abspath(__file__))
_MEMBER3   = os.path.dirname(_THIS_DIR)
_ROOT      = os.path.dirname(_MEMBER3)

for _p in [_MEMBER3, _ROOT,
           os.path.join(_ROOT, "Data And ML", "models"),
           os.path.join(_ROOT, "Data And ML", "src"),
           os.path.join(_ROOT, "Detection Logic")]:
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from scoring import analyze


# ═══════════════════════════════════════════════════════════════════════
#  Test cases
# ═══════════════════════════════════════════════════════════════════════
TESTS = [
    # --- SCAM cases: must produce "Scam" or "Suspicious" --------
    {
        "name": "Fake KYC + phishing URL",
        "text": "Dear SBI Customer, your YONO account has been suspended due to pending KYC. Visit http://sbi-kyc-verify.top/sbi.apk immediately.",
        "url": None,
        "expect_flagged": True,
    },
    {
        "name": "Electricity disconnection threat",
        "text": "Urgent: Electricity power will be disconnected at 9:30 PM. Please immediately contact our electricity officer 9876543210.",
        "url": None,
        "expect_flagged": True,
    },
    {
        "name": "UPI PIN collect fraud",
        "text": "Dear Customer, you received UPI collect request of Rs 4999 from Amazon Pay. Enter your UPI PIN to receive money in your bank account.",
        "url": None,
        "expect_flagged": True,
    },
    {
        "name": "Digital arrest threat",
        "text": "Delhi Police Cyber Cell: A parcel in your name containing illegal narcotics has been seized at Mumbai airport. Digital arrest warrant issued. Contact CBI Officer on Skype.",
        "url": None,
        "expect_flagged": True,
    },
    {
        "name": "Part-time job scam via Telegram",
        "text": "Congratulations! You have been selected for part-time work from home. Earn Rs 2500-5000 daily by liking YouTube videos. Contact on Telegram @work_hr",
        "url": None,
        "expect_flagged": True,
    },
    {
        "name": "Phishing URL only (IP-based)",
        "text": None,
        "url": "http://192.168.1.104/secure-bank-login/",
        "expect_flagged": True,
    },
    {
        "name": "Phishing URL only (blocklisted)",
        "text": None,
        "url": "http://yonosbi-login.online/download.apk",
        "expect_flagged": True,
    },
    {
        "name": "Combined text + blocklisted URL",
        "text": "Your BSES power connection will be cut off tonight. Pay immediately: http://electricity-bill-disconnection-alert.fit/pay",
        "url": "http://electricity-bill-disconnection-alert.fit/pay",
        "expect_flagged": True,
    },

    # --- SAFE cases: must produce "Safe" ---------------------------
    {
        "name": "Legitimate SBI OTP",
        "text": "Dear Customer, 849201 is your one time password (OTP) for SBI Internet Banking login. Valid for 3 mins. Never share OTP with anyone.",
        "url": None,
        "expect_flagged": False,
    },
    {
        "name": "Swiggy delivery notification",
        "text": "Dear Customer, your Swiggy order from Biryani Blues is out for delivery. Delivery partner Ravi will reach you shortly.",
        "url": None,
        "expect_flagged": False,
    },
    {
        "name": "IRCTC PNR confirmation",
        "text": "Your PNR 2451982301 for Train 12301 NDLS RAJDHANI is confirmed. Coach B3 Berth 42.",
        "url": "https://www.irctc.co.in",
        "expect_flagged": False,
    },
    {
        "name": "Personal message",
        "text": "Hi Priya, are we meeting at Starbucks Connaught Place at 5 PM today? Let me know if you are running late.",
        "url": None,
        "expect_flagged": False,
    },
    {
        "name": "Legitimate URL only (SBI)",
        "text": None,
        "url": "https://www.onlinesbi.sbi/",
        "expect_flagged": False,
    },
    {
        "name": "Legitimate URL only (HDFC)",
        "text": None,
        "url": "https://netbanking.hdfcbank.com/netbanking/",
        "expect_flagged": False,
    },
    {
        "name": "Bank debit alert",
        "text": "Dear Customer, your A/C ending 4502 is debited by Rs 1500.00 on 20-Nov-26 via UPI. Avail Bal: Rs 42,390.12.",
        "url": None,
        "expect_flagged": False,
    },

    # --- EMPTY input -----------------------------------------------
    {
        "name": "Empty input",
        "text": None,
        "url": None,
        "expect_flagged": False,
    },
]


def run_tests():
    print("=" * 70)
    print("🧪 SCAMLENS — MEMBER 3  END-TO-END INTEGRATION TESTS")
    print("=" * 70)

    passed = failed = 0

    for t in TESTS:
        result = analyze(
            message_text=t["text"],
            url=t["url"],
        )
        is_flagged = result["verdict"] in ("Scam", "Suspicious")
        ok = is_flagged == t["expect_flagged"]

        if ok:
            passed += 1
            tag = "PASS ✅"
        else:
            failed += 1
            tag = "FAIL ❌"

        print(f"  [{tag}] {t['name']:<45} → {result['verdict']} ({result['risk_score']}%)")

    total = passed + failed
    print(f"\n{'=' * 70}")
    print(f"RESULT: {passed}/{total} passed  ({passed/total*100:.1f}%)")
    if failed:
        print(f"⚠️  {failed} test(s) failed!")
    else:
        print("🎉 All tests passed!")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
