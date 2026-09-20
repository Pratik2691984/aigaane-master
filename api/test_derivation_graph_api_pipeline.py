import copy
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.derivation_session import DerivationSession
from kernel_api import app


class DerivationGraphApiPipelineTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def create_session(self):
        session = DerivationSession.create(
            "\u0930\u093e\u092e\u0903 \u0905\u0938\u094d\u0924\u093f",
            metadata={"source": "graph_api_test"},
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
        response = self.client.post("/api/v3/debug/graph/export", json={"session": session.to_dict()})

        self.assertEqual(response.status_code, 200)
        self.assertIn("graph", response.json())

    def test_graph_nodes_exist(self):
        session = self.create_session()
        response = self.client.post("/api/v3/debug/graph/export", json={"session": session.to_dict()})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["graph"]["nodes"]), 2)

    def test_graph_edges_exist(self):
        session = self.create_session()
        response = self.client.post("/api/v3/debug/graph/export", json={"session": session.to_dict()})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["graph"]["edges"],
            [
                {
                    "edge_id": "edge_s_0001_to_s_0002",
                    "source": "node_s_0001",
                    "target": "node_s_0002",
                    "relation": "derives_to",
                }
            ],
        )

    def test_metadata_preserved(self):
        session = self.create_session()
        response = self.client.post("/api/v3/debug/graph/export", json={"session": session.to_dict()})
        metadata = response.json()["graph"]["metadata"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(metadata["session_id"], session.session_id)
        self.assertEqual(metadata["created_at"], session.created_at)
        self.assertEqual(metadata["input_text"], "\u0930\u093e\u092e\u0903 \u0905\u0938\u094d\u0924\u093f")

    def test_utf8_sanskrit_preserved(self):
        session = self.create_session()
        response = self.client.post("/api/v3/debug/graph/export", json={"session": session.to_dict()})
        nodes = response.json()["graph"]["nodes"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(nodes[0]["output_state"]["form"], "\u0930\u093e\u092e\u0903")
        self.assertEqual(nodes[1]["output_state"]["merged"], "\u0930\u093e\u092e\u094b\u093d\u0938\u094d\u0924\u093f")

    def test_malformed_payload_rejection(self):
        response = self.client.post("/api/v3/debug/graph/export", json={"session": {"session_id": "bad"}})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "derivation_graph_error")

    def test_empty_session_export(self):
        session = DerivationSession.create("debug")
        response = self.client.post("/api/v3/debug/graph/export", json={"session": session.to_dict()})
        graph = response.json()["graph"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(graph["nodes"], [])
        self.assertEqual(graph["edges"], [])
        self.assertEqual(graph["metadata"]["total_nodes"], 0)

    def test_demo_endpoint_returns_200(self):
        response = self.client.get("/api/v3/debug/graph/demo")

        self.assertEqual(response.status_code, 200)
        self.assertIn("graph", response.json())

    def test_demo_graph_structure_valid(self):
        response = self.client.get("/api/v3/debug/graph/demo")
        graph = response.json()["graph"]

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(graph["nodes"]), 2)
        self.assertGreaterEqual(len(graph["edges"]), 1)
        self.assertEqual(graph["metadata"]["total_nodes"], len(graph["nodes"]))
        self.assertEqual(graph["nodes"][1]["output_state"]["semantic"]["surface_form"], "\u0930\u093e\u092e\u094b\u093d\u0938\u094d\u0924\u093f")

    def test_original_session_unchanged(self):
        session = self.create_session()
        original = copy.deepcopy(session.to_dict())

        response = self.client.post("/api/v3/debug/graph/export", json={"session": session.to_dict()})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(session.to_dict(), original)


if __name__ == "__main__":
    unittest.main()
