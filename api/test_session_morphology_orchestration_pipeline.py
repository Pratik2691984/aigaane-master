import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.derivation_session import DerivationSession
from kernel_api import app


class SessionMorphologyOrchestrationPipelineTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def run_morphology(self, session, request_payload):
        return self.client.post(
            "/api/v3/debug/session/run-morphology",
            json={
                "session": session,
                "request": request_payload,
            },
        )

    def noun_request(self, stem, case, number):
        return {
            "mode": "noun",
            "stem": stem,
            "case": case,
            "number": number,
        }

    def test_run_morphology_on_empty_session(self):
        session = DerivationSession.create("debug")
        response = self.run_morphology(
            session.to_dict(),
            self.noun_request("\u0930\u093e\u092e", "nominative", "singular"),
        )
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["total_steps"], 1)
        self.assertEqual(payload["steps"][0]["engine"], "Node 3 Morphology")
        self.assertEqual(payload["steps"][0]["operation"], "noun_inflection")
        self.assertEqual(payload["steps"][0]["output_state"]["form"], "\u0930\u093e\u092e\u0903")

    def test_run_morphology_sets_parent_to_last_step(self):
        session = DerivationSession.create("debug")
        previous_step = session.add_step(
            engine="debug.engine",
            operation="manual_debug_step",
            input_state={"text": "debug"},
            output_state={"text": "debug"},
        )
        response = self.run_morphology(
            session.to_dict(),
            self.noun_request("\u0930\u093e\u092e", "nominative", "singular"),
        )
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["total_steps"], 2)
        self.assertEqual(payload["steps"][1]["parent_step_id"], previous_step.step_id)

    def test_run_morphology_hari(self):
        session = DerivationSession.create("debug")
        response = self.run_morphology(
            session.to_dict(),
            self.noun_request("\u0939\u0930\u093f", "accusative", "singular"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["steps"][0]["output_state"]["form"], "\u0939\u0930\u093f\u092e\u094d")

    def test_run_morphology_nadi(self):
        session = DerivationSession.create("debug")
        response = self.run_morphology(
            session.to_dict(),
            self.noun_request("\u0928\u0926\u0940", "locative", "singular"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["steps"][0]["output_state"]["form"], "\u0928\u0926\u094d\u092f\u093e\u092e\u094d")

    def test_run_morphology_phala(self):
        session = DerivationSession.create("debug")
        response = self.run_morphology(
            session.to_dict(),
            self.noun_request("\u092b\u0932", "nominative", "plural"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["steps"][0]["output_state"]["form"], "\u092b\u0932\u093e\u0928\u093f")

    def test_missing_session_returns_400(self):
        response = self.client.post(
            "/api/v3/debug/session/run-morphology",
            json={"request": self.noun_request("\u0930\u093e\u092e", "nominative", "singular")},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "session_orchestration_error")

    def test_missing_request_returns_400(self):
        response = self.client.post(
            "/api/v3/debug/session/run-morphology",
            json={"session": DerivationSession.create("debug").to_dict()},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "session_orchestration_error")

    def test_unsupported_mode_returns_400(self):
        response = self.run_morphology(
            DerivationSession.create("debug").to_dict(),
            {
                "mode": "verb",
                "stem": "\u0930\u093e\u092e",
                "case": "nominative",
                "number": "singular",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "session_orchestration_error")

    def test_invalid_morphology_request_returns_400(self):
        response = self.run_morphology(
            DerivationSession.create("debug").to_dict(),
            self.noun_request("\u0930\u093e\u092e", "not_a_case", "singular"),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "session_orchestration_error")


if __name__ == "__main__":
    unittest.main()
