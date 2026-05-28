from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ChandasOverlayDiffStaticTests(unittest.TestCase):
    def test_diff_files_exist(self):
        expected = [
            "ui/tabs/sanskrit/chandas/chandas-overlay-diff-map.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-diff-engine.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-diff-renderer.js",
        ]

        for relative_path in expected:
            self.assertTrue((ROOT / relative_path).exists(), relative_path)

    def test_diff_contract_markers(self):
        files = {
            "map": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-diff-map.js",
            "engine": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-diff-engine.js",
            "renderer": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-diff-renderer.js",
            "controller": ROOT / "ui/tabs/sanskrit/controller.js",
            "style": ROOT / "ui/tabs/sanskrit/style.css",
        }

        contents = {name: path.read_text(encoding="utf-8") for name, path in files.items()}

        self.assertIn("chandas-overlay-diff.v1", contents["map"])
        self.assertIn("chandas-overlay-snapshot.v1", contents["map"])
        self.assertIn("immutableComparisonSafe: true", contents["map"])
        self.assertIn("diffChandasOverlaySnapshots", contents["engine"])
        self.assertIn("isChandasOverlayDiffReady", contents["engine"])
        self.assertIn("CHANDAS_OVERLAY_DIFF_FIELDS", contents["engine"])
        self.assertIn("renderChandasOverlayDiff", contents["renderer"])
        self.assertIn("chandas-overlay-diff-host", contents["controller"])
        self.assertIn("chandas-overlay-diff-card", contents["style"])


if __name__ == "__main__":
    unittest.main()