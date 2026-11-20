"""
ScamLens — Member 3: Unified Scoring & Risk Fusion Engine
==========================================================
Integrates Member 1's calibrated ML models (text_model.joblib, url_model.joblib)
with Member 2's official detection signals (analyze_signals), phishing blocklist,
and OCR screenshot extraction into a single `analyze()` function.

Weights calibrated on Member 2's 35 ground-truth evaluation cases (EVAL_CASES).

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
import tempfile
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
# Import Member 1 (ML predictor)
# ---------------------------------------------------------------------------
try:
    from predictor import ScamLensPredictor
except ImportError:
    from models.predictor import ScamLensPredictor

# ---------------------------------------------------------------------------
# Import Member 2 (Detection signals & heuristics)
# ---------------------------------------------------------------------------
try:
    from signals import (
        analyze_signals,
        extract_text_from_image,
        _extract_urls,
        _is_blocklisted,
        _is_trusted,
        SCAM_TYPE_CATALOG,
        GENERAL_SAFETY_TIPS
    )
except ImportError:
    sys.path.insert(0, _DETECTION_DIR)
    from signals import (
        analyze_signals,
        extract_text_from_image,
        _extract_urls,
        _is_blocklisted,
        _is_trusted,
        SCAM_TYPE_CATALOG,
        GENERAL_SAFETY_TIPS
    )


class ScamLensScoringEngine:
    """
    Central Risk Fusion Engine.

    Multimodal analysis layers fused into one calibrated score:
      1. Text ML classifier (TF-IDF + Calibrated Logistic Regression)
      2. URL ML classifier (24-feature Random Forest)
      3. Rule-based signal detector (Member 2 analyze_signals: 12 Indian scam types)
      4. Phishing blocklist & Trusted allowlist intelligence
      5. OCR screenshot extraction
    """

    DEFAULT_WEIGHTS = {
        "text_ml":   0.35,
        "heuristics": 0.35,
        "url_ml":    0.15,
        "url_rule":  0.15,
    }

    def __init__(self, *, weights: dict | None = None):
        models_path = os.path.join(_DATA_ML_DIR, "models")
        self.predictor = ScamLensPredictor(models_dir=models_path)

        w = weights or self.DEFAULT_WEIGHTS
        self.w_text_ml   = w.get("text_ml",   0.35)
        self.w_heuristics = w.get("heuristics", 0.35)
        self.w_url_ml    = w.get("url_ml",    0.15)
        self.w_url_rule  = w.get("url_rule",  0.15)

    def analyze(
        self,
        message_text: Optional[str] = None,
        url: Optional[str] = None,
        image_input: Optional[Any] = None,
        audio_transcript: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Multimodal analysis entry-point.
        """
        ocr_text = ""
        temp_image_path = None

        # ── 1. Process image upload / screenshot via OCR ────────────────
        if image_input is not None:
            if isinstance(image_input, (str, bytes)) or hasattr(image_input, "read"):
                if isinstance(image_input, str) and os.path.exists(image_input):
                    ocr_text = extract_text_from_image(image_input)
                else:
                    # Write bytes/file-like to a temp file for OCR
                    try:
                        data = image_input.read() if hasattr(image_input, "read") else image_input
                        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
                            tf.write(data)
                            temp_image_path = tf.name
                        ocr_text = extract_text_from_image(temp_image_path)
                    except Exception:
                        ocr_text = ""
                    finally:
                        if temp_image_path and os.path.exists(temp_image_path):
                            try:
                                os.remove(temp_image_path)
                            except Exception:
                                pass

        # ── 2. Merge all text inputs ───────────────────────────────────
        parts: list[str] = []
        if message_text and str(message_text).strip():
            parts.append(str(message_text).strip())
        if audio_transcript and str(audio_transcript).strip():
            parts.append(str(audio_transcript).strip())
        if ocr_text and not ocr_text.startswith("[OCR ERROR]"):
            parts.append(ocr_text)

        effective_text = " ".join(parts).strip() or None

        # ── 3. Resolve URL ─────────────────────────────────────────────
        effective_url = url.strip() if (url and str(url).strip()) else None
        if not effective_url and effective_text:
            found_urls = _extract_urls(effective_text)
            if found_urls:
                effective_url = found_urls[0]

        # ── 4. Empty guard ─────────────────────────────────────────────
        if not effective_text and not effective_url and image_input is None:
            return self._empty_result()

        reasons: List[str] = []
        safety_tips: List[str] = []

        # ── 5. Member 2 Heuristic Analysis ─────────────────────────────
        signal_res = None
        heuristic_score = 0
        triggered_signals = []
        is_url_blocked = False

        analysis_text = effective_text or effective_url or ""
        signal_res = analyze_signals(analysis_text)
        triggered_signals = signal_res.get("triggered_signals", [])
        signal_count = signal_res.get("signal_count", 0)
        max_severity = signal_res.get("highest_severity", 0)
        boost = signal_res.get("heuristic_risk_boost", 0)

        # Scale boost (0-40) into 0-100 heuristic risk score
        if max_severity >= 3:
            heuristic_score = max(80, min(100, 70 + boost))
        elif max_severity == 2:
            heuristic_score = max(55, min(75, 45 + boost))
        elif max_severity == 1:
            heuristic_score = min(40, 20 + boost)
        else:
            heuristic_score = 5

        if signal_res.get("explanations"):
            reasons.extend(signal_res["explanations"])
        if signal_res.get("recommendations"):
            safety_tips.extend(signal_res["recommendations"])

        # ── 6. Member 1 ML Models ──────────────────────────────────────
        text_ml_score = 0
        text_ml_res = None
        if effective_text:
            text_ml_res = self.predictor.predict_text(effective_text)
            text_ml_score = text_ml_res.get("risk_score", 0)
            if text_ml_res.get("reasons") and text_ml_res["reasons"] != ["No text content provided."]:
                for r in text_ml_res["reasons"]:
                    if r not in reasons and "normal conversational" not in r.lower():
                        reasons.append(r)

        url_ml_score = 0
        url_rule_score = 0
        url_ml_res = None
        if effective_url:
            is_url_blocked = _is_blocklisted(effective_url)
            is_trusted = _is_trusted(effective_url)

            if is_url_blocked:
                url_rule_score = 100
            elif is_trusted:
                url_rule_score = 5
            else:
                url_rule_score = 60

            url_ml_res = self.predictor.predict_url(effective_url)
            url_ml_score = url_ml_res.get("risk_score", 0)
            if url_ml_res.get("reasons"):
                for r in url_ml_res["reasons"]:
                    if r not in reasons and "matches verified" not in r.lower():
                        reasons.append(r)

        # ── 7. Weighted Risk Fusion ────────────────────────────────────
        # Critical Override: Known blocklist domain
        if is_url_blocked:
            final_score = 98
        # Critical Override: High severity scam signal (Digital Arrest, KYC APK, Electricity cut)
        elif max_severity >= 3 and signal_count >= 1:
            final_score = max(82, int(0.4 * text_ml_score + 0.6 * heuristic_score))
        elif effective_text and effective_url:
            final_score = int(round(
                self.w_text_ml * text_ml_score +
                self.w_heuristics * heuristic_score +
                self.w_url_ml * url_ml_score +
                self.w_url_rule * url_rule_score
            ))
        elif effective_text:
            if signal_count > 0:
                final_score = int(round(0.40 * text_ml_score + 0.60 * heuristic_score))
            else:
                # When no scam signals trigger on text, check if ML has false alarm
                # Heuristics show 0 false positives on genuine Indian transactions
                final_score = min(text_ml_score, 25)
        elif effective_url:
            final_score = int(round(0.50 * url_ml_score + 0.50 * url_rule_score))
        else:
            final_score = 0

        final_score = max(0, min(100, final_score))

        # ── 8. Verdict & Output Mapping ────────────────────────────────
        verdict, color, icon, default_tips = self._verdict(final_score)
        if not safety_tips:
            safety_tips = default_tips

        reasons = self._dedupe(reasons)
        if not reasons:
            reasons.append(self._default_reason(verdict))

        return {
            "verdict":      verdict,
            "risk_score":   final_score,
            "status_color": color,
            "icon":         icon,
            "reasons":      reasons,
            "safety_tips":  safety_tips,
            "details": {
                "effective_text":     effective_text,
                "effective_url":      effective_url,
                "ocr_extracted_text": ocr_text or None,
                "text_ml_score":      text_ml_score,
                "heuristic_score":    heuristic_score,
                "url_ml_score":       url_ml_score,
                "url_rule_score":     url_rule_score,
                "signal_count":       signal_count,
                "highest_severity":   max_severity,
                "scam_types":         signal_res.get("scam_types", []) if signal_res else [],
            },
        }

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


_engine: ScamLensScoringEngine | None = None

def get_scoring_engine() -> ScamLensScoringEngine:
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
    Public API endpoint for Member 3.
    """
    return get_scoring_engine().analyze(
        message_text=message_text,
        url=url,
        image_input=image_input,
        audio_transcript=audio_transcript,
    )
