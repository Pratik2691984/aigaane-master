import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kernel_api import app


class DebugAmbiguityPipelineTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_debug_ambiguity_demo_returns_synthetic_ambiguous_payload(self):
        response = self.client.get("/api/v3/debug/ambiguity-demo")
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertTrue(payload["is_ambiguous"])
        self.assertEqual(payload["strategy"], "enumeration_only")
        self.assertIsNone(payload["selected_candidate_id"])
        self.assertEqual(len(payload["candidates"]), 2)

    def test_debug_ambiguity_demo_candidate_zero_is_scutva_path(self):
        response = self.client.get("/api/v3/debug/ambiguity-demo")
        candidate = response.json()["candidates"][0]

        self.assertEqual(candidate["candidate_id"], "0")
        self.assertEqual(candidate["final_output"], "तच्च")
        self.assertEqual(candidate["source_engine"], "Node 6C Debug Ambiguity Demo")
        self.assertIsNone(candidate["confidence"])
        self.assertEqual(candidate["reason"], "Optional Ścutva assimilation via Sutra 8.4.40")
        self.assertEqual(candidate["derivation_path"][0]["sutra"], "8.4.40")
        self.assertEqual(candidate["derivation_path"][0]["sutra_name"], "स्तोः श्चुना श्चुः")
        self.assertEqual(candidate["derivation_path"][0]["operation"], "dental_to_palatal_assimilation")
        self.assertEqual(candidate["derivation_path"][0]["input_state"], "तत् + च")
        self.assertEqual(candidate["derivation_path"][0]["output_state"], "तच्च")

    def test_debug_ambiguity_demo_candidate_one_is_fallback_path(self):
        response = self.client.get("/api/v3/debug/ambiguity-demo")
        candidate = response.json()["candidates"][1]

        self.assertEqual(candidate["candidate_id"], "1")
        self.assertEqual(candidate["final_output"], "तद् च")
        self.assertEqual(candidate["source_engine"], "Node 6C Debug Ambiguity Demo")
        self.assertIsNone(candidate["confidence"])
        self.assertEqual(candidate["reason"], "Padānta preservation fallback candidate")
        self.assertEqual(candidate["derivation_path"][0]["sutra"], "debug.default")
        self.assertEqual(candidate["derivation_path"][0]["sutra_name"], "Debug fallback candidate")
        self.assertEqual(candidate["derivation_path"][0]["operation"], "padanta_preservation_fallback")
        self.assertEqual(candidate["derivation_path"][0]["input_state"], "तत् + च")
        self.assertEqual(candidate["derivation_path"][0]["output_state"], "तद् च")

    def test_debug_ambiguity_demo_uses_utf8_json(self):
        response = self.client.get("/api/v3/debug/ambiguity-demo")

        self.assertIn("charset=utf-8", response.headers["content-type"].lower())
        self.assertIn("तच्च", response.content.decode("utf-8"))

    def test_live_sandhi_endpoint_still_returns_existing_shape(self):
        response = self.client.post(
            "/api/v3/sandhi",
            json={"word1": "राम", "word2": "अस्ति"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["merged"], "रामास्ति")
        self.assertNotIn("candidates", payload)

    def test_live_morphology_endpoint_still_returns_existing_shape(self):
        response = self.client.post(
            "/api/v3/morphology/noun/inflect",
            json={"stem": "राम", "case": "nominative", "number": "singular"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["form"], "रामः")
        self.assertNotIn("candidates", payload)


if __name__ == "__main__":
    unittest.main()
