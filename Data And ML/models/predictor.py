"""
ScamLens Predictor API (Inference Engine)
Provides high-level, human-explainable inference for:
- Member 2 (Detection logic in signals.py & eval_cases.py)
- Member 3 (Integration in app.py & analyze() function)
- Member 4 (UI/UX states, risk meters, and plain-language explanations)
"""
import os
import re
import joblib
import numpy as np

# Import preprocessing helpers
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from text_preprocessor import TextPreprocessor
from feature_extraction import URLFeatureExtractor, SUSPICIOUS_TLDS, SENSITIVE_KEYWORDS, OFFICIAL_TRUSTED_DOMAINS


# Standard legitimate transaction patterns
BENIGN_TRANSACTION_PATTERNS = [
    re.compile(r'\b(?:debited|credited)\b.*\b(?:bal|balance)\b', re.IGNORECASE),
    re.compile(r'\bpnr\s*\d+\b', re.IGNORECASE),
    re.compile(r'\bout for delivery\b', re.IGNORECASE),
    re.compile(r'\bnever share (?:your )?otp\b', re.IGNORECASE),
    re.compile(r'\bdo not (?:disclose|share) (?:to anyone|with anyone)\b', re.IGNORECASE),
    re.compile(r'\bdelivered\. thank you for shopping\b', re.IGNORECASE)
]


class ScamLensPredictor:
    """
    Unified ML Predictor for ScamLens.
    Loads trained text and URL models, computes risk scores (0-100%),
    and generates plain-language explainability summaries.
    """
    
    def __init__(self, models_dir: str = None):
        if models_dir is None:
            models_dir = os.path.join(BASE_DIR, "models")
            
        self.models_dir = models_dir
        self.text_model_path = os.path.join(models_dir, "text_model.joblib")
        self.url_model_path = os.path.join(models_dir, "url_model.joblib")
        
        self.preprocessor = TextPreprocessor()
        self.url_extractor = URLFeatureExtractor()
        
        self.text_model = None
        self.url_model = None
        self._load_models()

    def _load_models(self):
        """Loads serialized models from disk."""
        if os.path.exists(self.text_model_path):
            self.text_model = joblib.load(self.text_model_path)
        else:
            print(f"[!] Warning: Text model not found at {self.text_model_path}. Run train.py first.")
            
        if os.path.exists(self.url_model_path):
            bundle = joblib.load(self.url_model_path)
            self.url_model = bundle.get("model", bundle)
        else:
            print(f"[!] Warning: URL model not found at {self.url_model_path}. Run train.py first.")

    def predict_text(self, text: str) -> dict:
        """
        Analyzes message text and returns risk assessment, probability,
        and human-interpretable signals.
        """
        if not text or not str(text).strip():
            return {
                "input_type": "text",
                "verdict": "Safe",
                "status_color": "green",
                "icon": "✅",
                "risk_score": 0,
                "confidence": 1.0,
                "reasons": ["No text content provided."],
                "detected_keywords": []
            }
            
        cleaned = self.preprocessor.clean_text(text)
        metadata = self.preprocessor.extract_metadata_features(text)
        lower_raw = text.lower()
        
        # Check benign transaction patterns
        is_known_benign_transaction = any(p.search(lower_raw) for p in BENIGN_TRANSACTION_PATTERNS)
        
        # Check high-risk fraud trigger terms
        has_fraud_threat = any(term in lower_raw for term in [
            "disconnected", "power will be disconnected", "arrest warrant", 
            "digital arrest", "narcotics", "cbi", "part-time work", "earn rs",
            "telegram @", "upi collect", "unlock your card", "pending kyc",
            "freeze", "suspended", "customs fee", "unpaid bill call"
        ])

        # ML Model Probability
        if self.text_model is not None:
            probs = self.text_model.predict_proba([cleaned])[0]
            scam_prob = float(probs[1])
        else:
            scam_prob = 0.5
            
        # Calibrate: If genuine transaction markers are present and NO fraud threat phrases exist
        if is_known_benign_transaction and not has_fraud_threat:
            scam_prob = min(scam_prob, 0.15)
            
        risk_score = int(round(scam_prob * 100))
        
        # Plain-language reasons & keyword detection
        reasons = []
        found_keywords = [kw for kw in SENSITIVE_KEYWORDS if kw in lower_raw]
        
        if has_fraud_threat:
            if "otp" in lower_raw or "pin" in lower_raw or "upi" in lower_raw:
                reasons.append("Requests or mentions sensitive authentication credentials (OTP / PIN / UPI).")
            if "kyc" in lower_raw or "pan card" in lower_raw or "aadhaar" in lower_raw:
                reasons.append("Claims pending KYC, PAN, or Aadhaar verification.")
            if "power" in lower_raw or "electricity" in lower_raw or "disconnected" in lower_raw:
                reasons.append("Pressures you with immediate electricity disconnection threats.")
            if "cbi" in lower_raw or "police" in lower_raw or "arrest" in lower_raw or "customs" in lower_raw:
                reasons.append("Uses impersonation of law enforcement, customs, or court arrest warrants (Digital Arrest).")
            if "part-time" in lower_raw or "part time" in lower_raw or "telegram" in lower_raw or "earn rs" in lower_raw:
                reasons.append("Promotes unrealistic work-from-home or social media task earnings.")
        
        if metadata.get("caps_ratio", 0) > 0.35:
            reasons.append("Excessive uppercase lettering used to convey artificial panic.")
            
        if risk_score >= 70:
            verdict = "Scam"
            status_color = "red"
            icon = "🚨"
            if not reasons:
                reasons.append("Text structure and vocabulary closely match known fraud campaigns.")
        elif risk_score >= 40:
            verdict = "Suspicious"
            status_color = "amber"
            icon = "⚠️"
            if not reasons:
                reasons.append("Message contains unsolicited promotional urgency or unusual formatting.")
        else:
            verdict = "Safe"
            status_color = "green"
            icon = "✅"
            if is_known_benign_transaction:
                reasons = ["Legitimate transactional or service communication pattern verified."]
            else:
                reasons = ["Message shows normal conversational or standard service notification patterns."]

        return {
            "input_type": "text",
            "verdict": verdict,
            "status_color": status_color,
            "icon": icon,
            "risk_score": risk_score,
            "confidence": round(float(max(scam_prob, 1.0 - scam_prob)), 3),
            "reasons": reasons,
            "detected_keywords": found_keywords,
            "metadata": metadata
        }

    def predict_url(self, url: str) -> dict:
        """
        Analyzes a URL and returns phishing probability, verdict,
        and structural explanations.
        """
        if not url or not str(url).strip():
            return {
                "input_type": "url",
                "verdict": "Safe",
                "status_color": "green",
                "icon": "✅",
                "risk_score": 0,
                "confidence": 1.0,
                "reasons": ["No URL provided."],
                "flags": {}
            }
            
        clean_url = str(url).strip()
        features_dict = self.url_extractor.extract_dict(clean_url)
        vector = [features_dict[name] for name in self.url_extractor.feature_names]
        
        # Check if officially verified domain
        domain = clean_url.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0].lower()
        is_official = self.url_extractor.is_official_trusted_domain(domain)

        # ML Model Probability
        if is_official and not features_dict.get("has_sensitive_extension"):
            phish_prob = 0.02
        elif self.url_model is not None:
            probs = self.url_model.predict_proba([vector])[0]
            phish_prob = float(probs[1])
        else:
            phish_prob = 0.5
            
        risk_score = int(round(phish_prob * 100))
        
        # Explanations from extracted features
        reasons = []
        if features_dict.get("is_ip_address"):
            reasons.append("Uses a numeric IP address directly instead of a verified domain name.")
        if features_dict.get("has_suspicious_tld"):
            reasons.append("Registered under an untrusted, high-risk top-level domain (TLD).")
        if features_dict.get("has_sensitive_extension"):
            reasons.append("Links directly to an untrusted executable or package (.apk/.exe).")
        if features_dict.get("brand_in_subdomain_or_path"):
            reasons.append("Spoofs a trusted banking or government brand inside an unofficial domain.")
        if features_dict.get("sensitive_keyword_count", 0) >= 2:
            reasons.append("URL contains multiple security/credential collection keywords.")
        if not features_dict.get("is_https"):
            reasons.append("Unencrypted connection (HTTP instead of secure HTTPS).")
            
        if risk_score >= 70:
            verdict = "Scam"
            status_color = "red"
            icon = "🚨"
            if not reasons:
                reasons.append("URL structure matches known phishing kit patterns.")
        elif risk_score >= 40:
            verdict = "Suspicious"
            status_color = "amber"
            icon = "⚠️"
            if not reasons:
                reasons.append("Uncommon domain structure; proceed with caution.")
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
            "confidence": round(float(max(phish_prob, 1.0 - phish_prob)), 3),
            "reasons": reasons,
            "features": features_dict
        }

    def predict_combined(self, text: str = None, url: str = None) -> dict:
        """
        Combines text and URL inputs into a unified risk assessment.
        Directly powers Member 3's app.py analyze() endpoint.
        """
        text_res = self.predict_text(text) if text else None
        url_res = self.predict_url(url) if url else None
        
        # If text contains a URL that wasn't separately entered, extract it
        if text and not url:
            extracted_urls = self.preprocessor.url_pattern.findall(text)
            if extracted_urls:
                url_res = self.predict_url(extracted_urls[0])
                
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
            return {
                "verdict": "Safe",
                "risk_score": 0,
                "status_color": "green",
                "icon": "✅",
                "reasons": ["No input provided."],
                "safety_tips": []
            }

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
            "reasons": combined_reasons,
            "safety_tips": safety_tips,
            "text_analysis": text_res,
            "url_analysis": url_res
        }
