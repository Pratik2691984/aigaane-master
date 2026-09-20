import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.semantic_query_engine import SemanticQueryEngine


class SemanticQueryEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = SemanticQueryEngine()
        self.corpus = [
            {
                "replay_id": "r1",
                "timeline": [{"step_id": "s_0001", "output_state": {"sutra": "1.3.12"}, "semantic": {"semanticTag": "atmanepada"}}],
                "ambiguity_branches": [{"branch_id": "a", "status": "selected"}],
                "provenanceScore": {"score": 0.91},
            },
            {
                "replay_id": "r2",
                "timeline": [{"step_id": "s_0001", "output_state": {"sutra": "6.1.101"}}],
                "provenanceScore": {"score": 0.4},
            },
            {"lexical_id": "dhatu_ram", "category": "verb", "padaRule": "1.3.12"},
        ]

    def test_finds_derivations_using_sutra(self):
        results = self.engine.find_derivations_using_sutra(self.corpus, "6.1.101")

        self.assertEqual([item["id"] for item in results], ["r2"])

    def test_finds_traces_with_ambiguity(self):
        results = self.engine.find_traces_with_ambiguity(self.corpus)

        self.assertEqual([item["id"] for item in results], ["r1"])

    def test_finds_outputs_by_semantic_tag(self):
        results = self.engine.find_outputs_linked_to_semantic_tag(self.corpus, "atmanepada")

        self.assertEqual([item["id"] for item in results], ["r1"])

    def test_finds_dhatus_by_pada_rule(self):
        results = self.engine.find_dhatus_with_pada_rule(self.corpus, "1.3.12")

        self.assertEqual(results[-1]["id"], "dhatu_ram")

    def test_finds_sessions_above_provenance_threshold(self):
        results = self.engine.find_replay_sessions_above_provenance(self.corpus, 0.9)

        self.assertEqual([item["id"] for item in results], ["r1"])

    def test_query_is_read_only(self):
        corpus = copy.deepcopy(self.corpus)
        self.engine.find_derivations_using_sutra(corpus, "1.3.12")

        self.assertEqual(corpus, self.corpus)

    def test_rejects_unsupported_query(self):
        with self.assertRaises(ValueError):
            self.engine.query(self.corpus, {"type": "unknown"})


if __name__ == "__main__":
    unittest.main()
