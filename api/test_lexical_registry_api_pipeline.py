import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kernel_api import app


class LexicalRegistryAPIPipelineTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_samples_endpoint_returns_200(self):
        response = self.client.get("/api/v3/debug/lexicon/samples")

        self.assertEqual(response.status_code, 200)
        self.assertIn("entries", response.json())
        self.assertEqual(response.json()["count"], len(response.json()["entries"]))

    def test_samples_include_seed_lemmas(self):
        response = self.client.get("/api/v3/debug/lexicon/samples")
        lemmas = {entry["lemma_devanagari"] for entry in response.json()["entries"]}

        self.assertTrue(
            {
                "\u0930\u093e\u092e",
                "\u0939\u0930\u093f",
                "\u0928\u0926\u0940",
                "\u092b\u0932",
                "\u092d\u0942",
                "\u092a\u0920\u094d",
                "\u0917\u092e\u094d",
            }.issubset(lemmas)
        )

    def test_sources_endpoint_returns_200(self):
        response = self.client.get("/api/v3/debug/lexicon/sources")

        self.assertEqual(response.status_code, 200)
        self.assertIn("sources", response.json())
        self.assertGreaterEqual(response.json()["count"], 1)

    def test_validate_endpoint_returns_valid_true(self):
        response = self.client.get("/api/v3/debug/lexicon/validate")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["valid"])
        self.assertEqual(response.json()["errors"], [])

    def test_validate_endpoint_returns_entry_count(self):
        response = self.client.get("/api/v3/debug/lexicon/validate")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["entry_count"], 7)
        self.assertEqual(len(payload["validated_ids"]), 7)

    def test_validate_endpoint_preserves_utf8_sanskrit(self):
        samples_response = self.client.get("/api/v3/debug/lexicon/samples")
        validate_response = self.client.get("/api/v3/debug/lexicon/validate")
        lemmas = {entry["lemma_devanagari"] for entry in samples_response.json()["entries"]}

        self.assertEqual(samples_response.status_code, 200)
        self.assertEqual(validate_response.status_code, 200)
        self.assertIn("\u0930\u093e\u092e", lemmas)
        self.assertIn("\u092a\u0920\u094d", lemmas)
        self.assertIn("lex-rama-noun-001", validate_response.json()["validated_ids"])


if __name__ == "__main__":
    unittest.main()
