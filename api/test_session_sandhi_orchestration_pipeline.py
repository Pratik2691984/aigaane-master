import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.derivation_session import DerivationSession
from kernel_api import app


class SessionSandhiOrchestrationPipelineTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def run_sandhi(self, session, request_payload):
        return self.client.post(
            "/api/v3/debug/session/run-sandhi",
            json={
                "session": session,
                "request": request_payload,
            },
        )

    def sandhi_request(self, word1, word2):
        return {
            "word1": word1,
            "word2": word2,
        }

    def test_run_vowel_sandhi_on_empty_session(self):
        session = DerivationSession.create("debug")
        response = self.run_sandhi(
            session.to_dict(),
            self.sandhi_request("\u0926\u0947\u0935", "\u0907\u0928\u094d\u0926\u094d\u0930"),
        )
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["total_steps"], 1)
        self.assertEqual(payload["steps"][0]["engine"], "Node 2 Sandhi")
        self.assertEqual(payload["steps"][0]["operation"], "sandhi_execution")
        self.assertEqual(payload["steps"][0]["output_state"]["merged"], "\u0926\u0947\u0935\u0947\u0928\u094d\u0926\u094d\u0930")
        self.assertEqual(payload["steps"][0]["output_state"]["sutra"], "6.1.87")

    def test_run_visarga_sandhi_on_empty_session(self):
        session = DerivationSession.create("debug")
        response = self.run_sandhi(
            session.to_dict(),
            self.sandhi_request("\u0930\u093e\u092e\u0903", "\u0905\u0938\u094d\u0924\u093f"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["steps"][0]["output_state"]["merged"], "\u0930\u093e\u092e\u094b\u093d\u0938\u094d\u0924\u093f")

    def test_run_consonant_sandhi_on_empty_session(self):
        session = DerivationSession.create("debug")
        response = self.run_sandhi(
            session.to_dict(),
            self.sandhi_request("\u0924\u0924\u094d", "\u091a"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["steps"][0]["output_state"]["merged"], "\u0924\u091a\u094d\u091a")

    def test_run_sandhi_sets_parent_to_last_step(self):
        session = DerivationSession.create("debug")
        previous_step = session.add_step(
            engine="debug.engine",
            operation="manual_debug_step",
            input_state={"text": "debug"},
            output_state={"text": "debug"},
        )
        response = self.run_sandhi(
            session.to_dict(),
            self.sandhi_request("\u0926\u0947\u0935", "\u0907\u0928\u094d\u0926\u094d\u0930"),
        )
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["total_steps"], 2)
        self.assertEqual(payload["steps"][1]["parent_step_id"], previous_step.step_id)

    def test_missing_session_returns_400(self):
        response = self.client.post(
            "/api/v3/debug/session/run-sandhi",
            json={"request": self.sandhi_request("\u0926\u0947\u0935", "\u0907\u0928\u094d\u0926\u094d\u0930")},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "session_orchestration_error")

    def test_missing_request_returns_400(self):
        response = self.client.post(
            "/api/v3/debug/session/run-sandhi",
            json={"session": DerivationSession.create("debug").to_dict()},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "session_orchestration_error")

    def test_missing_word1_returns_400(self):
        response = self.run_sandhi(
            DerivationSession.create("debug").to_dict(),
            {"word2": "\u0907\u0928\u094d\u0926\u094d\u0930"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "session_orchestration_error")

    def test_missing_word2_returns_400(self):
        response = self.run_sandhi(
            DerivationSession.create("debug").to_dict(),
            {"word1": "\u0926\u0947\u0935"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "session_orchestration_error")

    def test_latin_rejected_by_governance(self):
        response = self.run_sandhi(
            DerivationSession.create("debug").to_dict(),
            self.sandhi_request("\u0926\u0947\u0935", "indra"),
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            response.json()["detail"]["code"],
            {"session_orchestration_error", "lexical_governance_error"},
        )


if __name__ == "__main__":
    unittest.main()
