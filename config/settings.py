"""
ScamLens Centralized Configuration Module
Provides global configuration parameters for detection thresholds,
model paths, heuristic weights, and external cybersecurity feeds.
"""
import os
from pathlib import Path
from typing import Dict, Any

# Root paths
CONFIG_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CONFIG_DIR.parent

DATA_ML_DIR = PROJECT_ROOT / "Data And ML"
MODELS_DIR = DATA_ML_DIR / "models"
DETECTION_DIR = PROJECT_ROOT / "Detection Logic"
INTEGRATION_DIR = PROJECT_ROOT / "Integration App and Report"

# Model File Paths
TEXT_MODEL_PATH = MODELS_DIR / "text_model.joblib"
URL_MODEL_PATH = MODELS_DIR / "url_model.joblib"

# Global Scoring Thresholds
THRESHOLDS = {
    "scam_threshold": 70,       # Risk score >= 70 is classified as 'Scam' (Red 🚨)
    "suspicious_threshold": 40, # Risk score 40-69 is classified as 'Suspicious' (Amber ⚠️)
    "safe_threshold": 0         # Risk score 0-39 is classified as 'Safe' (Green ✅)
}

# Default Multimodal Fusion Weights (calibrated on Indian scam test cases)
FUSION_WEIGHTS = {
    "text_ml": 0.35,
    "heuristics": 0.35,
    "url_ml": 0.15,
    "url_rule": 0.15
}

# External Threat Feeds
FEEDS = {
    "openphish_url": "https://openphish.com/feed.txt",
    "national_cybercrime_portal": "https://cybercrime.gov.in",
    "national_helpline_number": "1930"
}

# Server and API Settings
SERVER = {
    "host": os.getenv("SCAMLENS_HOST", "0.0.0.0"),
    "port": int(os.getenv("SCAMLENS_PORT", "8000")),
    "debug": os.getenv("SCAMLENS_DEBUG", "False").lower() in ("true", "1")
}
