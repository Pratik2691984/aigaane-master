import copy
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kernel_api import app


class SemanticTracePipelineTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_link_endpoint_returns_200(self):
        response = self.client.post(
            "/api/v3/debug/trace/link",
            json={"trace": [{"sutra": "8.4.40", "operation": "dental_to_palatal_assimilation"}]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("linked_trace", response.json())

    def test_linked_trace_contains_sutra_ref(self):
        response = self.client.post(
            "/api/v3/debug/trace/link",
            json={"trace": [{"sutra": "8.4.40", "operation": "dental_to_palatal_assimilation"}]},
        )
        linked_step = response.json()["linked_trace"][0]

        self.assertEqual(linked_step["sutra_ref"]["sutra_id"], "8.4.40")
        self.assertEqual(linked_step["sutra_ref"]["domain"], "consonant_sandhi")

    def test_unresolved_sutra_gets_null_sutra_ref(self):
        response = self.client.post(
            "/api/v3/debug/trace/link",
            json={"trace": [{"sutra": "1.1.1", "operation": "unresolved"}]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["linked_trace"][0]["sutra_ref"])

    def test_original_trace_unchanged(self):
        trace = [
            {
                "sutra": "8.4.40",
                "operation": "dental_to_palatal_assimilation",
                "input_state": "\u0924\u0924\u094d + \u091a",
                "output_state": "\u0924\u091a\u094d\u091a",
            }
        ]
        original = copy.deepcopy(trace)

        response = self.client.post("/api/v3/debug/trace/link", json={"trace": trace})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(trace, original)
        self.assertNotIn("sutra_ref", trace[0])

    def test_demo_endpoint_returns_200(self):
        response = self.client.get("/api/v3/debug/trace/demo")

        self.assertEqual(response.status_code, 200)
        self.assertIn("linked_trace", response.json())

    def test_demo_endpoint_contains_governed_sutras(self):
        response = self.client.get("/api/v3/debug/trace/demo")
        trace = response.json()["linked_trace"]
        sutra_ids = {step["sutra_ref"]["sutra_id"] for step in trace}

        self.assertEqual(response.status_code, 200)
        self.assertTrue({"6.1.101", "8.4.40"}.issubset(sutra_ids))

    def test_utf8_sanskrit_preserved(self):
        response = self.client.post(
            "/api/v3/debug/trace/link",
            json={
                "trace": [
                    {
                        "sutra": "6.1.101",
                        "input_state": "\u0930\u093e\u092e + \u0905\u0938\u094d\u0924\u093f",
                        "output_state": "\u0930\u093e\u092e\u093e\u0938\u094d\u0924\u093f",
                    }
                ]
            },
        )
        linked_step = response.json()["linked_trace"][0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(linked_step["input_state"], "\u0930\u093e\u092e + \u0905\u0938\u094d\u0924\u093f")
        self.assertEqual(linked_step["sutra_ref"]["sutra_text_devanagari"], "\u0905\u0915\u0903 \u0938\u0935\u0930\u094d\u0923\u0947 \u0926\u0940\u0930\u094d\u0918\u0903")

    def test_malformed_payload_failure_path(self):
        response = self.client.post(
            "/api/v3/debug/trace/link",
            json={"trace": {"sutra": "8.4.40"}},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "semantic_trace_error")

    def test_empty_trace_handling(self):
        response = self.client.post("/api/v3/debug/trace/link", json={"trace": []})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["linked_trace"], [])


if __name__ == "__main__":
    unittest.main()
