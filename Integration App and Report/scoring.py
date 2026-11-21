"""
ScamLens — Member 3: Unified Scoring & Risk Fusion Engine
==========================================================
Integrates Member 1's calibrated ML models (text_model.joblib, url_model.joblib)
with Member 2's official detection signals (analyze_signals), phishing blocklist,
and OCR screenshot extraction into a single `analyze()` function.

Phase 1 P0 Hardening:
  - Configurable fusion via config/scoring.json (weights, thresholds, floors, ceilings)
  - Explicit status: OK | PARTIAL | OCR_FAILED | MODEL_UNAVAILABLE | NO_INPUT
  - Robust OCR failure handling (returns UNKNOWN, never SAFE)
  - Dedicated unknown URL signal and weighting (neither 0 nor confirmed malicious)
  - Conflicting evidence dampening instead of linear averaging
  - Multiple weak signals capped at ceiling without strong anchor
  - Graceful degradation when ML models are missing or unavailable
  - Signals list format: [{id, source, severity, explanation}]
  - Plain-language, jargon-free user messages
"""

import os
import re
import sys
import json
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
# Import Member 1 (ML predictor) with graceful degradation
# ---------------------------------------------------------------------------
_PREDICTOR_CLASS = None
try:
    from predictor import ScamLensPredictor
    _PREDICTOR_CLASS = ScamLensPredictor
except ImportError:
    try:
        from models.predictor import ScamLensPredictor
        _PREDICTOR_CLASS = ScamLensPredictor
    except ImportError:
        _PREDICTOR_CLASS = None

# ---------------------------------------------------------------------------
# Import Member 2 (Detection signals & heuristics)
# ---------------------------------------------------------------------------
try:
    from signals import (
        analyze_signals,
        extract_text_from_image,
        _extract_urls,
        _extract_domain,
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
        _extract_domain,
        _is_blocklisted,
        _is_trusted,
        SCAM_TYPE_CATALOG,
        GENERAL_SAFETY_TIPS
    )

# Regular expression for IP-based URLs
_IP_PATTERN = re.compile(
    r'^(?:https?://)?(?:www\.)?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:/.*)?$',
    re.IGNORECASE
)

# Benign transaction cues used for protective/conflicting evidence
_BENIGN_PATTERNS = [
    re.compile(r'\b(?:debited|credited)\b.*\b(?:bal|balance)\b', re.IGNORECASE),
    re.compile(r'\bpnr\s*\d+\b', re.IGNORECASE),
    re.compile(r'\bout for delivery\b', re.IGNORECASE),
    re.compile(r'\bdelivered\. thank you for shopping\b', re.IGNORECASE),
    re.compile(r'\bnever share (?:your )?otp\b', re.IGNORECASE),
    re.compile(r'\bdo not (?:disclose|share) (?:to anyone|with anyone)\b', re.IGNORECASE),
]


class ScamLensScoringEngine:
    """
    Central Risk Fusion Engine.

    Fuses:
      1. Text ML classifier (TF-IDF + Calibrated Logistic Regression)
      2. URL ML classifier (24-feature Random Forest)
      3. Heuristic signal detector (analyze_signals: Indian scam rules)
      4. Phishing blocklist, trusted allowlist, and unknown-domain analysis
      5. OCR screenshot extraction
    """

    DEFAULT_CONFIG = {
        "weights": {
            "text_ml": 0.35,
            "heuristics": 0.35,
            "url_ml": 0.15,
            "url_rule": 0.15,
            "unknown_url_score": 60
        },
        "thresholds": {
            "scam": 70,
            "suspicious": 40
        },
        "floors": {
            "blocklist": 98,
            "critical_rule": 82,
            "ip_url": 75,
            "strong_rule": 70
        },
        "ceilings": {
            "weak_signals_only": 65,
            "unanchored_text_ceiling": 25
        },
        "dampening": {
            "conflicting_evidence_factor": 0.30
        },
        "baseline": {
            "min_safe_score": 2,
            "default_safe_score": 10
        }
    }

    def __init__(self, *, config_path: str | None = None, weights: dict | None = None):
        self.config = self._load_config(config_path)
        if weights:
            self.config["weights"].update(weights)

        self.w_text_ml = self.config["weights"].get("text_ml", 0.35)
        self.w_heuristics = self.config["weights"].get("heuristics", 0.35)
        self.w_url_ml = self.config["weights"].get("url_ml", 0.15)
        self.w_url_rule = self.config["weights"].get("url_rule", 0.15)
        self.unknown_url_score = self.config["weights"].get("unknown_url_score", 60)

        # Initialize predictor
        self.predictor = None
        self.models_available = False
        models_path = os.path.join(_DATA_ML_DIR, "models")
        if _PREDICTOR_CLASS is not None:
            try:
                self.predictor = _PREDICTOR_CLASS(models_dir=models_path)
                has_text = getattr(self.predictor, "text_model", None) is not None
                has_url = getattr(self.predictor, "url_model", None) is not None
                self.models_available = has_text or has_url
            except Exception:
                self.predictor = None
                self.models_available = False

    def _load_config(self, explicit_path: str | None = None) -> dict:
        candidates = [
            explicit_path,
            os.path.join(_PROJECT_ROOT, "config", "scoring.json"),
            os.path.join(_THIS_DIR, "config", "scoring.json"),
        ]
        for p in candidates:
            if p and os.path.isfile(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        loaded = json.load(f)
                        merged = json.loads(json.dumps(self.DEFAULT_CONFIG))
                        for k, v in loaded.items():
                            if isinstance(v, dict) and k in merged:
                                merged[k].update(v)
                            else:
                                merged[k] = v
                        return merged
                except Exception:
                    pass
        return json.loads(json.dumps(self.DEFAULT_CONFIG))

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
        ocr_failed = False
        temp_image_path = None

        # ── 1. OCR Extraction ──────────────────────────────────────────
        if image_input is not None:
            try:
                if isinstance(image_input, str) and os.path.exists(image_input):
                    ocr_res = extract_text_from_image(image_input)
                else:
                    data = image_input.read() if hasattr(image_input, "read") else image_input
                    suffix = ".png"
                    if hasattr(image_input, "name") and image_input.name:
                        suffix = os.path.splitext(image_input.name)[-1] or ".png"
                    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                        tmp.write(data)
                        temp_image_path = tmp.name
                    ocr_res = extract_text_from_image(temp_image_path)

                if not ocr_res or not str(ocr_res).strip() or str(ocr_res).strip().startswith("[OCR ERROR]"):
                    ocr_failed = True
                    ocr_text = ""
                else:
                    ocr_text = str(ocr_res).strip()
            except Exception:
                ocr_failed = True
                ocr_text = ""
            finally:
                if temp_image_path and os.path.exists(temp_image_path):
                    try:
                        os.unlink(temp_image_path)
                    except OSError:
                        pass

        # ── 2. Synthesize Effective Inputs ─────────────────────────────
        effective_text = (message_text or "").strip()
        if not effective_text and audio_transcript and str(audio_transcript).strip():
            effective_text = str(audio_transcript).strip()
        if not effective_text and ocr_text:
            effective_text = ocr_text

        effective_url = (url or "").strip()
        extracted_from_text = []
        if effective_text:
            extracted_from_text = _extract_urls(effective_text)
            if not effective_url and extracted_from_text:
                effective_url = extracted_from_text[0]

        # ── 3. Handle Edge Cases (OCR failure, No input) ────────────────
        has_provided_text = bool((message_text or "").strip() or (audio_transcript or "").strip())
        has_provided_url = bool((url or "").strip())

        # Failure condition: image was uploaded but OCR produced nothing, and no text/url provided
        if image_input is not None and ocr_failed and not has_provided_text and not has_provided_url:
            return self._ocr_failed_result()

        # Failure condition: no inputs at all
        if not effective_text and not effective_url and not image_input:
            return self._empty_result()

        # Status tracking
        status = "OK"
        if image_input is not None and ocr_failed:
            status = "PARTIAL"
        elif not self.models_available:
            status = "PARTIAL"

        structured_signals: List[Dict[str, Any]] = []
        reasons: List[str] = []
        safety_tips: List[str] = []

        # ── 4. Text & Heuristics Layer ─────────────────────────────────
        text_ml_score = 0
        heuristic_score = 0
        signal_count = 0
        max_severity = 0
        boost = 0
        signal_res = None
        has_strong_rule = False

        if effective_text:
            # Member 2 heuristic rules
            try:
                signal_res = analyze_signals(effective_text)
                signal_count = signal_res.get("signal_count", 0)
                max_severity = signal_res.get("highest_severity", 0)
                boost = signal_res.get("heuristic_risk_boost", 0)

                # Calibrate heuristic score (0-100)
                if max_severity >= 3:
                    heuristic_score = max(80, min(100, 70 + boost))
                    has_strong_rule = True
                elif max_severity == 2:
                    heuristic_score = max(55, min(75, 45 + boost))
                    has_strong_rule = True
                elif max_severity == 1:
                    heuristic_score = min(40, 20 + boost)
                else:
                    heuristic_score = 5

                for trig in signal_res.get("triggered_signals", []):
                    sev_num = trig.get("severity", 1)
                    is_strong = sev_num >= 2
                    structured_signals.append({
                        "id": trig.get("signal_id", "HEURISTIC_RULE"),
                        "source": "rule",
                        "severity": "strong" if is_strong else "weak",
                        "explanation": trig.get("explanation", "")
                    })
                    if trig.get("explanation"):
                        reasons.append(trig["explanation"])
                    if trig.get("recommendation"):
                        safety_tips.append(trig["recommendation"])
            except Exception:
                signal_res = None

            # Member 1 ML text prediction
            if self.predictor is not None and getattr(self.predictor, "text_model", None) is not None:
                try:
                    pred_t = self.predictor.predict_text(effective_text)
                    text_ml_score = int(pred_t.get("risk_score", 0))
                    if text_ml_score >= 70:
                        structured_signals.append({
                            "id": "TEXT_ML_HIGH_RISK",
                            "source": "model",
                            "severity": "strong",
                            "explanation": "Statistical language model detected vocabulary strongly associated with fraud."
                        })
                    elif text_ml_score >= 40:
                        structured_signals.append({
                            "id": "TEXT_ML_MODERATE_RISK",
                            "source": "model",
                            "severity": "weak",
                            "explanation": "Language model detected elevated urgency or marketing pressure."
                        })
                    if pred_t.get("reasons"):
                        reasons.extend(pred_t["reasons"])
                except Exception:
                    text_ml_score = 0
            elif not signal_count and not effective_url and not self.models_available:
                return self._model_unavailable_result()

        # ── 5. URL Layer & Intelligence ────────────────────────────────
        url_ml_score = 0
        url_rule_score = 0
        is_blocklisted = False
        is_trusted_domain = False
        is_unknown_domain = False
        is_ip_domain = False

        if effective_url:
            domain = _extract_domain(effective_url)
            is_blocklisted = _is_blocklisted(effective_url)
            is_trusted_domain = _is_trusted(effective_url)
            is_ip_domain = bool(_IP_PATTERN.match(effective_url))

            # URL Rule & Blocklist Check
            if is_blocklisted:
                url_rule_score = 100
                structured_signals.append({
                    "id": "BLOCKLISTED_URL",
                    "source": "blocklist",
                    "severity": "strong",
                    "explanation": f"The link '{domain}' matches a confirmed phishing threat database."
                })
                reasons.append(f"Known phishing link detected: {domain}")
                safety_tips.append(f"Never visit '{domain}' — it is a confirmed fake/phishing website.")
            elif is_ip_domain:
                url_rule_score = 90
                structured_signals.append({
                    "id": "RAW_IP_URL",
                    "source": "url_structure",
                    "severity": "strong",
                    "explanation": f"URL '{effective_url}' points directly to a numeric IP address."
                })
                reasons.append("Link uses a numeric IP address instead of a standard domain name.")
            elif is_trusted_domain:
                url_rule_score = 5
                structured_signals.append({
                    "id": "TRUSTED_DOMAIN",
                    "source": "rule",
                    "severity": "weak",
                    "explanation": f"The domain '{domain}' belongs to a verified authentic organization."
                })
            else:
                # Unknown domain: not on blocklist, not on trusted list
                is_unknown_domain = True
                url_rule_score = self.unknown_url_score
                structured_signals.append({
                    "id": "UNKNOWN_URL_DOMAIN",
                    "source": "url_structure",
                    "severity": "weak",
                    "explanation": f"The domain '{domain}' is unverified: it is not on the known blocklist, but is not an official trusted domain."
                })
                reasons.append(f"Unverified web destination: '{domain}' is not an official verified domain.")

            # Member 1 ML URL prediction
            if self.predictor is not None and getattr(self.predictor, "url_model", None) is not None:
                try:
                    pred_u = self.predictor.predict_url(effective_url)
                    url_ml_score = int(pred_u.get("risk_score", 0))
                    if url_ml_score >= 70:
                        structured_signals.append({
                            "id": "URL_ML_HIGH_RISK",
                            "source": "model",
                            "severity": "strong",
                            "explanation": "Structural URL analysis identified attributes typical of phishing links."
                        })
                    elif url_ml_score >= 40:
                        structured_signals.append({
                            "id": "URL_ML_MODERATE_RISK",
                            "source": "model",
                            "severity": "weak",
                            "explanation": "Structural URL analysis detected non-standard link formatting."
                        })
                    if pred_u.get("reasons"):
                        reasons.extend(pred_u["reasons"])
                except Exception:
                    url_ml_score = 0

        # ── 6. Conflicting Evidence Check ──────────────────────────────
        is_benign_text_pattern = False
        if effective_text:
            lower_text = effective_text.lower()
            is_benign_text_pattern = any(p.search(lower_text) for p in _BENIGN_PATTERNS)

        has_conflicting_evidence = False
        if is_trusted_domain or (is_benign_text_pattern and not has_strong_rule and not is_blocklisted):
            has_conflicting_evidence = True

        # ── 7. Weighted Risk Fusion Engine ─────────────────────────────
        if is_blocklisted:
            final_score = self.config["floors"].get("blocklist", 98)
        elif max_severity >= 3 and signal_count >= 1:
            crit_floor = self.config["floors"].get("critical_rule", 82)
            final_score = max(crit_floor, int(0.4 * text_ml_score + 0.6 * heuristic_score))
        elif effective_text and effective_url:
            total_w = self.w_text_ml + self.w_heuristics + self.w_url_ml + self.w_url_rule
            final_score = int(round(
                (self.w_text_ml * text_ml_score +
                 self.w_heuristics * heuristic_score +
                 self.w_url_ml * url_ml_score +
                 self.w_url_rule * url_rule_score) / total_w
            ))
        elif effective_text:
            if signal_count > 0:
                final_score = int(round(0.40 * text_ml_score + 0.60 * heuristic_score))
            else:
                unanchored_ceiling = self.config["ceilings"].get("unanchored_text_ceiling", 25)
                final_score = min(text_ml_score, unanchored_ceiling)
        elif effective_url:
            final_score = int(round(0.50 * url_ml_score + 0.50 * url_rule_score))
        else:
            final_score = 0

        # Apply Conflicting Evidence Dampening (never linear averaging out)
        if has_conflicting_evidence and not is_blocklisted:
            damp_factor = self.config["dampening"].get("conflicting_evidence_factor", 0.30)
            final_score = int(round(final_score * damp_factor))

        # Apply Ceiling: weak signals without strong anchor cannot exceed ceiling
        has_strong_anchor = is_blocklisted or is_ip_domain or (max_severity >= 2)
        if not has_strong_anchor:
            weak_ceiling = self.config["ceilings"].get("weak_signals_only", 65)
            final_score = min(final_score, weak_ceiling)

        # Baseline floor: No evidence must not be scored as 0
        min_safe = self.config["baseline"].get("min_safe_score", 2)
        final_score = max(min_safe, min(100, final_score))

        # ── 8. Verdict Mapping & Friendly Messaging ────────────────────
        scam_th = self.config["thresholds"].get("scam", 70)
        susp_th = self.config["thresholds"].get("suspicious", 40)

        verdict, color, icon, default_tips = self._verdict(final_score, scam_th, susp_th)
        user_message = self._compose_user_message(verdict, status, has_conflicting_evidence, is_unknown_domain)

        if not safety_tips:
            safety_tips = default_tips

        reasons = self._dedupe(reasons)
        if not reasons:
            reasons.append(self._default_reason(verdict))

        return {
            "verdict": verdict,
            "status": status,
            "risk_score": final_score,
            "status_color": color,
            "icon": icon,
            "user_message": user_message,
            "reasons": reasons,
            "safety_tips": safety_tips,
            "signals": structured_signals,
            "details": {
                "effective_text": effective_text,
                "effective_url": effective_url,
                "ocr_extracted_text": ocr_text or None,
                "text_ml_score": text_ml_score,
                "heuristic_score": heuristic_score,
                "url_ml_score": url_ml_score,
                "url_rule_score": url_rule_score,
                "signal_count": signal_count,
                "highest_severity": max_severity,
                "scam_types": signal_res.get("scam_types", []) if signal_res else [],
                "is_blocklisted": is_blocklisted,
                "is_trusted": is_trusted_domain,
                "is_unknown_domain": is_unknown_domain,
                "has_conflicting_evidence": has_conflicting_evidence,
                "has_strong_anchor": has_strong_anchor,
            },
        }

    @staticmethod
    def _verdict(score: int, scam_th: int = 70, susp_th: int = 40):
        if score >= scam_th:
            return "Scam", "red", "🚨", [
                "⚠️ Do NOT click any links, open attachments, or install any APK files.",
                "🔒 Never share your OTP, UPI PIN, ATM PIN, or banking passwords with anyone.",
                "🛑 Official police, CBI, or tax officers will NEVER arrest you over Skype or ask you to transfer funds.",
                "📢 Report this fraud immediately at https://cybercrime.gov.in or call the 1930 National Helpline.",
            ]
        if score >= susp_th:
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
    def _compose_user_message(verdict: str, status: str, has_conflicting: bool, is_unknown_url: bool) -> str:
        if status == "PARTIAL":
            return "Analysis completed using available detection rules; some model components were degraded or unavailable."
        if verdict == "Scam":
            return "High risk of fraud detected. Do not click links, send money, or share any personal details or OTPs."
        if verdict == "Suspicious":
            if is_unknown_url:
                return "The link points to an unverified web domain. Please verify the sender through official channels before clicking."
            return "Proceed with caution. Several suspicious indicators were found. Verify independently before taking any action."
        if has_conflicting:
            return "Legitimate official domain or transaction format confirmed. Exercise standard digital awareness."
        return "No immediate fraud indicators were detected. Stay vigilant and never share passwords or authentication PINs."

    @staticmethod
    def _empty_result():
        return {
            "verdict": "Empty",
            "status": "NO_INPUT",
            "risk_score": None,
            "status_color": "gray",
            "icon": "ℹ️",
            "user_message": "Please paste a message, enter a URL, or upload a screenshot to start analysis.",
            "reasons": ["No message, URL, or screenshot was provided for analysis."],
            "safety_tips": ["Paste a message, enter a URL, or upload a screenshot to get started."],
            "signals": [],
            "details": {"has_text": False, "has_url": False, "has_ocr": False},
        }

    @staticmethod
    def _ocr_failed_result():
        return {
            "verdict": "UNKNOWN",
            "status": "OCR_FAILED",
            "risk_score": None,
            "status_color": "amber",
            "icon": "⚠️",
            "user_message": "Could not read clear text from the screenshot. Please paste the message text directly or try another clearer screenshot.",
            "reasons": ["OCR text extraction failed or image contained no readable text."],
            "safety_tips": [
                "Try uploading a clearer, higher-resolution screenshot.",
                "Copy and paste the message text directly into the text box.",
                "Ensure text is not blurry, skewed, or obstructed."
            ],
            "signals": [],
            "details": {"has_text": False, "has_url": False, "has_ocr": False, "ocr_failed": True},
        }

    @staticmethod
    def _model_unavailable_result():
        return {
            "verdict": "UNKNOWN",
            "status": "MODEL_UNAVAILABLE",
            "risk_score": None,
            "status_color": "gray",
            "icon": "⚙️",
            "user_message": "Analysis models are currently unavailable. Please verify model files and system setup.",
            "reasons": ["Machine learning model artifacts are missing or failed to initialize."],
            "safety_tips": ["Verify that trained models exist in the models directory."],
            "signals": [],
            "details": {"models_available": False},
        }

    @staticmethod
    def _default_reason(verdict: str) -> str:
        return {
            "Scam": "High correlation with documented digital fraud patterns.",
            "Suspicious": "Uncommon urgency or unverified source — proceed with vigilance.",
            "Safe": "No active fraud indicators or phishing attributes detected.",
            "UNKNOWN": "Assessment could not be determined due to incomplete or unreadable input.",
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
