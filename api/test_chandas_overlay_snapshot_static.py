from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ChandasOverlaySnapshotStaticTests(unittest.TestCase):
    def test_snapshot_files_exist(self):
        expected = [
            "ui/tabs/sanskrit/chandas/chandas-overlay-snapshot-map.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-snapshot-engine.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-snapshot-renderer.js",
        ]

        for relative_path in expected:
            self.assertTrue((ROOT / relative_path).exists(), relative_path)

    def test_snapshot_contract_markers(self):
        files = {
            "map": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-snapshot-map.js",
            "engine": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-snapshot-engine.js",
            "renderer": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-snapshot-renderer.js",
            "controller": ROOT / "ui/tabs/sanskrit/controller.js",
            "style": ROOT / "ui/tabs/sanskrit/style.css",
        }

        contents = {name: path.read_text(encoding="utf-8") for name, path in files.items()}

        self.assertIn("chandas-overlay-snapshot.v1", contents["map"])
        self.assertIn("chandas-overlay-inspection.v1", contents["map"])
        self.assertIn("immutable: true", contents["map"])
        self.assertIn("createChandasOverlaySnapshot", contents["engine"])
        self.assertIn("isChandasOverlaySnapshotReady", contents["engine"])
        self.assertIn("createDeterministicDigest", contents["engine"])
        self.assertIn("renderChandasOverlaySnapshot", contents["renderer"])
        self.assertIn("chandas-overlay-snapshot-host", contents["controller"])
        self.assertIn("chandas-overlay-snapshot-card", contents["style"])


if __name__ == "__main__":
    unittest.main()