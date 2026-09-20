import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.derivation_replay_exporter import DerivationReplayExporter
from engines.derivation_session import DerivationSession


class DerivationReplayPipelineTests(unittest.TestCase):
    def setUp(self):
        self.exporter = DerivationReplayExporter()

    def create_session(self):
        session = DerivationSession.create(
            "\u0930\u093e\u092e\u0903 \u0905\u0938\u094d\u0924\u093f",
            metadata={"source": "replay_test"},
        )
        first = session.add_step(
            "Node 3 Morphology",
            "noun_inflection",
            {"request": {"stem": "\u0930\u093e\u092e"}},
            {"form": "\u0930\u093e\u092e\u0903"},
        )
        session.add_step(
            "Node 2 Sandhi",
            "sandhi_execution",
            {"word1": "\u0930\u093e\u092e\u0903", "word2": "\u0905\u0938\u094d\u0924\u093f"},
            {"merged": "\u0930\u093e\u092e\u094b\u093d\u0938\u094d\u0924\u093f"},
            parent_step_id=first.step_id,
        )
        return session

    def test_empty_replay_export(self):
        session = DerivationSession.create("debug")
        replay = self.exporter.export_replay(session)

        self.assertEqual(replay["timeline"], [])
        self.assertEqual(replay["metadata"]["total_frames"], 0)

    def test_single_frame_replay(self):
        session = DerivationSession.create("debug")
        session.add_step("Node 3 Morphology", "noun_inflection", {"stem": "\u0930\u093e\u092e"}, {"form": "\u0930\u093e\u092e\u0903"})
        replay = self.exporter.export_replay(session)
        frame = replay["timeline"][0]

        self.assertEqual(len(replay["timeline"]), 1)
        self.assertEqual(frame["frame_id"], "frame_s_0001")
        self.assertEqual(frame["title"], "Node 3 Morphology: noun_inflection")
        self.assertEqual(frame["timestamp"], session.created_at)

    def test_multi_frame_replay(self):
        session = self.create_session()
        replay = self.exporter.export_replay(session)

        self.assertEqual(len(replay["timeline"]), 2)
        self.assertEqual(replay["timeline"][0]["step_id"], "s_0001")
        self.assertEqual(replay["timeline"][1]["step_id"], "s_0002")

    def test_ambiguity_frame_export(self):
        session = self.create_session()
        session.add_ambiguity_branch({"candidate_id": "candidate-a", "final_output": "\u0930\u093e\u092e\u094b\u093d\u0938\u094d\u0924\u093f"})
        replay = self.exporter.export_replay(session)

        self.assertEqual(replay["timeline"][0]["ambiguity_branch_ids"], ["candidate-a"])
        self.assertEqual(replay["timeline"][1]["ambiguity_branch_ids"], ["candidate-a"])

    def test_metadata_preservation(self):
        session = self.create_session()
        replay = self.exporter.export_replay(session)

        self.assertEqual(replay["metadata"]["session_id"], session.session_id)
        self.assertEqual(replay["metadata"]["created_at"], session.created_at)
        self.assertEqual(replay["metadata"]["input_text"], "\u0930\u093e\u092e\u0903 \u0905\u0938\u094d\u0924\u093f")
        self.assertEqual(replay["metadata"]["total_frames"], 2)

    def test_deterministic_ordering(self):
        session = self.create_session()
        first_replay = self.exporter.export_replay(session)
        second_replay = self.exporter.export_replay(session)

        self.assertEqual([frame["step_id"] for frame in first_replay["timeline"]], ["s_0001", "s_0002"])
        self.assertEqual(first_replay, second_replay)

    def test_original_session_unchanged(self):
        session = self.create_session()
        original = copy.deepcopy(session.to_dict())
        replay = self.exporter.export_replay(session)
        replay["timeline"][0]["input_state"]["request"]["stem"] = "changed"

        self.assertEqual(session.to_dict(), original)

    def test_utf8_sanskrit_preservation(self):
        session = self.create_session()
        replay = self.exporter.export_replay(session)

        self.assertEqual(replay["timeline"][0]["output_state"]["form"], "\u0930\u093e\u092e\u0903")
        self.assertEqual(replay["timeline"][1]["output_state"]["merged"], "\u0930\u093e\u092e\u094b\u093d\u0938\u094d\u0924\u093f")

    def test_serialization_compatibility(self):
        session = self.create_session()
        replay = self.exporter.export_replay(session)
        encoded = json.dumps(replay, ensure_ascii=False, sort_keys=True)
        decoded = json.loads(encoded)

        self.assertEqual(decoded, replay)

    def test_replay_id_existence(self):
        session = self.create_session()
        replay = self.exporter.export_replay(session)

        self.assertEqual(replay["replay_id"], f"replay_{session.session_id}")


if __name__ == "__main__":
    unittest.main()
