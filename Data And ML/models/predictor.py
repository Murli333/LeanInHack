"""
ScamLens Predictor API (Inference Engine) - Member 1: Data & ML
Provides high-level, human-explainable inference for:
- Member 2 (Detection logic in signals.py & eval_cases.py)
- Member 3 (Integration in app.py & analyze() / scoring.py)
- Member 4 (UI/UX states, risk meters, and plain-language explanations)

Upgrades in v2.1.0:
- [P0] Fixed empty/missing input handling: returns verdict='Unknown', is_empty=True (never defaults to Safe)
- [P1] Distinct raw_ml_score vs calibrated risk_score
- [P1] Model versioning and metadata inspection
- [P1] Explicit confidence and uncertainty quantification (ambiguity bands)
- [P1] Local explainability: token-level and structural feature attribution
- [P2] Graceful heuristic fallback mode when model files are missing
"""
import os
import re
import joblib
import numpy as np
from typing import Dict, Any, List, Optional

# Import preprocessing & feature extraction helpers
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from text_preprocessor import TextPreprocessor
from feature_extraction import (
    URLFeatureExtractor, SUSPICIOUS_TLDS, SENSITIVE_KEYWORDS,
    OFFICIAL_TRUSTED_DOMAINS, SHORTENER_DOMAINS
)


# Standard legitimate transaction patterns (verified Indian transactional SMS headers)
BENIGN_TRANSACTION_PATTERNS = [
    re.compile(r'\b(?:debited|credited)\b.*\b(?:bal|balance)\b', re.IGNORECASE),
    re.compile(r'\bpnr\s*\d+\b', re.IGNORECASE),
    re.compile(r'\bout for delivery\b', re.IGNORECASE),
    re.compile(r'\bnever share (?:your )?otp\b', re.IGNORECASE),
    re.compile(r'\bdo not (?:disclose|share) (?:to anyone|with anyone)\b', re.IGNORECASE),
    re.compile(r'\bdelivered\. thank you for shopping\b', re.IGNORECASE),
    re.compile(r'\bacct?\s*(?:ending|xx|\.\.\.)\s*\d+\b', re.IGNORECASE),
    re.compile(r'\bbill\b.*?(?:rs|inr|₹)\s*\d+.*?\bdue\s*(?:on|date|by)\b', re.IGNORECASE),
    re.compile(r'\b(?:unique identification authority of india|uidai)\b', re.IGNORECASE),
    re.compile(r'\botp\b.*?\bvalid for \d+ (?:mins?|minutes?)\b', re.IGNORECASE)
]

# High-threat Indian fraud patterns
FRAUD_THREAT_PATTERNS = [
    "disconnected", "power will be disconnected", "arrest warrant", 
    "digital arrest", "narcotics", "cbi", "part-time work", "earn rs",
    "telegram @", "upi collect", "unlock your card", "pending kyc",
    "freeze", "suspended", "customs fee", "unpaid bill call",
    "redelivery fee", "sim upgrade", "lucky draw", "claim prize",
    "kbc", "aapka account band"
]


class ScamLensPredictor:
    """
    Unified ML Predictor for ScamLens.
    Loads trained text and URL models, computes calibrated risk scores (0-100%),
    and generates plain-language explainability summaries.
    """
    
    def __init__(self, models_dir: Optional[str] = None):
        if models_dir is None:
            models_dir = os.path.join(BASE_DIR, "models")
            
        self.models_dir = models_dir
        self.text_model_path = os.path.join(models_dir, "text_model.joblib")
        self.url_model_path = os.path.join(models_dir, "url_model.joblib")
        
        self.preprocessor = TextPreprocessor()
        self.url_extractor = URLFeatureExtractor()
        
        self.text_model = None
        self.text_metadata = {}
        self.url_model = None
        self.url_metadata = {}
        self.url_feature_names = self.url_extractor.feature_names
        self.url_feature_importances = []
        
        self._load_models()

    def _load_models(self):
        """Loads serialized models from disk with fallback protection."""
        if os.path.exists(self.text_model_path):
            try:
                loaded = joblib.load(self.text_model_path)
                if isinstance(loaded, dict):
                    self.text_model = loaded.get("pipeline", loaded.get("model", loaded))
                    self.text_metadata = loaded.get("metadata", {})
                else:
                    self.text_model = loaded
                    self.text_metadata = {"model_type": "Pipeline", "version": "2.1.0"}
            except Exception as e:
                print(f"[!] Warning: Failed loading text model ({e}). Using heuristic fallback.")
                self.text_model = None
        else:
            print(f"[!] Notice: Text model not found at {self.text_model_path}. Fallback active.")
            self.text_model = None
            
        if os.path.exists(self.url_model_path):
            try:
                bundle = joblib.load(self.url_model_path)
                if isinstance(bundle, dict):
                    self.url_model = bundle.get("model", bundle)
                    self.url_metadata = bundle.get("metadata", {})
                    self.url_feature_names = bundle.get("feature_names", self.url_extractor.feature_names)
                    self.url_feature_importances = bundle.get("feature_importances", [])
                else:
                    self.url_model = bundle
                    self.url_metadata = {"model_type": "Model", "version": "2.1.0"}
            except Exception as e:
                print(f"[!] Warning: Failed loading URL model ({e}). Using heuristic fallback.")
                self.url_model = None
        else:
            print(f"[!] Notice: URL model not found at {self.url_model_path}. Fallback active.")
            self.url_model = None

    def get_model_metadata(self) -> Dict[str, Any]:
        """Returns version and configuration metadata of loaded models."""
        return {
            "text_model_loaded": self.text_model is not None,
            "text_model_version": self.text_metadata.get("version", "unknown"),
            "url_model_loaded": self.url_model is not None,
            "url_model_version": self.url_metadata.get("version", "unknown"),
            "engine_version": "2.1.0"
        }

    # =================================================================
    # 1. TEXT SCAM PREDICTION
    # =================================================================
    def predict_text(self, text: Optional[str]) -> Dict[str, Any]:
        """
        Analyzes message text and returns risk assessment, probability,
        and human-interpretable signals.
        """
        # [P0] Fix: Handle empty or whitespace-only inputs without defaulting to Safe
        if text is None or not str(text).strip():
            return {
                "input_type": "text",
                "verdict": "Unknown",
                "status_color": "gray",
                "icon": "❓",
                "risk_score": 0,
                "raw_ml_score": 0.0,
                "confidence": 0.0,
                "is_empty": True,
                "uncertainty": "High - No text provided for analysis",
                "reasons": ["No text content provided for analysis."],
                "detected_keywords": [],
                "contributing_signals": []
            }
            
        raw_text = str(text).strip()
        cleaned = self.preprocessor.clean_text(raw_text)
        metadata = self.preprocessor.extract_metadata_features(raw_text)
        lower_raw = raw_text.lower()
        
        # Check benign transaction patterns
        is_known_benign = any(p.search(lower_raw) for p in BENIGN_TRANSACTION_PATTERNS)
        
        # Check high-risk fraud triggers
        has_fraud_threat = any(term in lower_raw for term in FRAUD_THREAT_PATTERNS)
        
        is_fallback = False
        # ML Inference or Heuristic Fallback
        if self.text_model is not None:
            try:
                probs = self.text_model.predict_proba([cleaned])[0]
                raw_ml_prob = float(probs[1])
            except Exception:
                raw_ml_prob = 0.5
                is_fallback = True
        else:
            is_fallback = True
            # Heuristic calculation if model is unavailable
            raw_ml_prob = 0.85 if has_fraud_threat else (0.05 if is_known_benign else 0.30)
            
        scam_prob = raw_ml_prob
        
        # Benign transaction calibration: If verified transactional pattern with no threats
        if is_known_benign and not has_fraud_threat:
            scam_prob = min(scam_prob, 0.12)
        elif has_fraud_threat and scam_prob < 0.65:
            scam_prob = max(scam_prob, 0.75)
            
        # Check if text contains only markers or numbers without semantic scam context
        raw_words = [w for w in cleaned.split() if w not in [
            'phonemarker', 'codemarker', 'currencymarker', 'urlmarker', 
            'exclmarker', 'qmarkmarker', 'hindimarker'
        ]]
        if not raw_words and not has_fraud_threat:
            # Only phone numbers or numeric codes with no fraud language
            scam_prob = min(scam_prob, 0.45)
            
        risk_score = int(round(scam_prob * 100))
        
        # Quantify confidence and uncertainty
        confidence = round(float(max(scam_prob, 1.0 - scam_prob)), 3)
        if 0.40 <= scam_prob <= 0.60:
            uncertainty = "High - Ambiguous semantic indicators"
        elif 0.30 <= scam_prob <= 0.70:
            uncertainty = "Medium - Moderate semantic indicators"
        else:
            uncertainty = "Low - High confidence classification"

        # Local Explainability: Identify triggering words & phrases
        reasons = []
        found_keywords = [kw for kw in SENSITIVE_KEYWORDS if kw in lower_raw]
        contributing_signals = []
        
        if has_fraud_threat:
            if any(k in lower_raw for k in ["otp", "pin", "upi", "enter upi pin"]):
                reasons.append("Requests or mentions sensitive authentication credentials (OTP / PIN / UPI).")
                contributing_signals.append("credential_request")
            if any(k in lower_raw for k in ["kyc", "pan card", "aadhaar", "pan"]):
                reasons.append("Claims pending KYC, PAN, or Aadhaar deactivation.")
                contributing_signals.append("kyc_threat")
            if any(k in lower_raw for k in ["power", "electricity", "disconnected", "bill unpaid"]):
                reasons.append("Pressures you with immediate electricity disconnection threats.")
                contributing_signals.append("utility_disconnection")
            if any(k in lower_raw for k in ["cbi", "police", "arrest", "customs", "narcotics"]):
                reasons.append("Uses impersonation of law enforcement or fake arrest warrants (Digital Arrest).")
                contributing_signals.append("law_enforcement_impersonation")
            if any(k in lower_raw for k in ["part-time", "part time", "telegram", "earn rs", "liking youtube"]):
                reasons.append("Promotes unrealistic work-from-home or social media task earnings.")
                contributing_signals.append("task_job_scam")
            if any(k in lower_raw for k in ["lucky draw", "lottery", "kbc", "won rs"]):
                reasons.append("Unsolicited lottery or prize winnings claim.")
                contributing_signals.append("lottery_fraud")
                
        if metadata.get("caps_ratio", 0) > 0.35:
            reasons.append("Excessive uppercase lettering used to convey artificial panic.")
            contributing_signals.append("panic_typography")
            
        if metadata.get("emoji_scam_count", 0) >= 2:
            reasons.append("Uses deceptive celebratory/urgent emojis common in fraud campaigns.")
            contributing_signals.append("emoji_bait")
            
        if metadata.get("has_obfuscated_terms"):
            reasons.append("Contains intentionally obfuscated or spaced scam keywords to evade filters.")
            contributing_signals.append("obfuscation_evasion")

        if is_fallback:
            reasons.append("[Note: Running in rule-based heuristic fallback mode]")

        # Determine Verdict
        if risk_score >= 70:
            verdict = "Scam"
            status_color = "red"
            icon = "🚨"
            if not reasons:
                reasons.append("Text structure and vocabulary match known cybercrime fraud campaigns.")
        elif risk_score >= 40:
            verdict = "Suspicious"
            status_color = "amber"
            icon = "⚠️"
            if not reasons:
                reasons.append("Message contains unsolicited urgency or unfamiliar sender patterns.")
        else:
            verdict = "Safe"
            status_color = "green"
            icon = "✅"
            if is_known_benign:
                reasons = ["Legitimate transactional or service communication pattern verified."]
            else:
                reasons = ["Message shows normal conversational or standard service notification patterns."]

        return {
            "input_type": "text",
            "verdict": verdict,
            "status_color": status_color,
            "icon": icon,
            "risk_score": risk_score,
            "raw_ml_score": round(raw_ml_prob, 4),
            "confidence": confidence,
            "uncertainty": uncertainty,
            "is_empty": False,
            "is_fallback": is_fallback,
            "reasons": reasons,
            "detected_keywords": found_keywords,
            "contributing_signals": contributing_signals,
            "metadata": metadata
        }

    # =================================================================
    # 2. URL PHISHING PREDICTION
    # =================================================================
    def predict_url(self, url: Optional[str]) -> Dict[str, Any]:
        """
        Analyzes a URL and returns phishing probability, verdict,
        and structural explanations.
        """
        # [P0] Fix: Handle empty or whitespace-only inputs without defaulting to Safe
        if url is None or not str(url).strip():
            return {
                "input_type": "url",
                "verdict": "Unknown",
                "status_color": "gray",
                "icon": "❓",
                "risk_score": 0,
                "raw_ml_score": 0.0,
                "confidence": 0.0,
                "is_empty": True,
                "uncertainty": "High - No URL provided for analysis",
                "reasons": ["No URL provided for analysis."],
                "flags": {}
            }
            
        clean_url = str(url).strip()
        features_dict = self.url_extractor.extract_dict(clean_url)
        vector = [features_dict[name] for name in self.url_feature_names]
        
        # Check if officially verified domain
        domain = clean_url.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0].lower()
        is_official = self.url_extractor.is_official_trusted_domain(domain)
        
        is_fallback = False
        if is_official and not features_dict.get("has_sensitive_extension"):
            phish_prob = 0.02
        elif self.url_model is not None:
            try:
                probs = self.url_model.predict_proba([vector])[0]
                phish_prob = float(probs[1])
            except Exception:
                phish_prob = 0.5
                is_fallback = True
        else:
            is_fallback = True
            # Heuristic calculation if model file is missing
            score = 0.10
            if features_dict.get("is_ip_address"): score += 0.40
            if features_dict.get("has_suspicious_tld"): score += 0.35
            if features_dict.get("has_sensitive_extension"): score += 0.40
            if features_dict.get("brand_in_subdomain_or_path"): score += 0.35
            if features_dict.get("is_shortened_url"): score += 0.25
            phish_prob = min(0.98, score)

        risk_score = int(round(phish_prob * 100))
        confidence = round(float(max(phish_prob, 1.0 - phish_prob)), 3)
        
        if 0.40 <= phish_prob <= 0.60:
            uncertainty = "High - Ambiguous structural indicators"
        elif 0.30 <= phish_prob <= 0.70:
            uncertainty = "Medium - Moderate structural indicators"
        else:
            uncertainty = "Low - High confidence classification"

        # Structural Explainability
        reasons = []
        if features_dict.get("is_ip_address"):
            reasons.append("Uses a raw numeric IP address instead of a registered domain name.")
        if features_dict.get("has_suspicious_tld"):
            reasons.append("Registered under a high-risk, untrusted top-level domain (TLD).")
        if features_dict.get("has_sensitive_extension"):
            reasons.append("Directly downloads an executable or package (.apk/.exe) bypassing app stores.")
        if features_dict.get("brand_in_subdomain_or_path"):
            reasons.append("Spoofs a trusted banking, government, or retail brand inside an unofficial domain.")
        if features_dict.get("is_shortened_url"):
            reasons.append("Uses a link-shortening service (bit.ly/tinyurl) to obscure the true destination.")
        if features_dict.get("has_non_standard_port"):
            reasons.append("Connects via a non-standard TCP port commonly used by rogue web servers.")
        if features_dict.get("has_double_slash_path"):
            reasons.append("Contains path redirection characters (//) intended to bypass URL validation.")
        if features_dict.get("is_punycode"):
            reasons.append("Uses Punycode (IDN homograph) encoding to visually mimic legitimate domains.")
        if features_dict.get("sensitive_keyword_count", 0) >= 2:
            reasons.append("URL contains multiple credential harvesting keywords.")
        if not features_dict.get("is_https"):
            reasons.append("Unencrypted connection (HTTP instead of secure HTTPS).")

        if is_fallback:
            reasons.append("[Note: Running in rule-based heuristic fallback mode]")

        # Determine Verdict
        if risk_score >= 70:
            verdict = "Scam"
            status_color = "red"
            icon = "🚨"
            if not reasons:
                reasons.append("URL structure matches verified phishing kit fingerprints.")
        elif risk_score >= 40:
            verdict = "Suspicious"
            status_color = "amber"
            icon = "⚠️"
            if not reasons:
                reasons.append("Unusual domain structure; verify sender before proceeding.")
        else:
            verdict = "Safe"
            status_color = "green"
            icon = "✅"
            reasons = ["Domain matches verified, legitimate conventions."]

        return {
            "input_type": "url",
            "url": clean_url,
            "verdict": verdict,
            "status_color": status_color,
            "icon": icon,
            "risk_score": risk_score,
            "raw_ml_score": round(phish_prob, 4),
            "confidence": confidence,
            "uncertainty": uncertainty,
            "is_empty": False,
            "is_fallback": is_fallback,
            "reasons": reasons,
            "features": features_dict
        }

    # =================================================================
    # 3. COMBINED MULTIMODAL INFERENCE
    # =================================================================
    def predict_combined(self, text: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Combines text and URL inputs into a unified risk assessment.
        Directly powers Member 3's app.py analyze() endpoint and scoring.py.
        """
        has_text = text is not None and bool(str(text).strip())
        has_url = url is not None and bool(str(url).strip())
        
        # [P0] Fix: Handle empty inputs properly
        if not has_text and not has_url:
            return {
                "verdict": "Unknown",
                "status_color": "gray",
                "icon": "❓",
                "risk_score": 0,
                "is_empty": True,
                "uncertainty": "High - No input provided for analysis",
                "reasons": ["No message text or URL provided for analysis."],
                "safety_tips": [
                    "Paste a suspicious message, phone number, or URL to begin investigation."
                ]
            }

        text_res = self.predict_text(text) if has_text else None
        url_res = self.predict_url(url) if has_url else None
        
        # Auto-extract embedded URLs from message text if no separate URL was supplied
        if has_text and not has_url:
            extracted_urls = self.preprocessor.url_pattern.findall(text)
            if extracted_urls:
                # Evaluate all embedded links and surface the most malicious URL
                url_evals = [self.predict_url(u) for u in extracted_urls]
                url_res = max(url_evals, key=lambda r: r.get("risk_score", 0))
                
        if text_res and url_res:
            combined_score = int(round(0.45 * text_res["risk_score"] + 0.55 * url_res["risk_score"]))
            combined_reasons = list(dict.fromkeys(text_res["reasons"] + url_res["reasons"]))
        elif text_res:
            combined_score = text_res["risk_score"]
            combined_reasons = text_res["reasons"]
        elif url_res:
            combined_score = url_res["risk_score"]
            combined_reasons = url_res["reasons"]
        else:
            combined_score = 0
            combined_reasons = ["No valid input detected."]

        # Determine overall verdict
        if combined_score >= 70:
            verdict = "Scam"
            status_color = "red"
            icon = "🚨"
            safety_tips = [
                "Do NOT click any links, open APKs, or reply to this message.",
                "Never share your OTP, UPI PIN, or bank passwords with anyone.",
                "Report this immediately on the National Cyber Crime Reporting Portal at https://cybercrime.gov.in or call toll-free helpline 1930."
            ]
        elif combined_score >= 40:
            verdict = "Suspicious"
            status_color = "amber"
            icon = "⚠️"
            safety_tips = [
                "Verify independently via the official bank or service provider app before taking any action.",
                "Do not approve any UPI collect requests or transfer token booking amounts.",
                "Check sender identity carefully."
            ]
        else:
            verdict = "Safe"
            status_color = "green"
            icon = "✅"
            safety_tips = [
                "Message looks typical of normal communications.",
                "Always remember that genuine organizations will never ask for your PIN or password."
            ]

        return {
            "verdict": verdict,
            "status_color": status_color,
            "icon": icon,
            "risk_score": combined_score,
            "is_empty": False,
            "reasons": combined_reasons,
            "safety_tips": safety_tips,
            "text_analysis": text_res,
            "url_analysis": url_res
        }
