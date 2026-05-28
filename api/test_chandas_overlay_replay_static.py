from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ChandasOverlayReplayStaticTests(unittest.TestCase):
    def test_replay_files_exist(self):
        expected = [
            "ui/tabs/sanskrit/chandas/chandas-overlay-replay-map.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-replay-engine.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-replay-renderer.js",
        ]

        for relative_path in expected:
            self.assertTrue((ROOT / relative_path).exists(), relative_path)

    def test_replay_contract_markers(self):
        files = {
            "map": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-replay-map.js",
            "engine": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-replay-engine.js",
            "renderer": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-replay-renderer.js",
            "controller": ROOT / "ui/tabs/sanskrit/controller.js",
            "style": ROOT / "ui/tabs/sanskrit/style.css",
        }

        contents = {name: path.read_text(encoding="utf-8") for name, path in files.items()}

        self.assertIn("chandas-overlay-replay.v1", contents["map"])
        self.assertIn("chandas-overlay-history.v1", contents["map"])
        self.assertIn("immutableReplaySafe: true", contents["map"])
        self.assertIn("buildChandasOverlayReplay", contents["engine"])
        self.assertIn("isChandasOverlayReplayReady", contents["engine"])
        self.assertIn("normalizeIndex", contents["engine"])
        self.assertIn("renderChandasOverlayReplay", contents["renderer"])
        self.assertIn("chandas-overlay-replay-host", contents["controller"])
        self.assertIn("chandas-overlay-replay-card", contents["style"])


if __name__ == "__main__":
    unittest.main()