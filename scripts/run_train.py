"""
ScamLens CLI: Retrain All Machine Learning Models
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_ML_DIR = ROOT_DIR / "Data And ML"

def main():
    print("==================================================")
    print(">>> SCAMLENS ML RETRAINING PIPELINE")
    print("==================================================")
    cmd = [sys.executable, "-u", str(DATA_ML_DIR / "src" / "train.py")]
    result = subprocess.run(cmd, cwd=str(DATA_ML_DIR))
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
