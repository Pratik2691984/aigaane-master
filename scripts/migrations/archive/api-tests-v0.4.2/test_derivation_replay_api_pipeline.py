import copy
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.derivation_session import DerivationSession
from kernel_api import app


class DerivationReplayApiPipelineTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def create_session(self):
        session = DerivationSession.create(
            "\u0930\u093e\u092e\u0903 \u0905\u0938\u094d\u0924\u093f",
            metadata={"source": "replay_api_test"},
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

    def test_export_endpoint_returns_200(self):
        session = self.create_session()
        response = self.client.post("/api/v3/debug/replay/export", json={"session": session.to_dict()})

        self.assertEqual(response.status_code, 200)
        self.assertIn("replay", response.json())

    def test_replay_frames_exist(self):
        session = self.create_session()
        response = self.client.post("/api/v3/debug/replay/export", json={"session": session.to_dict()})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["replay"]["timeline"]), 2)
        self.assertEqual(response.json()["replay"]["timeline"][0]["frame_id"], "frame_s_0001")

    def test_metadata_preserved(self):
        session = self.create_session()
        response = self.client.post("/api/v3/debug/replay/export", json={"session": session.to_dict()})
        metadata = response.json()["replay"]["metadata"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(metadata["session_id"], session.session_id)
        self.assertEqual(metadata["created_at"], session.created_at)
        self.assertEqual(metadata["input_text"], "\u0930\u093e\u092e\u0903 \u0905\u0938\u094d\u0924\u093f")
        self.assertEqual(metadata["total_frames"], 2)

    def test_utf8_sanskrit_preserved(self):
        session = self.create_session()
        response = self.client.post("/api/v3/debug/replay/export", json={"session": session.to_dict()})
        timeline = response.json()["replay"]["timeline"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(timeline[0]["output_state"]["form"], "\u0930\u093e\u092e\u0903")
        self.assertEqual(timeline[1]["output_state"]["merged"], "\u0930\u093e\u092e\u094b\u093d\u0938\u094d\u0924\u093f")

    def test_malformed_payload_rejection(self):
        response = self.client.post("/api/v3/debug/replay/export", json={"session": {"session_id": "bad"}})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "derivation_replay_error")

    def test_empty_session_export(self):
        session = DerivationSession.create("debug")
        response = self.client.post("/api/v3/debug/replay/export", json={"session": session.to_dict()})
        replay = response.json()["replay"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(replay["timeline"], [])
        self.assertEqual(replay["metadata"]["total_frames"], 0)

    def test_demo_endpoint_returns_200(self):
        response = self.client.get("/api/v3/debug/replay/demo")

        self.assertEqual(response.status_code, 200)
        self.assertIn("replay", response.json())

    def test_demo_replay_structure_valid(self):
        response = self.client.get("/api/v3/debug/replay/demo")
        replay = response.json()["replay"]

        self.assertEqual(response.status_code, 200)
        self.assertTrue(replay["replay_id"].startswith("replay_"))
        self.assertGreaterEqual(len(replay["timeline"]), 2)
        self.assertEqual(replay["metadata"]["total_frames"], len(replay["timeline"]))
        self.assertEqual(replay["timeline"][1]["output_state"]["semantic"]["surface_form"], "\u0930\u093e\u092e\u094b\u093d\u0938\u094d\u0924\u093f")

    def test_ambiguity_branch_replay_support(self):
        response = self.client.get("/api/v3/debug/replay/demo")
        timeline = response.json()["replay"]["timeline"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(timeline[0]["ambiguity_branch_ids"], ["demo-branch-primary"])
        self.assertEqual(timeline[1]["ambiguity_branch_ids"], ["demo-branch-primary"])

    def test_original_session_unchanged(self):
        session = self.create_session()
        original = copy.deepcopy(session.to_dict())

        response = self.client.post("/api/v3/debug/replay/export", json={"session": session.to_dict()})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(session.to_dict(), original)


if __name__ == "__main__":
    unittest.main()
