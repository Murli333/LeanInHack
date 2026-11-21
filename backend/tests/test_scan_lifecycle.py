"""
Regression Test Suite for ScamLens Scan Lifecycle & State Synchronization
Uses Python's standard unittest library for universal portability.
"""
import os
import sys
import time
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

from fastapi.testclient import TestClient
from backend.main import app
import backend.database as db

client = TestClient(app)


class TestScanLifecycle(unittest.TestCase):

    def test_01_health_check(self):
        res = client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["version"], "2.2.0")

    def test_02_create_and_complete_suspicious_scan(self):
        payload = {
            "type": "text",
            "content": "URGENT: Your SBI account is blocked. Update KYC at http://sbi-kyc-fake.me/login immediately"
        }
        create_res = client.post("/api/scans", json=payload)
        self.assertEqual(create_res.status_code, 200)
        scan_id = create_res.json()["id"]
        self.assertTrue(scan_id.startswith("scan-"))

        # Poll until terminal state
        max_wait = 5.0
        start = time.time()
        terminal_scan = None

        while time.time() - start < max_wait:
            get_res = client.get(f"/api/scans/{scan_id}")
            self.assertEqual(get_res.status_code, 200)
            data = get_res.json()
            if data["status"] in ["completed", "failed"]:
                terminal_scan = data
                break
            time.sleep(0.1)

        self.assertIsNotNone(terminal_scan, "Scan timed out without reaching terminal state")
        self.assertEqual(terminal_scan["status"], "completed")
        self.assertIsNotNone(terminal_scan["result"])
        self.assertIn(terminal_scan["result"]["riskLevel"], ["high", "medium"])
        self.assertGreaterEqual(terminal_scan["result"]["score"], 70)
        self.assertTrue(terminal_scan["result"]["scoreValidated"])
        self.assertGreater(len(terminal_scan["result"]["evidence"]), 0)
        self.assertGreater(len(terminal_scan["result"]["actions"]), 0)

    def test_03_create_and_complete_legitimate_scan(self):
        payload = {
            "type": "text",
            "content": "Your Swiggy order has been delivered. Thank you for shopping with us."
        }
        create_res = client.post("/api/scans", json=payload)
        self.assertEqual(create_res.status_code, 200)
        scan_id = create_res.json()["id"]

        time.sleep(0.5)
        get_res = client.get(f"/api/scans/{scan_id}")
        self.assertEqual(get_res.status_code, 200)
        data = get_res.json()
        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["result"]["riskLevel"], "low")
        self.assertLessEqual(data["result"]["score"], 30)

    def test_04_empty_content_validation_rejection(self):
        res = client.post("/api/scans", json={"type": "text", "content": "   "})
        self.assertEqual(res.status_code, 400)
        self.assertIn("empty", res.json()["detail"].lower())

    def test_05_non_existent_scan_404(self):
        res = client.get("/api/scans/non-existent-scan-id-xyz")
        self.assertEqual(res.status_code, 404)

    def test_06_database_stats_consistency(self):
        stats_res = client.get("/api/stats")
        self.assertEqual(stats_res.status_code, 200)
        stats = stats_res.json()
        self.assertIn("total", stats)
        self.assertIn("highRisk", stats)
        self.assertGreaterEqual(stats["total"], stats["highRisk"])


if __name__ == "__main__":
    unittest.main()
