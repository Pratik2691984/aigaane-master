from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ChandasOverlayHistoryStaticTests(unittest.TestCase):
    def test_history_files_exist(self):
        expected = [
            "ui/tabs/sanskrit/chandas/chandas-overlay-history-map.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-history-engine.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-history-renderer.js",
        ]

        for relative_path in expected:
            self.assertTrue((ROOT / relative_path).exists(), relative_path)

    def test_history_contract_markers(self):
        files = {
            "map": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-history-map.js",
            "engine": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-history-engine.js",
            "renderer": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-history-renderer.js",
            "controller": ROOT / "ui/tabs/sanskrit/controller.js",
            "style": ROOT / "ui/tabs/sanskrit/style.css",
        }

        contents = {name: path.read_text(encoding="utf-8") for name, path in files.items()}

        self.assertIn("chandas-overlay-history.v1", contents["map"])
        self.assertIn("chandas-overlay-snapshot.v1", contents["map"])
        self.assertIn("chandas-overlay-diff.v1", contents["map"])
        self.assertIn("immutableTimelineSafe: true", contents["map"])
        self.assertIn("buildChandasOverlayHistory", contents["engine"])
        self.assertIn("isChandasOverlayHistoryReady", contents["engine"])
        self.assertIn("renderChandasOverlayHistory", contents["renderer"])
        self.assertIn("chandas-overlay-history-host", contents["controller"])
        self.assertIn("chandas-overlay-history-card", contents["style"])


if __name__ == "__main__":
    unittest.main()