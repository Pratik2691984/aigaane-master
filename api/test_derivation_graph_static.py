from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DERIVATION = ROOT / "ui" / "tabs" / "sanskrit" / "derivation"


class DerivationGraphStaticTests(unittest.TestCase):
    def test_derivation_graph_files_exist(self):
        self.assertTrue((DERIVATION / "derivation-graph-map.js").exists())
        self.assertTrue((DERIVATION / "derivation-graph-engine.js").exists())
        self.assertTrue((DERIVATION / "derivation-overlay-renderer.js").exists())

    def test_derivation_graph_map_exports(self):
        content = (DERIVATION / "derivation-graph-map.js").read_text(encoding="utf-8")
        self.assertIn("export const DERIVATION_GRAPH_NODES", content)
        self.assertIn("export const DERIVATION_GRAPH_EDGES", content)
        self.assertIn("export const DERIVATION_GRAPH_SAFETY_NOTE", content)

    def test_derivation_graph_engine_exports(self):
        content = (DERIVATION / "derivation-graph-engine.js").read_text(encoding="utf-8")
        self.assertIn("export function buildDerivationGraph", content)
        self.assertIn("export function inspectDerivationGraph", content)

    def test_derivation_overlay_renderer_exports(self):
        content = (DERIVATION / "derivation-overlay-renderer.js").read_text(encoding="utf-8")
        self.assertIn("export function renderDerivationOverlayList", content)

    def test_controller_imports_derivation_graph(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "controller.js").read_text(encoding="utf-8")
        self.assertIn(
            'import { inspectDerivationGraph } from "./derivation/derivation-graph-engine.js";',
            content,
        )

    def test_view_contains_derivation_graph_panel(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "view.html").read_text(encoding="utf-8")
        self.assertIn("derivation-graph-panel", content)

    def test_derivation_graph_engine_contains_safety_phrase(self):
        content = (DERIVATION / "derivation-graph-engine.js").read_text(encoding="utf-8")
        self.assertIn("no authoritative grammatical derivation claim", content)


if __name__ == "__main__":
    unittest.main()
