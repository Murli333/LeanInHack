# ScamLens REST API Specification

Base URL: `http://localhost:8000/api`

## Endpoints

### 1. Health Check
* **Route:** `GET /health`
* **Response:**
```json
{
  "status": "healthy",
  "version": "2.1.0",
  "models_loaded": true
}
```

### 2. Analyze Message / URL
* **Route:** `POST /analyze`
* **Content-Type:** `application/json`
* **Request Body:**
```json
{
  "message_text": "Dear SBI user, your YONO account is locked. Click http://sbi-kyc.top/sbi.apk",
  "url": "http://sbi-kyc.top/sbi.apk",
  "audio_transcript": null
}
```
* **Response (HTTP 200):**
```json
{
  "verdict": "Scam",
  "risk_score": 94,
  "status_color": "red",
  "icon": "🚨",
  "reasons": [
    "Demands urgent KYC verification under threat of account blocking.",
    "Directs to an untrusted external APK (.apk) bypassing app stores."
  ],
  "safety_tips": [
    "Never download APK files sent via SMS or WhatsApp.",
    "Report fraud at cybercrime.gov.in or call toll-free helpline 1930."
  ],
  "details": {
    "text_ml_score": 92,
    "url_ml_score": 96,
    "heuristic_score": 88
  }
}
```

### 3. Analyze Screenshot (Multipart Form)
* **Route:** `POST /analyze-image`
* **Content-Type:** `multipart/form-data`
* **Parameters:**
  * `file`: Binary image file (PNG, JPEG, WebP)
  * `message_text`: Optional string
  * `url`: Optional string
