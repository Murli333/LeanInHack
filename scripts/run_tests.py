"""
ScamLens CLI: Run All Unit and Integration Test Suites
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def main():
    print("==================================================")
    print(">>> 1. RUNNING MEMBER 1 ML UNIT TESTS")
    print("==================================================")
    cmd1 = [sys.executable, str(ROOT_DIR / "Data And ML" / "tests" / "test_models.py")]
    res1 = subprocess.run(cmd1, cwd=str(ROOT_DIR / "Data And ML"))

    print("\n==================================================")
    print(">>> 2. RUNNING MEMBER 3 INTEGRATION TESTS")
    print("==================================================")
    cmd2 = [sys.executable, str(ROOT_DIR / "Integration App and Report" / "tests" / "test_integration.py")]
    res2 = subprocess.run(cmd2, cwd=str(ROOT_DIR))

    print("\n==================================================")
    print(">>> 3. RUNNING BACKEND SCAN LIFECYCLE TESTS")
    print("==================================================")
    cmd3 = [sys.executable, "-m", "unittest", "backend/tests/test_scan_lifecycle.py"]
    res3 = subprocess.run(cmd3, cwd=str(ROOT_DIR))

    if res1.returncode != 0 or res2.returncode != 0 or res3.returncode != 0:
        print("\n[FAIL] One or more test suites failed!")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All Project Test Suites Passed Flawlessly (100%)!")
        sys.exit(0)

if __name__ == "__main__":
    main()
