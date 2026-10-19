from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUTRA = ROOT / "ui" / "tabs" / "sanskrit" / "sutra"


class SutraReferenceStaticTests(unittest.TestCase):
    def test_sutra_reference_files_exist(self):
        self.assertTrue((SUTRA / "sutra-reference-map.js").exists())
        self.assertTrue((SUTRA / "sutra-reference-engine.js").exists())
        self.assertTrue((SUTRA / "sutra-reference-renderer.js").exists())

    def test_sutra_reference_map_exports(self):
        content = (SUTRA / "sutra-reference-map.js").read_text(encoding="utf-8")
        self.assertIn("export const SUTRA_REFERENCE_NODES", content)
        self.assertIn("export const SUTRA_REFERENCE_EDGES", content)
        self.assertIn("export const SUTRA_REFERENCE_SAFETY_NOTE", content)

    def test_sutra_reference_engine_exports(self):
        content = (SUTRA / "sutra-reference-engine.js").read_text(encoding="utf-8")
        self.assertIn("export function buildSutraReferenceOverlay", content)
        self.assertIn("export function inspectSutraReferenceOverlay", content)

    def test_sutra_reference_renderer_exports(self):
        content = (SUTRA / "sutra-reference-renderer.js").read_text(encoding="utf-8")
        self.assertIn("export function renderSutraReferenceList", content)

    def test_controller_imports_sutra_reference_overlay(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "controller.js").read_text(encoding="utf-8")
        self.assertIn(
            'import { inspectSutraReferenceOverlay } from "./sutra/sutra-reference-engine.js";',
            content,
        )

    def test_view_contains_sutra_reference_panel(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "view.html").read_text(encoding="utf-8")
        self.assertIn("sutra-reference-panel", content)

    def test_sutra_reference_engine_contains_safety_phrase(self):
        content = (SUTRA / "sutra-reference-engine.js").read_text(encoding="utf-8")
        self.assertIn(
            "no authoritative sūtra interpretation or grammatical correctness claim",
            content,
        )


if __name__ == "__main__":
    unittest.main()
