import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

import kernel_api
from engines.derivation_session import DerivationSession
from engines.session_storage import DebugSessionStorage
from kernel_api import app


class DebugSessionStoragePipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage = DebugSessionStorage(Path(self.temp_dir.name))
        self.client = TestClient(app)
        self.previous_api_storage = kernel_api.debug_session_storage
        kernel_api.debug_session_storage = self.storage

    def tearDown(self):
        kernel_api.debug_session_storage = self.previous_api_storage
        self.temp_dir.cleanup()

    def create_session(self):
        session = DerivationSession.create(
            "\u0930\u093e\u092e\u0903 \u0905\u0938\u094d\u0924\u093f",
            metadata={"source": "storage_test", "label": "\u092a\u0930\u0940\u0915\u094d\u0937\u093e"},
        )
        first = session.add_step(
            engine="Node 3 Morphology",
            operation="noun_inflection",
            input_state={"request": {"stem": "\u0930\u093e\u092e"}},
            output_state={"form": "\u0930\u093e\u092e\u0903"},
            derivation_path=[{"sutra": "phase1_output", "operation": "phase1_morphology_output"}],
            metadata={"source": "test"},
        )
        session.add_step(
            engine="Node 2 Sandhi",
            operation="sandhi_execution",
            input_state={"word1": "\u0930\u093e\u092e\u0903", "word2": "\u0905\u0938\u094d\u0924\u093f"},
            output_state={"merged": "\u0930\u093e\u092e\u094b\u093d\u0938\u094d\u0924\u093f"},
            parent_step_id=first.step_id,
            derivation_path=[{"sutra": "6.1.114", "operation": "visarga_to_o_avagraha"}],
            metadata={"source": "test"},
        )
        session.add_ambiguity_branch(
            {
                "candidate_id": "debug-1",
                "final_output": "\u0930\u093e\u092e\u094b\u093d\u0938\u094d\u0924\u093f",
                "reason": "\u0938\u0902\u0926\u0930\u094d\u092d",
            }
        )
        return session

    def assert_storage_error(self, response):
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "session_storage_error")

    def test_save_session(self):
        session = self.create_session()
        path = self.storage.save_session(session)

        self.assertEqual(path, f"debug_sessions/{session.session_id}.json")
        self.assertTrue((Path(self.temp_dir.name) / f"{session.session_id}.json").exists())

    def test_load_session(self):
        session = self.create_session()
        self.storage.save_session(session)
        loaded = self.storage.load_session(session.session_id)

        self.assertEqual(loaded.to_dict(), session.to_dict())

    def test_list_sessions(self):
        session = self.create_session()
        self.storage.save_session(session)
        sessions = self.storage.list_sessions()

        self.assertEqual(
            sessions,
            [
                {
                    "session_id": session.session_id,
                    "created_at": session.created_at,
                    "step_count": 2,
                }
            ],
        )

    def test_delete_session(self):
        session = self.create_session()
        self.storage.save_session(session)

        self.assertTrue(self.storage.delete_session(session.session_id))
        self.assertFalse((Path(self.temp_dir.name) / f"{session.session_id}.json").exists())

    def test_preserve_step_graph(self):
        session = self.create_session()
        self.storage.save_session(session)
        loaded = self.storage.load_session(session.session_id)

        self.assertEqual(loaded.steps[1].parent_step_id, loaded.steps[0].step_id)
        self.assertEqual(loaded.steps[1].output_state["merged"], "\u0930\u093e\u092e\u094b\u093d\u0938\u094d\u0924\u093f")

    def test_preserve_ambiguity_branches(self):
        session = self.create_session()
        self.storage.save_session(session)
        loaded = self.storage.load_session(session.session_id)

        self.assertEqual(loaded.ambiguity_branches, session.ambiguity_branches)

    def test_preserve_metadata(self):
        session = self.create_session()
        self.storage.save_session(session)
        loaded = self.storage.load_session(session.session_id)

        self.assertEqual(loaded.metadata, {"source": "storage_test", "label": "\u092a\u0930\u0940\u0915\u094d\u0937\u093e"})

    def test_malformed_json_rejection(self):
        bad_path = Path(self.temp_dir.name) / "bad-session.json"
        bad_path.write_text("{not json", encoding="utf-8")

        with self.assertRaises(ValueError):
            self.storage.load_session("bad-session")

    def test_missing_session_rejection(self):
        with self.assertRaises(ValueError):
            self.storage.load_session("missing-session")

    def test_invalid_payload_rejection(self):
        bad_path = Path(self.temp_dir.name) / "invalid-session.json"
        bad_path.write_text('{"session_id": "invalid-session"}', encoding="utf-8")

        with self.assertRaises(ValueError):
            self.storage.load_session("invalid-session")

    def test_utf8_preservation(self):
        session = self.create_session()
        self.storage.save_session(session)
        raw = (Path(self.temp_dir.name) / f"{session.session_id}.json").read_text(encoding="utf-8")
        loaded = self.storage.load_session(session.session_id)

        self.assertIn("\u0930\u093e\u092e\u0903", raw)
        self.assertEqual(loaded.input_text, "\u0930\u093e\u092e\u0903 \u0905\u0938\u094d\u0924\u093f")

    def test_endpoint_roundtrip_save_load(self):
        session = self.create_session()
        save_response = self.client.post(
            "/api/v3/debug/session/save",
            json={"session": session.to_dict()},
        )
        self.assertEqual(save_response.status_code, 200)
        self.assertTrue(save_response.json()["saved"])
        self.assertEqual(save_response.json()["session_id"], session.session_id)

        load_response = self.client.post(
            "/api/v3/debug/session/load",
            json={"session_id": session.session_id},
        )

        self.assertEqual(load_response.status_code, 200)
        self.assertEqual(load_response.json()["session"], session.to_dict())

    def test_endpoint_delete(self):
        session = self.create_session()
        self.storage.save_session(session)
        response = self.client.post(
            "/api/v3/debug/session/delete",
            json={"session_id": session.session_id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"deleted": True})
        self.assertFalse((Path(self.temp_dir.name) / f"{session.session_id}.json").exists())

    def test_endpoint_list(self):
        session = self.create_session()
        self.storage.save_session(session)
        response = self.client.get("/api/v3/debug/session/list")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sessions"][0]["session_id"], session.session_id)
        self.assertEqual(response.json()["sessions"][0]["step_count"], 2)

    def test_load_preserves_next_step_counter(self):
        session = DerivationSession.create("debug")
        session.add_step("debug.engine", "first", {}, {})
        self.storage.save_session(session)
        loaded = self.storage.load_session(session.session_id)
        next_step = loaded.add_step("debug.engine", "second", {}, {})

        self.assertEqual(next_step.step_id, "s_0002")

    def test_endpoint_missing_session_rejection(self):
        response = self.client.post("/api/v3/debug/session/save", json={})

        self.assert_storage_error(response)

    def test_endpoint_invalid_payload_rejection(self):
        response = self.client.post(
            "/api/v3/debug/session/save",
            json={"session": {"session_id": "invalid"}},
        )

        self.assert_storage_error(response)


if __name__ == "__main__":
    unittest.main()
