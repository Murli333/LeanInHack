"""
ScamLens CLI: Launch FastAPI Backend Server
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

if __name__ == '__main__':
    try:
        import uvicorn
        print("[*] Starting ScamLens API on http://127.0.0.1:8000...")
        uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
    except ImportError:
        print("[!] Uvicorn not installed. Install with: pip install uvicorn fastapi python-multipart")
