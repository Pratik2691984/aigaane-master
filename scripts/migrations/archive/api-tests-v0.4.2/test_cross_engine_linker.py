import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.cross_engine_linker import CrossEngineLinker


class CrossEngineLinkerTests(unittest.TestCase):
    def setUp(self):
        self.linker = CrossEngineLinker(semantic_registry={"agent": {"label": "Agent role"}})

    def test_links_to_existing_registries_and_future_references(self):
        payload = {
            "timeline": [
                {
                    "step_id": "s_0001",
                    "output_state": {"sutra": "8.4.40", "lemma_iast": "ram"},
                    "semantic": {"semanticTag": "agent"},
                }
            ]
        }

        result = self.linker.link(payload)

        self.assertEqual(result["crossEngineLinkVersion"], "1.0")
        self.assertEqual(result["links"]["sutraRegistry"][0]["id"], "8.4.40")
        self.assertTrue(result["links"]["sutraRegistry"][0]["resolved"])
        self.assertEqual(result["links"]["semanticRegistry"][0]["id"], "agent")
        self.assertEqual(result["links"]["bijaRegistry"][0]["status"], "reserved_future_reference")
        self.assertEqual(result["links"]["vector49DLayer"][0]["status"], "reserved_future_reference")

    def test_unresolved_references_are_kept_as_references(self):
        result = self.linker.link({"sutra": "0.0.0", "semanticTag": "unknown"})

        self.assertFalse(result["links"]["sutraRegistry"][0]["resolved"])
        self.assertFalse(result["links"]["semanticRegistry"][0]["resolved"])

    def test_does_not_mutate_payload(self):
        payload = {"sutra": "8.4.40"}
        original = copy.deepcopy(payload)

        self.linker.link(payload)

        self.assertEqual(payload, original)

    def test_rejects_non_dict_input(self):
        with self.assertRaises(ValueError):
            self.linker.link([])


if __name__ == "__main__":
    unittest.main()
