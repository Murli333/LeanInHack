"""
Text Preprocessor and Normalizer for ScamLens
Cleans and normalizes incoming SMS and message text for ML classification.
"""
import re
import string

class TextPreprocessor:
    """
    Normalizes SMS / message text while preserving fraud signals:
    - Normalizes phone numbers to <PHONE>
    - Normalizes URLs to <URL>
    - Normalizes amounts/currencies (Rs, INR, ₹, $) to <CURRENCY>
    - Normalizes OTP codes and numeric sequences to <CODE>
    - Preserves scam-heavy punctuation and case characteristics
    """
    
    def __init__(self):
        # Patterns for normalization
        self.url_pattern = re.compile(
            r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.(?:com|in|org|net|xyz|top|site|app|link|cc|co|info|biz|club)[^\s]*',
            re.IGNORECASE
        )
        self.phone_pattern = re.compile(
            r'(?:\+91[\-\s]?)?[6789]\d{9}|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            re.IGNORECASE
        )
        self.currency_pattern = re.compile(
            r'(?:Rs\.?|INR|₹|\$)\s*\d+(?:,\d+)*(?:\.\d+)?|\b\d+\s*(?:rupees|rs)\b',
            re.IGNORECASE
        )
        self.code_pattern = re.compile(
            r'\b\d{4,8}\b'
        )

    def extract_metadata_features(self, text: str) -> dict:
        """
        Extracts structural indicators before text stripping
        which are valuable for fraud detection.
        """
        text = str(text) if text else ""
        length = len(text)
        has_url = 1 if self.url_pattern.search(text) else 0
        has_phone = 1 if self.phone_pattern.search(text) else 0
        has_currency = 1 if self.currency_pattern.search(text) else 0
        caps_count = sum(1 for c in text if c.isupper())
        caps_ratio = (caps_count / length) if length > 0 else 0.0
        excl_count = text.count('!')
        qmark_count = text.count('?')
        
        return {
            "length": length,
            "has_url": has_url,
            "has_phone": has_phone,
            "has_currency": has_currency,
            "caps_ratio": round(caps_ratio, 3),
            "excl_count": excl_count,
            "qmark_count": qmark_count
        }

    def clean_text(self, text: str, preserve_signals: bool = True) -> str:
        """
        Cleans and tokenizes text for TF-IDF vectorization.
        """
        if not text or not isinstance(text, str):
            return ""
        
        cleaned = text.strip()
        
        if preserve_signals:
            # Replace URLs with marker
            cleaned = self.url_pattern.sub(' urlmarker ', cleaned)
            # Replace currency with marker
            cleaned = self.currency_pattern.sub(' currencymarker ', cleaned)
            # Replace phone numbers with marker
            cleaned = self.phone_pattern.sub(' phonemarker ', cleaned)
            # Replace generic multi-digit codes with marker
            cleaned = self.code_pattern.sub(' codemarker ', cleaned)
            
        # Lowercase
        cleaned = cleaned.lower()
        
        # Remove excess whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned


def preprocess_text(text: str) -> str:
    """Convenience function for pipeline integration"""
    preprocessor = TextPreprocessor()
    return preprocessor.clean_text(text)
