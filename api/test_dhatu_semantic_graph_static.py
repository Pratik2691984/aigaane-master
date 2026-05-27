from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SEMANTIC = ROOT / "ui" / "tabs" / "sanskrit" / "semantic"


class DhatuSemanticGraphStaticTests(unittest.TestCase):
    def test_dhatu_semantic_files_exist(self):
        self.assertTrue((SEMANTIC / "dhatu-semantic-map.js").exists())
        self.assertTrue((SEMANTIC / "dhatu-semantic-engine.js").exists())
        self.assertTrue((SEMANTIC / "dhatu-semantic-renderer.js").exists())

    def test_dhatu_semantic_map_exports(self):
        content = (SEMANTIC / "dhatu-semantic-map.js").read_text(encoding="utf-8")
        self.assertIn("export const DHATU_SEMANTIC_NODES", content)
        self.assertIn("export const DHATU_SEMANTIC_EDGES", content)
        self.assertIn("export const DHATU_SEMANTIC_SAFETY_NOTE", content)

    def test_dhatu_semantic_engine_exports(self):
        content = (SEMANTIC / "dhatu-semantic-engine.js").read_text(encoding="utf-8")
        self.assertIn("export function buildDhatuSemanticGraph", content)
        self.assertIn("export function inspectDhatuSemanticGraph", content)

    def test_dhatu_semantic_renderer_exports(self):
        content = (SEMANTIC / "dhatu-semantic-renderer.js").read_text(encoding="utf-8")
        self.assertIn("export function renderDhatuSemanticList", content)

    def test_controller_imports_dhatu_semantic_graph(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "controller.js").read_text(encoding="utf-8")
        self.assertIn(
            'import { inspectDhatuSemanticGraph } from "./semantic/dhatu-semantic-engine.js";',
            content,
        )

    def test_view_contains_dhatu_semantic_panel(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "view.html").read_text(encoding="utf-8")
        self.assertIn("dhatu-semantic-panel", content)

    def test_dhatu_semantic_engine_contains_safety_phrase(self):
        content = (SEMANTIC / "dhatu-semantic-engine.js").read_text(encoding="utf-8")
        self.assertIn("no authoritative semantic or grammatical correctness claim", content)


if __name__ == "__main__":
    unittest.main()
