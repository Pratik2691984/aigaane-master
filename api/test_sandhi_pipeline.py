import json
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.sandhi import analyze_vowel_sandhi
from kernel_api import app


ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = ROOT / "tests" / "sandhi_corpus" / "suite.json"


class SandhiPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite = json.loads(SUITE_PATH.read_text(encoding="utf-8"))

    def test_sandhi_corpus_cases_pass(self):
        for case in self.suite["cases"]:
            with self.subTest(case=case["id"]):
                result = analyze_vowel_sandhi(case["word1"], case["word2"])
                expected = case["expected"]
                self.assertEqual(result["merged"], expected["merged"])
                self.assertEqual(result["sutra"], expected["sutra"])
                self.assertEqual(result["type"], "vowel_sandhi")
                self.assertTrue(result["sutra_name"])
                self.assertEqual(
                    [step["layer"] for step in result["trace"]],
                    [
                        "orthographic_input",
                        "phonological_representation",
                        "sandhi_rule_engine",
                        "orthographic_recomposition",
                    ],
                )

    def test_empty_word_returns_400_from_api(self):
        client = TestClient(app)
        response = client.post("/api/v3/sandhi", json={"word1": "", "word2": "\u0905\u0938\u094d\u0924\u093f"})
        self.assertEqual(response.status_code, 400)

    def test_consonant_initial_word2_returns_400_no_op(self):
        client = TestClient(app)
        response = client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0930\u093e\u092e", "word2": "\u0917\u091a\u094d\u091b\u0924\u093f"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("vowel boundaries", response.json()["detail"]["message"])

    def test_consonant_boundary_no_rule_returns_400(self):
        client = TestClient(app)
        response = client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0924\u0924\u094d", "word2": "\u0917\u091a\u094d\u091b\u0924\u093f"},
        )
        self.assertEqual(response.status_code, 400)

    def test_iast_not_enabled_in_phase_one(self):
        client = TestClient(app)
        response = client.post("/api/v3/sandhi", json={"word1": "rama", "word2": "asti"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Devanagari", response.json()["detail"]["message"])

    def test_response_schema_is_typed_and_traceable(self):
        client = TestClient(app)
        response = client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0926\u0947\u0935", "word2": "\u0907\u0928\u094d\u0926\u094d\u0930"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(set(payload.keys()), {"merged", "sutra", "sutra_name", "type", "trace"})
        self.assertEqual(payload["sutra"], "6.1.87")
        self.assertEqual(payload["trace"][0]["layer"], "orthographic_input")

    def test_sandhi_response_body_decodes_as_utf8(self):
        client = TestClient(app)
        response = client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0926\u0947\u0935", "word2": "\u0907\u0928\u094d\u0926\u094d\u0930"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("charset=utf-8", response.headers["content-type"].lower())
        decoded = response.content.decode("utf-8")
        self.assertIn("\u0926\u0947\u0935\u0947\u0928\u094d\u0926\u094d\u0930", decoded)

    def test_analyze_response_declares_utf8_json(self):
        client = TestClient(app)
        response = client.post("/api/v3/analyze", json={"input_text": "\u0930\u093e\u092e\u0903 \u0905\u0935\u0926\u0924\u094d"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("charset=utf-8", response.headers["content-type"].lower())
        decoded = response.content.decode("utf-8")
        self.assertIn("\u0930\u093e", decoded)

    def test_post_analyze_still_works(self):
        client = TestClient(app)
        response = client.post("/api/v3/analyze", json={"input_text": "purohitam"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["phonological_syllables"])

    def test_post_sandhi_works(self):
        client = TestClient(app)
        response = client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0930\u093e\u092e", "word2": "\u0905\u0938\u094d\u0924\u093f"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["merged"], "\u0930\u093e\u092e\u093e\u0938\u094d\u0924\u093f")


if __name__ == "__main__":
    unittest.main()
