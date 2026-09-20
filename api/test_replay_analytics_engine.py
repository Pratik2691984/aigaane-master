import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.replay_analytics_engine import ReplayAnalyticsEngine


class ReplayAnalyticsEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = ReplayAnalyticsEngine()
        self.graph = {
            "nodes": [
                {"node_id": "node_s_0001", "output_state": {"sutra": "6.1.101"}, "semantic": {"semanticTag": "agent"}, "ambiguity_branch_ids": ["a", "b"]},
                {"node_id": "node_s_0002", "output_state": {"sutra": "8.4.40"}, "semantic": {"semanticTag": "agent"}},
                {"node_id": "node_s_0003", "output_state": {"sutra": "8.4.40"}, "semantic": {"semanticTag": "action"}},
            ],
            "edges": [
                {"source": "node_s_0001", "target": "node_s_0002"},
                {"source": "node_s_0002", "target": "node_s_0003"},
            ],
            "ambiguity_branches": [{"branch_id": "a", "status": "selected"}, {"branch_id": "b", "status": "rejected"}],
        }

    def test_computes_graph_analytics(self):
        analytics = self.engine.compute_analytics(self.graph)

        self.assertEqual(analytics["nodeCount"], 3)
        self.assertEqual(analytics["edgeCount"], 2)
        self.assertEqual(analytics["ambiguityCount"], 2)
        self.assertEqual(analytics["maxDepth"], 3)
        self.assertEqual(analytics["selectedPathLength"], 3)
        self.assertEqual(analytics["rejectedBranchCount"], 1)
        self.assertEqual(analytics["semanticTagDistribution"], {"action": 1, "agent": 2})
        self.assertEqual(analytics["sutraFrequency"], {"6.1.101": 1, "8.4.40": 2})

    def test_accepts_replay_without_mutation(self):
        replay = {
            "timeline": [
                {"step_id": "s_0001", "output_state": {"sutra": "6.1.101"}, "semantic": {"semanticTag": "agent"}},
                {"step_id": "s_0002", "output_state": {"sutra": "8.4.40"}, "ambiguity_branch_ids": ["x"]},
            ],
        }
        original = copy.deepcopy(replay)

        analytics = self.engine.compute_analytics(replay)

        self.assertEqual(analytics["nodeCount"], 2)
        self.assertEqual(analytics["edgeCount"], 0)
        self.assertEqual(analytics["maxDepth"], 2)
        self.assertEqual(replay, original)

    def test_rejects_non_dict_input(self):
        with self.assertRaises(ValueError):
            self.engine.compute_analytics([])


if __name__ == "__main__":
    unittest.main()
