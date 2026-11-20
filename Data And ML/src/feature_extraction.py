"""
URL Feature Extractor for ScamLens
Extracts lexical, structural, and behavioral features from raw URLs.
"""
import re
import math
from urllib.parse import urlparse
import numpy as np

# High-risk TLDs frequently abused in phishing & scam campaigns
SUSPICIOUS_TLDS = {
    'top', 'xyz', 'click', 'site', 'fit', 'link', 'club', 'work', 
    'buzz', 'gq', 'cf', 'tk', 'ml', 'ga', 'online', 'vip', 'monster',
    'rest', 'stream', 'support', 'cam', 'icu', 'fun', 'win', 'bid'
}

# Scam / Phishing trigger keywords
SENSITIVE_KEYWORDS = [
    'login', 'signin', 'verify', 'verification', 'kyc', 'pan', 'aadhaar', 
    'bank', 'sbi', 'hdfc', 'icici', 'pnb', 'paytm', 'phonepe', 'gpay',
    'upi', 'update', 'security', 'secure', 'account', 'blocked', 'suspend',
    'reward', 'points', 'gift', 'bonus', 'claim', 'wallet', 'refund',
    'electricity', 'bill', 'disconnection', 'challan', 'customs', 'parcel',
    'apk', 'download', 'otp', 'pin', 'free', 'lottery', 'winner', 'loan'
]

# Trusted official domains mapping
OFFICIAL_TRUSTED_DOMAINS = {
    'sbi.co.in', 'onlinesbi.sbi', 'onlinesbi.com', 'hdfcbank.com', 
    'icicibank.com', 'axisbank.com', 'paytm.com', 'phonepe.com', 
    'google.com', 'google.co.in', 'gmail.com', 'microsoft.com', 
    'apple.com', 'amazon.in', 'amazon.com', 'flipkart.com', 
    'netflix.com', 'incometax.gov.in', 'uidai.gov.in', 
    'cybercrime.gov.in', 'digilocker.gov.in', 'irctc.co.in',
    'parivahan.gov.in', 'tatapower.com', 'bsesdelhi.com', 'rbi.org.in'
}

MAJOR_BRANDS = [
    'sbi', 'hdfc', 'icici', 'axisbank', 'paytm', 'phonepe', 
    'incometax', 'uidai', 'cybercrime', 'irctc', 'netflix'
]

IP_REGEX = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')


def calculate_entropy(text: str) -> float:
    """Calculates the Shannon entropy of a string."""
    if not text:
        return 0.0
    prob_dist = [float(text.count(c)) / len(text) for c in set(text)]
    return -sum(p * math.log2(p) for p in prob_dist)


class URLFeatureExtractor:
    """
    Extracts numerical features from a URL string for ML classification.
    """
    
    def __init__(self):
        self.feature_names = [
            'url_length',
            'domain_length',
            'path_length',
            'num_dots_url',
            'num_dots_domain',
            'num_hyphens_url',
            'num_hyphens_domain',
            'num_at_symbols',
            'num_question_marks',
            'num_equals',
            'num_percent',
            'num_slashes',
            'num_digits_url',
            'num_digits_domain',
            'digit_ratio_url',
            'is_https',
            'is_ip_address',
            'num_subdomains',
            'has_suspicious_tld',
            'has_sensitive_extension',
            'sensitive_keyword_count',
            'brand_in_subdomain_or_path',
            'domain_entropy',
            'url_entropy'
        ]

    def is_official_trusted_domain(self, domain: str) -> bool:
        """Checks if the domain is an authentic trusted domain."""
        domain = domain.lower()
        return any(domain == trusted or domain.endswith('.' + trusted) for trusted in OFFICIAL_TRUSTED_DOMAINS)

    def extract_dict(self, url: str) -> dict:
        """
        Extracts features as a dictionary.
        """
        raw_url = str(url).strip() if url else ""
        
        # Ensure scheme for urllib parsing
        if not (raw_url.startswith('http://') or raw_url.startswith('https://')):
            parse_target = 'http://' + raw_url
        else:
            parse_target = raw_url
            
        try:
            parsed = urlparse(parse_target)
            domain = parsed.netloc.lower()
            if ':' in domain:
                domain = domain.split(':')[0]
            path = parsed.path.lower()
            query = parsed.query.lower()
        except Exception:
            domain = raw_url.split('/')[0].lower()
            path = ""
            query = ""

        url_length = len(raw_url)
        domain_length = len(domain)
        path_length = len(path) + len(query)

        num_dots_url = raw_url.count('.')
        num_dots_domain = domain.count('.')
        num_hyphens_url = raw_url.count('-')
        num_hyphens_domain = domain.count('-')
        num_at_symbols = raw_url.count('@')
        num_question_marks = raw_url.count('?')
        num_equals = raw_url.count('=')
        num_percent = raw_url.count('%')
        num_slashes = raw_url.count('/')

        num_digits_url = sum(1 for c in raw_url if c.isdigit())
        num_digits_domain = sum(1 for c in domain if c.isdigit())
        digit_ratio_url = (num_digits_url / url_length) if url_length > 0 else 0.0

        is_https = 1 if raw_url.lower().startswith('https://') else 0
        is_ip_address = 1 if IP_REGEX.match(domain) else 0

        domain_parts = [p for p in domain.split('.') if p]
        num_subdomains = max(0, len(domain_parts) - 2) if not is_ip_address else 0

        tld = domain_parts[-1] if domain_parts else ""
        has_suspicious_tld = 1 if tld in SUSPICIOUS_TLDS else 0

        has_sensitive_extension = 1 if any(
            path.endswith(ext) or ext in query 
            for ext in ['.apk', '.exe', '.bat', '.scr', '.vbs', '.zip']
        ) else 0

        combined_text = (domain + ' ' + path + ' ' + query).lower()
        sensitive_keyword_count = sum(
            1 for kw in SENSITIVE_KEYWORDS if kw in combined_text
        )

        # Brand impersonation check:
        # Flag ONLY if the domain is NOT an official verified domain of that brand
        is_official = self.is_official_trusted_domain(domain)
        brand_in_subdomain_or_path = 0
        if not is_official:
            for brand in MAJOR_BRANDS:
                if re.search(r'\b' + re.escape(brand) + r'\b', combined_text) or (brand in domain):
                    brand_in_subdomain_or_path = 1
                    break

        domain_entropy = round(calculate_entropy(domain), 3)
        url_entropy = round(calculate_entropy(raw_url), 3)

        return {
            'url_length': url_length,
            'domain_length': domain_length,
            'path_length': path_length,
            'num_dots_url': num_dots_url,
            'num_dots_domain': num_dots_domain,
            'num_hyphens_url': num_hyphens_url,
            'num_hyphens_domain': num_hyphens_domain,
            'num_at_symbols': num_at_symbols,
            'num_question_marks': num_question_marks,
            'num_equals': num_equals,
            'num_percent': num_percent,
            'num_slashes': num_slashes,
            'num_digits_url': num_digits_url,
            'num_digits_domain': num_digits_domain,
            'digit_ratio_url': round(digit_ratio_url, 3),
            'is_https': is_https,
            'is_ip_address': is_ip_address,
            'num_subdomains': num_subdomains,
            'has_suspicious_tld': has_suspicious_tld,
            'has_sensitive_extension': has_sensitive_extension,
            'sensitive_keyword_count': sensitive_keyword_count,
            'brand_in_subdomain_or_path': brand_in_subdomain_or_path,
            'domain_entropy': domain_entropy,
            'url_entropy': url_entropy
        }

    def extract_vector(self, url: str) -> list:
        """Extracts feature vector in defined order."""
        features = self.extract_dict(url)
        return [features[name] for name in self.feature_names]

    def extract_matrix(self, urls: list) -> np.ndarray:
        """Extracts 2D feature matrix for list of URLs."""
        return np.array([self.extract_vector(u) for u in urls], dtype=float)
