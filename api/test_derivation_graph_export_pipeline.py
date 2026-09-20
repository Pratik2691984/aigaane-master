import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.derivation_graph_exporter import DerivationGraphExporter
from engines.derivation_session import DerivationSession


class DerivationGraphExportPipelineTests(unittest.TestCase):
    def setUp(self):
        self.exporter = DerivationGraphExporter()

    def create_session(self):
        session = DerivationSession.create("\u0930\u093e\u092e\u0903 \u0905\u0938\u094d\u0924\u093f", metadata={"source": "graph_test"})
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

    def test_empty_session_export(self):
        session = DerivationSession.create("debug")
        graph = self.exporter.export_session_graph(session)

        self.assertEqual(graph["nodes"], [])
        self.assertEqual(graph["edges"], [])
        self.assertEqual(graph["metadata"]["total_nodes"], 0)
        self.assertEqual(graph["metadata"]["total_edges"], 0)

    def test_single_step_graph(self):
        session = DerivationSession.create("debug")
        session.add_step("Node 3 Morphology", "noun_inflection", {"stem": "\u0930\u093e\u092e"}, {"form": "\u0930\u093e\u092e\u0903"})
        graph = self.exporter.export_session_graph(session)
        node = graph["nodes"][0]

        self.assertEqual(len(graph["nodes"]), 1)
        self.assertEqual(node["node_id"], "node_s_0001")
        self.assertEqual(node["title"], "Node 3 Morphology: noun_inflection")
        self.assertEqual(node["timestamp"], session.created_at)

    def test_multi_step_graph(self):
        session = self.create_session()
        graph = self.exporter.export_session_graph(session)

        self.assertEqual(len(graph["nodes"]), 2)
        self.assertEqual(graph["nodes"][0]["step_id"], "s_0001")
        self.assertEqual(graph["nodes"][1]["step_id"], "s_0002")

    def test_edge_creation(self):
        session = self.create_session()
        graph = self.exporter.export_session_graph(session)

        self.assertEqual(
            graph["edges"],
            [
                {
                    "edge_id": "edge_s_0001_to_s_0002",
                    "source": "node_s_0001",
                    "target": "node_s_0002",
                    "relation": "derives_to",
                }
            ],
        )

    def test_ambiguity_branch_export(self):
        session = self.create_session()
        session.add_ambiguity_branch({"candidate_id": "candidate-a", "final_output": "\u0930\u093e\u092e\u094b\u093d\u0938\u094d\u0924\u093f"})
        graph = self.exporter.export_session_graph(session)

        self.assertEqual(graph["nodes"][0]["ambiguity_branch_ids"], ["candidate-a"])
        self.assertEqual(graph["nodes"][1]["ambiguity_branch_ids"], ["candidate-a"])

    def test_metadata_preservation(self):
        session = self.create_session()
        graph = self.exporter.export_session_graph(session)

        self.assertEqual(graph["metadata"]["session_id"], session.session_id)
        self.assertEqual(graph["metadata"]["created_at"], session.created_at)
        self.assertEqual(graph["metadata"]["input_text"], "\u0930\u093e\u092e\u0903 \u0905\u0938\u094d\u0924\u093f")

    def test_deterministic_node_ordering(self):
        session = self.create_session()
        first_graph = self.exporter.export_session_graph(session)
        second_graph = self.exporter.export_session_graph(session)

        self.assertEqual([node["step_id"] for node in first_graph["nodes"]], ["s_0001", "s_0002"])
        self.assertEqual(first_graph, second_graph)

    def test_original_session_unchanged(self):
        session = self.create_session()
        original = copy.deepcopy(session.to_dict())
        graph = self.exporter.export_session_graph(session)
        graph["nodes"][0]["input_state"]["request"]["stem"] = "changed"

        self.assertEqual(session.to_dict(), original)

    def test_utf8_sanskrit_preservation(self):
        session = self.create_session()
        graph = self.exporter.export_session_graph(session)

        self.assertEqual(graph["nodes"][0]["output_state"]["form"], "\u0930\u093e\u092e\u0903")
        self.assertEqual(graph["nodes"][1]["output_state"]["merged"], "\u0930\u093e\u092e\u094b\u093d\u0938\u094d\u0924\u093f")

    def test_serialization_compatibility(self):
        session = self.create_session()
        graph = self.exporter.export_session_graph(session)
        encoded = json.dumps(graph, ensure_ascii=False, sort_keys=True)
        decoded = json.loads(encoded)

        self.assertEqual(decoded, graph)


if __name__ == "__main__":
    unittest.main()
