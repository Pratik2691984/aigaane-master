import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.trace_graph import DerivationStep, DerivationTraceGraph
from kernel_api import app


class TraceGraphPipelineTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_trace_graph_step_to_dict(self):
        step = DerivationStep(
            sutra="6.1.87",
            sutra_name="\u0906\u0926\u094d \u0917\u0941\u0923\u0903",
            operation="guna_substitution",
            input_state="\u0926\u0947\u0935 + \u0907\u0928\u094d\u0926\u094d\u0930",
            output_state="\u0926\u0947\u0935\u0947\u0928\u094d\u0926\u094d\u0930",
            engine_node="Node 2A Vowel Sandhi",
        )
        self.assertEqual(
            step.to_dict(),
            {
                "sutra": "6.1.87",
                "sutra_name": "\u0906\u0926\u094d \u0917\u0941\u0923\u0903",
                "operation": "guna_substitution",
                "input_state": "\u0926\u0947\u0935 + \u0907\u0928\u094d\u0926\u094d\u0930",
                "output_state": "\u0926\u0947\u0935\u0947\u0928\u094d\u0926\u094d\u0930",
                "engine_node": "Node 2A Vowel Sandhi",
            },
        )
        self.assertEqual(DerivationTraceGraph([step]).to_list(), [step.to_dict()])

    def test_vowel_sandhi_derivation_path_present(self):
        response = self.client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0926\u0947\u0935", "word2": "\u0907\u0928\u094d\u0926\u094d\u0930"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        step = payload["derivation_path"][0]
        self.assertEqual(step["sutra"], "6.1.87")
        self.assertEqual(step["sutra_name"], "\u0906\u0926\u094d \u0917\u0941\u0923\u0903")
        self.assertEqual(step["operation"], "guna_substitution")
        self.assertEqual(step["input_state"], "\u0926\u0947\u0935 + \u0907\u0928\u094d\u0926\u094d\u0930")
        self.assertEqual(step["output_state"], "\u0926\u0947\u0935\u0947\u0928\u094d\u0926\u094d\u0930")
        self.assertEqual(step["engine_node"], "Node 2A Vowel Sandhi")

    def test_visarga_sandhi_derivation_path_present(self):
        response = self.client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0930\u093e\u092e\u0903", "word2": "\u0905\u0938\u094d\u0924\u093f"},
        )
        self.assertEqual(response.status_code, 200)
        step = response.json()["derivation_path"][0]
        self.assertEqual(step["sutra"], "6.1.114")
        self.assertEqual(step["operation"], "visarga_to_o_avagraha")
        self.assertEqual(step["engine_node"], "Node 2B Visarga Sandhi")

    def test_morphology_derivation_path_present(self):
        response = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"dhatu": "\u092d\u0942", "lakara": "la\u1e6d", "person": "3", "number": "1"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["form"], "\u092d\u0935\u0924\u093f")
        operations = [step["operation"] for step in payload["derivation_path"]]
        self.assertEqual(
            operations,
            [
                "registry_lookup",
                "stem_selection",
                "table_driven_suffix_assignment",
                "phase1_morphology_output",
            ],
        )
        self.assertTrue(all(step["engine_node"] == "Node 3 Morphology" for step in payload["derivation_path"]))

    def test_existing_sandhi_fields_preserved(self):
        response = self.client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0926\u0947\u0935", "word2": "\u0907\u0928\u094d\u0926\u094d\u0930"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        for field in ["merged", "sutra", "sutra_name", "type", "trace"]:
            self.assertIn(field, payload)

    def test_existing_morphology_fields_preserved(self):
        response = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"dhatu": "\u092d\u0942", "lakara": "la\u1e6d", "person": "3", "number": "1"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        for field in ["form", "metadata", "rule", "type"]:
            self.assertIn(field, payload)


if __name__ == "__main__":
    unittest.main()
