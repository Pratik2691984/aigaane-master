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

    def test_chandas_overlay_query_projection(self):
        from api.engines.vyakarana import (
            build_chandas_overlay_api_projection,
            build_prakriya_graph,
            query_chandas_overlay_projection,
        )

        graph = build_prakriya_graph(
            [{"stage": "input", "input": "x", "output": "x", "rule": "identity"}],
            phonological_syllables=[{"text": "अ"}],
            padas=[],
        )

        projection = build_chandas_overlay_api_projection(graph)

        summary = query_chandas_overlay_projection(projection)

        self.assertEqual(
            summary["schemaVersion"],
            "chandas-overlay-query.v1",
        )
        self.assertEqual(summary["status"], "ready")
        self.assertEqual(summary["componentType"], "summary")
        self.assertIn("availableComponents", summary["result"])

        diagnostics = query_chandas_overlay_projection(
            projection,
            "diagnostics",
        )

        self.assertEqual(
            diagnostics["componentType"],
            "diagnostics",
        )
        self.assertIn(
            "metreCandidateCount",
            diagnostics["result"],
        )

        capabilities = query_chandas_overlay_projection(
            projection,
            "capabilities",
        )

        self.assertEqual(
            capabilities["componentType"],
            "capabilities",
        )
        self.assertTrue(capabilities["result"]["metreRegistry"])

    def test_chandas_overlay_navigation_projection(self):
        from api.engines.vyakarana import (
            build_chandas_overlay_api_projection,
            build_prakriya_graph,
            navigate_chandas_overlay_projection,
        )

        graph = build_prakriya_graph(
            [{"stage": "input", "input": "x", "output": "x", "rule": "identity"}],
            phonological_syllables=[{"text": "अ"}],
            padas=[],
        )

        projection = build_chandas_overlay_api_projection(graph)

        root = navigate_chandas_overlay_projection(projection)
        self.assertEqual(root["schemaVersion"], "chandas-overlay-navigation.v1")
        self.assertEqual(root["status"], "ready")
        self.assertEqual(root["path"], "root")
        self.assertIn("availablePaths", root["result"])

        diagnostics = navigate_chandas_overlay_projection(projection, "diagnostics")
        self.assertEqual(diagnostics["path"], "diagnostics")
        self.assertIn("metreCandidateCount", diagnostics["result"])

        capabilities = navigate_chandas_overlay_projection(projection, "capabilities")
        self.assertEqual(capabilities["path"], "capabilities")
        self.assertTrue(capabilities["result"]["metreRegistry"])

        unknown = navigate_chandas_overlay_projection(projection, "unknown")
        self.assertEqual(unknown["path"], "unknown")
        self.assertIn("Unknown chandas overlay navigation path.", unknown["warnings"])


if __name__ == "__main__":
    unittest.main()