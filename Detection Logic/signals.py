"""
ScamLens - signals.py
Member 2: Detection Logic & Test Set

Heuristic scam signal detection engine for Indian cybercrime patterns.
Covers: Fake KYC, UPI Collect Requests, Parcel/Customs threats,
Digital Arrest, Job Scams, Electricity Bill threats, and more.

Each signal returns a dict with:
  - triggered (bool): Whether the signal fired
  - signal_id (str): Internal identifier
  - scam_type (str): Human-readable category
  - severity (int): 1 (low) to 3 (high)
  - explanation (str): Plain-language explanation for the UI
  - recommendation (str): What the user should do
"""

import re
from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# PHISHING BLOCKLIST
# Known malicious domains confirmed in Indian scam campaigns
# ---------------------------------------------------------------------------

PHISHING_BLOCKLIST = {
    # Fake KYC / Banking phishing
    "sbi-kyc-verify.top", "sbikyc-update.xyz", "sbi-netbanking.site",
    "hdfc-kyc-verify.com", "hdfc-netbanking.site", "icici-verify.top",
    "paytm-kyc-update.xyz", "upi-reward-claim.top", "phonepe-cashback.xyz",
    "aadhaar-link-verify.site", "pancard-link.top", "kyc-verified-india.top",
    # Electricity / Utility scams
    "electricity-bill-pay.xyz", "bses-bill-update.top", "tatapower-pay.site",
    "discom-pay-portal.top", "electric-officer-portal.xyz",
    # Parcel / Customs scams
    "customs-clearance-india.top", "fedex-india-customs.xyz",
    "dhl-parcel-verify.top", "india-post-parcel.xyz", "parcel-track-india.site",
    # Job / Task scams
    "work-from-home-tasks.xyz", "youtube-like-earn.top", "daily-task-earn.site",
    "telegram-task-earn.xyz", "parttime-job-india.top",
    # Digital Arrest / Agency impersonation
    "cbi-cybercell.xyz", "cyber-police-india.top", "ed-enforcement.site",
    "delhi-police-cybercrime.xyz", "narcotics-control-india.top",
    # Generic phishing kits
    "secure-login-india.xyz", "account-verify-now.top", "otp-verify.site",
    "india-gov-portal.xyz", "india-kyc-portal.top",
}

# ---------------------------------------------------------------------------
# TRUSTED DOMAIN ALLOWLIST
# These domains are always safe and must NOT trigger any scam signal
# ---------------------------------------------------------------------------

TRUSTED_DOMAINS = {
    "sbi.co.in", "onlinesbi.sbi", "onlinesbi.com",
    "hdfcbank.com", "icicibank.com", "axisbank.com", "kotak.com",
    "paytm.com", "phonepe.com", "gpay.com", "bhimupi.org.in",
    "google.com", "google.co.in", "gmail.com",
    "microsoft.com", "apple.com",
    "amazon.in", "amazon.com", "flipkart.com", "myntra.com", "nykaa.com",
    "irctc.co.in", "indianrailways.gov.in",
    "uidai.gov.in", "incometax.gov.in", "mca.gov.in",
    "cybercrime.gov.in", "digilocker.gov.in", "parivahan.gov.in",
    "tatapower.com", "bsesdelhi.com", "bsesdl.co.in", "rbi.org.in",
    "swiggy.com", "zomato.com", "ola.in", "uber.com",
    "naukri.com", "linkedin.com", "indeed.com",
    "npci.org.in", "nach.co.in",
}


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def _extract_urls(text: str) -> List[str]:
    """Extract all URLs from a message."""
    pattern = re.compile(
        r'https?://[^\s]+|www\.[^\s]+|'
        r'[a-zA-Z0-9.\-]+\.(?:top|xyz|site|click|link|fun|win|bid|'
        r'cam|icu|club|work|buzz|gq|cf|tk|ml|ga|online|vip|monster)[^\s]*',
        re.IGNORECASE
    )
    return pattern.findall(text)


def _extract_domain(url: str) -> str:
    """Extract the registrable domain from a URL string."""
    # Remove scheme
    domain = re.sub(r'^https?://', '', url, flags=re.IGNORECASE)
    # Remove path
    domain = domain.split('/')[0].lower()
    # Remove port
    domain = domain.split(':')[0]
    return domain.strip()


def _is_blocklisted(url: str) -> bool:
    """Check if a URL's domain appears in the phishing blocklist."""
    domain = _extract_domain(url)
    # Direct match
    if domain in PHISHING_BLOCKLIST:
        return True
    # Subdomain match (e.g., login.sbi-kyc-verify.top)
    for blocked in PHISHING_BLOCKLIST:
        if domain.endswith('.' + blocked):
            return True
    return False


def _is_trusted(url: str) -> bool:
    """Check if a URL belongs to a known legitimate domain."""
    domain = _extract_domain(url)
    if domain in TRUSTED_DOMAINS:
        return True
    for trusted in TRUSTED_DOMAINS:
        if domain.endswith('.' + trusted):
            return True
    return False


def _normalize(text: str) -> str:
    """Lowercase and collapse whitespace for robust matching."""
    return re.sub(r'\s+', ' ', text.lower().strip())


# ---------------------------------------------------------------------------
# SIGNAL DEFINITIONS
# Each function returns a signal result dict or None if not triggered.
# ---------------------------------------------------------------------------

def signal_fake_kyc(text: str) -> Dict[str, Any]:
    """
    Detects fake KYC update scams targeting Indian bank customers.
    Fraudsters send urgent messages claiming accounts/SIMs will be blocked
    unless the user visits a phishing link to 'update' their KYC.
    """
    t = _normalize(text)
    patterns = [
        r'\bkyc\b.{0,60}(update|verify|expire|block|suspend|pending|complete)',
        r'(update|verify|complete).{0,60}\bkyc\b',
        r'(account|sim|debit card|atm|mobile).{0,40}(block|suspend|freeze).{0,40}kyc',
        r'kyc.{0,30}(link|click|visit|download)',
        r'(pending|incomplete|expired).{0,20}kyc',
        r'\bkyc\b.{0,30}(apk|app|download)',
        r'your (bank|sbi|hdfc|icici|paytm|phonepe).{0,30}(kyc|account).{0,40}(block|expire|suspend)',
        r'aadhaar.{0,30}(link|update|verify).{0,30}(bank|account|sim)',
    ]
    for p in patterns:
        if re.search(p, t):
            return {
                "triggered": True,
                "signal_id": "FAKE_KYC",
                "scam_type": "Fake KYC Update",
                "severity": 3,
                "explanation": (
                    "This message is pressuring you to update your KYC (Know Your Customer) details "
                    "urgently. Scammers send these to trick you into visiting a fake bank website "
                    "where they steal your login details, Aadhaar number, or install malware."
                ),
                "recommendation": (
                    "Do NOT click any link or download any app from this message. "
                    "If you need to update KYC, visit your bank's official website directly "
                    "(e.g., sbi.co.in) or visit your nearest branch in person."
                ),
            }
    return {"triggered": False, "signal_id": "FAKE_KYC"}


def signal_upi_collect_request(text: str) -> Dict[str, Any]:
    """
    Detects UPI collect request fraud.
    Scammers send a UPI 'collect' (debit) request disguised as a 'credit',
    fooling victims into entering their UPI PIN to 'receive' money, when
    in fact they are approving a payment to the scammer.
    """
    t = _normalize(text)
    patterns = [
        r'upi.{0,30}collect.{0,30}(request|rs|inr|rupee)',
        r'(collect|receive|cashback|refund|prize|reward|lottery).{0,40}(upi|pin)',
        r'(enter|approve|accept).{0,30}(upi|pin).{0,30}(receive|get|claim|money)',
        r'upi.{0,20}(pin|mpin).{0,30}(receive|credit|cashback|refund)',
        r'(accept|approve).{0,20}(collect request|payment request)',
        r'(prize|lottery|cashback|reward|winner).{0,50}(upi|gpay|phonepe|paytm)',
        r'(google pay|phonepe|paytm|bhim).{0,40}(collect|request)',
        r'scan.{0,20}(qr|code).{0,30}(receive|get|claim)',
    ]
    for p in patterns:
        if re.search(p, t):
            return {
                "triggered": True,
                "signal_id": "UPI_COLLECT_REQUEST",
                "scam_type": "UPI Collect Request Fraud",
                "severity": 3,
                "explanation": (
                    "This message is asking you to enter your UPI PIN to 'receive' money. "
                    "This is a classic scam — entering your UPI PIN does NOT receive money, "
                    "it APPROVES a payment FROM your account to the scammer."
                ),
                "recommendation": (
                    "NEVER enter your UPI PIN to receive money. "
                    "To receive a payment via UPI, you do not need to enter any PIN. "
                    "Report this fraud to NPCI at https://npci.org.in or call 1800-120-1740."
                ),
            }
    return {"triggered": False, "signal_id": "UPI_COLLECT_REQUEST"}


def signal_parcel_customs_threat(text: str) -> Dict[str, Any]:
    """
    Detects parcel/customs scams where fraudsters impersonate courier companies
    (FedEx, DHL, India Post) or customs officers and claim a package
    has been seized or held, demanding a 'customs clearance fee'.
    """
    t = _normalize(text)
    patterns = [
        r'(parcel|package|consignment|shipment).{0,60}(seize|hold|customs|illegal|arrest)',
        r'(customs|clearance).{0,40}(fee|charge|pay|fine|duty)',
        r'(fedex|dhl|india post|bluedart|dtdc).{0,50}(customs|seized|illegal|narcotics)',
        r'(narcotics|drugs|contraband).{0,40}(parcel|package|name|found)',
        r'(clearance|release).{0,30}(fee|charge|penalty).{0,30}(parcel|package)',
        r'your (parcel|package).{0,40}(contain|hold|seized|arrest)',
        r'(airport|customs officer).{0,40}(parcel|package|contact|call)',
        r'(courier|delivery).{0,30}(illegal|seized|customs|duty|charge)',
    ]
    for p in patterns:
        if re.search(p, t):
            return {
                "triggered": True,
                "signal_id": "PARCEL_CUSTOMS_THREAT",
                "scam_type": "Parcel / Customs Scam",
                "severity": 3,
                "explanation": (
                    "This message claims a package in your name was seized by customs or contains "
                    "illegal items. Scammers impersonate courier companies (FedEx, DHL) or customs "
                    "officers to extort a 'clearance fee' from you, or scare you into revealing "
                    "personal information."
                ),
                "recommendation": (
                    "Do not pay any fee or call any number in this message. "
                    "Contact the courier company directly using the number on their official website. "
                    "Report to Cyber Crime helpline 1930 or https://cybercrime.gov.in."
                ),
            }
    return {"triggered": False, "signal_id": "PARCEL_CUSTOMS_THREAT"}


def signal_digital_arrest(text: str) -> Dict[str, Any]:
    """
    Detects 'digital arrest' scams — a uniquely Indian cybercrime where
    fraudsters impersonate CBI, ED, Delhi Police, Narcotics Bureau, or Customs
    and place victims under a fake 'digital arrest' via video call, threatening
    immediate arrest unless money is transferred.
    """
    t = _normalize(text)
    patterns = [
        r'digital arrest',
        r'(cbi|enforcement directorate|ed|narcotics bureau|ncb).{0,50}(arrest|warrant|case|notice)',
        r'(arrest warrant|fir|case registered).{0,40}(your name|against you)',
        r'(cyber crime|cybercell|cyber police).{0,30}(arrest|notice|warrant|call|officer)',
        r'(stay on|remain on|video call).{0,40}(arrested|custody|officer|police)',
        r'(skype|whatsapp|video).{0,30}(officer|police|cbi|arrest)',
        r'(money laundering|hawala|illegal transaction).{0,40}(your (name|account|number))',
        r'(sealed|freeze).{0,20}(account|assets).{0,30}(court|order|officer)',
        r'(aadhaar|pan card).{0,30}(misuse|fraud|case|crime)',
        r'(stay at home|do not leave).{0,30}(arrest|custody|case)',
        r'officer.{0,20}(badge|id).{0,20}(verify|genuine|authentic)',
    ]
    for p in patterns:
        if re.search(p, t):
            return {
                "triggered": True,
                "signal_id": "DIGITAL_ARREST",
                "scam_type": "Digital Arrest / Agency Impersonation",
                "severity": 3,
                "explanation": (
                    "This message is impersonating a government agency (like CBI, Police, or ED) "
                    "and threatening you with arrest. This is called a 'Digital Arrest' scam — "
                    "one of India's most dangerous cybercrime types. No real government agency "
                    "ever arrests you via phone/video call or demands money to avoid arrest."
                ),
                "recommendation": (
                    "Hang up immediately and do not transfer any money. "
                    "Real government agencies send official written notices, not WhatsApp messages. "
                    "Report this immediately on the National Cyber Crime Reporting Portal at "
                    "https://cybercrime.gov.in or call 1930."
                ),
            }
    return {"triggered": False, "signal_id": "DIGITAL_ARREST"}


def signal_job_offer_scam(text: str) -> Dict[str, Any]:
    """
    Detects part-time job / task-based scams promising high daily earnings
    for simple tasks like liking YouTube videos, rating Google Maps, or
    clicking ads — ultimately requiring an advance fee deposit.
    """
    t = _normalize(text)
    patterns = [
        r'(part.?time|work from home|wfh).{0,50}(earn|income|daily|task)',
        r'(earn|income).{0,20}(rs|inr|₹)?.{0,10}\d{3,5}.{0,20}(daily|per day|day)',
        r'(like|liking).{0,30}(youtube|video|post|instagram).{0,30}(earn|money|task)',
        r'(rate|rating).{0,30}(google|maps|app|review).{0,30}(earn|money|task)',
        r'(telegram|whatsapp).{0,30}(task|job|work|earn|group|channel)',
        r'(simple|easy|basic).{0,20}(task|job|work).{0,30}(earn|money|income)',
        r'(join|contact|message).{0,20}(telegram|whatsapp).{0,30}(earn|job|work)',
        r'(daily earning|daily income).{0,30}(guaranteed|fixed|assured)',
        r'(no experience|no qualification|fresher).{0,40}(earn|job|work|income)',
        r'(advance|deposit|registration fee).{0,40}(job|task|earn|work)',
        r'work.{0,20}home.{0,20}(₹|rs|inr).?\d+',
        r'(youtube|instagram|facebook).{0,20}(like|subscribe|follow).{0,20}(earn|paid|money)',
    ]
    for p in patterns:
        if re.search(p, t):
            return {
                "triggered": True,
                "signal_id": "JOB_OFFER_SCAM",
                "scam_type": "Fake Job / Task Scam",
                "severity": 2,
                "explanation": (
                    "This message is offering suspiciously easy money for simple tasks like liking "
                    "YouTube videos or rating Google Maps. These are advance-fee scams — after a "
                    "few small payments, they will ask you to 'deposit' a large amount for 'higher "
                    "value tasks' or 'unlock earnings', and then disappear with your money."
                ),
                "recommendation": (
                    "No legitimate employer asks you to pay money upfront to receive a job or salary. "
                    "Block and report this number. Report the scam at https://cybercrime.gov.in."
                ),
            }
    return {"triggered": False, "signal_id": "JOB_OFFER_SCAM"}


def signal_electricity_bill_threat(text: str) -> Dict[str, Any]:
    """
    Detects electricity bill disconnection scam messages that threaten
    immediate power cutoff and direct victims to call a fake 'electricity officer'.
    """
    t = _normalize(text)
    patterns = [
        r'(electricity|electric|power|current).{0,50}(disconnect|disconnected|cut|cutoff)',
        r'(disconnect|cut).{0,30}(electricity|power|supply|connection).{0,30}(tonight|today|immediately|now)',
        r'(unpaid|pending|due|overdue).{0,30}(electricity|electric|bill)',
        r'(electricity|power|discom|bses|tata power).{0,40}(officer|helpline|contact|call)',
        r'(bill).{0,30}(electricity|electric).{0,30}(pay|payment|update)',
        r'(meter|unit).{0,30}(reading|update).{0,30}(block|suspend|disconnect)',
        r'(electricity officer|lineman|power officer).{0,30}(contact|call|immediately)',
        r'connection.{0,20}(disconnect|suspend|stop).{0,20}(due|pending|bill)',
        r'(last warning|final notice).{0,30}(electricity|power|bill)',
    ]
    for p in patterns:
        if re.search(p, t):
            # Allowlist: official communication patterns
            safe_patterns = [
                r'pay via official portal',
                r'(bsesdelhi\.com|tatapower\.com|cesc\.co\.in)',
                r'your (ca number|consumer number|account number).{0,20}(is|no\.)',
                r'due on \d{1,2}[-/]\w+',
            ]
            for sp in safe_patterns:
                if re.search(sp, t):
                    return {"triggered": False, "signal_id": "ELECTRICITY_BILL_THREAT"}
            return {
                "triggered": True,
                "signal_id": "ELECTRICITY_BILL_THREAT",
                "scam_type": "Electricity Bill Disconnection Scam",
                "severity": 3,
                "explanation": (
                    "This message threatens to cut your electricity supply and urges you to call "
                    "a number urgently. Scammers pretend to be electricity department officers and "
                    "collect money or remote access to your phone. Real electricity companies send "
                    "official bills and do not threaten immediate disconnection via SMS."
                ),
                "recommendation": (
                    "Do NOT call the number in this message. Check your actual bill on your DISCOM's "
                    "official website (e.g., bsesdelhi.com, tatapower.com). "
                    "Call the official customer care number on your electricity bill."
                ),
            }
    return {"triggered": False, "signal_id": "ELECTRICITY_BILL_THREAT"}


def signal_otp_phishing(text: str) -> Dict[str, Any]:
    """
    Detects messages that attempt to steal OTPs by either directly asking for
    them or creating urgency around OTP sharing.
    """
    t = _normalize(text)
    patterns = [
        r'share.{0,20}(otp|pin|password)',
        r'(give|send|tell|provide|enter).{0,20}(otp|one.?time.?password|pin)',
        r'otp.{0,30}(agent|officer|executive|representative)',
        r'(verify|confirm|validate).{0,20}otp.{0,20}(call|call us|agent)',
        r'(customer care|executive).{0,30}otp',
        r'(otp|pin).{0,20}(expire|expired|valid for).{0,20}(share|tell|give)',
    ]
    for p in patterns:
        if re.search(p, t):
            # Legitimate OTP messages warn you NOT to share
            if re.search(r'never share|do not share|do not disclose|not to share', t):
                return {"triggered": False, "signal_id": "OTP_PHISHING"}
            return {
                "triggered": True,
                "signal_id": "OTP_PHISHING",
                "scam_type": "OTP / PIN Phishing",
                "severity": 3,
                "explanation": (
                    "This message is asking you to share or enter your OTP or PIN with someone. "
                    "Legitimate banks and services NEVER ask for your OTP over a call, message, "
                    "or website that you didn't navigate to yourself. This is a direct attempt "
                    "to steal access to your bank account."
                ),
                "recommendation": (
                    "NEVER share your OTP with anyone — not even someone who claims to be from "
                    "your bank or the government. If you've already shared it, contact your bank "
                    "immediately to block your account."
                ),
            }
    return {"triggered": False, "signal_id": "OTP_PHISHING"}


def signal_loan_fraud(text: str) -> Dict[str, Any]:
    """
    Detects fake loan offers that require upfront 'processing fees',
    or loan app scams that trap users in debt traps.
    """
    t = _normalize(text)
    patterns = [
        r'(instant|quick|fast|immediate|guaranteed).{0,30}(loan|credit)',
        r'(loan).{0,30}(no document|without document|no cibil|bad cibil)',
        r'(processing fee|registration fee).{0,30}(loan|credit)',
        r'(pre.?approved|pre-approved).{0,20}loan',
        r'(personal loan|home loan|business loan).{0,40}(apply now|click|link|whatsapp)',
        r'(low interest|0%.{0,10}interest|no interest).{0,30}loan',
        r'(loan|credit).{0,30}(approved|sanctioned|disburse).{0,30}(click|link|apply)',
        r'(₹|rs|inr).?\d{4,}.{0,20}(loan|credit).{0,20}(instant|quick|fast)',
    ]
    for p in patterns:
        if re.search(p, t):
            return {
                "triggered": True,
                "signal_id": "LOAN_FRAUD",
                "scam_type": "Fake Loan Offer",
                "severity": 2,
                "explanation": (
                    "This message is offering a quick loan with unrealistic conditions "
                    "(no documents, guaranteed approval, low/zero interest). These are loan scams "
                    "that collect advance 'processing fees' and disappear, or install malicious apps "
                    "that blackmail you using your phone's contacts and photos."
                ),
                "recommendation": (
                    "Only apply for loans through your bank's official app or website. "
                    "Never pay any fee before receiving a loan. "
                    "Check if the lender is RBI-registered at https://rbi.org.in."
                ),
            }
    return {"triggered": False, "signal_id": "LOAN_FRAUD"}


def signal_phishing_url(text: str) -> Dict[str, Any]:
    """
    Checks all URLs in the message against the phishing blocklist
    and also flags suspicious URL patterns (suspicious TLDs, APK links, etc.).
    """
    urls = _extract_urls(text)
    if not urls:
        return {"triggered": False, "signal_id": "PHISHING_URL"}

    for url in urls:
        # Skip trusted domains
        if _is_trusted(url):
            continue

        domain = _extract_domain(url)

        # Blocklist check
        if _is_blocklisted(url):
            return {
                "triggered": True,
                "signal_id": "PHISHING_URL",
                "scam_type": "Known Phishing URL",
                "severity": 3,
                "url": url,
                "explanation": (
                    f"The link '{domain}' is on our list of known phishing websites used in "
                    "Indian scam campaigns. Visiting this link could steal your bank login, "
                    "install malware on your phone, or compromise your personal information."
                ),
                "recommendation": (
                    "Do NOT open this link. Delete this message immediately. "
                    "Report the link at https://cybercrime.gov.in."
                ),
            }

        # Suspicious TLD check
        suspicious_tlds = {
            'top', 'xyz', 'click', 'site', 'fit', 'link', 'club', 'work',
            'buzz', 'gq', 'cf', 'tk', 'ml', 'ga', 'online', 'vip', 'monster',
            'rest', 'stream', 'support', 'cam', 'icu', 'fun', 'win', 'bid'
        }
        tld = domain.split('.')[-1] if '.' in domain else ''
        if tld in suspicious_tlds:
            return {
                "triggered": True,
                "signal_id": "PHISHING_URL",
                "scam_type": "Suspicious URL (High-Risk Domain)",
                "severity": 2,
                "url": url,
                "explanation": (
                    f"The link uses a '.{tld}' domain extension which is very commonly used in "
                    "phishing and scam websites. Legitimate Indian banks and government services "
                    "use trusted extensions like '.gov.in', '.co.in', '.com', or '.in'."
                ),
                "recommendation": (
                    "Avoid clicking this link. If you need to access a service, navigate directly "
                    "to the official website by typing it in your browser."
                ),
            }

        # APK / dangerous file download
        if re.search(r'\.(apk|exe|bat|scr|vbs)', url, re.IGNORECASE):
            return {
                "triggered": True,
                "signal_id": "PHISHING_URL",
                "scam_type": "Malicious File Download Link",
                "severity": 3,
                "url": url,
                "explanation": (
                    "This link downloads a file (like an APK or EXE) that is likely malware. "
                    "Scammers send fake bank or KYC apps this way to gain full control of "
                    "your phone and steal your banking credentials."
                ),
                "recommendation": (
                    "NEVER install apps from links in messages. "
                    "Only install apps from the official Google Play Store or Apple App Store. "
                    "If you have already installed it, uninstall it immediately and factory reset "
                    "your device as a precaution."
                ),
            }

        # Brand impersonation in URL
        major_brands = ['sbi', 'hdfc', 'icici', 'paytm', 'phonepe', 'aadhaar',
                        'incometax', 'uidai', 'irctc', 'npci', 'rbi']
        for brand in major_brands:
            if brand in domain and not _is_trusted(url):
                return {
                    "triggered": True,
                    "signal_id": "PHISHING_URL",
                    "scam_type": "Brand Impersonation URL",
                    "severity": 3,
                    "url": url,
                    "explanation": (
                        f"The link appears to impersonate '{brand.upper()}' — a trusted Indian "
                        "bank or service — but it is NOT their official website. This is a fake "
                        "copy designed to steal your login credentials."
                    ),
                    "recommendation": (
                        f"The real '{brand.upper()}' website does NOT send links like this. "
                        "Always type the official URL directly in your browser. "
                        "Report this link at https://cybercrime.gov.in."
                    ),
                }

    return {"triggered": False, "signal_id": "PHISHING_URL"}


def signal_urgency_pressure(text: str) -> Dict[str, Any]:
    """
    Detects high-pressure urgency tactics used in social engineering,
    designed to prevent victims from thinking critically.
    """
    t = _normalize(text)
    urgency_phrases = [
        r'\b(immediately|urgent|urgently|asap|right now|at once)\b',
        r'\b(last chance|final notice|last warning|act now|do not delay)\b',
        r'\b(expires? (today|tonight|in \d+ (hours?|minutes?)))\b',
        r'\b(tonight|within \d+ (hours?|minutes?)|before midnight)\b',
        r'\b(your account will be (blocked|suspended|frozen|closed))\b',
        r'\b(immediately (call|contact|click|visit|pay))\b',
        r'\bif you (don.?t|fail to|do not).{0,30}(block|suspend|arrest|legal)\b',
        r'\b(do not ignore|must (call|act|respond|pay))\b',
    ]
    hit_count = sum(1 for p in urgency_phrases if re.search(p, t))
    if hit_count >= 2:
        return {
            "triggered": True,
            "signal_id": "URGENCY_PRESSURE",
            "scam_type": "High-Pressure Urgency Tactic",
            "severity": 1,
            "explanation": (
                "This message uses multiple urgent, threatening phrases to pressure you into "
                "acting without thinking. Creating panic and urgency is a core social engineering "
                "technique used by scammers. Legitimate organizations give you reasonable time "
                "and use official channels."
            ),
            "recommendation": (
                "Take a breath and do not act impulsively. Verify any claim independently by "
                "contacting the organization directly through their official website or helpline."
            ),
        }
    return {"triggered": False, "signal_id": "URGENCY_PRESSURE"}


def signal_prize_lottery_scam(text: str) -> Dict[str, Any]:
    """
    Detects lottery, prize, and lucky draw scams.
    """
    t = _normalize(text)
    patterns = [
        r'(congratulations?|congrats).{0,50}(winner|won|selected|chosen)',
        r'(won|winner|selected).{0,30}(lottery|lucky draw|prize|cash|car|iphone)',
        r'(lottery|lucky draw|lucky winner).{0,30}(claim|collect|redeem)',
        r'(prize|reward|gift).{0,30}(claim|collect|redeem).{0,30}(now|immediately)',
        r'(₹|rs|inr).?\d{4,}.{0,20}(prize|lottery|reward|won)',
        r'(gift|voucher|coupon).{0,20}(claim|redeem|collect).{0,20}(now|today|link)',
        r'(lucky|winner).{0,30}(number|ticket|draw).{0,30}(your|you)',
    ]
    for p in patterns:
        if re.search(p, t):
            return {
                "triggered": True,
                "signal_id": "PRIZE_LOTTERY_SCAM",
                "scam_type": "Lottery / Prize Scam",
                "severity": 2,
                "explanation": (
                    "You cannot win a lottery or prize that you never entered. This is a common "
                    "scam where fraudsters claim you've won money or prizes, then ask for a "
                    "'processing fee', 'tax payment', or your bank details to 'transfer' the prize."
                ),
                "recommendation": (
                    "Ignore and delete this message. Never pay money to claim a prize. "
                    "Block the sender number."
                ),
            }
    return {"triggered": False, "signal_id": "PRIZE_LOTTERY_SCAM"}


def signal_impersonation(text: str) -> Dict[str, Any]:
    """
    Detects impersonation of banks, government bodies, and trusted services.
    """
    t = _normalize(text)
    patterns = [
        r'\b(rbi|reserve bank).{0,30}(notice|alert|warning|officer)',
        r'\b(income tax|it department).{0,30}(notice|refund|officer|call)',
        r'\b(trai|telecom).{0,30}(sim|mobile|block|disconnect)',
        r'\b(sebi|insurance|irdai).{0,30}(policy|notice|officer)',
        r'\b(pm cares|pradhan mantri|government of india).{0,40}(fund|money|relief|help)',
        r'\b(amazon|flipkart|swiggy|zomato).{0,30}(selected|winner|prize|reward)',
        r'\b(microsoft|apple|google).{0,30}(virus|hacked|support|call|tech)',
    ]
    for p in patterns:
        if re.search(p, t):
            return {
                "triggered": True,
                "signal_id": "IMPERSONATION",
                "scam_type": "Organizational Impersonation",
                "severity": 2,
                "explanation": (
                    "This message is claiming to be from a government body, bank, or large company. "
                    "Scammers frequently impersonate trusted organizations to appear legitimate. "
                    "RBI, TRAI, and income tax authorities do NOT send warnings via SMS/WhatsApp."
                ),
                "recommendation": (
                    "Verify by visiting the official website of the organization or calling their "
                    "published helpline number. Do not use the contact details provided in this message."
                ),
            }
    return {"triggered": False, "signal_id": "IMPERSONATION"}


# ---------------------------------------------------------------------------
# OCR MODULE (Screenshot Analysis)
# ---------------------------------------------------------------------------

def extract_text_from_image(image_path: str) -> str:
    """
    Extracts text from an image file using OCR (Tesseract via pytesseract).

    Args:
        image_path: Absolute path to the image file (PNG, JPEG, etc.)

    Returns:
        Extracted text string, or empty string on failure.

    Requirements:
        pip install pytesseract Pillow
        Tesseract-OCR must be installed: https://github.com/UB-Mannheim/tesseract/wiki
    """
    try:
        from PIL import Image
        import pytesseract

        # Windows: Uncomment and adjust if Tesseract is not in PATH
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        img = Image.open(image_path)

        # Upscale small images for better OCR accuracy
        min_dim = 1000
        w, h = img.size
        if min(w, h) < min_dim:
            scale = min_dim / min(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        # Use LANG=eng+hin for bilingual (English + Hindi) OCR
        config = '--oem 3 --psm 6'
        extracted = pytesseract.image_to_string(img, lang='eng', config=config)
        return extracted.strip()

    except ImportError:
        return "[OCR ERROR] pytesseract or Pillow not installed. Run: pip install pytesseract Pillow"
    except FileNotFoundError:
        return f"[OCR ERROR] Image file not found: {image_path}"
    except Exception as e:
        return f"[OCR ERROR] Failed to extract text: {str(e)}"


# ---------------------------------------------------------------------------
# MASTER SIGNAL ANALYZER
# ---------------------------------------------------------------------------

ALL_SIGNAL_FUNCTIONS = [
    signal_fake_kyc,
    signal_upi_collect_request,
    signal_parcel_customs_threat,
    signal_digital_arrest,
    signal_job_offer_scam,
    signal_electricity_bill_threat,
    signal_otp_phishing,
    signal_loan_fraud,
    signal_phishing_url,
    signal_urgency_pressure,
    signal_prize_lottery_scam,
    signal_impersonation,
]


def analyze_signals(text: str, image_path: str = None) -> Dict[str, Any]:
    """
    Master function: runs all scam signals against the given text
    (and optional OCR-extracted image text) and returns a combined result.

    Args:
        text: The message/URL text to analyze.
        image_path: Optional path to a screenshot image for OCR extraction.

    Returns:
        A dict with:
          - ocr_text: Text extracted from image (if image_path provided)
          - triggered_signals: List of triggered signal dicts
          - signal_count: Number of signals triggered
          - highest_severity: 0 (none), 1 (low), 2 (medium), 3 (high)
          - scam_types: List of unique scam category strings
          - explanations: List of plain-language explanation strings
          - recommendations: List of action recommendation strings
          - heuristic_risk_boost: Score boost to add to ML score (0-40)
    """
    combined_text = str(text) if text else ""

    # OCR extraction if image provided
    ocr_text = ""
    if image_path:
        ocr_text = extract_text_from_image(image_path)
        if ocr_text and not ocr_text.startswith("[OCR ERROR]"):
            combined_text = combined_text + "\n" + ocr_text

    triggered = []
    for signal_fn in ALL_SIGNAL_FUNCTIONS:
        result = signal_fn(combined_text)
        if result.get("triggered"):
            triggered.append(result)

    if not triggered:
        return {
            "ocr_text": ocr_text,
            "triggered_signals": [],
            "signal_count": 0,
            "highest_severity": 0,
            "scam_types": [],
            "explanations": [],
            "recommendations": [],
            "heuristic_risk_boost": 0,
        }

    highest_severity = max(s.get("severity", 0) for s in triggered)
    scam_types = list(dict.fromkeys(s["scam_type"] for s in triggered))
    explanations = [s["explanation"] for s in triggered]
    recommendations = list(dict.fromkeys(s["recommendation"] for s in triggered))

    # Risk boost: based on number and severity of triggered signals
    boost = 0
    for sig in triggered:
        sev = sig.get("severity", 1)
        if sev == 3:
            boost += 15
        elif sev == 2:
            boost += 8
        elif sev == 1:
            boost += 3
    # Cap boost at 40 to let ML model retain primary control
    boost = min(boost, 40)

    return {
        "ocr_text": ocr_text,
        "triggered_signals": triggered,
        "signal_count": len(triggered),
        "highest_severity": highest_severity,
        "scam_types": scam_types,
        "explanations": explanations,
        "recommendations": recommendations,
        "heuristic_risk_boost": boost,
    }


# ---------------------------------------------------------------------------
# SCAM TYPE CATALOG — for Member 4 (UI explanations on-screen text)
# ---------------------------------------------------------------------------

SCAM_TYPE_CATALOG = {
    "Fake KYC Update": {
        "icon": "🏦",
        "short_description": "Fake bank KYC update request",
        "full_explanation": (
            "Scammers send SMS or WhatsApp messages pretending to be your bank, "
            "claiming your account will be blocked unless you update your KYC. "
            "They share a fake link that looks like your bank's website but steals "
            "your login credentials or makes you download a malicious app."
        ),
        "user_advice": "Visit your bank's official website or branch directly. Never click links in SMS.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "UPI Collect Request Fraud": {
        "icon": "💸",
        "short_description": "Fake UPI money request disguised as payment",
        "full_explanation": (
            "A scammer sends you a UPI 'collect' request (which debits your account) "
            "while claiming it will add money to your account. Entering your UPI PIN "
            "approves THEIR withdrawal, not a credit to you."
        ),
        "user_advice": "To receive money on UPI, you never need to enter your PIN. If asked, it's a scam.",
        "report_at": "NPCI: 1800-120-1740 | https://cybercrime.gov.in",
    },
    "Parcel / Customs Scam": {
        "icon": "📦",
        "short_description": "Fake courier or customs clearance fee demand",
        "full_explanation": (
            "Fraudsters impersonate FedEx, DHL, India Post, or customs officers claiming "
            "a package in your name has been seized for containing illegal items. "
            "They demand a 'clearance fee' or personal information to release it."
        ),
        "user_advice": "No courier company collects fees via SMS/WhatsApp. Contact the courier through their official website.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "Digital Arrest / Agency Impersonation": {
        "icon": "🚨",
        "short_description": "Fake arrest threat from fake government officer",
        "full_explanation": (
            "Scammers pretend to be CBI, Delhi Police, ED, or Narcotics Bureau officers "
            "and place you under a fake 'digital arrest' via video call, claiming your "
            "Aadhaar/account is involved in a crime. They demand money to 'settle' the case. "
            "No real government officer ever does this."
        ),
        "user_advice": "Hang up. No real officer arrests people via phone. Contact local police if threatened.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "Fake Job / Task Scam": {
        "icon": "💼",
        "short_description": "Advance-fee job or online task fraud",
        "full_explanation": (
            "Part-time job scams on Telegram/WhatsApp promise ₹500–₹5000/day for "
            "liking YouTube videos or rating Google Maps. After small initial payments, "
            "they ask for a large 'deposit' to unlock higher earnings — and vanish."
        ),
        "user_advice": "No legitimate job asks you to pay first. Block and report the recruiter.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "Electricity Bill Disconnection Scam": {
        "icon": "⚡",
        "short_description": "Fake electricity disconnection threat",
        "full_explanation": (
            "Scammers send urgent messages claiming your electricity will be cut tonight "
            "due to an unpaid bill. They ask you to call a fake 'electricity officer' who "
            "then collects payment or steals remote access to your phone via apps like AnyDesk."
        ),
        "user_advice": "Check your bill on your DISCOM's official website. Never call numbers from SMS.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "OTP / PIN Phishing": {
        "icon": "🔐",
        "short_description": "Attempt to steal your OTP or bank PIN",
        "full_explanation": (
            "Any message or call that asks you to share your OTP, UPI PIN, or bank password "
            "is a scam. Banks and legitimate services NEVER ask for your OTP or PIN over "
            "a call, SMS, or link."
        ),
        "user_advice": "NEVER share OTP or PIN with anyone. If compromised, call your bank immediately.",
        "report_at": "Your bank's fraud helpline | https://cybercrime.gov.in",
    },
    "Fake Loan Offer": {
        "icon": "💰",
        "short_description": "Fraudulent instant loan with upfront fees",
        "full_explanation": (
            "Scam loan apps and messages promise instant loans with no documents or low "
            "interest rates, then charge upfront 'processing fees' and disappear. Some "
            "malicious loan apps also harvest your contacts and photos for blackmail."
        ),
        "user_advice": "Only use RBI-registered lenders. Never pay fees before receiving a loan.",
        "report_at": "RBI: https://rbi.org.in | https://cybercrime.gov.in",
    },
    "Known Phishing URL": {
        "icon": "🌐",
        "short_description": "Link to a confirmed scam website",
        "full_explanation": (
            "The link in this message points to a website that is confirmed to be used "
            "in phishing campaigns targeting Indian users. Visiting it may steal your "
            "banking credentials or install malware on your device."
        ),
        "user_advice": "Do not click this link. Report it at cybercrime.gov.in.",
        "report_at": "https://cybercrime.gov.in | Google Safe Browsing report",
    },
    "Suspicious URL (High-Risk Domain)": {
        "icon": "🔗",
        "short_description": "Link using an unusual, high-risk domain extension",
        "full_explanation": (
            "The URL uses a domain extension (.xyz, .top, .site, etc.) that is very "
            "frequently abused in phishing websites. While not all such URLs are malicious, "
            "legitimate Indian banks and government services do not use them."
        ),
        "user_advice": "Avoid clicking this link. Navigate to the service's official website directly.",
        "report_at": "https://cybercrime.gov.in",
    },
    "Lottery / Prize Scam": {
        "icon": "🎰",
        "short_description": "Fake lottery win or prize claim",
        "full_explanation": (
            "You cannot win a lottery you never entered. These messages trick you into "
            "paying a 'processing fee', 'tax', or 'shipping charge' to claim a prize "
            "that does not exist."
        ),
        "user_advice": "Ignore and delete. Never pay money to claim a prize.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "Organizational Impersonation": {
        "icon": "🏛️",
        "short_description": "Message pretending to be a trusted organization",
        "full_explanation": (
            "The message claims to be from RBI, TRAI, Income Tax, or a large company. "
            "These organizations do NOT send warnings, prizes, or refund offers via "
            "unsolicited SMS or WhatsApp."
        ),
        "user_advice": "Verify by calling the organization's official helpline number directly.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "High-Pressure Urgency Tactic": {
        "icon": "⏰",
        "short_description": "Artificial urgency to prevent careful thinking",
        "full_explanation": (
            "Scammers deliberately create panic and urgency to stop you from thinking "
            "clearly. Phrases like 'act immediately', 'tonight', or 'final warning' are "
            "designed to rush you into making a costly mistake."
        ),
        "user_advice": "Slow down. Any legitimate request can wait for verification. Take your time.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "Brand Impersonation URL": {
        "icon": "🎭",
        "short_description": "Fake website disguised as a trusted brand",
        "full_explanation": (
            "The URL contains the name of a trusted brand (SBI, HDFC, Paytm, etc.) but "
            "is NOT their official website. Scammers copy the look of real websites to "
            "steal your login credentials."
        ),
        "user_advice": "Always check the full URL carefully. When in doubt, type the official address yourself.",
        "report_at": "https://cybercrime.gov.in | Report to the impersonated brand directly",
    },
    "Malicious File Download Link": {
        "icon": "☠️",
        "short_description": "Link that downloads a harmful app or file",
        "full_explanation": (
            "The link in this message downloads a file (usually an APK for Android) that "
            "is malware. Once installed, it can steal your banking credentials, intercept "
            "OTPs, and give scammers complete control of your device."
        ),
        "user_advice": "NEVER install apps from links in messages. Only use Google Play Store or Apple App Store.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
}

# ---------------------------------------------------------------------------
# SAFETY TIPS (for UI display)
# ---------------------------------------------------------------------------

GENERAL_SAFETY_TIPS = [
    "🔐 NEVER share your OTP, UPI PIN, or bank password with anyone — not even bank employees.",
    "🏦 Your bank will NEVER ask you to click a link or call a number to avoid account suspension.",
    "📲 Only install apps from Google Play Store or Apple App Store. Never from links in SMS.",
    "🌐 Always type bank URLs directly in your browser. Do not follow SMS/WhatsApp links.",
    "⚡ Electricity companies send official bills — they do NOT threaten disconnection via SMS.",
    "💸 To RECEIVE money on UPI, you do NOT need to enter your PIN.",
    "🚨 Report online fraud at https://cybercrime.gov.in or call the national helpline 1930.",
    "👮 No real police officer arrests you via phone or video call.",
]


if __name__ == "__main__":
    # Quick self-test
    test_cases = [
        "Dear SBI user, your account KYC is pending. Click http://sbi-kyc-verify.top/update to avoid suspension.",
        "Electricity power will be disconnected tonight. Call officer 9876543210 immediately.",
        "Congratulations! You won ₹10,00,000 in KBC Lucky Draw. Call now to claim your prize.",
        "Your Swiggy order is out for delivery. Estimated arrival: 25 minutes.",
        "Earn ₹5000 daily liking YouTube videos. Join Telegram @easyjobs_india now!",
    ]

    for t in test_cases:
        result = analyze_signals(t)
        print(f"\nText: {t[:70]}...")
        print(f"  Signals triggered: {result['signal_count']}")
        print(f"  Scam types: {result['scam_types']}")
        print(f"  Severity: {result['highest_severity']}")
        print(f"  Risk Boost: +{result['heuristic_risk_boost']}%")
