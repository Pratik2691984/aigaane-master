import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.derivation_session import DerivationSession
from kernel_api import app


class SessionPipelineOrchestrationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def valid_pipeline(self):
        return [
            {
                "engine": "morphology",
                "request": {
                    "mode": "noun",
                    "stem": "\u0930\u093e\u092e",
                    "case": "nominative",
                    "number": "singular",
                },
            },
            {
                "engine": "sandhi",
                "request": {
                    "word2": "\u0905\u0938\u094d\u0924\u093f",
                },
            },
        ]

    def run_pipeline(self, session, pipeline):
        return self.client.post(
            "/api/v3/debug/session/run-pipeline",
            json={
                "session": session,
                "pipeline": pipeline,
            },
        )

    def assert_pipeline_error(self, response):
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "session_pipeline_error")

    def test_morphology_then_sandhi_pipeline(self):
        session = DerivationSession.create("debug")
        response = self.run_pipeline(session.to_dict(), self.valid_pipeline())
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["final_output"], "\u0930\u093e\u092e\u094b\u093d\u0938\u094d\u0924\u093f")
        self.assertEqual(payload["session"]["total_steps"], 2)
        self.assertEqual(len(payload["pipeline_steps"]), 2)
        self.assertEqual(payload["pipeline_steps"][0]["output_state"]["form"], "\u0930\u093e\u092e\u0903")
        self.assertEqual(payload["pipeline_steps"][1]["output_state"]["merged"], "\u0930\u093e\u092e\u094b\u093d\u0938\u094d\u0924\u093f")
        self.assertEqual(
            payload["pipeline_steps"][1]["parent_step_id"],
            payload["pipeline_steps"][0]["step_id"],
        )

    def test_pipeline_uses_existing_parent_if_session_has_prior_step(self):
        session = DerivationSession.create("debug")
        manual_step = session.add_step(
            engine="debug.engine",
            operation="manual_debug_step",
            input_state={"text": "debug"},
            output_state={"text": "debug"},
        )
        response = self.run_pipeline(session.to_dict(), self.valid_pipeline())
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["pipeline_steps"][0]["parent_step_id"], manual_step.step_id)
        self.assertEqual(
            payload["pipeline_steps"][1]["parent_step_id"],
            payload["pipeline_steps"][0]["step_id"],
        )

    def test_missing_session_returns_400(self):
        response = self.client.post(
            "/api/v3/debug/session/run-pipeline",
            json={"pipeline": self.valid_pipeline()},
        )

        self.assert_pipeline_error(response)

    def test_malformed_session_returns_400(self):
        response = self.run_pipeline({"session_id": "debug"}, self.valid_pipeline())

        self.assert_pipeline_error(response)

    def test_missing_pipeline_returns_400(self):
        response = self.client.post(
            "/api/v3/debug/session/run-pipeline",
            json={"session": DerivationSession.create("debug").to_dict()},
        )

        self.assert_pipeline_error(response)

    def test_empty_pipeline_returns_400(self):
        response = self.run_pipeline(DerivationSession.create("debug").to_dict(), [])

        self.assert_pipeline_error(response)

    def test_pipeline_length_not_two_returns_400(self):
        pipeline = self.valid_pipeline() + [{"engine": "sandhi", "request": {"word2": "\u091a"}}]
        response = self.run_pipeline(DerivationSession.create("debug").to_dict(), pipeline)

        self.assert_pipeline_error(response)

    def test_first_step_not_morphology_returns_400(self):
        pipeline = self.valid_pipeline()
        pipeline[0]["engine"] = "sandhi"
        response = self.run_pipeline(DerivationSession.create("debug").to_dict(), pipeline)

        self.assert_pipeline_error(response)

    def test_second_step_not_sandhi_returns_400(self):
        pipeline = self.valid_pipeline()
        pipeline[1]["engine"] = "morphology"
        response = self.run_pipeline(DerivationSession.create("debug").to_dict(), pipeline)

        self.assert_pipeline_error(response)

    def test_missing_morphology_fields_returns_400(self):
        for field_name in ["stem", "case", "number"]:
            with self.subTest(field_name=field_name):
                pipeline = self.valid_pipeline()
                del pipeline[0]["request"][field_name]
                response = self.run_pipeline(DerivationSession.create("debug").to_dict(), pipeline)

                self.assert_pipeline_error(response)

    def test_missing_sandhi_word2_returns_400(self):
        pipeline = self.valid_pipeline()
        del pipeline[1]["request"]["word2"]
        response = self.run_pipeline(DerivationSession.create("debug").to_dict(), pipeline)

        self.assert_pipeline_error(response)

    def test_invalid_morphology_returns_400(self):
        pipeline = self.valid_pipeline()
        pipeline[0]["request"]["stem"] = "\u0926\u0947\u0935"
        response = self.run_pipeline(DerivationSession.create("debug").to_dict(), pipeline)

        self.assert_pipeline_error(response)


if __name__ == "__main__":
    unittest.main()
