"""
ScamLens FastAPI Service Layer (Backend)
Provides high-performance REST APIs for web and mobile frontends.
"""
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Ensure project paths are in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
for p in [
    str(BASE_DIR),
    str(BASE_DIR / "Data And ML"),
    str(BASE_DIR / "Data And ML" / "models"),
    str(BASE_DIR / "Data And ML" / "src"),
    str(BASE_DIR / "Detection Logic"),
    str(BASE_DIR / "Integration App and Report")
]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from fastapi import FastAPI, UploadFile, File, Form, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from backend.schemas import AnalyzeRequest, AnalyzeResponse, HealthResponse
    from scoring import analyze
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    from scoring import analyze

app = None
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="ScamLens Cybersecurity API",
        version="2.1.0",
        description="AI-powered digital fraud intelligence API detecting scams across SMS, URLs, screenshots, and audio transcripts."
    )

    # Enable CORS for cross-origin mobile and web frontend clients
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health", response_model=HealthResponse)
    def health_check():
        return {
            "status": "healthy",
            "version": "2.1.0",
            "models_loaded": True
        }

    @app.post("/api/analyze", response_model=AnalyzeResponse)
    def analyze_endpoint(request: AnalyzeRequest):
        try:
            result = analyze(
                message_text=request.message_text,
                url=request.url,
                audio_transcript=request.audio_transcript
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/analyze-image", response_model=AnalyzeResponse)
    async def analyze_image_endpoint(
        file: UploadFile = File(...),
        message_text: Optional[str] = Form(None),
        url: Optional[str] = Form(None)
    ):
        try:
            content = await file.read()
            result = analyze(
                message_text=message_text,
                url=url,
                image_input=content
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/samples")
    def get_quick_samples():
        """Pre-configured authentic Indian scam and genuine test cases for 1-click frontend testing."""
        return [
            {
                "id": "kyc_apk",
                "label": "Fake SBI KYC APK",
                "type": "scam",
                "text": "Dear SBI user, your YONO account is locked due to pending KYC update. Click http://sbi-kyc-verify.top/sbi.apk to update immediately.",
                "url": "http://sbi-kyc-verify.top/sbi.apk"
            },
            {
                "id": "electricity",
                "label": "Electricity Disconnection Threat",
                "type": "scam",
                "text": "Urgent: Electricity power will be disconnected at 9:30 PM from power office because your previous month bill was not updated. Please immediately contact our electricity officer 9876543210.",
                "url": None
            },
            {
                "id": "digital_arrest",
                "label": "Digital Arrest Extortion",
                "type": "scam",
                "text": "Delhi Police Cyber Cell: A parcel in your name containing illegal narcotics has been seized at Mumbai airport. Digital arrest warrant issued. Contact CBI Officer on Skype.",
                "url": "https://cbi-investigation.top/court"
            },
            {
                "id": "upi_pin",
                "label": "UPI Collect Request Fraud",
                "type": "scam",
                "text": "Dear Customer, you received UPI collect request of Rs 4999 from Amazon Pay. Enter your UPI PIN to receive money in your bank account.",
                "url": None
            },
            {
                "id": "sbi_otp",
                "label": "Genuine Bank Login OTP",
                "type": "safe",
                "text": "Dear Customer, 849201 is your one time password (OTP) for SBI Internet Banking login. Valid for 3 mins. Never share OTP with anyone.",
                "url": None
            },
            {
                "id": "swiggy",
                "label": "Genuine Food Delivery",
                "type": "safe",
                "text": "Dear Customer, your Swiggy order from Biryani Blues is out for delivery. Delivery partner Ravi will reach you shortly.",
                "url": None
            }
        ]


if __name__ == "__main__":
    if FASTAPI_AVAILABLE:
        import uvicorn
        print("[*] Starting ScamLens Backend API server on http://localhost:8000...")
        uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        print("[!] FastAPI/uvicorn not installed. To run backend API: pip install fastapi uvicorn python-multipart")
