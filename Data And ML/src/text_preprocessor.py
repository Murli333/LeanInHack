"""
Text Preprocessor and Normalizer for ScamLens
Cleans and normalizes incoming SMS and message text for ML classification.
Supports multilingual (Hindi/Hinglish), Unicode homoglyph normalization,
obfuscation detection, and fraud signal extraction.
"""
import re
import string
import unicodedata
from typing import Dict, Any, List

# Cyrillic and lookalike homoglyphs mapped to ASCII equivalents
HOMOGLYPH_MAP = {
    'а': 'a', 'А': 'A',
    'с': 'c', 'С': 'C',
    'е': 'e', 'Е': 'E',
    'о': 'o', 'О': 'O',
    'р': 'p', 'Р': 'P',
    'у': 'y', 'У': 'Y',
    'х': 'x', 'Х': 'X',
    'і': 'i', 'І': 'I',
    'ј': 'j', 'Ј': 'J',
    'ѕ': 's', 'Ѕ': 'S',
    'ԁ': 'd', 'Ԃ': 'D',
    'ԛ': 'q', 'Ԛ': 'Q',
    'ԝ': 'w', 'Ԝ': 'W'
}

# Zero-width and hidden formatting characters to strip
ZERO_WIDTH_CHARS = [
    '\u200b',  # zero-width space
    '\u200c',  # zero-width non-joiner
    '\u200d',  # zero-width joiner
    '\ufeff',  # zero-width no-break space (BOM)
    '\u200e',  # left-to-right mark
    '\u200f',  # right-to-left mark
    '\u00a0'   # non-breaking space -> space
]

# High-risk scam emoji signals
SCAM_EMOJI_PATTERN = re.compile(
    r'[\U0001F389\U0001F3C6\U0001F4B0\U0001F381\U0001F4B5\U0001F6A8\U000026A0\U0001F4B3\U0001F4B8\U0001F911]'
)

# Common Hinglish and Hindi scam indicator phrases
HINGLISH_SCAM_PATTERNS = [
    (re.compile(r'\baapka account (?:band|block|freeze)\b', re.IGNORECASE), "hindimarker_account_block"),
    (re.compile(r'\bturant (?:sampark|kare|call|update)\b', re.IGNORECASE), "hindimarker_urgency"),
    (re.compile(r'\botp (?:kisi ko na|bataye|share kare)\b', re.IGNORECASE), "hindimarker_otp"),
    (re.compile(r'\bbijli (?:ka )?connection kat\b', re.IGNORECASE), "hindimarker_electricity"),
    (re.compile(r'\binaam (?:jeeta|mila)\b', re.IGNORECASE), "hindimarker_lottery"),
    (re.compile(r'\bpaise (?:kamaye|milenge|transfer)\b', re.IGNORECASE), "hindimarker_money"),
    (re.compile(r'\bjaldi se jaldi\b', re.IGNORECASE), "hindimarker_urgency"),
    (re.compile(r'\bgift voucher mila hai\b', re.IGNORECASE), "hindimarker_lottery"),
    (re.compile(r'\bghar baithe paise\b', re.IGNORECASE), "hindimarker_job")
]

# Obfuscated term regex replacements
OBFUSCATION_RULES = [
    (re.compile(r'\bf[\s\._\-*]+r[\s\._\-*]+e[\s\._\-*]+e\b', re.IGNORECASE), "free"),
    (re.compile(r'\bw[\s\._\-*]*[1!][\s\._\-*]*n\b', re.IGNORECASE), "win"),
    (re.compile(r'\bl[\s\._\-*]*[o0@][\s\._\-*]*[a@][\s\._\-*]*n\b', re.IGNORECASE), "loan"),
    (re.compile(r'\bk[\s\._\-*]+y[\s\._\-*]+c\b', re.IGNORECASE), "kyc"),
    (re.compile(r'\bo[\s\._\-*]+t[\s\._\-*]+p\b', re.IGNORECASE), "otp"),
    (re.compile(r'\bp[\s\._\-*]*[!1][\s\._\-*]*n\b', re.IGNORECASE), "pin"),
    (re.compile(r'\bp[\s\._\-*]*[@a][\s\._\-*]*y\b', re.IGNORECASE), "pay"),
    (re.compile(r'\bc[\s\._\-*]*[@a][\s\._\-*]*[\$s][\s\._\-*]*h\b', re.IGNORECASE), "cash"),
    (re.compile(r'\bb[\s\._\-*]*[@a][\s\._\-*]*n[\s\._\-*]*k\b', re.IGNORECASE), "bank"),
    (re.compile(r'\bu[\s\._\-*]+p[\s\._\-*]+i\b', re.IGNORECASE), "upi")
]


class TextPreprocessor:
    """
    Normalizes SMS / message text while preserving and highlighting fraud signals:
    - Normalizes URLs to 'urlmarker'
    - Normalizes phone numbers to 'phonemarker'
    - Normalizes amounts/currencies (Rs, INR, ₹, $) to 'currencymarker'
    - Normalizes OTP codes and numeric sequences to 'codemarker'
    - Handles Unicode homoglyphs and zero-width cloaking
    - Detects and de-obfuscates spaced or punctuated fraud terms
    - Identifies Hindi/Hinglish scam triggers
    - Measures structural metadata (capitalization, emojis, punctuation)
    """

    def __init__(self):
        # Patterns for entity normalization
        self.url_pattern = re.compile(
            r'https?://[^\s<>"]+|www\.[^\s<>"]+|[a-zA-Z0-9.-]+\.(?:com|in|org|net|xyz|top|site|app|link|cc|co|info|biz|club|work|buzz|vip|fit|click)[^\s<>"]*',
            re.IGNORECASE
        )
        self.phone_pattern = re.compile(
            r'(?:\+91[\-\s]?)?[6789]\d{9}|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            re.IGNORECASE
        )
        self.currency_pattern = re.compile(
            r'(?:Rs\.?|INR|₹|\$)\s*\d+(?:,\d+)*(?:\.\d+)?|\b\d+\s*(?:rupees|rs|lakh|crore)\b',
            re.IGNORECASE
        )
        self.code_pattern = re.compile(
            r'\b\d{4,8}\b'
        )

    def normalize_unicode_and_homoglyphs(self, text: str) -> str:
        """
        Strips invisible characters and normalizes Unicode homoglyphs (e.g. Cyrillic spoofing).
        """
        if not text:
            return ""
        # Strip zero-width and cloaking characters
        for ch in ZERO_WIDTH_CHARS:
            text = text.replace(ch, " " if ch == '\u00a0' else "")

        # Decompose unicode into compatibility form (NFKD)
        normalized = unicodedata.normalize('NFKD', text)

        # Replace known Cyrillic lookalikes
        chars = []
        for ch in normalized:
            if ch in HOMOGLYPH_MAP:
                chars.append(HOMOGLYPH_MAP[ch])
            else:
                chars.append(ch)
        return "".join(chars)

    def deobfuscate_terms(self, text: str) -> tuple[str, bool]:
        """
        De-obfuscates trick spellings like 'f r e e', 'w1n', 'lo@n', 'K Y C'.
        Returns (deobfuscated_text, had_obfuscation).
        """
        had_obfuscation = False
        result = text
        for pattern, replacement in OBFUSCATION_RULES:
            if pattern.search(result):
                had_obfuscation = True
                result = pattern.sub(replacement, result)
        return result, had_obfuscation

    def extract_metadata_features(self, text: str) -> Dict[str, Any]:
        """
        Extracts structural and behavioral indicators before text normalization,
        which serve as strong statistical features for fraud heuristics.
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

        # Emoji signals
        emoji_matches = SCAM_EMOJI_PATTERN.findall(text)
        emoji_scam_count = len(emoji_matches)

        # Hindi/Hinglish indicators
        has_hindi = 0
        for pattern, _ in HINGLISH_SCAM_PATTERNS:
            if pattern.search(text):
                has_hindi = 1
                break

        # Check obfuscated terms
        _, has_obfuscation = self.deobfuscate_terms(text)

        return {
            "length": length,
            "has_url": has_url,
            "has_phone": has_phone,
            "has_currency": has_currency,
            "caps_ratio": round(caps_ratio, 3),
            "excl_count": excl_count,
            "qmark_count": qmark_count,
            "emoji_scam_count": emoji_scam_count,
            "has_hindi_text": has_hindi,
            "has_obfuscated_terms": 1 if has_obfuscation else 0
        }

    def clean_text(self, text: str, preserve_signals: bool = True) -> str:
        """
        Cleans and tokenizes text for TF-IDF vectorization and NLP inference.
        """
        if not text or not isinstance(text, str):
            return ""

        # 1. Normalize Unicode and homoglyphs
        cleaned = self.normalize_unicode_and_homoglyphs(text.strip())

        # 2. De-obfuscate masked terms (fr.ee -> free, K Y C -> kyc)
        cleaned, _ = self.deobfuscate_terms(cleaned)

        # 3. Detect and insert Hinglish fraud markers
        for pattern, marker in HINGLISH_SCAM_PATTERNS:
            cleaned = pattern.sub(f' {marker} ', cleaned)

        if preserve_signals:
            # Replace URLs with marker
            cleaned = self.url_pattern.sub(' urlmarker ', cleaned)
            # Replace currency amounts with marker
            cleaned = self.currency_pattern.sub(' currencymarker ', cleaned)
            # Replace phone numbers with marker
            cleaned = self.phone_pattern.sub(' phonemarker ', cleaned)
            # Replace generic multi-digit codes with marker
            cleaned = self.code_pattern.sub(' codemarker ', cleaned)

        # 4. Lowercase
        cleaned = cleaned.lower()

        # 5. Remove excess punctuation but keep markers intact
        # Clean multiple punctuation repetitions
        cleaned = re.sub(r'[!]{2,}', ' exclmarker ', cleaned)
        cleaned = re.sub(r'[\?]{2,}', ' qmarkmarker ', cleaned)

        # 6. Collapse excess whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned


def preprocess_text(text: str) -> str:
    """Convenience function for pipeline integration."""
    preprocessor = TextPreprocessor()
    return preprocessor.clean_text(text)
