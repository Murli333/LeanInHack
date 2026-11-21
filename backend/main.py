"""
ScamLens FastAPI Service Layer (Backend)
Provides high-performance REST APIs for web and mobile frontends.
Full lifecycle state management: IDLE -> VALIDATING -> PROCESSING -> COMPLETED / FAILED
"""
import os
import sys
import uuid
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

# Ensure project paths are in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
for p in [
    str(BASE_DIR),
    str(BASE_DIR / "backend"),
    str(BASE_DIR / "Data And ML"),
    str(BASE_DIR / "Data And ML" / "models"),
    str(BASE_DIR / "Data And ML" / "src"),
    str(BASE_DIR / "Detection Logic"),
    str(BASE_DIR / "Integration App and Report")
]:
    if p not in sys.path:
        sys.path.insert(0, p)

from backend import database as db
from backend.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    HealthResponse,
    CreateScanRequest,
    CreateScanResponse,
    ScanResponse,
    StatsResponse
)
from scoring import analyze

try:
    from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


def _seed_initial_data_if_empty():
    stats = db.get_stats()
    if stats["total"] == 0:
        initial_samples = [
            {
                "id": "scan-mock-1",
                "type": "text",
                "title": "Urgent SBI OTP verification request",
                "content": "Dear Customer, your SBI account has been locked. Please update your KYC immediately at http://sbi-kyc-update.me/login or call 9876543210. Do not share your OTP.",
                "createdAt": "2026-11-20T14:32:00Z",
                "status": "completed",
                "steps": [
                    {"key": "extract", "label": "Extract content", "status": "completed"},
                    {"key": "patterns", "label": "Check patterns", "status": "completed"},
                    {"key": "reputation", "label": "Check URL reputation", "status": "completed"},
                    {"key": "evidence", "label": "Combine evidence", "status": "completed"},
                    {"key": "report", "label": "Prepare report", "status": "completed"}
                ],
                "result": {
                    "riskLevel": "high",
                    "summary": "Fake bank message impersonating SBI and asking for sensitive credentials.",
                    "score": 92,
                    "scoreValidated": True,
                    "category": "Banking / KYC Fraud",
                    "evidence": [
                        {
                            "id": "ev-1",
                            "title": "Threat database match",
                            "kind": "confirmed",
                            "detail": "Domain sbi-kyc-update.me is listed on OpenPhish and verified blocklists.",
                            "source": "OpenPhish Threat Feed"
                        },
                        {
                            "id": "ev-2",
                            "title": "Urgent account lockout threat",
                            "kind": "warning",
                            "detail": "Message claims your account has been locked to induce panic and immediate compliance.",
                            "source": "Heuristic Rule Engine"
                        }
                    ],
                    "actions": [
                        "Do not click the link or reply to the sender",
                        "Do not share your OTP, PIN, password, or Aadhaar number",
                        "Verify your account status exclusively via official bank net-banking or mobile app"
                    ],
                    "providerDetails": {
                        "modelScore": 94,
                        "ruleScore": 90,
                        "openPhishMatch": True,
                        "patternsDetected": ["Fake KYC", "Account Lockout", "Unofficial Domain"]
                    }
                }
            },
            {
                "id": "scan-mock-2",
                "type": "url",
                "title": "Suspicious reward portal link",
                "content": "http://claim-festive-bonus-now.xyz/spin",
                "createdAt": "2026-11-19T10:15:00Z",
                "status": "completed",
                "steps": [
                    {"key": "extract", "label": "Extract content", "status": "completed"},
                    {"key": "patterns", "label": "Check patterns", "status": "completed"},
                    {"key": "reputation", "label": "Check URL reputation", "status": "completed"},
                    {"key": "evidence", "label": "Combine evidence", "status": "completed"},
                    {"key": "report", "label": "Prepare report", "status": "completed"}
                ],
                "result": {
                    "riskLevel": "medium",
                    "summary": "Unverified website with high-pressure reward hooks and non-standard domain registry.",
                    "score": 58,
                    "scoreValidated": True,
                    "category": "Prize / Lottery Lure",
                    "evidence": [
                        {
                            "id": "ev-201",
                            "title": "Unverified domain registry",
                            "kind": "warning",
                            "detail": "Domain has no legitimate commercial history and uses a disposable .xyz top-level domain.",
                            "source": "Structural URL Inspection"
                        }
                    ],
                    "actions": [
                        "Avoid submitting any personal or bank information on this website",
                        "Do not pay any advance fee or registration charge to claim prizes"
                    ]
                }
            },
            {
                "id": "scan-mock-3",
                "type": "text",
                "title": "Food delivery confirmation notification",
                "content": "Your Swiggy order #98214 from Pizza Hut has been picked up by delivery partner Ramesh. Track live in the Swiggy app.",
                "createdAt": "2026-11-18T19:45:00Z",
                "status": "completed",
                "steps": [
                    {"key": "extract", "label": "Extract content", "status": "completed"},
                    {"key": "patterns", "label": "Check patterns", "status": "completed"},
                    {"key": "reputation", "label": "Check URL reputation", "status": "completed"},
                    {"key": "evidence", "label": "Combine evidence", "status": "completed"},
                    {"key": "report", "label": "Prepare report", "status": "completed"}
                ],
                "result": {
                    "riskLevel": "low",
                    "summary": "Standard service fulfillment notification with no suspicious links, demands, or credential requests.",
                    "score": 4,
                    "scoreValidated": True,
                    "category": "Service Notification",
                    "evidence": [
                        {
                            "id": "ev-301",
                            "title": "No malicious indicators detected",
                            "kind": "confirmed",
                            "detail": "Contains no urgent threats, no external links, and requests no payment or OTP.",
                            "source": "Calibrated Classifier Engine"
                        }
                    ],
                    "actions": [
                        "No immediate risk indicators found",
                        "Always verify orders directly through the official app rather than unknown links"
                    ]
                }
            }
        ]
        for s in initial_samples:
            db.save_scan(s)


_seed_initial_data_if_empty()

app = None
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="ScamLens Cybersecurity API",
        version="2.2.0",
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
            "version": "2.2.0",
            "models_loaded": True
        }

    # ---------------------------------------------------------------------------
    # Core Scan Lifecycle Management: IDLE -> VALIDATING -> PROCESSING -> COMPLETED / FAILED
    # ---------------------------------------------------------------------------
    def _process_scan_background(scan_id: str, scan_type: str, content: str):
        """Executes full threat analysis and persists state updates to SQLite."""
        scan = db.get_scan(scan_id)
        if not scan:
            return

        try:
            # Step 1: Extract content
            steps = [
                {"key": "extract", "label": "Extract content", "status": "completed"},
                {"key": "patterns", "label": "Check patterns", "status": "running"},
                {"key": "reputation", "label": "Check URL reputation", "status": "waiting"},
                {"key": "evidence", "label": "Combine evidence", "status": "waiting"},
                {"key": "report", "label": "Prepare report", "status": "waiting"}
            ]
            scan["steps"] = steps
            db.save_scan(scan)

            # Step 2 & 3: Run AI analysis
            msg_text = content if scan_type == "text" else None
            target_url = content if scan_type == "url" else None
            
            raw_res = analyze(message_text=msg_text, url=target_url)

            # Step progression
            steps[1]["status"] = "completed"
            steps[2]["status"] = "completed"
            steps[3]["status"] = "completed"
            steps[4]["status"] = "completed"

            # Map raw_res to ScanResult
            verdict = (raw_res.get("verdict") or "Unknown").lower()
            risk_score = raw_res.get("risk_score")
            
            if verdict == "scam":
                risk_level = "high"
            elif verdict == "suspicious":
                risk_level = "medium"
            elif verdict == "safe":
                risk_level = "low"
            else:
                risk_level = "unknown"

            score_validated = bool(risk_score is not None and risk_level != "unknown")

            evidence_items = []
            for idx, sig in enumerate(raw_res.get("signals", [])):
                is_strong = sig.get("severity") == "strong"
                evidence_items.append({
                    "id": f"ev-{scan_id}-{idx}",
                    "title": sig.get("id", "Fraud Pattern").replace("_", " ").title(),
                    "kind": "confirmed" if is_strong else "warning",
                    "detail": sig.get("explanation", ""),
                    "source": sig.get("source", "ScamLens Engine").replace("_", " ").title()
                })

            if not evidence_items and raw_res.get("reasons"):
                for idx, r in enumerate(raw_res["reasons"]):
                    evidence_items.append({
                        "id": f"ev-r-{scan_id}-{idx}",
                        "title": "Heuristic Assessment",
                        "kind": "warning" if risk_level in ["high", "medium"] else "confirmed",
                        "detail": r,
                        "source": "Heuristic Analyzer"
                    })

            if not evidence_items:
                evidence_items.append({
                    "id": f"ev-clean-{scan_id}",
                    "title": "Clean baseline assessment",
                    "kind": "confirmed",
                    "detail": "No recognized malicious patterns, urgent threats, or suspicious links detected.",
                    "source": "ScamLens Engine"
                })

            actions = raw_res.get("safety_tips") or [
                "Verify through official channels before acting",
                "Never share OTPs, PINs, or banking passwords"
            ]

            details = raw_res.get("details", {})
            cat = details.get("scam_types", [None])[0] if details.get("scam_types") else None
            if not cat:
                cat = "Threat Verification"

            scan["status"] = "completed"
            scan["steps"] = steps
            scan["result"] = {
                "riskLevel": risk_level,
                "summary": raw_res.get("user_message") or (raw_res.get("reasons") or ["Analysis complete"])[0],
                "score": risk_score,
                "scoreValidated": score_validated,
                "evidence": evidence_items,
                "actions": actions,
                "category": cat,
                "isPartial": raw_res.get("status") == "PARTIAL",
                "providerDetails": {
                    "modelScore": details.get("text_ml_score", 0),
                    "ruleScore": details.get("heuristic_score", 0),
                    "openPhishMatch": details.get("is_blocklisted", False),
                    "patternsDetected": details.get("scam_types", [])
                }
            }
            db.save_scan(scan)
        except Exception as e:
            # Mark scan as failed cleanly
            scan["status"] = "failed"
            scan["error"] = str(e)
            for st in scan.get("steps", []):
                if st.get("status") == "running":
                    st["status"] = "failed"
                    st["detail"] = str(e)
            db.save_scan(scan)

    @app.post("/api/scans", response_model=CreateScanResponse)
    def create_scan_endpoint(request: CreateScanRequest, background_tasks: BackgroundTasks):
        """VALIDATING -> PROCESSING: Validates input, creates DB record, initiates analysis."""
        content = (request.content or "").strip()
        if not content:
            raise HTTPException(status_code=400, detail="Scan content cannot be empty")

        scan_type = request.type.lower()
        if scan_type not in ["text", "url", "screenshot", "qr", "audio"]:
            raise HTTPException(status_code=400, detail=f"Unsupported scan type: {scan_type}")

        scan_id = "scan-" + uuid.uuid4().hex[:10]
        now_iso = datetime.now(timezone.utc).isoformat()

        if scan_type == "url":
            title = f"Link: {content.replace('https://', '').replace('http://', '')[:30]}..."
        else:
            title = content[:36] + ("..." if len(content) > 36 else "")

        initial_steps = [
            {"key": "extract", "label": "Extract content", "status": "completed"},
            {"key": "patterns", "label": "Check patterns", "status": "running"},
            {"key": "reputation", "label": "Check URL reputation", "status": "waiting"},
            {"key": "evidence", "label": "Combine evidence", "status": "waiting"},
            {"key": "report", "label": "Prepare report", "status": "waiting"}
        ]

        new_scan = {
            "id": scan_id,
            "type": scan_type,
            "content": content,
            "title": title,
            "status": "running",
            "createdAt": now_iso,
            "steps": initial_steps,
            "result": None,
            "error": None
        }

        # Persist in SQLite
        db.save_scan(new_scan)

        # Trigger background analysis (keeps processing even if client navigates)
        background_tasks.add_task(_process_scan_background, scan_id, scan_type, content)

        return {"id": scan_id, "status": "running"}

    @app.get("/api/scans/{scan_id}", response_model=ScanResponse)
    def get_scan_endpoint(scan_id: str):
        """Retrieves exact real-time scan state from SQLite database."""
        scan = db.get_scan(scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        return scan

    @app.get("/api/scans", response_model=List[ScanResponse])
    def list_scans_endpoint(
        query: Optional[str] = Query(None),
        type: Optional[str] = Query(None),
        risk: Optional[str] = Query(None)
    ):
        """Lists stored scan history ordered by creation date."""
        return db.list_scans(query=query, scan_type=type, risk=risk)

    @app.delete("/api/scans/{scan_id}")
    def delete_scan_endpoint(scan_id: str):
        deleted = db.delete_scan(scan_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Scan not found")
        return {"deleted": True, "id": scan_id}

    @app.delete("/api/scans")
    def delete_all_scans_endpoint():
        db.delete_all_scans()
        return {"deleted": True, "count": "all"}

    @app.get("/api/stats", response_model=StatsResponse)
    def get_stats_endpoint():
        """Computes true statistics directly from stored scan records."""
        return db.get_stats()

    # ---------------------------------------------------------------------------
    # Legacy Direct Evaluation Endpoints
    # ---------------------------------------------------------------------------
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
            }
        ]


if __name__ == "__main__":
    if FASTAPI_AVAILABLE:
        import uvicorn
        print("[*] Starting ScamLens Backend API server on http://127.0.0.1:8000...")
        uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
