import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.replay_diff_engine import ReplayDiffEngine


class ReplayDiffEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = ReplayDiffEngine()
        self.base = {
            "replay_id": "base",
            "timeline": [
                {
                    "frame_id": "frame_s_0001",
                    "step_id": "s_0001",
                    "output_state": {"form": "rama", "sutra": "6.1.101"},
                    "ambiguity_branch_ids": ["branch-a"],
                    "semantic": {"semanticTag": "agent"},
                },
                {"frame_id": "frame_s_0002", "step_id": "s_0002", "output_state": {"sutra": "8.4.40"}},
            ],
        }
        self.target = {
            "replay_id": "target",
            "timeline": [
                {
                    "frame_id": "frame_s_0001",
                    "step_id": "s_0001",
                    "output_state": {"form": "ramah", "sutra": "6.1.101"},
                    "ambiguity_branch_ids": ["branch-b"],
                    "semantic": {"semanticTag": "subject"},
                },
                {"frame_id": "frame_s_0003", "step_id": "s_0003", "output_state": {"sutra": "1.3.12"}},
            ],
        }

    def test_compare_replays_returns_stable_shape(self):
        diff = self.engine.compare_replays(self.base, self.target)

        self.assertEqual(diff["baseReplayId"], "base")
        self.assertEqual(diff["targetReplayId"], "target")
        self.assertEqual(set(diff.keys()), {"baseReplayId", "targetReplayId", "stepDiffs", "sutraDiffs", "branchDiffs", "semanticDiffs", "summary"})

    def test_detects_added_removed_and_changed_steps(self):
        diff = self.engine.compare_replays(self.base, self.target)
        step_types = {(item["type"], item["stepId"]) for item in diff["stepDiffs"]}

        self.assertIn(("changed", "s_0001"), step_types)
        self.assertIn(("removed", "s_0002"), step_types)
        self.assertIn(("added", "s_0003"), step_types)

    def test_compares_sutras_branches_and_semantics(self):
        diff = self.engine.compare_replays(self.base, self.target)

        self.assertIn({"type": "removed", "sutraId": "8.4.40"}, diff["sutraDiffs"])
        self.assertIn({"type": "added", "sutraId": "1.3.12"}, diff["sutraDiffs"])
        self.assertIn({"type": "removed", "branchId": "branch-a"}, diff["branchDiffs"])
        self.assertIn({"type": "added", "branchId": "branch-b"}, diff["branchDiffs"])
        self.assertIn({"type": "removed", "semanticId": "agent", "base": {"semanticTag": "agent"}}, diff["semanticDiffs"])
        self.assertIn({"type": "added", "semanticId": "subject", "target": {"semanticTag": "subject"}}, diff["semanticDiffs"])

    def test_summary_counts_are_deterministic(self):
        diff = self.engine.compare_replays(self.base, self.target)

        self.assertEqual(diff["summary"]["addedSteps"], 1)
        self.assertEqual(diff["summary"]["removedSteps"], 1)
        self.assertEqual(diff["summary"]["changedSteps"], 1)
        json.dumps(diff, ensure_ascii=False, sort_keys=True)

    def test_inputs_are_not_mutated(self):
        base = copy.deepcopy(self.base)
        target = copy.deepcopy(self.target)

        self.engine.compare_replays(base, target)

        self.assertEqual(base, self.base)
        self.assertEqual(target, self.target)

    def test_rejects_non_dict_inputs(self):
        with self.assertRaises(ValueError):
            self.engine.compare_replays([], {})


if __name__ == "__main__":
    unittest.main()
