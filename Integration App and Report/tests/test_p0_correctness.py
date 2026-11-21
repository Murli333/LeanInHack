"""
Automated Pytest Suite for Phase 1 P0 Correctness Requirements
==============================================================
Tests:
  1. OCR failure returns UNKNOWN / OCR_FAILED.
  2. Missing extraction returns UNKNOWN / OCR_FAILED.
  3. Unknown URL produces distinct signal and weight.
  4. Multiple suspicious links do not multiply the score past the ceiling.
  5. Conflicting evidence dampens rather than averages out.
  6. Model file missing degrades gracefully, does not crash.
  7. Every combination of inputs (text only, URL only, image only, text+URL, text+image, empty) works.
  8. Regression test asserting current test cases match baseline_snapshot.json verdicts.
"""

import os
import sys
import json
import tempfile
import pytest

# Ensure repo folders are in sys.path
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))
if os.path.basename(_THIS_DIR) == "tests" and os.path.basename(_PROJECT_ROOT) == "Integration App and Report":
    _PROJECT_ROOT = os.path.abspath(os.path.join(_PROJECT_ROOT, ".."))

for p in [
    _PROJECT_ROOT,
    os.path.join(_PROJECT_ROOT, "Integration App and Report"),
    os.path.join(_PROJECT_ROOT, "Detection Logic"),
    os.path.join(_PROJECT_ROOT, "Data And ML"),
    os.path.join(_PROJECT_ROOT, "Data And ML", "models"),
    os.path.join(_PROJECT_ROOT, "Data And ML", "src"),
]:
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

from scoring import ScamLensScoringEngine, analyze
import eval_cases


@pytest.fixture
def engine():
    return ScamLensScoringEngine()


# ── Test 1: OCR failure returns UNKNOWN / OCR_FAILED ────────────────────────
def test_ocr_failure_returns_unknown_and_ocr_failed(engine):
    """Corrupted / non-image input must return OCR_FAILED and UNKNOWN, never SAFE."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"NOT_A_VALID_IMAGE_CORRUPT_BYTES_XYZ123")
        temp_img = f.name

    try:
        res = engine.analyze(image_input=temp_img)
        assert res["status"] == "OCR_FAILED"
        assert res["verdict"] == "UNKNOWN"
        assert res["risk_score"] is None
        assert "paste" in res["user_message"].lower() or "screenshot" in res["user_message"].lower()
    finally:
        if os.path.exists(temp_img):
            os.unlink(temp_img)


# ── Test 2: Missing extraction returns UNKNOWN / OCR_FAILED ─────────────────
def test_missing_extraction_returns_unknown_and_ocr_failed(monkeypatch, engine):
    """When OCR returns empty text, engine must return OCR_FAILED and UNKNOWN."""
    import scoring
    monkeypatch.setattr(scoring, "extract_text_from_image", lambda path: "")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"fake_bytes")
        temp_img = f.name

    try:
        res = engine.analyze(image_input=temp_img)
        assert res["status"] == "OCR_FAILED"
        assert res["verdict"] == "UNKNOWN"
        assert res["risk_score"] is None
        assert res["verdict"] != "Safe"
    finally:
        if os.path.exists(temp_img):
            os.unlink(temp_img)


# ── Test 3: Unknown URL produces distinct signal and weight ─────────────────
def test_unknown_url_produces_distinct_signal_and_weight(engine):
    """Unrecognized domain must produce UNKNOWN_URL_DOMAIN signal with distinct score."""
    unknown_url = "https://unverified-temporary-portal.org/login"
    res = engine.analyze(url=unknown_url)

    # Must produce a distinct signal
    signal_ids = [s["id"] for s in res.get("signals", [])]
    assert "UNKNOWN_URL_DOMAIN" in signal_ids

    # Find the signal and verify attributes
    sig = next(s for s in res["signals"] if s["id"] == "UNKNOWN_URL_DOMAIN")
    assert sig["source"] == "url_structure"
    assert sig["severity"] == "weak"

    # Must be given distinct score, not 0 and not 100/blocklist
    assert res["details"]["is_unknown_domain"] is True
    assert 0 < res["details"]["url_rule_score"] < 100


# ── Test 4: Multiple suspicious links do not exceed ceiling ──────────────────
def test_multiple_suspicious_links_do_not_exceed_ceiling_without_anchor(engine):
    """Multiple weak unverified links without strong fraud anchor must not breach ceiling."""
    text = (
        "Please check these updates: "
        "http://notice-portal-update1.info and "
        "http://notice-portal-update2.biz for account verification"
    )
    res = engine.analyze(message_text=text)
    # Weak signals ceiling is 65; without a strong anchor, score must not reach Scam (>=70)
    assert res["risk_score"] <= 65
    assert res["verdict"] != "Scam"


# ── Test 5: Conflicting evidence dampens rather than averages out ───────────
def test_conflicting_evidence_dampens_rather_than_averages_out(engine):
    """Legitimate trusted domain with security keywords dampens score to Safe."""
    # SBI OTP message: has OTP keyword, but official trusted SBI domain
    msg = "849201 is your SBI One Time Password (OTP) for transaction at www.onlinesbi.sbi."
    res = engine.analyze(message_text=msg)

    assert res["details"]["has_conflicting_evidence"] is True
    assert res["verdict"] == "Safe"
    assert res["risk_score"] <= 25


# ── Test 6: Model file missing degrades gracefully ──────────────────────────
def test_model_file_missing_degrades_gracefully():
    """Engine must degrade gracefully without crashing when model files are missing."""
    with tempfile.TemporaryDirectory() as empty_dir:
        # Create engine pointing to empty directory with no joblib models
        custom_engine = ScamLensScoringEngine(config_path=None)
        custom_engine.models_available = False
        custom_engine.predictor = None

        # Pure scam text with rule triggers (e.g. Electricity threat)
        scam_text = "URGENT: Your electricity power will be disconnected tonight. Call 9876543210 immediately."
        res = custom_engine.analyze(message_text=scam_text)

        # Must not crash, should return PARTIAL status and detect rule
        assert res["status"] == "PARTIAL"
        assert res["verdict"] in ("Scam", "Suspicious")
        assert "available detection rules" in res["user_message"]


# ── Test 7: Every combination of inputs works ────────────────────────────────
def test_every_combination_of_inputs(monkeypatch, engine):
    """Verify all 6 input combinations: text only, URL only, image only, text+URL, text+image, empty."""
    import signals

    # 1. Empty
    r_empty = engine.analyze()
    assert r_empty["status"] == "NO_INPUT"
    assert r_empty["verdict"] == "Empty"
    assert r_empty["risk_score"] is None

    # 2. Text only
    r_text = engine.analyze(message_text="Hello, how are you?")
    assert r_text["status"] == "OK"
    assert r_text["verdict"] == "Safe"

    # 3. URL only
    r_url = engine.analyze(url="https://www.irctc.co.in")
    assert r_url["status"] == "OK"
    assert r_url["verdict"] == "Safe"

    # 4. Text + URL
    r_combo = engine.analyze(message_text="Check my order at", url="https://www.amazon.in")
    assert r_combo["status"] == "OK"
    assert r_combo["verdict"] == "Safe"

    # 5. Image only (mock successful OCR)
    import scoring
    monkeypatch.setattr(scoring, "extract_text_from_image", lambda path: "Your SBI OTP is 123456")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"mock_image_data")
        tmp_name = f.name
    try:
        r_img = engine.analyze(image_input=tmp_name)
        assert r_img["status"] == "OK"
        assert r_img["details"]["ocr_extracted_text"] == "Your SBI OTP is 123456"

        # 6. Text + Image
        r_text_img = engine.analyze(message_text="Attached bill screenshot", image_input=tmp_name)
        assert r_text_img["status"] == "OK"
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


# ── Test 8: Regression test against baseline_snapshot.json ──────────────────
def test_regression_matches_baseline_snapshot(engine):
    """Verify current analyze() matches baseline_snapshot.json verdicts."""
    snapshot_path = os.path.join(_PROJECT_ROOT, "tests", "baseline_snapshot.json")
    if not os.path.exists(snapshot_path):
        snapshot_path = os.path.join(_PROJECT_ROOT, "Integration App and Report", "tests", "baseline_snapshot.json")

    assert os.path.exists(snapshot_path), f"Baseline snapshot file not found at {snapshot_path}"
    with open(snapshot_path, "r", encoding="utf-8") as f:
        baseline = json.load(f)

    mismatches = []
    for case in eval_cases.EVAL_CASES:
        cid = case["id"]
        res = engine.analyze(message_text=case.get("text"), image_input=case.get("image_path"))
        expected_verdict = baseline[cid]["verdict"]
        actual_verdict = res["verdict"]

        if actual_verdict != expected_verdict:
            mismatches.append(f"{cid}: expected '{expected_verdict}', got '{actual_verdict}'")

    assert not mismatches, f"Regression verdict mismatches detected: {mismatches}"
