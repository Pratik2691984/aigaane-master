import copy
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.vyakarana import analyze_sanskrit, build_prakriya_graph
from kernel_api import app


EXPECTED_OVERLAYS = ["karaka", "vakya", "chandas", "sandarbha", "semantic", "rule-trace"]


class PrakriyaBackendAnalyzeRuntimeTests(unittest.TestCase):
    def test_analyze_runtime_returns_unified_prakriya_graph(self):
        payload = analyze_sanskrit("agnim ile")
        graph = payload["prakriya_graph"]

        self.assertEqual(graph["status"], "ready")
        self.assertEqual(graph["metadata"]["overlaysAttached"], EXPECTED_OVERLAYS)
        self.assertGreater(graph["diagnostics"]["overlayCount"], 0)
        self.assertTrue(any(node.get("overlays") for node in graph["nodes"]))
        self.assertTrue(any(edge.get("overlays") for edge in graph["edges"]))

    def test_prakriya_graph_preserves_legacy_backend_render_contract(self):
        graph = analyze_sanskrit("ramah avadat")["prakriya_graph"]

        self.assertTrue(all("id" in node and "label" in node for node in graph["nodes"]))
        self.assertTrue(all("from" in edge and "to" in edge and "rule" in edge for edge in graph["edges"]))

    def test_build_prakriya_graph_does_not_mutate_inputs(self):
        history = [
            {"stage": "input", "rule": "normalize", "input": "a", "output": "a"},
            {"stage": "final-form cleanup", "rule": "cleanup", "input": "a", "output": "a"},
        ]
        lexical = [{"token": "a", "lemma": "a", "gloss": "test", "gender": None, "source": None}]
        padas = [{"label": "P1", "text": "a"}]
        syllables = [{"text": "a", "weight": "Laghu"}]
        before = copy.deepcopy((history, lexical, padas, syllables))

        graph = build_prakriya_graph(history, lexical_entries=lexical, padas=padas, phonological_syllables=syllables)

        self.assertEqual((history, lexical, padas, syllables), before)
        self.assertEqual(graph["metadata"]["overlaysAttached"], EXPECTED_OVERLAYS)

    def test_unified_prakriya_graph_is_stable_for_same_input(self):
        first = analyze_sanskrit("devam rtvijam")["prakriya_graph"]
        second = analyze_sanskrit("devam rtvijam")["prakriya_graph"]

        self.assertEqual(first, second)

    def test_analyze_endpoint_returns_unified_graph_payload(self):
        client = TestClient(app)
        response = client.post("/api/v3/analyze", json={"input_text": "agnim ile"})

        self.assertEqual(response.status_code, 200)
        graph = response.json()["prakriya_graph"]
        self.assertEqual(graph["schemaVersion"], "prakriya-unified-graph.backend.v1")
        self.assertEqual(graph["metadata"]["overlaysAttached"], EXPECTED_OVERLAYS)


if __name__ == "__main__":
    unittest.main()
