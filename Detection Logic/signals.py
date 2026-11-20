"""
ScamLens - Member 2: Detection Logic & Indian Scam Rule Engine
Defines specialized detection rules for prevalent Indian digital scams:
- Fake KYC / Banking Suspension Threats
- UPI Collect & Fraudulent Refund Requests
- Parcel & Customs Extortion (Narcotics / Airport seizures)
- "Digital Arrest" & Law Enforcement Impersonation (CBI, ED, Cyber Cell)
- Part-Time Job / Task / Telegram Work Scams
- Electricity & Utility Disconnection Threats
- Phishing Domain Blocklist & Typosquatting Analysis
- OCR Text Extraction from Screenshot Uploads
"""

import os
import re
from urllib.parse import urlparse
from typing import List, Dict, Any, Optional

# Pre-compiled high-risk Indian scam rules & indicators

# 1. Fake KYC & Banking Alerts
FAKE_KYC_PATTERNS = [
    re.compile(r'\b(?:yono|sbi|hdfc|icici|axis|pnb|bob|kotak|paytm|airtel)\b.*\b(?:kyc|pan|aadhaar|debit card|netbanking|wallet)\b.*\b(?:blocked|suspended|deactivated|expire[ds]?|locked|update|verify|verify immediately|on hold|hold)\b', re.IGNORECASE),
    re.compile(r'\b(?:update|complete|verify)\s*(?:your)?\s*(?:kyc|pan card|aadhaar)\b', re.IGNORECASE),
    re.compile(r'\byour\s*(?:account|card|sim|wallet|balance)\s*(?:has been|will be|is)\s*(?:blocked|suspended|terminated|deactivated|put on hold|on hold)\b', re.IGNORECASE),
    re.compile(r'\b(?:submit|upload)\s*(?:your)?\s*(?:pan|aadhaar|documents)\s*(?:immediately|here)\b', re.IGNORECASE),
    re.compile(r'\b(?:kyc\s*(?:is\s*)?expired|wallet balance.*put on hold)\b', re.IGNORECASE),
]

# 2. UPI Collect & PIN Fraud Patterns
UPI_COLLECT_PATTERNS = [
    re.compile(r'\b(?:upi collect|collect request|pay request|payment request)\b', re.IGNORECASE),
    re.compile(r'\b(?:enter|put|type)\s*(?:your)?\s*(?:upi pin|mpin|pin)\s*(?:to receive|to accept|to claim|to credit|for receiving)\b', re.IGNORECASE),
    re.compile(r'\b(?:cashback|refund|lottery|reward|bonus)\s*(?:of|worth)?\s*(?:rs\.?|inr|₹)?\s*\d+.*\b(?:click|claim|receive)\b', re.IGNORECASE),
    re.compile(r'\b(?:receive money|claim money|get refund)\s*(?:click|enter pin)\b', re.IGNORECASE),
]

# 3. Parcel, Customs & Airport Extortion
PARCEL_CUSTOMS_PATTERNS = [
    re.compile(r'\b(?:fedex|dhl|india post|blue dart|courier|parcel|package)\b.*\b(?:held|seized|detained|stopped|customs|customs duty|penalty|drugs|passport)\b', re.IGNORECASE),
    re.compile(r'\b(?:illegal items|narcotics|contraband|drugs|unauthorized goods)\s*(?:found in|sent to|in your parcel)\b', re.IGNORECASE),
    re.compile(r'\b(?:clearance fee|customs duty|release charge|unpaid tax)\s*(?:required|needed|pay now)\b', re.IGNORECASE),
]

# 4. Digital Arrest & Law Enforcement Impersonation
DIGITAL_ARREST_PATTERNS = [
    re.compile(r'\b(?:digital arrest|digital warrant|arrest warrant|non-bailable warrant|nbw)\b', re.IGNORECASE),
    re.compile(r'\b(?:delhi police|mumbai police|cyber crime branch|cbi|ncb|ed|enforcement directorate|supreme court|trai)\b.*\b(?:investigation|money laundering|fir|crime|arrest)\b', re.IGNORECASE),
    re.compile(r'\b(?:skype|whatsapp video|video call|surveillance)\s*(?:interrogation|investigation|statement|hearing)\b', re.IGNORECASE),
    re.compile(r'\b(?:transfer funds|rbi verification account|security deposit|clear your name)\b', re.IGNORECASE),
]

# 5. Part-time Job & Task Scams
JOB_SCAM_PATTERNS = [
    re.compile(r'\b(?:part-time job|part-time|work from home|online job|online part-time|earn from home|earn rs|daily income|hiring online|assistants)\b.*\b(?:earn|salary|daily|per day|telegram|rs per day|paid instantly)\b', re.IGNORECASE),
    re.compile(r'\b(?:like youtube videos|subscribe channels|rate hotels|google maps review)\b', re.IGNORECASE),
    re.compile(r'\b(?:telegram\s*@|join telegram|contact hr on telegram|whatsapp hr|telegram vip|t\.me/)\b', re.IGNORECASE),
    re.compile(r'\b(?:recharge task|prepaid task|deposit to unlock|bonus withdrawal|task india)\b', re.IGNORECASE),
]

# 6. Electricity & Utility Bill Threats
ELECTRICITY_BILL_PATTERNS = [
    re.compile(r'\b(?:electricity|power|power supply|bijli)\s*(?:will be|is)\s*(?:disconnected|cut off|terminated|suspended)\b', re.IGNORECASE),
    re.compile(r'\b(?:previous month|last month)?\s*(?:bill was not updated|unpaid bill|pending bill)\b', re.IGNORECASE),
    re.compile(r'\b(?:contact|call)\s*(?:our)?\s*(?:electricity officer|officer|manager|executive)\s*(?:at|on|number)?\s*\d{10}\b', re.IGNORECASE),
    re.compile(r'\b(?:update your bill|pay immediately)\s*(?:to avoid disconnection|before 9:30 pm|tonight)\b', re.IGNORECASE),
]

# 7. High-Urgency & Coercion Markers
URGENCY_PATTERNS = [
    re.compile(r'\b(?:immediately|urgent|within 24 hours|within 2 hours|tonight|before \d+(?::\d+)?\s*(?:pm|am)?|final notice|immediate action)\b', re.IGNORECASE),
    re.compile(r'\b(?:account suspended|legal action will be taken|action will be taken|punishable offense)\b', re.IGNORECASE),
]

# 8. Malicious App & APK Download Triggers
MALICIOUS_APP_PATTERNS = [
    re.compile(r'\b(?:download|install|open)\s*(?:the\s*)?(?:app|apk|application)\s*(?:from|at)?\s*(?:http[s]?://|\.apk)\b', re.IGNORECASE),
    re.compile(r'\.apk\b', re.IGNORECASE),
    re.compile(r'\b(?:anydesk|teamviewer|rustdesk|quicksupport|quick\s*support)\b', re.IGNORECASE),
]

# Benign Legitimate Transaction Patterns (for whitelist / false positive reduction)
BENIGN_TRANSACTION_PATTERNS = [
    re.compile(r'\b(?:debited|credited)\s*(?:by|with)?\s*(?:rs\.?|inr|₹)?\s*\d+.*(?:a/c|acct|account).*(?:bal|avail bal|balance)\b', re.IGNORECASE),
    re.compile(r'\botp\b.*\b(?:is|code is)\s*\d{4,8}\b.*\b(?:valid for|never share|do not share)\b', re.IGNORECASE),
    re.compile(r'\bnever share (?:your)?\s*otp\b', re.IGNORECASE),
    re.compile(r'\bdo not (?:disclose|share) (?:to|with) anyone\b', re.IGNORECASE),
    re.compile(r'\bpnr\s*\d{10}\b', re.IGNORECASE),
    re.compile(r'\b(?:out for delivery|delivered)\b.*\b(?:order|package|delivery partner)\b', re.IGNORECASE),
]

# Known Phishing Blocklist (Abused domains, spoofed brands, malicious patterns)
PHISHING_BLOCKLIST = {
    # Fake SBI / YONO
    'sbi-kyc-verify.top', 'sbi-update.site', 'yonosbi-login.online', 'sbi-reward-points.xyz',
    'sbi-pan-link.info', 'onlinesbi-verification.buzz',
    # Fake HDFC / ICICI / Axis
    'hdfc-card-unlock.xyz', 'hdfc-netbanking-verify.top', 'icici-kyc-update.site',
    'axis-card-reward.online', 'kotak-kyc-service.club',
    # Fake Utility / Electricity
    'electricity-bill-disconnection-alert.fit', 'bijli-bill-payment.site',
    'state-power-update.online', 'bses-bill-portal.top',
    # Fake Courier / Customs
    'fedex-customs-clearance.top', 'dhl-express-parcel.site', 'indiapost-track-fee.xyz',
    # Fake Telecom / SIM KYC
    'jio-sim-kyc.top', 'airtel-5g-upgrade.site', 'vi-sim-verification.online',
    # Fake Job / Crypto portals
    'parttime-task-reward.top', 'telegram-tasks-mall.vip', 'global-crypto-recharge.site'
}

# Plain-language explanations mapped to each threat type (Member 4 UI ready)
EXPLANATION_CATALOG = {
    "fake_kyc": "Urges you to complete KYC, PAN, or account updates to prevent immediate bank account or card suspension.",
    "upi_collect": "Deceptively asks you to enter your UPI PIN to 'receive' money or claims. (Remember: UPI PIN is ONLY needed to SEND money, never to receive).",
    "parcel_customs": "Falsely claims an intercepted parcel containing illegal drugs or passports at an airport, demanding clearance fees.",
    "digital_arrest": "Extorts money by falsely impersonating police, CBI, or judges, threatening illegal 'digital arrest' or video interrogations.",
    "job_scam": "Promises high daily income for trivial online tasks (liking YouTube videos, reviewing places), leading to financial recharge traps.",
    "electricity_bill": "Threatens immediate power disconnection tonight and pressures you to call an unofficial mobile number.",
    "urgency": "Employs high-pressure urgency tactics ('immediately', 'tonight', 'before 9:30 PM') to bypass critical thinking.",
    "malicious_apk": "Prompts direct download of an unverified Android APK or remote access application (AnyDesk / RustDesk).",
    "phishing_domain": "Directs to an unverified phishing domain masquerading as an authentic institution.",
    "untrusted_tld": "Uses a cheap, high-risk top-level domain (.top, .xyz, .site, .fit) commonly associated with transient fraud rings.",
    "ip_address_host": "Points directly to an IP address instead of an authenticated, verified domain name.",
}


class ScamSignalDetector:
    """
    Indian Scam Signal Detector (Member 2 Engine).
    Scans text and URLs for domain-specific Indian cybercrime patterns,
    assigns signal confidence weights, and returns plain-language explanations.
    """

    def __init__(self):
        self.blocklist = PHISHING_BLOCKLIST
        self.url_regex = re.compile(
            r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.(?:com|in|org|net|xyz|top|site|app|link|cc|co|info|biz|club|fit|online|vip)[^\s]*',
            re.IGNORECASE
        )

    def extract_urls(self, text: str) -> List[str]:
        """Extracts all URLs and domain-like substrings from text."""
        if not text:
            return []
        matches = self.url_regex.findall(str(text))
        cleaned_urls = []
        for match in matches:
            # Strip trailing punctuation
            clean = match.rstrip(".,;!?'\")>]")
            if clean:
                cleaned_urls.append(clean)
        return cleaned_urls

    def evaluate_rules(self, text: str) -> Dict[str, Any]:
        """
        Evaluates input text against all Indian scam patterns.
        Returns triggered signals, confidence score (0-100), and explanations.
        """
        if not text or not str(text).strip():
            return {
                "triggered_signals": [],
                "rule_risk_score": 0,
                "explanations": [],
                "is_benign_transaction": False
            }

        raw_text = str(text)
        lower_text = raw_text.lower()
        triggered_signals = []
        explanations = []

        # Check for genuine benign transactional markers
        is_benign = any(p.search(raw_text) for p in BENIGN_TRANSACTION_PATTERNS)

        # 1. Fake KYC
        if any(p.search(raw_text) for p in FAKE_KYC_PATTERNS):
            triggered_signals.append("fake_kyc")
            explanations.append(EXPLANATION_CATALOG["fake_kyc"])

        # 2. UPI Collect
        if any(p.search(raw_text) for p in UPI_COLLECT_PATTERNS):
            triggered_signals.append("upi_collect")
            explanations.append(EXPLANATION_CATALOG["upi_collect"])

        # 3. Parcel / Customs
        if any(p.search(raw_text) for p in PARCEL_CUSTOMS_PATTERNS):
            triggered_signals.append("parcel_customs")
            explanations.append(EXPLANATION_CATALOG["parcel_customs"])

        # 4. Digital Arrest
        if any(p.search(raw_text) for p in DIGITAL_ARREST_PATTERNS):
            triggered_signals.append("digital_arrest")
            explanations.append(EXPLANATION_CATALOG["digital_arrest"])

        # 5. Job / Task Scam
        if any(p.search(raw_text) for p in JOB_SCAM_PATTERNS):
            triggered_signals.append("job_scam")
            explanations.append(EXPLANATION_CATALOG["job_scam"])

        # 6. Electricity Bill
        if any(p.search(raw_text) for p in ELECTRICITY_BILL_PATTERNS):
            triggered_signals.append("electricity_bill")
            explanations.append(EXPLANATION_CATALOG["electricity_bill"])

        # 7. Urgency / Coercion
        if any(p.search(raw_text) for p in URGENCY_PATTERNS):
            triggered_signals.append("urgency")
            explanations.append(EXPLANATION_CATALOG["urgency"])

        # 8. Malicious APK or Remote Support App
        if any(p.search(raw_text) for p in MALICIOUS_APP_PATTERNS):
            triggered_signals.append("malicious_apk")
            explanations.append(EXPLANATION_CATALOG["malicious_apk"])

        # Calculate rule risk score
        # Major scam categories have high baseline weights
        major_signals = {"fake_kyc", "upi_collect", "parcel_customs", "digital_arrest", "job_scam", "electricity_bill"}
        triggered_majors = [s for s in triggered_signals if s in major_signals]

        if triggered_majors:
            # If any major scam signal triggers, base score starts at 75
            rule_score = 75 + (len(triggered_majors) - 1) * 10
            if "urgency" in triggered_signals:
                rule_score += 10
            if "malicious_apk" in triggered_signals:
                rule_score += 15
            rule_score = min(rule_score, 100)
        elif "urgency" in triggered_signals or "malicious_apk" in triggered_signals:
            rule_score = 50
        elif is_benign:
            rule_score = 5
        else:
            rule_score = 15

        # If benign indicators are strong and NO major scam signals triggered
        if is_benign and not triggered_majors:
            rule_score = min(rule_score, 10)

        return {
            "triggered_signals": triggered_signals,
            "rule_risk_score": rule_score,
            "explanations": explanations,
            "is_benign_transaction": is_benign
        }

    def check_url(self, url: str) -> Dict[str, Any]:
        """
        Inspects URL for blocklist presence, suspicious domain markers, and TLD abuse.
        """
        if not url:
            return {"is_blocked": False, "url_risk_score": 0, "explanations": []}

        clean_url = str(url).strip()
        if not (clean_url.startswith('http://') or clean_url.startswith('https://')):
            target = 'http://' + clean_url
        else:
            target = clean_url

        try:
            parsed = urlparse(target)
            domain = parsed.netloc.lower()
            if ':' in domain:
                domain = domain.split(':')[0]
            path = parsed.path.lower()
        except Exception:
            domain = clean_url.split('/')[0].lower()
            path = ""

        explanations = []
        is_blocked = False
        url_score = 10

        # Check exact or subdomain blocklist match
        if any(domain == b or domain.endswith('.' + b) for b in self.blocklist):
            is_blocked = True
            url_score = 98
            explanations.append(f"Domain '{domain}' is listed on the verified active fraud & phishing blocklist.")

        # Check for IP address domain
        ip_pattern = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
        if ip_pattern.match(domain):
            url_score = max(url_score, 90)
            explanations.append(EXPLANATION_CATALOG["ip_address_host"])

        # Check for suspicious TLDs
        tld = domain.split('.')[-1] if '.' in domain else ''
        if tld in {'top', 'xyz', 'click', 'site', 'fit', 'link', 'club', 'work', 'buzz', 'vip', 'online', 'rest'}:
            url_score = max(url_score, 75)
            explanations.append(f"Uses an untrusted high-risk top-level domain (.{tld}).")

        # Check for APK or EXE executable download in path
        if path.endswith('.apk') or '.apk?' in target or path.endswith('.exe'):
            url_score = max(url_score, 90)
            explanations.append("Directly initiates an untrusted APK application package download.")

        # Check for spoofed brands in non-official domains
        official_domains = {
            'sbi.co.in', 'onlinesbi.sbi', 'onlinesbi.com', 'hdfcbank.com', 
            'icicibank.com', 'axisbank.com', 'paytm.com', 'phonepe.com', 
            'google.com', 'amazon.in', 'flipkart.com', 'cybercrime.gov.in',
            'incometax.gov.in', 'uidai.gov.in', 'irctc.co.in'
        }
        is_official = any(domain == off or domain.endswith('.' + off) for off in official_domains)
        if not is_official:
            for brand in ['sbi', 'hdfc', 'icici', 'axis', 'paytm', 'phonepe', 'yono', 'rbi', 'income-tax']:
                if brand in domain:
                    url_score = max(url_score, 88)
                    explanations.append(f"Impersonates official brand '{brand.upper()}' on an unauthorized third-party domain.")
                    break

        return {
            "domain": domain,
            "is_blocked": is_blocked,
            "url_risk_score": url_score,
            "explanations": explanations
        }


def extract_text_from_image(image_file_or_bytes) -> str:
    """
    Extracts text from uploaded screenshot using OCR (pytesseract or fallback).
    Resilient to environments without external tesseract installation.
    """
    try:
        import pytesseract
        from PIL import Image
        import io

        if isinstance(image_file_or_bytes, bytes):
            image = Image.open(io.BytesIO(image_file_or_bytes))
        elif hasattr(image_file_or_bytes, 'read'):
            image = Image.open(image_file_or_bytes)
        else:
            image = Image.open(image_file_or_bytes)

        # Attempt OCR
        extracted_text = pytesseract.image_to_string(image)
        if extracted_text and extracted_text.strip():
            return extracted_text.strip()
    except Exception as e:
        # Fallback if tesseract binary is not installed on the system
        pass

    return ""
