from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PHONETICS = ROOT / "ui" / "tabs" / "sanskrit" / "phonetics"


class SandhiEngineStaticTests(unittest.TestCase):
    def test_sandhi_files_exist(self):
        self.assertTrue((PHONETICS / "sandhi-rules.js").exists())
        self.assertTrue((PHONETICS / "sandhi-transition-map.js").exists())
        self.assertTrue((PHONETICS / "sandhi-engine.js").exists())

    def test_sandhi_rules_exports(self):
        content = (PHONETICS / "sandhi-rules.js").read_text(encoding="utf-8")
        self.assertIn("export const SANDHI_TRANSITION_RULES", content)
        self.assertIn("export const SANDHI_RULE_SAFETY_NOTE", content)

    def test_sandhi_transition_map_exports(self):
        content = (PHONETICS / "sandhi-transition-map.js").read_text(encoding="utf-8")
        self.assertIn("export function buildSandhiTransitionMap", content)
        self.assertIn("export function lookupSandhiTransition", content)

    def test_sandhi_engine_exports(self):
        content = (PHONETICS / "sandhi-engine.js").read_text(encoding="utf-8")
        self.assertIn("export function inspectSandhiPair", content)
        self.assertIn("export function inspectSandhiText", content)

    def test_controller_imports_sandhi_inspector(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "controller.js").read_text(encoding="utf-8")
        self.assertIn('import { inspectSandhiText } from "./phonetics/sandhi-engine.js";', content)

    def test_view_contains_sandhi_transition_panel(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "view.html").read_text(encoding="utf-8")
        self.assertIn("sandhi-transition-panel", content)

    def test_sandhi_engine_contains_safety_note(self):
        content = (PHONETICS / "sandhi-engine.js").read_text(encoding="utf-8")
        self.assertIn("Deterministic sandhi boundary inspection only", content)


if __name__ == "__main__":
    unittest.main()
