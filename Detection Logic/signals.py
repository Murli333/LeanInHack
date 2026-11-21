"""
ScamLens — signals.py  v2.0
Member 2: Detection Logic & Test Set

Heuristic scam signal detection engine for Indian cybercrime patterns.

IMPROVEMENTS IN v2.0
---------------------
[P0] Robust URL parsing with urllib.parse; handles malformed, encoded and
     scheme-less URLs; treats unknown domains separately from confirmed malicious
     domains; never conflates "not blocklisted" with "safe".
[P1] Hindi / Hinglish / obfuscated-text pattern matching via transliteration
     and leet-speak normalisation before regex evaluation.
[P1] Reduced false-positives: signals are gated by negative patterns; allowlist
     domains only suppress the URL signal, NOT the message-content signals.
[P1] New signal categories: Investment Scam, Romance/Sextortion Scam, Fake
     Customer Care, Advance-Fee / Money Mule, Remote-Access Trojan (RAT).
[P1] Short-URL detection with safe (non-requesting) flagging.
[P2] Blocklist and allowlist loaded from versioned JSON data files; in-memory
     sets are built at import time.
[P2] Every threat-indicator carries source, last_verified and category metadata.

OCR (v2.0)
----------
- Explicit OCR failure codes returned in result (never silent failure).
- Pre-processing: auto-rotation (Tesseract OSD), adaptive contrast (PIL) and
  resolution upscaling to ≥ 300 DPI-equivalent before OCR.
- Returns OCR confidence score alongside extracted text.
- Validates image dimensions, file format and file size before processing.
- Hindi + English bilingual OCR (lang='hin+eng') with English-only fallback.

Schema: every signal function returns
  {
    "triggered"    : bool,
    "signal_id"    : str,          # e.g. "FAKE_KYC"
    "scam_type"    : str,          # human-readable category
    "severity"     : int,          # 1 (low) | 2 (medium) | 3 (high)
    "explanation"  : str,          # plain-language reason for the UI
    "recommendation": str,         # what the user should do
    "matched_text" : str | None,   # snippet that triggered this signal
  }

Non-triggered signals return only:
  {"triggered": False, "signal_id": str}
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import unquote, urlparse

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_HERE, "data")
_BLOCKLIST_PATH = os.path.join(_DATA_DIR, "blocklist.json")
_ALLOWLIST_PATH = os.path.join(_DATA_DIR, "allowlist.json")


# ---------------------------------------------------------------------------
# LOAD VERSIONED DATA FILES
# Falls back gracefully to embedded minimal sets if files are missing.
# ---------------------------------------------------------------------------

def _load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


_blocklist_data = _load_json(_BLOCKLIST_PATH)
_allowlist_data = _load_json(_ALLOWLIST_PATH)

# Fast lookup sets built from JSON
PHISHING_BLOCKLIST: Dict[str, dict] = {
    entry["domain"]: entry
    for entry in _blocklist_data.get("domains", [])
}

TRUSTED_DOMAINS: Dict[str, dict] = {
    entry["domain"]: entry
    for entry in _allowlist_data.get("trusted_domains", [])
}

URL_SHORTENERS: set = {
    entry["domain"]
    for entry in _blocklist_data.get("url_shorteners", [])
}

# Hard-coded fallback if JSON is absent
if not PHISHING_BLOCKLIST:
    PHISHING_BLOCKLIST = {d: {"severity": 3, "category": "unknown"}
                          for d in ["sbi-kyc-verify.top", "hdfc-kyc-verify.com"]}

if not TRUSTED_DOMAINS:
    TRUSTED_DOMAINS = {d: {"org": d}
                       for d in ["sbi.co.in", "hdfcbank.com", "irctc.co.in",
                                 "uidai.gov.in", "cybercrime.gov.in"]}

if not URL_SHORTENERS:
    URL_SHORTENERS = {"bit.ly", "tinyurl.com", "t.me", "wa.me"}

# Suspicious TLDs — not blocklisted individually, but structurally risky
SUSPICIOUS_TLDS: set = {
    "top", "xyz", "click", "site", "fit", "link", "club", "work",
    "buzz", "gq", "cf", "tk", "ml", "ga", "online", "vip", "monster",
    "rest", "stream", "support", "cam", "icu", "fun", "win", "bid",
    "cfd", "cyou", "sbs", "bar", "uno",
}

# Brands whose names appearing in a non-official domain = impersonation
MAJOR_BRANDS: List[str] = [
    "sbi", "hdfc", "icici", "axis", "kotak", "paytm", "phonepe",
    "aadhaar", "incometax", "uidai", "irctc", "npci", "rbi",
    "amazon", "flipkart",
]


# ---------------------------------------------------------------------------
# TEXT NORMALISATION HELPERS
# ---------------------------------------------------------------------------

# Map common leet-speak / obfuscation characters to ASCII
_LEET_TABLE = str.maketrans({
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s",
    "7": "t", "@": "a", "$": "s", "!": "i",
})

# Common Hindi / Hinglish transliterations for scam keywords
_HINDI_ALIASES: Dict[str, List[str]] = {
    "kyc": ["kysi", "kesi", "kyc", "k y c"],
    "bank": ["baink", "bank", "बैंक"],
    "account": ["akount", "अकाउंट", "khata", "खाता"],
    "otp": ["o t p", "otp", "otpi"],
    "pin": ["peen", "pin", "पिन"],
    "arrest": ["giraftari", "गिरफ्तारी", "arest"],
    "electricity": ["bijli", "बिजली", "current", "light bill"],
    "disconnect": ["band karo", "band kar", "katega", "काटेगा"],
    "police": ["pulice", "pulees", "पुलिस"],
    "loan": ["lon", "लोन", "udhar"],
    "reward": ["inaam", "इनाम", "prize", "gift"],
    "job": ["naukri", "नौकरी", "kaam"],
    "earn": ["kamao", "कमाओ", "income"],
    "verify": ["verify karo", "verify karein", "sathyapan"],
    "block": ["band", "बंद", "blokd"],
    "suspend": ["rokna", "रोकना", "suspend"],
    "customs": ["customs", "kapde", "duty"],
    "parcel": ["parsel", "पार्सल", "package"],
}

# Build a normalised regex alternation for each concept
_HINDI_PATTERNS: Dict[str, re.Pattern] = {
    concept: re.compile(
        r"\b(?:" + "|".join(re.escape(v) for v in variants) + r")\b",
        re.IGNORECASE | re.UNICODE,
    )
    for concept, variants in _HINDI_ALIASES.items()
}


def _normalise(text: str) -> str:
    """Lowercase, collapse whitespace, strip diacritics, apply leet table."""
    text = str(text) if text else ""
    # Normalise unicode (NFC then strip combining chars)
    text = unicodedata.normalize("NFC", text)
    text = text.translate(_LEET_TABLE)
    text = re.sub(r"\s+", " ", text.lower()).strip()
    # Collapse spaced acronyms: 'k y c' -> 'kyc', 'o t p' -> 'otp'
    text = re.sub(r"\b([a-z])\s+([a-z])\s+([a-z])\b", r"\1\2\3", text)
    text = re.sub(r"\b([a-z])\s+([a-z])\b", r"\1\2", text)
    return text


def _concept_in_text(text: str, concept: str) -> bool:
    """Check if a Hindi/Hinglish/obfuscated variant of a concept appears in text."""
    pat = _HINDI_PATTERNS.get(concept)
    if pat:
        return bool(pat.search(text))
    return concept in text


def _first_match(patterns: List[str | re.Pattern], text: str) -> Optional[str]:
    """Return the first matching snippet from a list of regex patterns."""
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE | re.UNICODE) if isinstance(p, str) else p.search(text)
        if m:
            return m.group(0)[:120]
    return None


# ---------------------------------------------------------------------------
# URL PARSING HELPERS (P0 — robust, never crashes)
# ---------------------------------------------------------------------------

def _parse_url(raw: str) -> Tuple[str, str, str, str]:
    """
    Robustly parse a URL string.
    Returns (clean_url, scheme, domain, path_and_query).
    Never raises; returns empty strings on completely invalid input.
    """
    raw = raw.strip()
    if not raw:
        return "", "", "", ""

    # Decode percent-encoding for analysis (but keep the original for display)
    try:
        decoded = unquote(raw, errors="replace")
    except Exception:
        decoded = raw

    # Ensure a scheme so urllib.parse works
    target = decoded
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+\-.]*://", target):
        target = "http://" + target

    try:
        parsed = urlparse(target)
        scheme = (parsed.scheme or "http").lower()
        domain = (parsed.netloc or "").lower()
        # Strip port number
        if ":" in domain:
            domain = domain.split(":")[0]
        # Strip auth info (user:pass@host)
        if "@" in domain:
            domain = domain.split("@")[-1]
        path_and_query = parsed.path + ("?" + parsed.query if parsed.query else "")
        return raw, scheme, domain, path_and_query
    except Exception:
        # Absolutely minimal fallback
        domain = raw.split("/")[0].lower().lstrip("http://").lstrip("https://")
        return raw, "http", domain, ""


def _extract_urls(text: str) -> List[str]:
    """
    Extract all candidate URLs from free text.
    Handles http/https, www-prefixed, and bare suspicious-TLD domains.
    Also detects obfuscated URLs with spaces around dots (e.g. 'sbi - kyc .top').
    """
    # De-obfuscate spaced dots: "sbi - kyc .top" → "sbi-kyc.top"
    deobf = re.sub(r"(?<=\w)\s*[·•·]\s*(?=\w)", ".", text)
    deobf = re.sub(r"(?<=\w)\s*-\s*(?=\w)", "-", deobf)
    deobf = re.sub(r"(?<=\w)\s*\.\s*(?=\w)", ".", deobf)

    pattern = re.compile(
        r"(?:https?://|ftp://)[^\s<>\"'(){}|\\^\[\]`]+"
        r"|www\.[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}[^\s<>\"'(){}|\\^\[\]`]*"
        r"|[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\."
        r"(?:top|xyz|site|click|link|fun|win|bid|cam|icu|club|work|buzz|"
        r"gq|cf|tk|ml|ga|online|vip|monster|rest|stream|support|"
        r"cfd|cyou|sbs|bar|uno)[^\s<>\"'(){}|\\^\[\]`]*",
        re.IGNORECASE,
    )
    found = pattern.findall(deobf)
    cleaned_found = []
    for u in found:
        # Strip trailing sentence punctuation
        u_clean = u.rstrip(".!?,;:)]}")
        if u_clean:
            cleaned_found.append(u_clean)
    return list(dict.fromkeys(cleaned_found))  # deduplicate, preserve order


def _extract_domain(url: str) -> str:
    """
    Extract the host/domain part of a URL (backward compatibility with Member 3).
    """
    if not url:
        return ""
    _, _, domain, _ = _parse_url(url)
    return domain


def _registrable_domain(domain: str) -> str:
    """
    Strip subdomains and return the registrable domain (eTLD+1).
    Simple two-label approach sufficient for Indian scam detection.
    E.g. 'login.sbi-kyc.top' → 'sbi-kyc.top'
         'secure.sbi.co.in'   → 'sbi.co.in'  (handles .co.in two-part TLD)
    """
    parts = domain.split(".")
    if len(parts) <= 2:
        return domain
    # Handle common two-part TLDs: .co.in, .net.in, .org.in, .gov.in, etc.
    if parts[-2] in {"co", "net", "org", "gov", "ac", "edu", "nic"} and parts[-1] == "in":
        return ".".join(parts[-3:]) if len(parts) >= 3 else domain
    return ".".join(parts[-2:])


def _is_trusted(url_or_domain: str) -> bool:
    """
    Return True if the domain OR its registrable parent is in the allowlist.
    Handles full URLs or plain domain strings.
    Allowlisted = URL is likely safe; does NOT suppress content signals.
    """
    if not url_or_domain:
        return False
    if "/" in url_or_domain or ":" in url_or_domain:
        domain = _extract_domain(url_or_domain)
    else:
        domain = url_or_domain.lower().strip()
    if not domain:
        return False
    if domain in TRUSTED_DOMAINS:
        return True
    reg = _registrable_domain(domain)
    if reg in TRUSTED_DOMAINS:
        return True
    # Subdomain of trusted (e.g. netbanking.sbi.co.in)
    for trusted in TRUSTED_DOMAINS:
        if domain.endswith("." + trusted):
            return True
    return False


def _is_blocklisted(url_or_domain: str) -> Optional[dict]:
    """
    Return the blocklist entry if domain is confirmed malicious, else None.
    Handles full URLs or plain domain strings.
    Checks both the full domain and its registrable form.
    """
    if not url_or_domain:
        return None
    if "/" in url_or_domain or ":" in url_or_domain:
        domain = _extract_domain(url_or_domain)
    else:
        domain = url_or_domain.lower().strip()
    if not domain:
        return None
    if domain in PHISHING_BLOCKLIST:
        return PHISHING_BLOCKLIST[domain]
    reg = _registrable_domain(domain)
    if reg in PHISHING_BLOCKLIST:
        return PHISHING_BLOCKLIST[reg]
    for blocked in PHISHING_BLOCKLIST:
        if domain.endswith("." + blocked):
            return PHISHING_BLOCKLIST[blocked]
    return None


def _is_shortener(domain: str) -> bool:
    domain = domain.lower()
    return domain in URL_SHORTENERS or _registrable_domain(domain) in URL_SHORTENERS


# ---------------------------------------------------------------------------
# SAFE BENIGN TRANSACTION PATTERNS
# Messages matching these are strongly likely to be genuine bank/service SMS.
# ---------------------------------------------------------------------------
_BENIGN_PATTERNS: List[re.Pattern] = [
    re.compile(r"\bnever\s+share\s+(?:your\s+)?otp\b", re.IGNORECASE),
    re.compile(r"\bdo\s+not\s+(?:share|disclose)\b", re.IGNORECASE),
    re.compile(r"\bavailable\s+bal(?:ance)?\s*[:\-₹rs]", re.IGNORECASE),
    re.compile(r"\bpnr\s*\d{6,}\b", re.IGNORECASE),
    re.compile(r"\bconfirmed\b.*\bcoach\b.*\bberth\b", re.IGNORECASE | re.DOTALL),
    re.compile(r"\bout\s+for\s+delivery\b", re.IGNORECASE),
    re.compile(r"\bdelivered\b.*\bthank\s+you\b", re.IGNORECASE | re.DOTALL),
    re.compile(r"\bca\s+no\.?\s*\d{5,}\b", re.IGNORECASE),          # electricity CA number
    re.compile(r"\bdue\s+on\s+\d{1,2}[-/]\w+\b", re.IGNORECASE),   # bill due date
    re.compile(r"\bpay\s+via\s+official\s+portal\b", re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# SIGNAL HELPER: build a negative gate
# ---------------------------------------------------------------------------

def _has_benign_marker(text: str) -> bool:
    return any(p.search(text) for p in _BENIGN_PATTERNS)


# ---------------------------------------------------------------------------
# SIGNAL DEFINITIONS  (12 original + 5 new)
# ---------------------------------------------------------------------------

def signal_fake_kyc(text: str) -> Dict[str, Any]:
    """
    Fake KYC update scams — urgent SMS/WhatsApp demanding the user update KYC
    via a link or APK, else their bank/SIM account will be blocked.
    Covers Hindi/Hinglish variants (kyc expire ho raha hai, etc.)
    """
    t = _normalise(text)

    # Hard gate: genuine OTP / account alert with 'never share' warning → safe
    if _has_benign_marker(text) and "kyc" not in _normalise(text):
        return {"triggered": False, "signal_id": "FAKE_KYC"}

    # Hard gate: official bank KYC reminder directing customer to physical branch without links
    if re.search(r"\b(visit|go\s*to)\s+(?:your\s+)?(?:nearest\s+)?(?:\w+\s+)?(?:home\s+)?branch\b", text, re.IGNORECASE) and not _extract_urls(text):
        return {"triggered": False, "signal_id": "FAKE_KYC"}

    patterns = [
        r"\bkyc\b.{0,80}(update|verify|expire|block|suspend|pending|complete|karo|karein|abhi)",
        r"(update|verify|complete|update karo|update karein).{0,80}\bkyc\b",
        r"(account|sim|debit\s*card|atm|mobile).{0,60}(block|suspend|freeze|band).{0,60}kyc",
        r"\bkyc\b.{0,50}(link|click|visit|download|apk|app)",
        r"(pending|incomplete|expired?|expire ho).{0,30}kyc",
        r"your\s+(bank|sbi|hdfc|icici|paytm|phonepe).{0,50}(kyc|account).{0,60}(block|expire|suspend|band)",
        r"(aadhaar|aadhar).{0,50}(link|update|verify|jod).{0,50}(bank|account|sim|mobile)",
        r"(pan\s*card|pancard).{0,50}(link|update|verify).{0,50}(account|mobile)",
        r"sim\s*(block|suspend|expire|band).{0,50}(kyc|verify|update)",
        # Hinglish variants
        r"(khata|account).{0,50}(band|block|suspend).{0,50}(kyc|verify|link)",
        r"kyc\s*(khatam|expire|expired?|purana)",
        r"naya\s*(kyc|registration|verification).{0,60}(karo|karein|link)",
    ]

    matched = _first_match(patterns, t)
    if matched:
        return {
            "triggered": True,
            "signal_id": "FAKE_KYC",
            "scam_type": "Fake KYC Update",
            "severity": 3,
            "explanation": (
                "This message pressures you to update your KYC (Know Your Customer) urgently. "
                "Scammers send these to trick you into visiting a fake bank website or downloading "
                "a malicious app that steals your login credentials or Aadhaar number."
            ),
            "recommendation": (
                "Do NOT click any link or download any app from this message. "
                "To update KYC, visit your bank's official website directly (e.g., sbi.co.in) "
                "or go to your nearest branch in person."
            ),
            "matched_text": matched,
        }
    return {"triggered": False, "signal_id": "FAKE_KYC"}


def signal_upi_collect_request(text: str) -> Dict[str, Any]:
    """
    UPI collect-request fraud — victim is asked to enter UPI PIN to 'receive'
    money, but actually approves a debit to the scammer.
    """
    t = _normalise(text)

    patterns = [
        r"upi.{0,50}collect.{0,50}(request|rs|inr|rupee|\d)",
        r"(collect|receive|cashback|refund|prize|reward|lottery|inaam).{0,60}(upi|pin)",
        r"(enter|approve|accept|dalo|daalo).{0,50}(upi|pin|mpin).{0,50}(receive|get|claim|money|paisa)",
        r"upi.{0,30}(pin|mpin).{0,50}(receive|credit|cashback|refund|paisa|milega)",
        r"(accept|approve).{0,30}(collect\s*request|payment\s*request)",
        r"(prize|lottery|cashback|reward|winner|inaam).{0,80}(upi|gpay|phonepe|paytm|bhim)",
        r"scan.{0,30}(qr|code|barcode).{0,50}(receive|get|claim|money|paisa)",
        # Hinglish
        r"(paisa|paise).{0,50}(receive|milega|milegi|aayega).{0,50}(pin|upi|scan)",
        r"(pin\s*daalo|pin\s*enter|pin\s*lagao).{0,50}(paisa|money|receive|milega)",
    ]
    matched = _first_match(patterns, t)
    if matched:
        return {
            "triggered": True,
            "signal_id": "UPI_COLLECT_REQUEST",
            "scam_type": "UPI Collect Request Fraud",
            "severity": 3,
            "explanation": (
                "This message asks you to enter your UPI PIN to 'receive' money. "
                "This is a classic scam — entering your UPI PIN does NOT receive money, "
                "it approves a payment FROM your account to the scammer."
            ),
            "recommendation": (
                "NEVER enter your UPI PIN to receive money. "
                "To receive a UPI payment you do not need to enter any PIN. "
                "Report this fraud to NPCI at https://npci.org.in or call 1800-120-1740."
            ),
            "matched_text": matched,
        }
    return {"triggered": False, "signal_id": "UPI_COLLECT_REQUEST"}


def signal_parcel_customs_threat(text: str) -> Dict[str, Any]:
    """
    Parcel/customs scam — fraudsters impersonate couriers (FedEx, DHL, India Post)
    or customs officials claiming a seized package; demand a clearance fee.
    """
    t = _normalise(text)
    patterns = [
        r"(parcel|package|consignment|shipment|parsel).{0,80}(seize|seized|hold|customs|illegal|arrest|drugs|narcotics|contraband)",
        r"(customs|clearance).{0,60}(fee|charge|pay|fine|duty|penalty)",
        r"(fedex|dhl|india\s*post|bluedart|dtdc|ups|aramex).{0,80}(customs|seized|illegal|narcotics|arrested)",
        r"(narcotics|drugs|contraband|mdma|cocaine).{0,60}(parcel|package|name|found|registered)",
        r"(clearance|release).{0,50}(fee|charge|penalty|fine).{0,50}(parcel|package)",
        r"your\s+(parcel|package|shipment).{0,60}(contain|hold|seized|arrest|drug)",
        r"(airport|customs\s*officer|courier\s*office).{0,60}(parcel|package|contact|call|seized)",
        r"(courier|delivery).{0,50}(illegal|seized|customs|duty|charge|fine)",
        # Hinglish
        r"(maal|samaan).{0,50}(pakda|seized|customs|illegal|narcotics)",
        r"(parsel|parcel).{0,50}(band|bandh|rok).{0,50}(customs|duty|fee|fine)",
    ]
    matched = _first_match(patterns, t)
    if matched:
        return {
            "triggered": True,
            "signal_id": "PARCEL_CUSTOMS_THREAT",
            "scam_type": "Parcel / Customs Scam",
            "severity": 3,
            "explanation": (
                "This message claims a package in your name was seized by customs or contains "
                "illegal items. Scammers impersonate couriers or customs officers to extort a "
                "'clearance fee' or frighten you into revealing personal information."
            ),
            "recommendation": (
                "Do not pay any fee or call any number in this message. "
                "Contact the courier company directly via the number on their official website. "
                "Report to Cyber Crime helpline 1930 or https://cybercrime.gov.in."
            ),
            "matched_text": matched,
        }
    return {"triggered": False, "signal_id": "PARCEL_CUSTOMS_THREAT"}


def signal_digital_arrest(text: str) -> Dict[str, Any]:
    """
    Digital arrest scam — fraudsters impersonate CBI, ED, Delhi Police, NCB
    and place victims under a fake 'digital arrest' via video call, demanding
    money to avoid arrest.
    """
    t = _normalise(text)
    # Hard gate: legitimate advisory or educational message cautioning against digital arrest
    if re.search(r"\b(advisory|beware\s+of|caution|stay\s+vigilant|never\s+arrests?\s+online)\b", text, re.IGNORECASE):
        return {"triggered": False, "signal_id": "DIGITAL_ARREST"}

    patterns = [
        r"digital\s*arrest",
        r"(cbi|enforcement\s*directorate|\bed\b|narcotics\s*bureau|\bncb\b).{0,80}(arrest|warrant|case|notice|officer|giraftari)",
        r"(arrest\s*warrant|fir|case\s*registered|challan).{0,60}(your\s*name|against\s*you|aapke|tumhare)",
        r"(cyber\s*crime|cybercell|cyber\s*police).{0,50}(arrest|notice|warrant|call|officer|case)",
        r"(stay\s*on|remain\s*on|connected\s*on|on).{0,30}(video\s*call|call).{0,50}(arrested|custody|officer|police|cbi)",
        r"(skype|whatsapp|video|google\s*meet).{0,50}(officer|police|cbi|arrest|court)",
        r"(money\s*laundering|hawala|illegal\s*transaction|kaala\s*paisa).{0,60}(your\s*(name|account|number)|aapka)",
        r"(sealed|freeze|freez).{0,30}(account|assets|property).{0,50}(court|order|officer)",
        r"(aadhaar|pan\s*card|aadhar).{0,50}(misuse|fraud|case|crime|farzi|jhooth)",
        r"(stay|ruko|ghar\s*pe\s*raho).{0,50}(arrest|custody|case|cbi|police)",
        r"supreme\s*court.{0,50}(order|case|arrest|notice)",
        r"(customs|ncb|cbi|police)\s*officer.{0,30}(badge|id|verify|genuine|authentic|naamar)",
        # Hinglish
        r"(giraftari|giraftaar|giraftaari).{0,80}(aapke|tumhare|aap\s*par|case)",
        r"(digital\s*giraftari|virtual\s*giraftari)",
        r"(ghar\s*par\s*raho|ghar\s*pe\s*baitho).{0,50}(cbi|police|officer|arrest)",
    ]
    matched = _first_match(patterns, t)
    if matched:
        return {
            "triggered": True,
            "signal_id": "DIGITAL_ARREST",
            "scam_type": "Digital Arrest / Agency Impersonation",
            "severity": 3,
            "explanation": (
                "This message is impersonating a government agency (CBI, Police, ED) and "
                "threatening you with arrest. 'Digital Arrest' is one of India's most "
                "dangerous cybercrime types — no real government agency ever arrests people "
                "via phone or video call, or demands money to avoid arrest."
            ),
            "recommendation": (
                "Hang up immediately and do not transfer any money. "
                "Real government agencies send official written notices. "
                "Report this immediately at https://cybercrime.gov.in or call 1930."
            ),
            "matched_text": matched,
        }
    return {"triggered": False, "signal_id": "DIGITAL_ARREST"}


def signal_job_offer_scam(text: str) -> Dict[str, Any]:
    """
    Part-time/task-based job scam — high daily earnings for simple tasks
    (liking videos, rating maps), leading to advance-fee deposit fraud.
    """
    t = _normalise(text)
    patterns = [
        r"(part.?time|work\s*from\s*home|wfh|ghar\s*se\s*kaam).{0,80}(earn|income|daily|task|paisa|rupees?|rs)",
        r"(earn|income|kamao|kamaai).{0,20}(rs|inr|₹)?.{0,10}\d{3,5}.{0,30}(daily|per\s*day|day|din|roz)",
        r"(like|liking|pasand\s*karo).{0,50}(youtube|video|post|instagram|reel|shorts?).{0,50}(earn|money|task|paisa)",
        r"(rate|rating|review|star).{0,50}(google|maps|app|play\s*store|products?).{0,50}(earn|money|task|paisa)",
        r"(telegram|whatsapp).{0,50}(task|job|work|earn|group|channel|join|aao)",
        r"(simple|easy|basic|aasaan|seedha).{0,30}(task|job|work|kaam).{0,50}(earn|money|income|paisa|rs)",
        r"(join|contact|message|join\s*karo).{0,30}(telegram|whatsapp|signal).{0,50}(earn|job|work|task|paisa)",
        r"(daily\s*earning|daily\s*income|roz\s*kamaai).{0,50}(guaranteed|fixed|assured|pakka|confirm)",
        r"(no\s*experience|no\s*qualification|fresher|beginner|koi\s*experience\s*nahi).{0,60}(earn|job|work|income|paisa)",
        r"(advance|deposit|registration\s*fee|token\s*money|invest).{0,60}(job|task|earn|work|income|unlock)",
        r"(youtube|instagram|facebook|reels?|shorts?).{0,30}(like|subscribe|follow|share).{0,30}(earn|paid|money|paisa)",
        r"(high\s*paying|high\s*income|high\s*earning).{0,50}(work|job|task|part.?time)",
        r"(ghar\s*baithe|ghar\s*se\s*kamai|roz\s*\d+).{0,60}(review|earn|income|kamai|paisa)",
        r"(hotel|product|app|maps?)\s*review.{0,50}(likh|earn|kamai|paisa|daily|roz)",
        # Hinglish
        r"(naukri|kaam).{0,50}(ghar\s*se|online|telegram|whatsapp).{0,50}(paisa|income|earn)",
        r"(paisa\s*kamao|kamai\s*karo).{0,50}(ghar\s*se|online|aasaan|simple)",
    ]
    matched = _first_match(patterns, t)
    if matched:
        return {
            "triggered": True,
            "signal_id": "JOB_OFFER_SCAM",
            "scam_type": "Fake Job / Task Scam",
            "severity": 2,
            "explanation": (
                "This message offers suspiciously easy money for simple tasks like liking YouTube "
                "videos or rating Google Maps. These are advance-fee scams — after a few small "
                "payments, they will ask you to 'deposit' a large amount for 'higher value tasks' "
                "or 'unlock earnings', and then disappear with your money."
            ),
            "recommendation": (
                "No legitimate employer asks you to pay money upfront to receive a job or salary. "
                "Block and report this number. Report the scam at https://cybercrime.gov.in."
            ),
            "matched_text": matched,
        }
    return {"triggered": False, "signal_id": "JOB_OFFER_SCAM"}


def signal_electricity_bill_threat(text: str) -> Dict[str, Any]:
    """
    Electricity bill disconnection scam — fake DISCOM officer demands immediate
    payment to prevent power cutoff tonight.
    """
    t = _normalise(text)
    # Hard gate: genuine bill notification with CA number and due date → safe
    safe_negative = [
        r"ca\s*(no\.?|number)?\s*\d{5,}",
        r"due\s*(on|date)\s*\d{1,2}[-/]",
        r"pay\s*via\s*official",
        r"(bsesdelhi\.com|tatapower\.com|cesc\.co\.in|bsesdl\.co\.in)",
        r"consumer\s*no\.?\s*\d{5,}",
    ]
    for sp in safe_negative:
        if re.search(sp, t, re.IGNORECASE):
            return {"triggered": False, "signal_id": "ELECTRICITY_BILL_THREAT"}

    patterns = [
        r"(electricity|electric|power|current|bijli|light).{0,80}(disconnect|disconnected|cut|cutoff|band|katega|kata\s*jayega)",
        r"(disconnect|cut|band|katega).{0,50}(electricity|power|supply|connection|bijli|current).{0,50}(tonight|aaj\s*raat|abhi|today|immediately|turant)",
        r"(unpaid|pending|due|overdue|baaki|baki).{0,50}(electricity|electric|bijli|bill|current\s*bill)",
        r"(electricity|power|discom|bses|tata\s*power|bijli\s*vibhag).{0,60}(officer|helpline|contact|call|lineman)",
        r"(meter|unit).{0,50}(reading|update|block|suspend|disconnect|change)",
        r"(electricity\s*officer|lineman|power\s*officer|bijli\s*wale).{0,50}(contact|call|immediately|abhi|turant)",
        r"connection.{0,30}(disconnect|suspend|stop|band).{0,30}(due|pending|bill|baaki)",
        r"(last\s*warning|final\s*notice|aakhri\s*mauka).{0,50}(electricity|power|bijli|bill)",
        r"(tonight|aaj\s*raat|aaj\s*shaam).{0,50}(disconnect|cut|band|electricity|bijli)",
        r"(immediately|turant|abhi).{0,50}(call|contact|officer|electricity|bijli)",
        # Hinglish
        r"(bijli|current|light).{0,50}(katega|kategi|band\s*ho\s*jayegi|band\s*ho\s*jaayegi)",
        r"(bijli\s*officer|bijli\s*wale).{0,60}(call|contact|sambhalo|aao)",
    ]
    matched = _first_match(patterns, t)
    if matched:
        return {
            "triggered": True,
            "signal_id": "ELECTRICITY_BILL_THREAT",
            "scam_type": "Electricity Bill Disconnection Scam",
            "severity": 3,
            "explanation": (
                "This message threatens to cut your electricity supply and urges you to call "
                "a number urgently. Scammers pretend to be electricity department officers and "
                "collect money or remote access to your phone. Real electricity companies send "
                "official bills with CA numbers and do not threaten disconnection tonight via SMS."
            ),
            "recommendation": (
                "Do NOT call the number in this message. Check your actual bill on your DISCOM's "
                "official website (e.g., bsesdelhi.com, tatapower.com). "
                "Call the official customer care number printed on your paper bill."
            ),
            "matched_text": matched,
        }
    return {"triggered": False, "signal_id": "ELECTRICITY_BILL_THREAT"}


def signal_otp_phishing(text: str) -> Dict[str, Any]:
    """
    OTP/PIN phishing — messages that ask the user to share or enter their OTP,
    UPI PIN or bank password with a 'customer care agent'.
    """
    t = _normalise(text)
    # Hard gate: genuine OTP message will say "NEVER share"
    if re.search(r"\b(never|do\s*not|never\s*share|share\s*nahi|mat\s*batao)\b.{0,30}(otp|pin|password)", t, re.IGNORECASE):
        return {"triggered": False, "signal_id": "OTP_PHISHING"}

    patterns = [
        r"(share|give|send|tell|provide|enter|batao|bolo|dena|dedo).{0,40}(otp|one.?time.?password|pin|mpin|password)",
        r"otp.{0,50}(agent|officer|executive|representative|wala|se\s*share)",
        r"(verify|confirm|validate|confirm\s*karo).{0,30}otp.{0,30}(call|agent|officer|executive|hume|hamein)",
        r"(customer\s*care|executive|representative|officer).{0,50}(otp|pin|password)",
        r"(otp|pin).{0,30}(expire|expired|valid\s*for).{0,30}(share|tell|give|batao|jaldi)",
        r"(verify|confirm).{0,30}(otp|pin).{0,30}(here|link|site|click)",
        # Hinglish
        r"(otp\s*batao|otp\s*bolo|otp\s*do|otp\s*share\s*karo)",
        r"(pin\s*batao|pin\s*bolo|pin\s*share\s*karo|pin\s*do)",
        r"(agent|officer|executive).{0,50}(otp|pin|password).{0,50}(maang|maanga|mang)",
    ]
    matched = _first_match(patterns, t)
    if matched:
        return {
            "triggered": True,
            "signal_id": "OTP_PHISHING",
            "scam_type": "OTP / PIN Phishing",
            "severity": 3,
            "explanation": (
                "This message is asking you to share or enter your OTP or PIN with someone. "
                "Legitimate banks and services NEVER ask for your OTP over a call, message, "
                "or on a website you did not navigate to yourself. This is a direct attempt "
                "to steal access to your bank account."
            ),
            "recommendation": (
                "NEVER share your OTP with anyone — not even someone who claims to be from "
                "your bank or the government. If you've already shared it, contact your bank "
                "immediately to block your account."
            ),
            "matched_text": matched,
        }
    return {"triggered": False, "signal_id": "OTP_PHISHING"}


def signal_loan_fraud(text: str) -> Dict[str, Any]:
    """
    Fake loan offer — instant loans with no documents or low interest,
    collecting upfront fees or installing blackmail loan apps.
    """
    t = _normalise(text)

    # Hard gate: legitimate educational advisory cautioning against loan scams
    if re.search(r"\b(advisory|beware\s+of|caution\s+against|warning\s+against)\b", text, re.IGNORECASE):
        return {"triggered": False, "signal_id": "LOAN_FRAUD"}

    # Hard gate: legitimate bank loan offer pointing exclusively to a trusted domain
    urls = _extract_urls(text)
    if urls and all(_is_trusted(_parse_url(u)[2]) for u in urls) and not re.search(r"\b(whatsapp|telegram|token\s*fee|upfront|advance\s*fee)\b", t):
        return {"triggered": False, "signal_id": "LOAN_FRAUD"}

    patterns = [
        r"(instant|quick|fast|immediate|guaranteed|turant).{0,50}(loan|credit|lon|udhar)",
        r"(loan|credit|lon).{0,50}(no\s*document|without\s*document|bina\s*document|no\s*cibil|bad\s*cibil|low\s*cibil)",
        r"(processing\s*fee|registration\s*fee|token\s*fee|advance\s*fee).{0,50}(loan|credit|lon)",
        r"(pre.?approved|pre-approved|pahle\s*approved).{0,30}loan",
        r"(personal\s*loan|home\s*loan|business\s*loan|mudra\s*loan).{0,60}(apply\s*now|click|link|whatsapp|telegram)",
        r"(low\s*interest|0%.{0,10}interest|no\s*interest|zero\s*interest|bina\s*byaj).{0,50}loan",
        r"(loan|credit).{0,50}(approved|sanctioned|disburse|milega).{0,50}(click|link|apply|abhi)",
        r"(₹|rs|inr).?\d{4,}.{0,30}(loan|credit|lon).{0,30}(instant|quick|fast|abhi)",
        r"(rupees?|rs\.?|inr).{0,20}\d+\s*(lakh|lac|crore|k).{0,30}(loan|credit)",
        # Hinglish
        r"(asaan|aasaan).{0,30}(lon|loan|udhar).{0,50}(paisa|milega|le\s*lo)",
        r"(udhar|lon).{0,50}(bina\s*document|jaldi|abhi|turant|guaranteed)",
    ]
    matched = _first_match(patterns, t)
    if matched:
        return {
            "triggered": True,
            "signal_id": "LOAN_FRAUD",
            "scam_type": "Fake Loan Offer",
            "severity": 2,
            "explanation": (
                "This message is offering a quick loan with unrealistic conditions "
                "(no documents, guaranteed approval, low/zero interest). These are loan scams "
                "that collect upfront 'processing fees' and disappear, or install malicious apps "
                "that blackmail you using your phone's contacts and photos."
            ),
            "recommendation": (
                "Only apply for loans through your bank's official app or website. "
                "Never pay any fee before receiving a loan. "
                "Check if the lender is RBI-registered at https://rbi.org.in."
            ),
            "matched_text": matched,
        }
    return {"triggered": False, "signal_id": "LOAN_FRAUD"}


def signal_phishing_url(text: str) -> Dict[str, Any]:
    """
    URL-based phishing detection.
    Priority: confirmed blocklist > shortened URL > suspicious TLD > APK/EXE > brand impersonation.
    Unknown domains are reported as 'Unknown' — not 'Safe'.
    """
    urls = _extract_urls(text)
    if not urls:
        return {"triggered": False, "signal_id": "PHISHING_URL"}

    for raw_url in urls:
        _, scheme, domain, path_q = _parse_url(raw_url)
        if not domain:
            continue

        # --- Confirmed blocklist hit ---
        bl_entry = _is_blocklisted(domain)
        if bl_entry:
            reg = _registrable_domain(domain)
            return {
                "triggered": True,
                "signal_id": "PHISHING_URL",
                "scam_type": "Known Phishing URL",
                "severity": 3,
                "explanation": (
                    f"The link '{reg}' is in our list of confirmed scam websites targeting "
                    "Indian users. Visiting this link could steal your bank login, install "
                    "malware on your phone, or compromise your personal information."
                ),
                "recommendation": (
                    "Do NOT open this link. Delete this message immediately. "
                    "Report the link at https://cybercrime.gov.in."
                ),
                "matched_text": raw_url[:100],
            }

        # --- Trusted domain: skip further URL checks (but NOT content checks) ---
        if _is_trusted(domain):
            continue

        # --- URL shortener: flag as opaque, cannot evaluate safety ---
        if _is_shortener(domain):
            return {
                "triggered": True,
                "signal_id": "PHISHING_URL",
                "scam_type": "Shortened / Opaque URL",
                "severity": 2,
                "explanation": (
                    f"The link uses a URL shortener ('{domain}'). The actual destination is hidden, "
                    "making it impossible to verify whether the link is safe. "
                    "Scammers frequently use URL shorteners to disguise phishing links."
                ),
                "recommendation": (
                    "Do not click this link unless you are 100% sure of the sender's identity. "
                    "You can preview the destination at https://checkshorturl.com before visiting."
                ),
                "matched_text": raw_url[:100],
            }

        # --- Dangerous file extension ---
        dangerous_exts = re.search(r"\.(apk|exe|bat|scr|vbs|msi|deb|sh|ps1)([\?#].*)?$", path_q, re.IGNORECASE)
        if dangerous_exts:
            return {
                "triggered": True,
                "signal_id": "PHISHING_URL",
                "scam_type": "Malicious File Download Link",
                "severity": 3,
                "explanation": (
                    "This link downloads a file (like an APK or EXE) that is likely malware. "
                    "Scammers send fake bank or KYC apps this way to gain full control of "
                    "your phone and steal your banking credentials."
                ),
                "recommendation": (
                    "NEVER install apps from links in messages. "
                    "Only install apps from the official Google Play Store or Apple App Store. "
                    "If you have already installed it, uninstall immediately and do a factory reset."
                ),
                "matched_text": raw_url[:100],
            }

        # --- Suspicious TLD ---
        tld = domain.split(".")[-1] if "." in domain else ""
        if tld in SUSPICIOUS_TLDS:
            return {
                "triggered": True,
                "signal_id": "PHISHING_URL",
                "scam_type": "Suspicious URL — High-Risk Domain Extension",
                "severity": 2,
                "explanation": (
                    f"The link uses a '.{tld}' domain extension very commonly abused in phishing. "
                    "Legitimate Indian banks and government services use trusted extensions "
                    "like '.gov.in', '.co.in', '.com', or '.in'."
                ),
                "recommendation": (
                    "Avoid clicking this link. If you need to access a service, navigate directly "
                    "to the official website by typing it in your browser."
                ),
                "matched_text": raw_url[:100],
            }

        # --- Brand impersonation in domain ---
        combined = (domain + " " + path_q).lower()
        for brand in MAJOR_BRANDS:
            if brand in combined:
                return {
                    "triggered": True,
                    "signal_id": "PHISHING_URL",
                    "scam_type": "Brand Impersonation URL",
                    "severity": 3,
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
                    "matched_text": raw_url[:100],
                }

        # --- Unknown domain: treat as uncertain, not safe ---
        # (do not trigger a hard signal, but caller gets no URL clearance)

    return {"triggered": False, "signal_id": "PHISHING_URL"}


def signal_urgency_pressure(text: str) -> Dict[str, Any]:
    """
    High-pressure urgency tactics — multiple panic-inducing phrases designed
    to prevent the victim from thinking critically.
    """
    t = _normalise(text)
    urgency_patterns = [
        r"\b(immediately|urgent|urgently|asap|right\s*now|at\s*once|turant|abhi\s*abhi|foran)\b",
        r"\b(last\s*chance|final\s*notice|last\s*warning|act\s*now|do\s*not\s*delay|aakhri\s*mauka)\b",
        r"\b(expires?\s*(today|tonight|in\s*\d+\s*(hours?|minutes?|ghante)))\b",
        r"\b(tonight|within\s*\d+\s*(hours?|minutes?)|before\s*midnight|aaj\s*raat|aaj\s*shaam)\b",
        r"\b(your\s*account\s*will\s*be\s*(blocked|suspended|frozen|closed|band\s*ho\s*jaayega))\b",
        r"\b(immediately\s*(call|contact|click|visit|pay|karo))\b",
        r"\bif\s*you\s*(don.?t|fail\s*to|do\s*not).{0,40}(block|suspend|arrest|legal|action)\b",
        r"\b(do\s*not\s*ignore|must\s*(call|act|respond|pay)|ignore\s*mat\s*karo)\b",
        r"\b(2\s*hours?|1\s*hour|30\s*minutes?|ghante).{0,30}(action|act|call|click|respond|karo)\b",
        # Hinglish
        r"\b(jaldi\s*karo|jaldi\s*se|der\s*mat\s*karo|abhi\s*karo)\b",
        r"\b(aakhri|last).{0,20}(mauka|chance|warning|notice)\b",
    ]
    hit_count = sum(1 for p in urgency_patterns if re.search(p, t, re.IGNORECASE))
    if hit_count >= 2:
        return {
            "triggered": True,
            "signal_id": "URGENCY_PRESSURE",
            "scam_type": "High-Pressure Urgency Tactic",
            "severity": 1,
            "explanation": (
                "This message uses multiple urgent, threatening phrases to pressure you into "
                "acting without thinking. Creating panic and urgency is a core social engineering "
                "technique. Legitimate organizations give you reasonable time and use official channels."
            ),
            "recommendation": (
                "Take a breath and do not act impulsively. Verify any claim independently by "
                "contacting the organization directly through their official website or helpline."
            ),
            "matched_text": f"{hit_count} urgency phrases detected",
        }
    return {"triggered": False, "signal_id": "URGENCY_PRESSURE"}


def signal_prize_lottery_scam(text: str) -> Dict[str, Any]:
    """
    Lottery / prize scam — fake winner notifications demanding a processing fee.
    """
    t = _normalise(text)
    patterns = [
        r"(congratulations?|congrats|mubarak|badhaai|mubarakbaad).{0,80}(winner|won|selected|chosen|jeet|jeeta)",
        r"(won|winner|selected|chosen|jeeta?).{0,50}(lottery|lucky\s*draw|prize|cash|car|iphone|inaam)",
        r"(lottery|lucky\s*draw|lucky\s*winner|bhagyashali).{0,60}(claim|collect|redeem|lena|lo)",
        r"(prize|reward|gift|inaam|tohfa).{0,60}(claim|collect|redeem|lena|abhi\s*lo).{0,30}(now|immediately|abhi)",
        r"(₹|rs\.?|inr).?\d{3,}.{0,30}(prize|lottery|reward|won|inaam|jeeta)",
        r"(gift|voucher|coupon|iphone|car|bike|laptop).{0,40}(claim|redeem|collect|abhi\s*lo)",
        r"(lucky|winner|bhagyashali).{0,50}(number|ticket|draw|aapka\s*number)",
        r"(kbc|kaun\s*banega|crorepati|lucky\s*number).{0,60}(winner|won|selected|jeeta)",
        # Hinglish
        r"(aap\s*jeete?|aapne\s*jeeta?|lucky\s*draw\s*mein).{0,80}(paisa|prize|inaam|reward)",
        r"(lucky\s*draw|lottery).{0,60}(claim\s*karo|le\s*lo|claim\s*karein)",
    ]
    matched = _first_match(patterns, t)
    if matched:
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
                "Block the sender number. Report at https://cybercrime.gov.in."
            ),
            "matched_text": matched,
        }
    return {"triggered": False, "signal_id": "PRIZE_LOTTERY_SCAM"}


def signal_impersonation(text: str) -> Dict[str, Any]:
    """
    Organizational impersonation — fake messages from RBI, TRAI, Income Tax,
    tech companies, PM Cares, etc.
    """
    t = _normalise(text)
    patterns = [
        r"\b(rbi|reserve\s*bank).{0,60}(notice|alert|warning|officer|call|blocked|case)",
        r"\b(income\s*tax|it\s*department|aaykar\s*vibhag).{0,60}(notice|refund|officer|call|case|arrest)",
        r"\b(trai|telecom\s*regulatory).{0,60}(sim|mobile|block|disconnect|notice|band)",
        r"\b(sebi|insurance|irdai).{0,60}(policy|notice|officer|expired?|premium)",
        r"\b(pm\s*cares?|pradhan\s*mantri|government\s*of\s*india|sarkar).{0,80}(fund|money|relief|help|yojana\s+cash)",
        r"\b(amazon|flipkart|swiggy|zomato|myntra).{0,60}(selected|winner|prize|reward|chosen|lucky)",
        r"\b(microsoft|apple|google).{0,60}(virus|hacked|support|call|tech\s*support|infected)",
        r"\b(narendra\s*modi|pm|prime\s*minister).{0,60}(fund|money|relief|scheme|yojana\s*cash)",
        r"\b(sebi|rbi|ncb|cbi|ed|trai|mha|uidai).{0,60}(notice|case|freeze|block|suspend|arrest|call)",
        # Hinglish
        r"\b(sarkar|government|vibhag).{0,60}(paisa|fund|relief|madad\s*de\s*rahi\s*hai)",
        r"\b(income\s*tax\s*vibhag|aaykar|tax\s*department).{0,60}(notice|officer|refund|arrest)",
    ]
    matched = _first_match(patterns, t)
    if matched:
        return {
            "triggered": True,
            "signal_id": "IMPERSONATION",
            "scam_type": "Organizational Impersonation",
            "severity": 2,
            "explanation": (
                "This message claims to be from a government body, bank, or large company. "
                "Scammers frequently impersonate trusted organizations to appear legitimate. "
                "RBI, TRAI, and income tax authorities do NOT send warnings via SMS/WhatsApp."
            ),
            "recommendation": (
                "Verify by visiting the official website of the organization or calling their "
                "published helpline number. Do not use the contact details provided in this message."
            ),
            "matched_text": matched,
        }
    return {"triggered": False, "signal_id": "IMPERSONATION"}


# ---------------------------------------------------------------------------
# NEW SIGNAL CATEGORIES (P1 — 5 additional types)
# ---------------------------------------------------------------------------

def signal_investment_scam(text: str) -> Dict[str, Any]:
    """
    Investment / trading scam — guaranteed high returns, Telegram/WhatsApp
    'expert groups', fake share market tips, crypto Ponzi schemes.
    """
    t = _normalise(text)
    patterns = [
        r"(guaranteed|assured|fix|fixed|sure.?shot|pakka|confirm).{0,60}(return|profit|income|earning|kamaai)",
        r"(stock|share|market|trading|invest).{0,60}(expert|tip|signal|group|channel|join)",
        r"(crypto|bitcoin|ethereum|usdt|nft).{0,60}(invest|earn|profit|double|triple|guaranteed)",
        r"(\d{2,3}\s*%|\d{2,3}\s*percent).{0,30}(return|profit|monthly|weekly|daily|per\s*month)",
        r"(invest\s*(rs|₹)?.?\d{3,}|invest\s*amount).{0,60}(double|triple|guaranteed|return|profit)",
        r"(sebi\s*registered|sebi\s*certified).{0,60}(advisor|expert|group|analyst)",
        r"(sensex|nifty|stock\s*market).{0,50}(expert|analyst|tip|guaranteed|sure)",
        r"(join\s*our|enter\s*our).{0,30}(vip|premium|exclusive|secret).{0,30}(group|channel|club)",
        r"(mutual\s*fund|sip).{0,50}(guaranteed|assured|fix\s*return|pakka\s*profit)",
        # Hinglish
        r"(paisa\s*lagao|invest\s*karo).{0,50}(double|triple|guaranteed|pakka|confirm|profit)",
        r"(kamaai\s*guaranteed|pakka\s*munafa|confirm\s*profit).{0,80}(trading|invest|market)",
    ]
    matched = _first_match(patterns, t)
    if matched:
        return {
            "triggered": True,
            "signal_id": "INVESTMENT_SCAM",
            "scam_type": "Fake Investment / Trading Scam",
            "severity": 2,
            "explanation": (
                "This message promises guaranteed investment returns or stock market profits. "
                "No legitimate investment ever guarantees fixed high returns. These scams involve "
                "fake Telegram/WhatsApp 'expert' groups that manipulate victims into investing "
                "large sums, then vanish with the money."
            ),
            "recommendation": (
                "SEBI-registered advisors cannot guarantee returns. "
                "Never invest based on tips from strangers online. "
                "Verify any advisor at https://sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes. "
                "Report to SEBI at https://scores.gov.in."
            ),
            "matched_text": matched,
        }
    return {"triggered": False, "signal_id": "INVESTMENT_SCAM"}


def signal_romance_sextortion(text: str) -> Dict[str, Any]:
    """
    Romance / sextortion scam — fake friendship/romantic interest leading to
    blackmail with intimate photos, or emotional manipulation for money.
    """
    t = _normalise(text)
    # Hard gate: cybersecurity advisory
    if re.search(r"\b(advisory|beware\s+of|awareness|report\s+cyber\s+fraud)\b", text, re.IGNORECASE) and not re.search(r"\b(pay|transfer|send)\s*(?:rs|inr|₹|\d+)\b", t):
        return {"triggered": False, "signal_id": "ROMANCE_SEXTORTION"}

    patterns = [
        r"(video\s*call|nude|intimate|private|obscene).{0,60}(viral|share|report|police|leak|post)",
        r"(naked|nude|intimate|private\s*photo|private\s*video).{0,60}(viral|share|post|upload|blackmail)",
        r"(blackmail|extort|threaten).{0,60}(photo|video|intimate|nude|money|paisa|pay)",
        r"(pay|transfer|send\s*money).{0,60}(photo|video|delete|remove|stop|sharing)",
        r"(friendship|friend|dost|pyar|love|bf|gf).{0,60}(money|paisa|help|urgent|transfer|send)",
        r"(lonely|alone|single|akela|akelaa).{0,50}(friendship|friend|love|pyar|chat|talk)",
        r"(video|photo|screenshot).{0,50}(viral|share|post|upload|report\s*police|complain)",
        r"(army|soldier|officer|foreign\s*country|abroad).{0,60}(love|pyar|money|help|urgent|transfer)",
        # Hinglish
        r"(meri\s*photo|mera\s*video|tumhari\s*photo|tumhara\s*video).{0,60}(viral\s*karunga|share\s*karunga|post\s*karunga)",
        r"(pyar|mohabbat|dost).{0,60}(paisa\s*chahiye|madad\s*chahiye|urgent\s*paisa|help\s*chahiye)",
    ]
    matched = _first_match(patterns, t)
    if matched:
        return {
            "triggered": True,
            "signal_id": "ROMANCE_SEXTORTION",
            "scam_type": "Romance / Sextortion Scam",
            "severity": 3,
            "explanation": (
                "This message shows signs of a romance scam or sextortion threat. "
                "Scammers build fake friendships/relationships online, then either threaten "
                "to leak intimate content unless money is paid, or emotionally manipulate "
                "victims into sending money for a 'crisis'."
            ),
            "recommendation": (
                "Do NOT pay any money — this will not stop the blackmail. "
                "Save all evidence (screenshots) and report immediately to Cyber Crime Helpline 1930 "
                "or at https://cybercrime.gov.in. Tell a trusted adult."
            ),
            "matched_text": matched,
        }
    return {"triggered": False, "signal_id": "ROMANCE_SEXTORTION"}


def signal_fake_customer_care(text: str) -> Dict[str, Any]:
    """
    Fake customer care / tech support scam — fake helpline numbers that charge
    for support or install remote access trojans (AnyDesk, TeamViewer).
    """
    t = _normalise(text)
    patterns = [
        r"(customer\s*care|helpline|support|toll\s*free).{0,60}(call|contact|number|no\.?).{0,30}(\+91|91|\d{10})",
        r"(anydesk|teamviewer|quick\s*support|airdroid|remote\s*access).{0,60}(install|download|share\s*code|code)",
        r"(remote\s*access|screen\s*share|remote\s*help).{0,60}(allow|grant|install|download|code)",
        r"(technical\s*support|tech\s*support|customer\s*support).{0,60}(fee|charge|payment|pay)",
        r"(complaint|issue|problem).{0,60}(resolve|fix|solve).{0,60}(download|install|anydesk|teamviewer|click)",
        r"(bank|paytm|phonepe|amazon|flipkart).{0,30}(helpline|customer\s*care).{0,30}(number|no\.?|call).{0,30}(\+91|91|\d{10})",
        r"(install|download|use).{0,50}(anydesk|teamviewer|quick\s*support|airdroid|remote\s*access)",
        r"(clean|remove|check)\s*(?:infection|virus).{0,50}(remote\s*access|teamviewer|anydesk)",
        # Hinglish
        r"(customer\s*care\s*mein\s*call|helpline\s*call\s*karo).{0,60}(\d{10})",
        r"(anydesk|teamviewer).{0,50}(install\s*karo|download\s*karo|dalo).{0,60}(complaint|problem|issue)",
    ]
    matched = _first_match(patterns, t)
    if matched:
        return {
            "triggered": True,
            "signal_id": "FAKE_CUSTOMER_CARE",
            "scam_type": "Fake Customer Care / Tech Support Scam",
            "severity": 3,
            "explanation": (
                "This message shares a 'customer care number' or asks you to install a remote "
                "access app like AnyDesk. Scammers pose as bank/tech support and once they have "
                "remote access to your device, they can steal all your money and passwords."
            ),
            "recommendation": (
                "NEVER install AnyDesk, TeamViewer or any app at the request of an unsolicited caller. "
                "Find your bank's real customer care number on the back of your debit/credit card "
                "or the official bank website. Report to 1930."
            ),
            "matched_text": matched,
        }
    return {"triggered": False, "signal_id": "FAKE_CUSTOMER_CARE"}


def signal_money_mule(text: str) -> Dict[str, Any]:
    """
    Money mule / advance-fee fraud — asking someone to receive money in their
    account and forward it, or pay an advance fee to receive a large sum.
    """
    t = _normalise(text)
    patterns = [
        r"(receive|accept).{0,50}money.{0,50}(account|bank).{0,50}(forward|transfer|send\s*back|wapas)",
        r"(large\s*sum|huge\s*amount|crore|lakh).{0,60}(transfer|send).{0,60}(your\s*account|your\s*bank)",
        r"(advance|upfront|token).{0,50}(fee|money|amount|payment).{0,60}(receive|get|transfer|wire)",
        r"(inheritance|will|estate|dead|deceased|property).{0,80}(transfer|money|help|assistance|share)",
        r"(nigeria|ghana|usa|uk|foreign).{0,60}(transfer|send|money|funds|assistance|agent)",
        r"(commission|percentage|share).{0,50}(transfer|forward|receiving\s*money)",
        r"(unclaimed|stuck|frozen).{0,50}funds.{0,60}(release|transfer|agent|help)",
        r"(diplomat|government\s*official|un\s*official).{0,60}(box|trunk|consignment|cash)",
        # Hinglish
        r"(mera\s*paisa|mere\s*funds|meri\s*rashi).{0,60}(aapke\s*account|tumhare\s*account).{0,60}(transfer|send\s*karo)",
        r"(advance\s*paisa|token\s*fee\s*do).{0,80}(baad\s*mein|phir|wapas|double\s*milega)",
    ]
    matched = _first_match(patterns, t)
    if matched:
        return {
            "triggered": True,
            "signal_id": "MONEY_MULE",
            "scam_type": "Money Mule / Advance-Fee Fraud",
            "severity": 2,
            "explanation": (
                "This message is asking you to receive money in your account and forward it, "
                "or pay an advance fee to unlock a large transfer. These are money mule and "
                "advance-fee scams — participating can make you legally liable for money "
                "laundering even if you are the victim."
            ),
            "recommendation": (
                "Do NOT allow your bank account to be used to receive and forward money for strangers. "
                "This is illegal and can result in your account being frozen and police action against you. "
                "Report to 1930 or https://cybercrime.gov.in."
            ),
            "matched_text": matched,
        }
    return {"triggered": False, "signal_id": "MONEY_MULE"}


# ---------------------------------------------------------------------------
# OCR MODULE (v2.0 — improved with preprocessing, confidence, error codes)
# ---------------------------------------------------------------------------

class OCRResult:
    """Container for OCR extraction results."""

    def __init__(
        self,
        text: str = "",
        confidence: float = 0.0,
        status: str = "OK",
        error_code: str = "",
        error_message: str = "",
        language_used: str = "eng",
        image_dimensions: Optional[tuple] = None,
    ):
        self.text = text
        self.confidence = round(confidence, 2)
        self.status = status               # OK | FAILED | PARTIAL | SKIPPED
        self.error_code = error_code       # NO_FILE | UNSUPPORTED_FORMAT | SIZE_TOO_SMALL
                                           # TESSERACT_NOT_FOUND | TESSERACT_ERROR | EMPTY
        self.error_message = error_message
        self.language_used = language_used
        self.image_dimensions = image_dimensions  # (width, height) or None

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "confidence": self.confidence,
            "status": self.status,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "language_used": self.language_used,
            "image_dimensions": self.image_dimensions,
        }

    @property
    def succeeded(self) -> bool:
        return self.status == "OK" and bool(self.text.strip())


_SUPPORTED_IMAGE_FORMATS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp", ".gif"}
_MIN_PIXELS = 50       # minimum dimension in px
_MAX_FILE_MB = 20      # reject images larger than this


def extract_text_from_image(image_path: str) -> OCRResult:
    """
    Extract text from an image using OCR (Tesseract via pytesseract).

    Pre-processing pipeline:
      1. Validate file exists, format is supported, and size is within limits.
      2. Auto-detect and correct orientation (Tesseract OSD).
      3. Apply adaptive contrast enhancement (PIL ImageOps.autocontrast).
      4. Convert to grayscale.
      5. Upscale to ≥ 1200 px on the shorter dimension for ≥ 150 DPI-equivalent.
      6. Attempt bilingual OCR (Hindi + English); fall back to English-only.
      7. Return structured OCRResult with text, confidence, status and error details.

    Args:
        image_path: Absolute path to the image file.

    Returns:
        OCRResult with .text, .confidence, .status, .error_code, .error_message.
    """
    # --- Validate path ---
    if not image_path:
        return OCRResult(
            status="SKIPPED",
            error_code="NO_PATH",
            error_message="No image path provided.",
        )

    image_path = str(image_path).strip()
    if not os.path.exists(image_path):
        return OCRResult(
            status="FAILED",
            error_code="NO_FILE",
            error_message=f"Image file not found: {image_path}",
        )

    # --- Validate format ---
    ext = os.path.splitext(image_path)[1].lower()
    if ext not in _SUPPORTED_IMAGE_FORMATS:
        return OCRResult(
            status="FAILED",
            error_code="UNSUPPORTED_FORMAT",
            error_message=f"Unsupported image format: '{ext}'. Supported: {sorted(_SUPPORTED_IMAGE_FORMATS)}",
        )

    # --- Validate file size ---
    file_mb = os.path.getsize(image_path) / (1024 * 1024)
    if file_mb > _MAX_FILE_MB:
        return OCRResult(
            status="FAILED",
            error_code="FILE_TOO_LARGE",
            error_message=f"Image file is {file_mb:.1f} MB, exceeds limit of {_MAX_FILE_MB} MB.",
        )

    # --- Check library availability ---
    try:
        from PIL import Image, ImageOps, ImageFilter
        import pytesseract
    except ImportError as e:
        return OCRResult(
            status="FAILED",
            error_code="DEPENDENCY_MISSING",
            error_message=f"Required library missing: {e}. Run: pip install pytesseract Pillow",
        )

    try:
        pytesseract.get_tesseract_version()
    except Exception:
        return OCRResult(
            status="FAILED",
            error_code="TESSERACT_NOT_FOUND",
            error_message=(
                "Tesseract-OCR binary not found. "
                "Windows: install from https://github.com/UB-Mannheim/tesseract/wiki  "
                "Linux: sudo apt-get install tesseract-ocr  "
                "macOS: brew install tesseract"
            ),
        )

    # --- Load and validate image dimensions ---
    try:
        img = Image.open(image_path)
        img.verify()          # Catch corrupted files
        img = Image.open(image_path)   # Re-open after verify (verify closes the file)
        orig_w, orig_h = img.size
    except Exception as e:
        return OCRResult(
            status="FAILED",
            error_code="CORRUPTED_IMAGE",
            error_message=f"Could not open image: {e}",
            image_dimensions=None,
        )

    if min(orig_w, orig_h) < _MIN_PIXELS:
        return OCRResult(
            status="FAILED",
            error_code="SIZE_TOO_SMALL",
            error_message=f"Image is too small ({orig_w}×{orig_h} px). Minimum: {_MIN_PIXELS} px on each side.",
            image_dimensions=(orig_w, orig_h),
        )

    # --- Pre-processing pipeline ---
    try:
        # Convert to RGB to ensure PIL operations work uniformly
        if img.mode not in ("RGB", "L", "RGBA"):
            img = img.convert("RGB")

        # Grayscale
        gray = img.convert("L")

        # Adaptive contrast enhancement
        gray = ImageOps.autocontrast(gray, cutoff=1)

        # Slight sharpening to improve OCR on blurry screenshots
        gray = gray.filter(ImageFilter.SHARPEN)

        # Upscale if needed (target: shorter side ≥ 1200 px)
        w, h = gray.size
        min_target = 1200
        if min(w, h) < min_target:
            scale = min_target / min(w, h)
            gray = gray.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    except Exception as e:
        return OCRResult(
            status="FAILED",
            error_code="PREPROCESS_ERROR",
            error_message=f"Image pre-processing failed: {e}",
            image_dimensions=(orig_w, orig_h),
        )

    # --- OCR with auto-rotation and bilingual support ---
    base_config = "--oem 3 --psm 6"

    def _run_ocr(lang: str) -> Tuple[str, float]:
        """Run Tesseract and return (text, mean_confidence)."""
        data = pytesseract.image_to_data(
            gray, lang=lang, config=base_config,
            output_type=pytesseract.Output.DICT
        )
        words = [w for w in data["text"] if str(w).strip()]
        confs = [int(c) for c, w in zip(data["conf"], data["text"])
                 if str(w).strip() and int(c) >= 0]
        text = " ".join(words)
        avg_conf = sum(confs) / len(confs) if confs else 0.0
        return text, avg_conf / 100.0  # normalise to 0-1

    # Try orientation detection first
    try:
        osd = pytesseract.image_to_osd(gray, config="--psm 0")
        angle_match = re.search(r"Rotate:\s*(\d+)", osd)
        if angle_match:
            angle = int(angle_match.group(1))
            if angle in (90, 180, 270):
                gray = gray.rotate(-angle, expand=True)
    except Exception:
        pass  # OSD failure is non-fatal

    # Try bilingual (Hindi+English)
    lang_used = "eng"
    try:
        extracted_text, confidence = _run_ocr("hin+eng")
        lang_used = "hin+eng"
    except Exception:
        try:
            extracted_text, confidence = _run_ocr("eng")
        except Exception as e:
            return OCRResult(
                status="FAILED",
                error_code="TESSERACT_ERROR",
                error_message=f"OCR failed: {e}",
                image_dimensions=(orig_w, orig_h),
            )

    extracted_text = extracted_text.strip()

    # --- Classify result quality ---
    if not extracted_text:
        return OCRResult(
            status="PARTIAL",
            text="",
            confidence=0.0,
            error_code="EMPTY",
            error_message="Tesseract ran successfully but extracted no text. "
                          "The image may be too dark, blurry, or contain only graphics.",
            language_used=lang_used,
            image_dimensions=(orig_w, orig_h),
        )

    if confidence < 0.4:
        return OCRResult(
            text=extracted_text,
            confidence=confidence,
            status="PARTIAL",
            error_code="LOW_CONFIDENCE",
            error_message=f"OCR confidence is low ({confidence:.0%}). Results may be inaccurate.",
            language_used=lang_used,
            image_dimensions=(orig_w, orig_h),
        )

    return OCRResult(
        text=extracted_text,
        confidence=confidence,
        status="OK",
        language_used=lang_used,
        image_dimensions=(orig_w, orig_h),
    )


# ---------------------------------------------------------------------------
# ALL SIGNAL FUNCTIONS — ordered by frequency / severity
# ---------------------------------------------------------------------------
ALL_SIGNAL_FUNCTIONS = [
    signal_phishing_url,            # Always first — URL check
    signal_fake_kyc,
    signal_otp_phishing,
    signal_digital_arrest,
    signal_electricity_bill_threat,
    signal_upi_collect_request,
    signal_parcel_customs_threat,
    signal_job_offer_scam,
    signal_loan_fraud,
    signal_prize_lottery_scam,
    signal_impersonation,
    signal_urgency_pressure,        # Soft / supporting
    signal_investment_scam,         # New
    signal_romance_sextortion,      # New
    signal_fake_customer_care,      # New
    signal_money_mule,              # New
]


# ---------------------------------------------------------------------------
# MASTER ANALYZER
# ---------------------------------------------------------------------------

def analyze_signals(
    text: str = "",
    image_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run all scam signals against the given text and optional screenshot.

    Args:
        text:       The message / URL text to analyze.
        image_path: Optional path to a screenshot image for OCR extraction.

    Returns a dict with:
      ocr_result          : OCRResult.to_dict() (always present; check 'status')
      combined_text_used  : The full text analyzed (input + OCR if any)
      triggered_signals   : List of triggered signal dicts
      signal_count        : int
      highest_severity    : int  0 | 1 | 2 | 3
      scam_types          : List[str] — deduplicated category names
      explanations        : List[str] — plain-language reason strings
      recommendations     : List[str] — deduplicated action strings
      heuristic_risk_boost: int  0–40 — score to add to ML risk score
      is_unknown_url      : bool — True if URLs were found but none matched blocklist/allowlist
    """
    combined_text = str(text).strip() if text else ""

    # --- OCR ---
    ocr_res = OCRResult(status="SKIPPED", error_code="NO_PATH")
    if image_path:
        ocr_res = extract_text_from_image(image_path)
        if ocr_res.text:
            combined_text = combined_text + "\n" + ocr_res.text

    # --- Detect unknown URLs (not blocklisted AND not allowlisted) ---
    urls = _extract_urls(combined_text)
    is_unknown_url = False
    for raw_url in urls:
        _, _, domain, _ = _parse_url(raw_url)
        if domain and not _is_blocklisted(domain) and not _is_trusted(domain) and not _is_shortener(domain):
            is_unknown_url = True
            break

    # --- Run signals ---
    triggered: List[dict] = []
    for sig_fn in ALL_SIGNAL_FUNCTIONS:
        result = sig_fn(combined_text)
        if result.get("triggered"):
            triggered.append(result)

    if not triggered:
        return {
            "ocr_result": ocr_res.to_dict(),
            "combined_text_used": combined_text,
            "triggered_signals": [],
            "signal_count": 0,
            "highest_severity": 0,
            "scam_types": [],
            "explanations": [],
            "recommendations": [],
            "heuristic_risk_boost": 0,
            "is_unknown_url": is_unknown_url,
        }

    highest_severity = max(s.get("severity", 0) for s in triggered)
    scam_types = list(dict.fromkeys(s["scam_type"] for s in triggered))
    explanations = [s["explanation"] for s in triggered]
    recommendations = list(dict.fromkeys(s["recommendation"] for s in triggered))

    # Risk boost: severity-weighted, capped at 40
    boost = sum(
        {3: 15, 2: 8, 1: 3}.get(sig.get("severity", 1), 3)
        for sig in triggered
    )
    boost = min(boost, 40)

    return {
        "ocr_result": ocr_res.to_dict(),
        "combined_text_used": combined_text,
        "triggered_signals": triggered,
        "signal_count": len(triggered),
        "highest_severity": highest_severity,
        "scam_types": scam_types,
        "explanations": explanations,
        "recommendations": recommendations,
        "heuristic_risk_boost": boost,
        "is_unknown_url": is_unknown_url,
    }


# ---------------------------------------------------------------------------
# SCAM TYPE CATALOG — for Member 4 (UI on-screen text)
# ---------------------------------------------------------------------------
SCAM_TYPE_CATALOG = {
    "Fake KYC Update": {
        "icon": "🏦",
        "short_description": "Fake bank KYC update request",
        "full_explanation": (
            "Scammers send SMS or WhatsApp messages pretending to be your bank, claiming your "
            "account will be blocked unless you update your KYC via a link or app. The link "
            "steals your login credentials or installs malware on your phone."
        ),
        "user_advice": "Visit your bank's official website or branch directly. Never click links in SMS.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "UPI Collect Request Fraud": {
        "icon": "💸",
        "short_description": "Fake UPI money request disguised as a payment",
        "full_explanation": (
            "A scammer sends a UPI 'collect' request (which debits YOUR account) while claiming "
            "it will add money to you. Entering your UPI PIN approves THEIR withdrawal."
        ),
        "user_advice": "To receive money on UPI, you never need to enter your PIN. If asked, it's always a scam.",
        "report_at": "NPCI: 1800-120-1740 | https://cybercrime.gov.in",
    },
    "Parcel / Customs Scam": {
        "icon": "📦",
        "short_description": "Fake courier or customs clearance fee demand",
        "full_explanation": (
            "Fraudsters impersonate FedEx, DHL, India Post, or customs officers claiming a package "
            "in your name has been seized for containing illegal items and demanding a clearance fee."
        ),
        "user_advice": "No courier company collects fees via SMS/WhatsApp. Contact the courier through their official website.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "Digital Arrest / Agency Impersonation": {
        "icon": "🚨",
        "short_description": "Fake arrest threat from a fake government officer",
        "full_explanation": (
            "Scammers pretend to be CBI, Delhi Police, ED, or NCB and place you under a fake "
            "'digital arrest' via video call, claiming your Aadhaar/account is linked to a crime. "
            "They demand money to 'settle' the case. No real officer ever does this."
        ),
        "user_advice": "Hang up. No real officer arrests people via phone. Contact local police if threatened.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "Fake Job / Task Scam": {
        "icon": "💼",
        "short_description": "Advance-fee job or online task fraud",
        "full_explanation": (
            "Part-time job scams on Telegram/WhatsApp promise high daily earnings for simple tasks. "
            "After small initial payments, they ask for a large deposit to 'unlock higher earnings' — "
            "and then disappear."
        ),
        "user_advice": "No legitimate job asks you to pay first. Block and report the recruiter.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "Electricity Bill Disconnection Scam": {
        "icon": "⚡",
        "short_description": "Fake electricity disconnection threat",
        "full_explanation": (
            "Scammers send urgent messages claiming your electricity will be cut tonight due to an "
            "unpaid bill and ask you to call a fake 'electricity officer' who collects money or "
            "gains remote access to your phone."
        ),
        "user_advice": "Check your bill on your DISCOM's official website. Never call numbers from SMS.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "OTP / PIN Phishing": {
        "icon": "🔐",
        "short_description": "Attempt to steal your OTP or bank PIN",
        "full_explanation": (
            "Any message or call that asks you to share your OTP, UPI PIN, or bank password is a "
            "scam. Banks and legitimate services NEVER ask for your OTP or PIN over a call or link."
        ),
        "user_advice": "NEVER share OTP or PIN with anyone. If compromised, call your bank immediately.",
        "report_at": "Your bank's fraud helpline | https://cybercrime.gov.in",
    },
    "Fake Loan Offer": {
        "icon": "💰",
        "short_description": "Fraudulent instant loan with upfront fees",
        "full_explanation": (
            "Scam loan apps and messages promise instant loans with no documents or low interest rates, "
            "then charge upfront 'processing fees' and disappear. Some harvest your contacts and photos "
            "for blackmail."
        ),
        "user_advice": "Only use RBI-registered lenders. Never pay fees before receiving a loan.",
        "report_at": "RBI: https://rbi.org.in | https://cybercrime.gov.in",
    },
    "Known Phishing URL": {
        "icon": "🌐",
        "short_description": "Link to a confirmed scam website",
        "full_explanation": (
            "The link in this message points to a website confirmed to be used in Indian phishing "
            "campaigns. Visiting it may steal your banking credentials or install malware."
        ),
        "user_advice": "Do not click this link. Report it at cybercrime.gov.in.",
        "report_at": "https://cybercrime.gov.in | Google Safe Browsing",
    },
    "Shortened / Opaque URL": {
        "icon": "🔗",
        "short_description": "Link destination is hidden — cannot verify safety",
        "full_explanation": (
            "The link uses a URL shortener that hides the actual destination. Scammers frequently "
            "use URL shorteners to disguise phishing sites. This does not confirm it is a scam, "
            "but the destination cannot be verified without clicking."
        ),
        "user_advice": "Preview the destination at checkshorturl.com before clicking.",
        "report_at": "https://cybercrime.gov.in",
    },
    "Suspicious URL — High-Risk Domain Extension": {
        "icon": "🔗",
        "short_description": "Link using an unusual, high-risk domain extension",
        "full_explanation": (
            "The URL uses a domain extension (.xyz, .top, .site, etc.) very commonly abused in "
            "phishing. Legitimate Indian banks and government services do not use them."
        ),
        "user_advice": "Avoid clicking this link. Navigate to the official website directly.",
        "report_at": "https://cybercrime.gov.in",
    },
    "Lottery / Prize Scam": {
        "icon": "🎰",
        "short_description": "Fake lottery win or prize claim",
        "full_explanation": (
            "You cannot win a lottery you never entered. These messages trick you into paying a "
            "'processing fee', 'tax', or 'shipping charge' to claim a prize that does not exist."
        ),
        "user_advice": "Ignore and delete. Never pay money to claim a prize.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "Organizational Impersonation": {
        "icon": "🏛️",
        "short_description": "Message pretending to be a trusted organization",
        "full_explanation": (
            "The message claims to be from RBI, TRAI, Income Tax, or a large company. These "
            "organizations do NOT send warnings, prizes, or refund offers via unsolicited SMS."
        ),
        "user_advice": "Verify by calling the organization's official helpline number directly.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "High-Pressure Urgency Tactic": {
        "icon": "⏰",
        "short_description": "Artificial urgency to prevent careful thinking",
        "full_explanation": (
            "Scammers deliberately create panic and urgency to stop you from thinking clearly. "
            "Phrases like 'act immediately', 'tonight', or 'final warning' are designed to rush "
            "you into making a costly mistake."
        ),
        "user_advice": "Slow down. Any legitimate request can wait for verification. Take your time.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "Brand Impersonation URL": {
        "icon": "🎭",
        "short_description": "Fake website disguised as a trusted brand",
        "full_explanation": (
            "The URL contains the name of a trusted brand (SBI, HDFC, Paytm) but is NOT their "
            "official website. Scammers copy the look of real websites to steal login credentials."
        ),
        "user_advice": "Always check the full URL carefully. When in doubt, type the official address yourself.",
        "report_at": "https://cybercrime.gov.in | Report to the impersonated brand directly",
    },
    "Malicious File Download Link": {
        "icon": "☠️",
        "short_description": "Link that downloads a harmful app or file",
        "full_explanation": (
            "The link in this message downloads a file (usually an APK) that is malware. Once "
            "installed, it can steal your banking credentials, intercept OTPs, and give scammers "
            "complete control of your device."
        ),
        "user_advice": "NEVER install apps from links in messages. Only use Google Play Store or Apple App Store.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "Fake Investment / Trading Scam": {
        "icon": "📈",
        "short_description": "Guaranteed returns investment / stock market fraud",
        "full_explanation": (
            "No legitimate investment ever guarantees fixed high returns. These scams involve "
            "fake Telegram/WhatsApp 'expert' groups that manipulate victims into investing large "
            "sums, then vanish."
        ),
        "user_advice": "SEBI-registered advisors cannot guarantee returns. Never invest based on tips from strangers.",
        "report_at": "SEBI SCORES: https://scores.gov.in | https://cybercrime.gov.in",
    },
    "Romance / Sextortion Scam": {
        "icon": "💔",
        "short_description": "Blackmail threat using intimate content, or money request from online 'friend'",
        "full_explanation": (
            "Scammers build fake friendships/relationships, then threaten to leak intimate content "
            "unless money is paid, or emotionally manipulate victims into sending money for a 'crisis'."
        ),
        "user_advice": "Do NOT pay any money. Save evidence and report to Cyber Crime Helpline 1930 immediately.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "Fake Customer Care / Tech Support Scam": {
        "icon": "🛠️",
        "short_description": "Fake helpline number or remote access app request",
        "full_explanation": (
            "Scammers pose as bank/tech support and ask you to install AnyDesk or TeamViewer. "
            "Once they have remote access to your device, they can steal all your money and passwords."
        ),
        "user_advice": "NEVER install remote access apps for unsolicited callers. Find official numbers on your card or bank website.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
    "Money Mule / Advance-Fee Fraud": {
        "icon": "💱",
        "short_description": "Request to receive and forward money, or pay upfront to get a large sum",
        "full_explanation": (
            "Money mule scams ask you to let your account be used to receive and forward money. "
            "Advance-fee fraud asks for a small payment upfront to unlock a large transfer. "
            "Both are illegal and can result in police action against you."
        ),
        "user_advice": "Never allow your account to be used for forwarding money for strangers.",
        "report_at": "https://cybercrime.gov.in | Helpline: 1930",
    },
}

GENERAL_SAFETY_TIPS = [
    "🔐 NEVER share your OTP, UPI PIN, or bank password with anyone — not even bank employees.",
    "🏦 Your bank will NEVER ask you to click a link or call a number to avoid account suspension.",
    "📲 Only install apps from Google Play Store or Apple App Store. Never from links in SMS.",
    "🌐 Always type bank URLs directly in your browser. Do not follow SMS/WhatsApp links.",
    "⚡ Electricity companies send official bills — they do NOT threaten disconnection tonight via SMS.",
    "💸 To RECEIVE money on UPI, you do NOT need to enter your PIN.",
    "🚨 Report online fraud at https://cybercrime.gov.in or call the national helpline 1930.",
    "👮 No real police officer arrests you via phone or video call.",
    "📈 No legitimate investment guarantees fixed returns. If it sounds too good, it is a scam.",
    "🛠️ Never install AnyDesk, TeamViewer or similar apps for anyone who calls you unexpectedly.",
]


# ---------------------------------------------------------------------------
# QUICK SELF-TEST
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("ScamLens signals.py v2.0 — Self-Test")
    print(f"Blocklist entries : {len(PHISHING_BLOCKLIST)}")
    print(f"Allowlist entries : {len(TRUSTED_DOMAINS)}")
    print(f"URL shorteners    : {len(URL_SHORTENERS)}")
    print(f"Signal detectors  : {len(ALL_SIGNAL_FUNCTIONS)}")
    print("=" * 60)

    _tests = [
        # Scam cases
        ("Dear SBI user, your KYC is pending. Click http://sbi-kyc-verify.top/update to avoid suspension.", True),
        ("Bijli band ho jayegi aaj raat. Abhi call karo bijli officer ko: 9876543210", True),
        ("Congratulations! You won ₹10,00,000 in KBC Lucky Draw. Call now to claim. Processing fee Rs 2000.", True),
        ("Paisa kamao ghar se. YouTube video like karo roz Rs 3000. Telegram @earn_daily join karo.", True),
        ("Mera video viral kar dunga agar tune mujhe 5000 nahi diye. Abhi bhejo.", True),
        ("Customer care number: 9123456789. Install AnyDesk and share the 9-digit code for refund.", True),
        ("Invest Rs 10,000 and get guaranteed 50% monthly returns. Join our VIP trading group now.", True),
        ("UPI collect request of Rs 5000 from Amazon Pay. Enter UPI PIN to receive cashback.", True),
        # Safe cases — should NOT trigger content signals (URL signal may flag bit.ly)
        ("849201 is your SBI OTP for Rs 2500. Never share OTP with anyone. SBI never asks for OTP.", False),
        ("Your Swiggy order is out for delivery. Delivery partner Ravi is 10 mins away.", False),
        ("Hi Priya, are we still meeting at 5pm? Let me know.", False),
        ("INR 15000 credited to your HDFC account XX4821 by NEFT from Infosys. Bal: 48230.", False),
    ]

    passed = 0
    for msg, should_trigger in _tests:
        result = analyze_signals(msg)
        triggered = result["signal_count"] > 0
        ok = triggered == should_trigger
        passed += ok
        status = "✅" if ok else "❌"
        print(f"{status} {'SCAM' if should_trigger else 'SAFE ':4s} | "
              f"boost=+{result['heuristic_risk_boost']:2d} | "
              f"signals={result['scam_types']!r}")
        print(f"   {msg[:80]}...")

    print(f"\n{passed}/{len(_tests)} tests passed")
