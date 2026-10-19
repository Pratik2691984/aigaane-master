from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PHONETICS = ROOT / "ui" / "tabs" / "sanskrit" / "phonetics"


class SymbolicCompressionStaticTests(unittest.TestCase):
    def test_symbolic_compression_files_exist(self):
        self.assertTrue((PHONETICS / "symbolic-compression-map.js").exists())
        self.assertTrue((PHONETICS / "symbolic-compression-engine.js").exists())

    def test_symbolic_compression_map_exports(self):
        content = (PHONETICS / "symbolic-compression-map.js").read_text(encoding="utf-8")
        self.assertIn("export const SYMBOLIC_COMPRESSION_RULES", content)
        self.assertIn("export const SYMBOLIC_COMPRESSION_SAFETY_NOTE", content)

    def test_symbolic_compression_engine_exports(self):
        content = (PHONETICS / "symbolic-compression-engine.js").read_text(encoding="utf-8")
        self.assertIn("export function expandSymbolicClass", content)
        self.assertIn("export function inspectSymbolicCompression", content)

    def test_controller_imports_symbolic_compression(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "controller.js").read_text(encoding="utf-8")
        self.assertIn(
            'import { inspectSymbolicCompression } from "./phonetics/symbolic-compression-engine.js";',
            content,
        )

    def test_view_contains_symbolic_compression_panel(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "view.html").read_text(encoding="utf-8")
        self.assertIn("symbolic-compression-panel", content)

    def test_symbolic_compression_engine_contains_safety_phrase(self):
        content = (PHONETICS / "symbolic-compression-engine.js").read_text(encoding="utf-8")
        self.assertIn("no authoritative Paninian derivation claim", content)


if __name__ == "__main__":
    unittest.main()
