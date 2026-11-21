"""
Unit tests for OCR screenshot extraction and error handling (signals.py).
"""

import os
import sys
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_DETECTION_DIR = os.path.dirname(_HERE)
if _DETECTION_DIR not in sys.path:
    sys.path.insert(0, _DETECTION_DIR)

import signals


class TestOCRProcessingAndFailures(unittest.TestCase):

    def test_ocr_missing_path(self):
        res = signals.extract_text_from_image("")
        self.assertEqual(res.status, "SKIPPED")
        self.assertEqual(res.error_code, "NO_PATH")
        self.assertFalse(res.succeeded)

    def test_ocr_nonexistent_file(self):
        res = signals.extract_text_from_image("C:/nonexistent_image_12345.png")
        self.assertEqual(res.status, "FAILED")
        self.assertEqual(res.error_code, "NO_FILE")
        self.assertIn("not found", res.error_message.lower())

    def test_ocr_unsupported_format(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not an image")
            temp_path = f.name

        try:
            res = signals.extract_text_from_image(temp_path)
            self.assertEqual(res.status, "FAILED")
            self.assertEqual(res.error_code, "UNSUPPORTED_FORMAT")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_ocr_image_too_small(self):
        # Create a tiny 10x10 px image
        try:
            from PIL import Image
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                img = Image.new("RGB", (10, 10), color="white")
                img.save(f.name)
                temp_path = f.name

            try:
                res = signals.extract_text_from_image(temp_path)
                if res.error_code == "DEPENDENCY_MISSING":
                    self.skipTest("pytesseract or Pillow not installed in environment")
                self.assertEqual(res.status, "FAILED")
                self.assertEqual(res.error_code, "SIZE_TOO_SMALL")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        except ImportError:
            self.skipTest("Pillow not installed in test environment")

    def test_ocr_result_structure(self):
        res = signals.OCRResult(
            text="Electricity power will be disconnected",
            confidence=0.88,
            status="OK",
            language_used="eng"
        )
        d = res.to_dict()
        self.assertEqual(d["text"], "Electricity power will be disconnected")
        self.assertEqual(d["confidence"], 0.88)
        self.assertEqual(d["status"], "OK")
        self.assertTrue(res.succeeded)


if __name__ == "__main__":
    unittest.main()
