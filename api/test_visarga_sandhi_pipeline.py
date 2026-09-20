import json
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.visarga_sandhi import analyze_visarga_sandhi
from kernel_api import app


ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = ROOT / "tests" / "sandhi_corpus" / "visarga_cases.json"


class VisargaSandhiPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite = json.loads(SUITE_PATH.read_text(encoding="utf-8"))

    def test_visarga_corpus_cases_pass(self):
        for case in self.suite["cases"]:
            with self.subTest(case=case["id"]):
                result = analyze_visarga_sandhi(case["word1"], case["word2"])
                expected = case["expected"]
                self.assertEqual(result["merged"], expected["merged"])
                self.assertEqual(result["sutra"], expected["sutra"])
                self.assertEqual(result["type"], "visarga_sandhi")
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

    def test_sandhi_endpoint_dispatches_ramah_asti_to_visarga_engine(self):
        client = TestClient(app)
        response = client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0930\u093e\u092e\u0903", "word2": "\u0905\u0938\u094d\u0924\u093f"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["merged"], "\u0930\u093e\u092e\u094b\u093d\u0938\u094d\u0924\u093f")
        self.assertEqual(payload["sutra"], "6.1.114")
        self.assertEqual(payload["type"], "visarga_sandhi")
        self.assertEqual(payload["trace"][1]["right_class"], "VOWEL")

    def test_sandhi_endpoint_dispatches_ramah_gacchati_to_visarga_engine(self):
        client = TestClient(app)
        response = client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0930\u093e\u092e\u0903", "word2": "\u0917\u091a\u094d\u091b\u0924\u093f"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["merged"], "\u0930\u093e\u092e\u094b \u0917\u091a\u094d\u091b\u0924\u093f")
        self.assertEqual(payload["sutra"], "8.2.66 / 6.1.113")
        self.assertEqual(payload["type"], "visarga_sandhi")
        self.assertEqual(payload["trace"][1]["right_class"], "HASH")

    def test_sandhi_endpoint_dispatches_bhaktah_carati_to_visarga_engine(self):
        client = TestClient(app)
        response = client.post(
            "/api/v3/sandhi",
            json={"word1": "\u092d\u0915\u094d\u0924\u0903", "word2": "\u091a\u0930\u0924\u093f"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["merged"], "\u092d\u0915\u094d\u0924\u0936\u094d\u091a\u0930\u0924\u093f")
        self.assertEqual(payload["sutra"], "8.3.34")
        self.assertEqual(payload["type"], "visarga_sandhi")
        self.assertEqual(payload["trace"][1]["right_class"], "KHAR")

    def test_existing_vowel_sandhi_dispatch_still_works(self):
        client = TestClient(app)
        response = client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0930\u093e\u092e", "word2": "\u0905\u0938\u094d\u0924\u093f"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["merged"], "\u0930\u093e\u092e\u093e\u0938\u094d\u0924\u093f")
        self.assertEqual(response.json()["type"], "vowel_sandhi")

    def test_unsupported_visarga_slot_returns_structured_sandhi_error(self):
        client = TestClient(app)
        response = client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0930\u093e\u092e\u0903", "word2": "\u0924\u093f\u0937\u094d\u0920\u0924\u093f"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "sandhi_error")


if __name__ == "__main__":
    unittest.main()
