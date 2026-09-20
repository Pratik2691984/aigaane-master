from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ChandasOverlayVerificationStaticTests(unittest.TestCase):
    def test_verification_files_exist(self):
        expected = [
            "ui/tabs/sanskrit/chandas/chandas-overlay-verification-map.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-verification-engine.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-verification-renderer.js",
        ]

        for relative_path in expected:
            self.assertTrue((ROOT / relative_path).exists(), relative_path)

    def test_verification_contract_markers(self):
        files = {
            "map": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-verification-map.js",
            "engine": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-verification-engine.js",
            "renderer": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-verification-renderer.js",
            "controller": ROOT / "ui/tabs/sanskrit/controller.js",
            "style": ROOT / "ui/tabs/sanskrit/style.css",
        }

        contents = {name: path.read_text(encoding="utf-8") for name, path in files.items()}

        self.assertIn("chandas-overlay-verification.v1", contents["map"])
        self.assertIn("chandas-overlay-audit.v1", contents["map"])
        self.assertIn("immutableVerificationSafe: true", contents["map"])
        self.assertIn("CHANDAS_OVERLAY_VERIFICATION_INVARIANTS", contents["engine"])
        self.assertIn("verifyChandasOverlayAudit", contents["engine"])
        self.assertIn("isChandasOverlayVerificationReady", contents["engine"])
        self.assertIn("renderChandasOverlayVerification", contents["renderer"])
        self.assertIn("chandas-overlay-verification-host", contents["controller"])
        self.assertIn("chandas-overlay-verification-card", contents["style"])


if __name__ == "__main__":
    unittest.main()