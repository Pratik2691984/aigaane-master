import unittest


class TestChandasMetreRegistry(unittest.TestCase):
    def test_backend_chandas_metadata_attached(self):
        from api.engines.vyakarana import (
            build_chandas_overlay_api_projection,
            build_prakriya_graph,
        )

        graph = build_prakriya_graph(
            [{"stage": "input", "input": "x", "output": "x", "rule": "identity"}],
            phonological_syllables=[{"text": "अ"}],
            padas=[],
        )

        self.assertIn("metadata", graph)
        self.assertTrue(graph["metadata"].get("chandasMetreRegistryAttached"))
        self.assertTrue(graph["metadata"].get("chandasRhythmLayerAttached"))
        self.assertTrue(graph["metadata"].get("chandasStructuralGraphAttached"))
        self.assertTrue(graph["metadata"].get("chandasRecitationFlowAttached"))
        self.assertTrue(graph["metadata"].get("chandasRecitationTimingAttached"))

        chandas_overlay = next(
            overlay
            for overlay in graph["overlays"]
            if overlay["overlayType"] == "chandas"
        )

        self.assertIn("metreCandidateCount", chandas_overlay["diagnostics"])
        self.assertIn("padaRhythmCandidateCount", chandas_overlay["diagnostics"])
        self.assertIn("caesuraCandidateCount", chandas_overlay["diagnostics"])
        self.assertIn("structuralGraphNodeCount", chandas_overlay["diagnostics"])
        self.assertIn("structuralGraphEdgeCount", chandas_overlay["diagnostics"])
        self.assertIn("recitationFlowCandidateCount", chandas_overlay["diagnostics"])
        self.assertIn("breathWindowCandidateCount", chandas_overlay["diagnostics"])
        self.assertIn("recitationTimingCandidateCount", chandas_overlay["diagnostics"])
        self.assertIn("padaTimingSummaryCount", chandas_overlay["diagnostics"])
        self.assertIn("timingMatraTotal", chandas_overlay["diagnostics"])

    def test_chandas_overlay_api_projection(self):
        from api.engines.vyakarana import (
            build_chandas_overlay_api_projection,
            build_prakriya_graph,
        )

        graph = build_prakriya_graph(
            [{"stage": "input", "input": "x", "output": "x", "rule": "identity"}],
            phonological_syllables=[{"text": "अ"}],
            padas=[],
        )

        projection = build_chandas_overlay_api_projection(graph)

        self.assertEqual(
            projection["schemaVersion"],
            "chandas-overlay-api-projection.v1",
        )
        self.assertEqual(projection["status"], "ready")
        self.assertEqual(projection["overlayType"], "chandas")

        self.assertTrue(projection["capabilities"]["metreRegistry"])
        self.assertTrue(projection["capabilities"]["rhythmLayer"])
        self.assertTrue(projection["capabilities"]["structuralGraph"])
        self.assertTrue(projection["capabilities"]["recitationFlow"])
        self.assertTrue(projection["capabilities"]["recitationTiming"])

        self.assertEqual(
            projection["overlay"]["overlayType"],
            "chandas",
        )

        self.assertIn("graphDiagnostics", projection)


if __name__ == "__main__":
    unittest.main()