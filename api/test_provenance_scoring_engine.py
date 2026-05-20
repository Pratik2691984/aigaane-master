import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.provenance_scoring_engine import ProvenanceScoringEngine


class ProvenanceScoringEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = ProvenanceScoringEngine()

    def test_scores_explainable_components(self):
        payload = {
            "replay_id": "r1",
            "timeline": [
                {"step_id": "s_0001", "operation": "morphology", "input_state": {}, "output_state": {"sutra": "1.3.12"}},
                {"step_id": "s_0002", "operation": "sandhi", "input_state": {}, "output_state": {"sutra": "6.1.101"}},
            ],
            "metadata": {"session_id": "s1", "total_frames": 2},
            "ambiguity_branches": [{"branch_id": "a", "status": "selected"}, {"branch_id": "b", "status": "rejected"}],
            "semanticAttributions": [{"stepId": "s_0001", "semanticTag": "agent", "confidence": 0.8}],
        }

        result = self.engine.score_derivation(payload)

        self.assertGreaterEqual(result["score"], 0.8)
        self.assertIn(result["grade"], {"high", "canonical"})
        self.assertEqual(set(result["components"].keys()), set(ProvenanceScoringEngine.COMPONENT_WEIGHTS.keys()))
        self.assertTrue(result["explanation"])

    def test_low_score_for_sparse_payload(self):
        result = self.engine.score_derivation({"timeline": [{"step_id": "s_0001"}]})

        self.assertLess(result["score"], 0.5)
        self.assertEqual(result["grade"], "low")

    def test_rejects_non_dict_input(self):
        with self.assertRaises(ValueError):
            self.engine.score_derivation([])


if __name__ == "__main__":
    unittest.main()
