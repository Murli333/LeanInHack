"""
ScamLens CLI: Launch FastAPI Backend Server
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    import uvicorn
    print("[*] Starting ScamLens API on http://localhost:8000...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
except ImportError:
    print("[!] Uvicorn not installed. Install with: pip install uvicorn fastapi python-multipart")
