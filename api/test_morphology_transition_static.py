from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MORPHOLOGY = ROOT / "ui" / "tabs" / "sanskrit" / "morphology"


class MorphologyTransitionStaticTests(unittest.TestCase):
    def test_morphology_transition_files_exist(self):
        self.assertTrue((MORPHOLOGY / "morphology-transition-map.js").exists())
        self.assertTrue((MORPHOLOGY / "morphology-transition-engine.js").exists())
        self.assertTrue((MORPHOLOGY / "morphology-transition-renderer.js").exists())

    def test_morphology_transition_map_exports(self):
        content = (MORPHOLOGY / "morphology-transition-map.js").read_text(encoding="utf-8")
        self.assertIn("export const MORPHOLOGY_TRANSITION_NODES", content)
        self.assertIn("export const MORPHOLOGY_TRANSITION_EDGES", content)
        self.assertIn("export const MORPHOLOGY_TRANSITION_SAFETY_NOTE", content)

    def test_morphology_transition_engine_exports(self):
        content = (MORPHOLOGY / "morphology-transition-engine.js").read_text(encoding="utf-8")
        self.assertIn("export function buildMorphologyTransitionGraph", content)
        self.assertIn("export function inspectMorphologyTransitions", content)

    def test_morphology_transition_renderer_exports(self):
        content = (MORPHOLOGY / "morphology-transition-renderer.js").read_text(encoding="utf-8")
        self.assertIn("export function renderMorphologyTransitionList", content)

    def test_controller_imports_morphology_transitions(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "controller.js").read_text(encoding="utf-8")
        self.assertIn(
            'import { inspectMorphologyTransitions } from "./morphology/morphology-transition-engine.js";',
            content,
        )

    def test_view_contains_morphology_transition_panel(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "view.html").read_text(encoding="utf-8")
        self.assertIn("morphology-transition-panel", content)

    def test_morphology_transition_engine_contains_safety_phrase(self):
        content = (MORPHOLOGY / "morphology-transition-engine.js").read_text(encoding="utf-8")
        self.assertIn(
            "no authoritative morphology generation or grammatical correctness claim",
            content,
        )


if __name__ == "__main__":
    unittest.main()
