import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kernel_api import app


class MorphologyPipelineTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_meta_returns_nouns_and_dhatus(self):
        response = self.client.get("/api/v3/morphology/meta")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("nouns", payload)
        self.assertIn("dhatus", payload)
        self.assertTrue(any(item["stem"] == "\u0930\u093e\u092e" for item in payload["nouns"]))
        self.assertTrue(any(item["dhatu"] == "\u092d\u0942" for item in payload["dhatus"]))

    def test_rama_nominative_singular(self):
        response = self.client.post(
            "/api/v3/morphology/noun/inflect",
            json={"stem": "\u0930\u093e\u092e", "case": "nominative", "number": "singular"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["form"], "\u0930\u093e\u092e\u0903")

    def test_rama_accusative_singular(self):
        response = self.client.post(
            "/api/v3/morphology/noun/inflect",
            json={"stem": "\u0930\u093e\u092e", "case": "accusative", "number": "singular"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["form"], "\u0930\u093e\u092e\u092e\u094d")

    def test_bhu_lat_prathama_ekavacana(self):
        response = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"dhatu": "\u092d\u0942", "lakara": "la\u1e6d", "person": "3", "number": "1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["form"], "\u092d\u0935\u0924\u093f")

    def test_path_lat_prathama_ekavacana(self):
        response = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"dhatu": "\u092a\u0920\u094d", "lakara": "la\u1e6d", "person": "3", "number": "1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["form"], "\u092a\u0920\u0924\u093f")

    def test_gam_lat_prathama_ekavacana(self):
        response = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"dhatu": "\u0917\u092e\u094d", "lakara": "la\u1e6d", "person": "3", "number": "1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["form"], "\u0917\u091a\u094d\u091b\u0924\u093f")

    def test_named_lat_prathama_ekavacana_remains_supported(self):
        response = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"dhatu": "\u092d\u0942", "lakara": "lat", "person": "prathama", "number": "ekavacana"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["form"], "\u092d\u0935\u0924\u093f")

    def test_invalid_stem_returns_structured_morphology_error(self):
        response = self.client.post(
            "/api/v3/morphology/noun/inflect",
            json={"stem": "\u0926\u0947\u0935", "case": "nominative", "number": "singular"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"]["code"], "morphology_error")

    def test_invalid_dhatu_returns_structured_morphology_error(self):
        response = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"dhatu": "\u0915\u0943", "lakara": "lat", "person": "prathama", "number": "ekavacana"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"]["code"], "morphology_error")

    def test_unsupported_verb_slot_returns_structured_morphology_error(self):
        response = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"dhatu": "\u092d\u0942", "lakara": "la\u1e6d", "person": "2", "number": "1"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"]["code"], "morphology_error")

    def test_existing_chandas_endpoint_still_passes(self):
        response = self.client.post("/api/v3/analyze", json={"input_text": "\u0930\u093e\u092e\u0903 \u0905\u0935\u0926\u0924\u094d"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["phonological_syllables"])

    def test_existing_sandhi_endpoint_still_passes(self):
        response = self.client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0930\u093e\u092e", "word2": "\u0905\u0938\u094d\u0924\u093f"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["merged"], "\u0930\u093e\u092e\u093e\u0938\u094d\u0924\u093f")


if __name__ == "__main__":
    unittest.main()
