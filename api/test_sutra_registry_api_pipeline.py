import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

import kernel_api
from kernel_api import app


class FailingSutraRegistryValidator:
    def load_sample_sutras(self):
        return [{"sutra_id": "bad"}]

    def validate_registry(self, entries):
        raise ValueError("Invalid internal sutra registry.")


class SutraRegistryAPIPipelineTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_samples_endpoint_returns_200(self):
        response = self.client.get("/api/v3/debug/sutras/samples")

        self.assertEqual(response.status_code, 200)
        self.assertIn("sutras", response.json())

    def test_seven_sutras_returned(self):
        response = self.client.get("/api/v3/debug/sutras/samples")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 7)
        self.assertEqual(len(response.json()["sutras"]), 7)

    def test_sutra_ids_present(self):
        response = self.client.get("/api/v3/debug/sutras/samples")
        sutra_ids = {sutra["sutra_id"] for sutra in response.json()["sutras"]}

        self.assertEqual(
            sutra_ids,
            {"6.1.101", "6.1.87", "6.1.77", "8.3.15", "8.3.34", "8.4.40", "8.2.39"},
        )

    def test_sources_endpoint_returns_200(self):
        response = self.client.get("/api/v3/debug/sutras/sources")

        self.assertEqual(response.status_code, 200)
        self.assertIn("sources", response.json())
        self.assertGreaterEqual(response.json()["count"], 4)

    def test_validate_endpoint_returns_valid_true(self):
        response = self.client.get("/api/v3/debug/sutras/validate")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["valid"])
        self.assertEqual(response.json()["errors"], [])

    def test_validate_endpoint_returns_sutra_count(self):
        response = self.client.get("/api/v3/debug/sutras/validate")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["sutra_count"], 7)
        self.assertEqual(len(payload["validated_ids"]), 7)

    def test_utf8_sanskrit_preserved(self):
        response = self.client.get("/api/v3/debug/sutras/samples")
        sutra_texts = {sutra["sutra_text_devanagari"] for sutra in response.json()["sutras"]}

        self.assertEqual(response.status_code, 200)
        self.assertIn("\u0906\u0926\u094d\u0917\u0941\u0923\u0903", sutra_texts)
        self.assertIn("\u0938\u094d\u0924\u094b\u0903 \u0936\u094d\u091a\u0941\u0928\u093e \u0936\u094d\u091a\u0941\u0903", sutra_texts)

    def test_invalid_internal_registry_failure_path(self):
        previous_validator = kernel_api.sutra_registry_validator
        kernel_api.sutra_registry_validator = FailingSutraRegistryValidator()
        try:
            response = self.client.get("/api/v3/debug/sutras/validate")
        finally:
            kernel_api.sutra_registry_validator = previous_validator

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "sutra_registry_error")


if __name__ == "__main__":
    unittest.main()
