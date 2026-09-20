import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.ambiguity_resolver import ExecutableAmbiguityDAG


class ExecutableDAGPipelineTests(unittest.TestCase):
    def setUp(self):
        self.dag = ExecutableAmbiguityDAG()

    def test_empty_variants_returns_non_ambiguous_empty_payload(self):
        payload = self.dag.execute_fork("Node 6B Test Engine", [])

        self.assertFalse(payload["is_ambiguous"])
        self.assertEqual(payload["candidates"], [])
        self.assertEqual(payload["strategy"], "none")
        self.assertIsNone(payload["selected_candidate_id"])

    def test_single_variant_returns_unambiguous_payload(self):
        payload = self.dag.execute_fork(
            "Node 2C Consonant Sandhi",
            [
                {
                    "final_output": "तच्च",
                    "reason": "Single derivation",
                    "derivation_path": [{"sutra": "8.4.40"}],
                }
            ],
        )

        self.assertFalse(payload["is_ambiguous"])
        self.assertIsNone(payload["selected_candidate_id"])
        self.assertEqual(payload["candidates"][0]["final_output"], "तच्च")

    def test_multiple_variants_returns_ambiguous_payload(self):
        payload = self.dag.execute_fork(
            "Node 6B Test Engine",
            [
                {"final_output": "तच्च", "reason": "Path A", "derivation_path": []},
                {"final_output": "तद् च", "reason": "Path B", "derivation_path": []},
            ],
        )

        self.assertTrue(payload["is_ambiguous"])
        self.assertEqual(len(payload["candidates"]), 2)
        self.assertEqual(payload["candidates"][0]["candidate_id"], "0")
        self.assertEqual(payload["candidates"][1]["candidate_id"], "1")
        self.assertIsNone(payload["selected_candidate_id"])
        self.assertEqual(payload["strategy"], "enumeration_only")

    def test_candidate_fields_are_preserved(self):
        derivation_path = [{"sutra": "8.4.40"}]
        payload = self.dag.execute_fork(
            "Node 2C Consonant Sandhi",
            [
                {
                    "final_output": "तच्च",
                    "reason": "Path A",
                    "derivation_path": derivation_path,
                },
                {
                    "final_output": "तद् च",
                    "reason": "Path B",
                    "derivation_path": [],
                },
            ],
        )
        candidate = payload["candidates"][0]

        self.assertEqual(candidate["final_output"], "तच्च")
        self.assertEqual(candidate["source_engine"], "Node 2C Consonant Sandhi")
        self.assertEqual(candidate["reason"], "Path A")
        self.assertEqual(candidate["derivation_path"], derivation_path)
        self.assertIsNone(candidate["confidence"])

    def test_missing_final_output_raises_value_error(self):
        with self.assertRaisesRegex(ValueError, "final_output"):
            self.dag.execute_fork("Node 6B Test Engine", [{"reason": "Missing output"}])


if __name__ == "__main__":
    unittest.main()
