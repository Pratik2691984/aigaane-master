import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.semantic_rule_attribution_engine import SemanticRuleAttributionEngine


class SemanticRuleAttributionEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = SemanticRuleAttributionEngine()

    def test_attributes_rule_semantics_to_steps_and_sutras(self):
        payload = {
            "timeline": [
                {"step_id": "s_0001", "output_state": {"sutra": "1.3.12"}},
                {"step_id": "s_0002", "output_state": {"sutra": "6.1.101"}, "semantic": {"semanticTag": "vowel_coalescence"}},
            ]
        }
        rules = [{"sutraId": "1.3.12", "semanticTag": "atmanepada_marker", "confidence": 0.95, "source": "rule"}]

        result = self.engine.attribute_semantics(payload, rules)

        self.assertEqual(result["semanticAttributionVersion"], "1.0")
        self.assertIn(
            {"stepId": "s_0001", "sutraId": "1.3.12", "semanticTag": "atmanepada_marker", "confidence": 0.95, "source": "rule"},
            result["semanticAttributions"],
        )
        self.assertIn(
            {"stepId": "s_0002", "sutraId": "6.1.101", "semanticTag": "vowel_coalescence", "confidence": 0.8, "source": "derived"},
            result["semanticAttributions"],
        )

    def test_does_not_mutate_trace_payload(self):
        payload = {"steps": [{"step_id": "s_0001", "sutra": "8.4.40", "semanticTag": "assimilation"}]}
        original = copy.deepcopy(payload)

        self.engine.attribute_semantics(payload)

        self.assertEqual(payload, original)

    def test_rejects_non_dict_input(self):
        with self.assertRaises(ValueError):
            self.engine.attribute_semantics([])


if __name__ == "__main__":
    unittest.main()
