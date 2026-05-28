import unittest


class TestChandasMetreRegistry(unittest.TestCase):
    def test_backend_chandas_metadata_attached(self):
        from api.engines.vyakarana import build_prakriya_graph

        graph = build_prakriya_graph(
            [{"stage": "input", "input": "x", "output": "x", "rule": "identity"}],
            phonological_syllables=[{"text": "अ"}],
            padas=[],
        )

        self.assertIn("metadata", graph)
        self.assertTrue(graph["metadata"].get("chandasMetreRegistryAttached"))
        self.assertTrue(graph["metadata"].get("chandasRhythmLayerAttached"))
        self.assertTrue(graph["metadata"].get("chandasStructuralGraphAttached"))

        chandas_overlay = next(
            overlay for overlay in graph["overlays"] if overlay["overlayType"] == "chandas"
        )

        self.assertIn("metreCandidateCount", chandas_overlay["diagnostics"])
        self.assertIn("padaRhythmCandidateCount", chandas_overlay["diagnostics"])
        self.assertIn("caesuraCandidateCount", chandas_overlay["diagnostics"])
        self.assertIn("structuralGraphNodeCount", chandas_overlay["diagnostics"])
        self.assertIn("structuralGraphEdgeCount", chandas_overlay["diagnostics"])


if __name__ == "__main__":
    unittest.main()