import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.consonant_sandhi import (
    ConsonantSandhiEngine,
    analyze_consonant_sandhi,
    build_rule_key,
    is_voiced_or_vowel_initial,
    normalize_halant_token,
)
from kernel_api import app


class ConsonantSandhiPipelineTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_halant_token_normalization_does_not_double_virama(self):
        self.assertEqual(normalize_halant_token("\u0924"), "\u0924\u094d")
        self.assertEqual(normalize_halant_token("\u0924\u094d"), "\u0924\u094d")
        self.assertEqual(build_rule_key("\u0924\u094d", "\u091a"), "\u0924\u094d+\u091a")

    def test_voiced_or_vowel_initial_helper(self):
        self.assertTrue(is_voiced_or_vowel_initial("\u0908"))
        self.assertTrue(is_voiced_or_vowel_initial("\u0917"))
        self.assertTrue(is_voiced_or_vowel_initial("\u0917\u094d"))
        self.assertFalse(is_voiced_or_vowel_initial("\u091a"))

    def test_tat_ca_consonant_sandhi_engine(self):
        payload = analyze_consonant_sandhi("\u0924\u0924\u094d", "\u091a")
        self.assertEqual(payload["merged"], "\u0924\u091a\u094d\u091a")
        self.assertEqual(payload["sutra"], "8.4.40")
        self.assertEqual(payload["type"], "consonant_sandhi")
        self.assertEqual(payload["trace"][1]["left_consonant"], "\u0924\u094d")
        self.assertEqual(payload["trace"][1]["right_consonant"], "\u091a")

    def test_vak_ishah_jastva_direct_engine(self):
        payload = ConsonantSandhiEngine().process("\u0935\u093e\u0915\u094d", "\u0908\u0936\u0903")
        self.assertEqual(payload["merged"], "\u0935\u093e\u0917\u0940\u0936\u0903")
        self.assertEqual(payload["sutra"], "8.2.39")
        self.assertEqual(payload["type"], "consonant_sandhi")
        self.assertEqual(payload["derivation_path"][0]["sutra"], "8.2.39")
        self.assertIn("jastva", payload["derivation_path"][0]["operation"])

    def test_consonant_sandhi_api_preserves_response_shape(self):
        response = self.client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0924\u0924\u094d", "word2": "\u091a"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        for field in ["merged", "sutra", "sutra_name", "type", "trace"]:
            self.assertIn(field, payload)
        self.assertNotIn("final_output", payload)
        self.assertEqual(payload["merged"], "\u0924\u091a\u094d\u091a")

    def test_vak_ishah_jastva_api(self):
        response = self.client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0935\u093e\u0915\u094d", "word2": "\u0908\u0936\u0903"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["merged"], "\u0935\u093e\u0917\u0940\u0936\u0903")
        self.assertEqual(payload["sutra"], "8.2.39")
        self.assertEqual(payload["sutra_name"], "\u091d\u0932\u093e\u0902 \u091c\u0936\u094b\u093d\u0928\u094d\u0924\u0947")
        self.assertEqual(payload["type"], "consonant_sandhi")
        self.assertEqual(payload["derivation_path"][0]["operation"], "jastva")

    def test_consonant_sandhi_derivation_path_present(self):
        response = self.client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0924\u0924\u094d", "word2": "\u091a"},
        )
        self.assertEqual(response.status_code, 200)
        step = response.json()["derivation_path"][0]
        self.assertEqual(step["operation"], "dental_to_palatal_assimilation")
        self.assertEqual(step["engine_node"], "Node 2C Consonant Sandhi")
        self.assertEqual(step["output_state"], "\u0924\u091a\u094d\u091a")

    def test_unsupported_consonant_boundary_remains_structured_sandhi_error(self):
        response = self.client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0924\u0924\u094d", "word2": "\u0917\u091a\u094d\u091b\u0924\u093f"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "sandhi_error")


if __name__ == "__main__":
    unittest.main()
