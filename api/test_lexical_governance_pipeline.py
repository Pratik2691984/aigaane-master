import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.lexical_governance import normalize_nfc
from kernel_api import app


class LexicalGovernancePipelineTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_nfc_normalization(self):
        self.assertEqual(normalize_nfc("e\u0301", "word"), "\u00e9")

    def test_sandhi_rejects_latin_input(self):
        response = self.client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0926\u0947\u0935", "word2": "indra"},
        )
        self.assertEqual(response.status_code, 400)
        detail = response.json()["detail"]
        self.assertEqual(detail["code"], "lexical_governance_error")
        self.assertTrue(detail["invalid_characters"])

    def test_sandhi_accepts_devanagari(self):
        response = self.client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0926\u0947\u0935", "word2": "\u0907\u0928\u094d\u0926\u094d\u0930"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["merged"], "\u0926\u0947\u0935\u0947\u0928\u094d\u0926\u094d\u0930")
        self.assertEqual(payload["governance"]["normalization"], "NFC")
        self.assertEqual(payload["governance"]["script_policy"], "devanagari_only")
        self.assertEqual(payload["governance"]["source"], "sandhi_rule_registry")

    def test_morphology_rejects_latin_stem(self):
        response = self.client.post(
            "/api/v3/morphology/noun/inflect",
            json={"stem": "rama", "case": "nominative", "number": "singular"},
        )
        self.assertEqual(response.status_code, 400)
        detail = response.json()["detail"]
        self.assertEqual(detail["code"], "lexical_governance_error")
        self.assertTrue(detail["invalid_characters"])

    def test_morphology_accepts_rama(self):
        response = self.client.post(
            "/api/v3/morphology/noun/inflect",
            json={"stem": "\u0930\u093e\u092e", "case": "nominative", "number": "singular"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["form"], "\u0930\u093e\u092e\u0903")
        self.assertEqual(payload["governance"]["normalization"], "NFC")
        self.assertEqual(payload["governance"]["script_policy"], "devanagari_only")
        self.assertEqual(payload["governance"]["source"], "classical_paradigm_registry")

    def test_analyze_endpoint_still_accepts_latin_iast(self):
        response = self.client.post("/api/v3/analyze", json={"input_text": "r\u0101ma\u1e25 avadat"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["transliteration"], "ramah avadat")
        self.assertEqual(payload["governance"]["script_policy"], "mixed_chandas_ingress")

    def test_analyze_endpoint_still_accepts_devanagari(self):
        response = self.client.post("/api/v3/analyze", json={"input_text": "\u0930\u093e\u092e\u0903 \u0905\u0935\u0926\u0924\u094d"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["transliteration"], "ramah avadat")

    def test_emoji_rejected_in_sandhi_and_morphology(self):
        sandhi_response = self.client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0926\u0947\u0935\U0001f642", "word2": "\u0907\u0928\u094d\u0926\u094d\u0930"},
        )
        self.assertEqual(sandhi_response.status_code, 400)
        self.assertEqual(sandhi_response.json()["detail"]["code"], "lexical_governance_error")

        morphology_response = self.client.post(
            "/api/v3/morphology/noun/inflect",
            json={"stem": "\u0930\u093e\u092e\U0001f642", "case": "nominative", "number": "singular"},
        )
        self.assertEqual(morphology_response.status_code, 400)
        self.assertEqual(morphology_response.json()["detail"]["code"], "lexical_governance_error")

    def test_danda_and_pipe_still_accepted_in_analyze_endpoint(self):
        response = self.client.post(
            "/api/v3/analyze",
            json={"input_text": "\u0930\u093e\u092e\u0903 \u0905\u0935\u0926\u0924\u094d \u0964 \u0930\u093e\u092e\u0903 | \u0905\u0935\u0926\u0924\u094d ||"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["padas"])
        self.assertEqual(payload["governance"]["script_policy"], "mixed_chandas_ingress")


if __name__ == "__main__":
    unittest.main()
