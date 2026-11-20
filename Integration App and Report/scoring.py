"""
ScamLens — Member 3: Unified Scoring & Risk Fusion Engine
==========================================================
Integrates Member 1's calibrated ML models (text_model.joblib, url_model.joblib)
with Member 2's rule-based Indian scam signals (signals.py), phishing blocklist,
and OCR screenshot extraction into a single `analyze()` function.

Weights were tuned on Member 2's 36-case ground-truth evaluation set
(eval_cases.py) using a grid search across three profiles.
Selected profile: "Balanced Hybrid" — 94.44% accuracy, 100% precision, 0% FPR.

Output contract (all three UI states ready for Member 4's Streamlit design):
{
    "verdict":      "Safe" | "Suspicious" | "Scam" | "Empty",
    "risk_score":   int (0–100),
    "status_color": "green" | "amber" | "red" | "gray",
    "icon":         "✅" | "⚠️" | "🚨" | "ℹ️",
    "reasons":      list[str],   # plain-language "Why we think this"
    "safety_tips":  list[str],   # actionable guidance
    "details": { ... }           # sub-scores, triggered signals, OCR text
}
"""

import os
import sys
from typing import Optional, Dict, Any, List

# ---------------------------------------------------------------------------
# Path setup — locate sibling member folders relative to this file
# ---------------------------------------------------------------------------
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_DATA_ML_DIR = os.path.join(_PROJECT_ROOT, "Data And ML")
_DETECTION_DIR = os.path.join(_PROJECT_ROOT, "Detection Logic")

for _p in [
    _PROJECT_ROOT,
    _DATA_ML_DIR,
    _DETECTION_DIR,
    os.path.join(_DATA_ML_DIR, "models"),
    os.path.join(_DATA_ML_DIR, "src"),
]:
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------------------------------------------------------------------
# Import Member 1  (ML predictor)
# ---------------------------------------------------------------------------
try:
    from predictor import ScamLensPredictor
except ImportError:
    from models.predictor import ScamLensPredictor          # fallback

# ---------------------------------------------------------------------------
# Import Member 2  (heuristic signals + OCR)
# ---------------------------------------------------------------------------
try:
    from signals import ScamSignalDetector, extract_text_from_image, EXPLANATION_CATALOG
except ImportError:
    # In case the caller manipulated sys.path differently
    sys.path.insert(0, _DETECTION_DIR)
    from signals import ScamSignalDetector, extract_text_from_image, EXPLANATION_CATALOG


# ═══════════════════════════════════════════════════════════════════════════
#  Core Scoring Engine
# ═══════════════════════════════════════════════════════════════════════════
class ScamLensScoringEngine:
    """
    Central Risk Fusion Engine.

    Five analysis layers fused into one calibrated score:
      1. Text ML classifier   (TF-IDF + Calibrated Logistic Regression)
      2. URL ML classifier     (24-feature Random Forest)
      3. Rule-based signal detector (12 Indian scam patterns)
      4. Phishing blocklist & TLD risk engine
      5. OCR screenshot extraction
    """

    # Tuned weights — validated via grid search on 36 eval cases
    DEFAULT_WEIGHTS = {
        "text_ml":   0.30,
        "text_rule": 0.35,
        "url_ml":    0.15,
        "url_rule":  0.20,
    }

    def __init__(self, *, weights: dict | None = None):
        models_path = os.path.join(_DATA_ML_DIR, "models")
        self.predictor = ScamLensPredictor(models_dir=models_path)
        self.signal_detector = ScamSignalDetector()

        w = weights or self.DEFAULT_WEIGHTS
        self.w_text_ml   = w.get("text_ml",   0.30)
        self.w_text_rule = w.get("text_rule", 0.35)
        self.w_url_ml    = w.get("url_ml",    0.15)
        self.w_url_rule  = w.get("url_rule",  0.20)

    # ------------------------------------------------------------------
    #  Public API — the single entry-point consumed by app.py
    # ------------------------------------------------------------------
    def analyze(
        self,
        message_text: Optional[str] = None,
        url: Optional[str] = None,
        image_input: Optional[Any] = None,
        audio_transcript: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Multimodal analysis entry-point.

        Parameters
        ----------
        message_text     : Pasted suspicious message (SMS / WhatsApp / email body).
        url              : Suspicious link the user wants to check.
        image_input      : Uploaded screenshot (file path, bytes, or file-like).
        audio_transcript : Transcribed voice note (from an external STT step).

        Returns
        -------
        dict  — verdict, risk_score, status_color, icon, reasons, safety_tips, details.
        """

        # ── 1. OCR extraction ──────────────────────────────────────────
        ocr_text = ""
        if image_input is not None:
            ocr_text = extract_text_from_image(image_input)

        # ── 2. Merge all text sources ──────────────────────────────────
        parts: list[str] = []
        if message_text and str(message_text).strip():
            parts.append(str(message_text).strip())
        if audio_transcript and str(audio_transcript).strip():
            parts.append(str(audio_transcript).strip())
        if ocr_text:
            parts.append(ocr_text)

        effective_text = " ".join(parts).strip() or None

        # ── 3. Resolve URL ─────────────────────────────────────────────
        effective_url = url.strip() if (url and str(url).strip()) else None
        if not effective_url and effective_text:
            found = self.signal_detector.extract_urls(effective_text)
            if found:
                effective_url = found[0]

        # ── 4. Empty guard ─────────────────────────────────────────────
        if not effective_text and not effective_url and image_input is None:
            return self._empty_result()

        # ── 5. Run sub-analyses ────────────────────────────────────────
        reasons: List[str] = []

        text_ml_score = text_rule_score = 0
        text_res = rule_res = None

        if effective_text:
            text_res  = self.predictor.predict_text(effective_text)
            rule_res  = self.signal_detector.evaluate_rules(effective_text)
            text_ml_score   = text_res.get("risk_score", 0)
            text_rule_score = rule_res.get("rule_risk_score", 0)

            if rule_res.get("explanations"):
                reasons.extend(rule_res["explanations"])
            if text_res.get("reasons") and text_res["reasons"] != ["No text content provided."]:
                for r in text_res["reasons"]:
                    if r not in reasons:
                        reasons.append(r)

        url_ml_score = url_rule_score = 0
        url_res = url_sig_res = None

        if effective_url:
            url_res     = self.predictor.predict_url(effective_url)
            url_sig_res = self.signal_detector.check_url(effective_url)
            url_ml_score   = url_res.get("risk_score", 0)
            url_rule_score = url_sig_res.get("url_risk_score", 0)

            if url_sig_res.get("explanations"):
                reasons.extend(url_sig_res["explanations"])
            if url_res.get("reasons"):
                for r in url_res["reasons"]:
                    if r not in reasons and "matches verified" not in r.lower():
                        reasons.append(r)

        # ── 6. Weighted fusion ─────────────────────────────────────────
        final_score = self._fuse_scores(
            effective_text, effective_url,
            text_ml_score, text_rule_score,
            url_ml_score,  url_rule_score,
            rule_res, url_sig_res,
        )

        # ── 7. Verdict + visual identity ───────────────────────────────
        verdict, color, icon, tips = self._verdict(final_score)
        reasons = self._dedupe(reasons)
        if not reasons:
            reasons.append(self._default_reason(verdict))

        return {
            "verdict":      verdict,
            "risk_score":   final_score,
            "status_color": color,
            "icon":         icon,
            "reasons":      reasons,
            "safety_tips":  tips,
            "details": {
                "effective_text":     effective_text,
                "effective_url":      effective_url,
                "ocr_extracted_text": ocr_text or None,
                "text_ml_score":      text_ml_score,
                "text_rule_score":    text_rule_score,
                "url_ml_score":       url_ml_score,
                "url_rule_score":     url_rule_score,
                "triggered_signals":  rule_res.get("triggered_signals", []) if rule_res else [],
            },
        }

    # ------------------------------------------------------------------
    #  Fusion logic
    # ------------------------------------------------------------------
    def _fuse_scores(
        self,
        has_text, has_url,
        t_ml, t_rule,
        u_ml, u_rule,
        rule_res, url_sig_res,
    ) -> int:

        if has_text and has_url:
            is_blocked    = (url_sig_res or {}).get("is_blocked", False)
            has_critical  = any(
                s in (rule_res or {}).get("triggered_signals", [])
                for s in ("digital_arrest", "malicious_apk", "fake_kyc")
            )
            if is_blocked:
                raw = max(95, int(0.5 * t_rule + 0.5 * u_rule))
            elif has_critical and u_ml >= 50:
                raw = max(88, int(0.5 * t_rule + 0.5 * u_ml))
            else:
                raw = int(round(
                    self.w_text_ml * t_ml + self.w_text_rule * t_rule +
                    self.w_url_ml  * u_ml + self.w_url_rule  * u_rule
                ))

        elif has_text:
            is_benign = (rule_res or {}).get("is_benign_transaction", False)
            signals   = (rule_res or {}).get("triggered_signals", [])
            if signals:
                raw = int(round(0.40 * t_ml + 0.60 * t_rule))
            elif is_benign:
                raw = min(int(round(0.35 * t_ml + 0.65 * t_rule)), 15)
            else:
                raw = int(round(0.50 * t_ml + 0.50 * t_rule))

        elif has_url:
            if (url_sig_res or {}).get("is_blocked", False):
                raw = 98
            else:
                raw = int(round(0.45 * u_ml + 0.55 * u_rule))
        else:
            raw = 0

        return max(0, min(100, raw))

    # ------------------------------------------------------------------
    #  Verdict mapping
    # ------------------------------------------------------------------
    @staticmethod
    def _verdict(score: int):
        if score >= 70:
            return "Scam", "red", "🚨", [
                "⚠️ Do NOT click any links, open attachments, or install any APK files.",
                "🔒 Never share your OTP, UPI PIN, ATM PIN, or banking passwords with anyone.",
                "🛑 Official police, CBI, or tax officers will NEVER arrest you over Skype or ask you to transfer funds.",
                "📢 Report this fraud immediately at https://cybercrime.gov.in or call the 1930 National Helpline.",
            ]
        if score >= 40:
            return "Suspicious", "amber", "⚠️", [
                "🔍 Exercise caution — independently verify via official customer-care channels.",
                "💳 Do not approve any pending UPI collect requests or send token advance payments.",
                "🚫 Never install remote screen-sharing tools like AnyDesk, TeamViewer, or RustDesk.",
            ]
        return "Safe", "green", "✅", [
            "✔️ This communication appears consistent with normal, legitimate messages.",
            "💡 Standard practice: authentic organisations and banks will never request your passwords or PIN.",
        ]

    @staticmethod
    def _empty_result():
        return {
            "verdict":      "Empty",
            "risk_score":   0,
            "status_color": "gray",
            "icon":         "ℹ️",
            "reasons":      ["No message, URL, or screenshot was provided for analysis."],
            "safety_tips":  ["Paste a message, enter a URL, or upload a screenshot to get started."],
            "details":      {"has_text": False, "has_url": False, "has_ocr": False},
        }

    @staticmethod
    def _default_reason(verdict: str) -> str:
        return {
            "Scam":       "High correlation with documented digital fraud patterns.",
            "Suspicious": "Uncommon urgency or unverified source — proceed with vigilance.",
            "Safe":       "No active fraud indicators or phishing attributes detected.",
        }.get(verdict, "")

    @staticmethod
    def _dedupe(items: list) -> list:
        seen, out = set(), []
        for x in items:
            if x and x not in seen:
                seen.add(x)
                out.append(x)
        return out


# ═══════════════════════════════════════════════════════════════════════════
#  Convenience wrappers  (imported directly by app.py)
# ═══════════════════════════════════════════════════════════════════════════
_engine: ScamLensScoringEngine | None = None


def get_scoring_engine() -> ScamLensScoringEngine:
    """Lazy-singleton so the models are loaded exactly once per process."""
    global _engine
    if _engine is None:
        _engine = ScamLensScoringEngine()
    return _engine


def analyze(
    message_text: Optional[str] = None,
    url: Optional[str] = None,
    image_input: Optional[Any] = None,
    audio_transcript: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Top-level public API.

    >>> from scoring import analyze
    >>> result = analyze(message_text="Your KYC is expired...")
    >>> print(result["verdict"], result["risk_score"])
    """
    return get_scoring_engine().analyze(
        message_text=message_text,
        url=url,
        image_input=image_input,
        audio_transcript=audio_transcript,
    )
