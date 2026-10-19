from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PHONETICS = ROOT / "ui" / "tabs" / "sanskrit" / "phonetics"


class TransliterationEngineStaticTests(unittest.TestCase):
    def test_transliteration_files_exist(self):
        self.assertTrue((PHONETICS / "transliteration-map.js").exists())
        self.assertTrue((PHONETICS / "ipa-map.js").exists())
        self.assertTrue((PHONETICS / "transliteration-engine.js").exists())

    def test_transliteration_map_exports(self):
        content = (PHONETICS / "transliteration-map.js").read_text(encoding="utf-8")
        self.assertIn("export const DEVANAGARI_IAST_MAP", content)
        self.assertIn("export const TRANSLITERATION_SAFETY_NOTE", content)

    def test_ipa_map_exports(self):
        content = (PHONETICS / "ipa-map.js").read_text(encoding="utf-8")
        self.assertIn("export const DEVANAGARI_IPA_MAP", content)
        self.assertIn("export const IPA_SAFETY_NOTE", content)

    def test_transliteration_engine_exports(self):
        content = (PHONETICS / "transliteration-engine.js").read_text(encoding="utf-8")
        self.assertIn("export function transliterateDevanagariToIast", content)
        self.assertIn("export function transliterateDevanagariToIpa", content)
        self.assertIn("export function inspectTransliteration", content)

    def test_controller_imports_transliteration_inspector(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "controller.js").read_text(encoding="utf-8")
        self.assertIn('import { inspectTransliteration } from "./phonetics/transliteration-engine.js";', content)

    def test_view_contains_transliteration_panel(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "view.html").read_text(encoding="utf-8")
        self.assertIn("transliteration-analysis-panel", content)

    def test_transliteration_engine_contains_safety_note(self):
        content = (PHONETICS / "transliteration-engine.js").read_text(encoding="utf-8")
        self.assertIn("Deterministic transliteration inspection only", content)


if __name__ == "__main__":
    unittest.main()
