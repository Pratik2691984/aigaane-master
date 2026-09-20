import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.derivation_session import DerivationSession
from kernel_api import app


class DerivationSessionAPIPipelineTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def create_session(self):
        response = self.client.post(
            "/api/v3/debug/session/create",
            json={
                "input_text": "\u0930\u093e\u092e\u0903 \u0917\u091a\u094d\u091b\u0924\u093f",
                "metadata": {"source": "debug"},
            },
        )
        self.assertEqual(response.status_code, 200)
        return response.json()

    def append_step(self, session, parent_step_id=None):
        return self.client.post(
            "/api/v3/debug/session/append",
            json={
                "session": session,
                "step": {
                    "engine": "debug.engine",
                    "operation": "debug_operation",
                    "input_state": {"text": "\u0930\u093e\u092e\u0903"},
                    "output_state": {"text": "\u0930\u093e\u092e\u094b"},
                    "parent_step_id": parent_step_id,
                    "derivation_path": [],
                    "metadata": {"sutra": "debug"},
                },
            },
        )

    def test_create_session_endpoint(self):
        payload = self.create_session()

        self.assertEqual(payload["total_steps"], 0)
        self.assertEqual(payload["input_text"], "\u0930\u093e\u092e\u0903 \u0917\u091a\u094d\u091b\u0924\u093f")
        self.assertEqual(payload["steps"], [])
        self.assertEqual(payload["ambiguity_branches"], [])
        self.assertEqual(payload["metadata"], {"source": "debug"})
        self.assertEqual(payload["total_ambiguity_branches"], 0)

    def test_create_session_rejects_blank_input(self):
        response = self.client.post(
            "/api/v3/debug/session/create",
            json={"input_text": "   ", "metadata": {"source": "debug"}},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "session_error")

    def test_append_step_endpoint(self):
        session = self.create_session()
        response = self.append_step(session)
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["total_steps"], 1)
        self.assertEqual(payload["steps"][0]["step_id"], "s_0001")

    def test_append_second_step_parent_link(self):
        session = self.append_step(self.create_session()).json()
        response = self.append_step(session, parent_step_id="s_0001")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["total_steps"], 2)
        self.assertEqual(payload["steps"][1]["parent_step_id"], "s_0001")

    def test_append_invalid_parent_returns_400(self):
        response = self.append_step(self.create_session(), parent_step_id="s_9999")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "session_error")

    def test_append_missing_session_returns_400(self):
        response = self.client.post(
            "/api/v3/debug/session/append",
            json={
                "step": {
                    "engine": "debug.engine",
                    "operation": "debug_operation",
                    "input_state": {},
                    "output_state": {},
                }
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "session_error")

    def test_from_dict_preserves_next_step_counter(self):
        session = DerivationSession.create("\u0930\u093e\u092e\u0903")
        session.add_step("debug.engine", "first", {}, {})
        reconstructed = DerivationSession.from_dict(session.to_dict())
        next_step = reconstructed.add_step("debug.engine", "second", {}, {})

        self.assertEqual(next_step.step_id, "s_0002")

    def test_append_malformed_session_returns_400(self):
        response = self.client.post(
            "/api/v3/debug/session/append",
            json={
                "session": {"session_id": "debug"},
                "step": {
                    "engine": "debug.engine",
                    "operation": "debug_operation",
                    "input_state": {},
                    "output_state": {},
                },
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "session_error")


if __name__ == "__main__":
    unittest.main()
