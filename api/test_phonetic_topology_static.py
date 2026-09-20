from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PHONETICS = ROOT / "ui" / "tabs" / "sanskrit" / "phonetics"


class PhoneticTopologyStaticTests(unittest.TestCase):
    def test_phonetic_topology_files_exist(self):
        self.assertTrue((PHONETICS / "phonetic-topology-map.js").exists())
        self.assertTrue((PHONETICS / "phonetic-topology-engine.js").exists())

    def test_phonetic_topology_map_exports(self):
        content = (PHONETICS / "phonetic-topology-map.js").read_text(encoding="utf-8")
        self.assertIn("export const PHONETIC_TOPOLOGY_NODES", content)
        self.assertIn("export const PHONETIC_TOPOLOGY_EDGES", content)
        self.assertIn("export const PHONETIC_TOPOLOGY_SAFETY_NOTE", content)

    def test_phonetic_topology_engine_exports(self):
        content = (PHONETICS / "phonetic-topology-engine.js").read_text(encoding="utf-8")
        self.assertIn("export function buildPhoneticTopology", content)
        self.assertIn("export function inspectInputTopology", content)

    def test_controller_imports_phonetic_topology(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "controller.js").read_text(encoding="utf-8")
        self.assertIn(
            'import { inspectInputTopology } from "./phonetics/phonetic-topology-engine.js";',
            content,
        )

    def test_view_contains_phonetic_topology_panel(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "view.html").read_text(encoding="utf-8")
        self.assertIn("phonetic-topology-panel", content)

    def test_phonetic_topology_engine_contains_safety_phrase(self):
        content = (PHONETICS / "phonetic-topology-engine.js").read_text(encoding="utf-8")
        self.assertIn(
            "Phonetic topology map is deterministic structural visualization metadata only",
            content,
        )


if __name__ == "__main__":
    unittest.main()
