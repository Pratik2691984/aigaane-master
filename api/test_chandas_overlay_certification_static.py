from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ChandasOverlayCertificationStaticTests(unittest.TestCase):
    def test_certification_files_exist(self):
        expected = [
            "ui/tabs/sanskrit/chandas/chandas-overlay-certification-map.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-certification-engine.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-certification-renderer.js",
        ]

        for relative_path in expected:
            self.assertTrue((ROOT / relative_path).exists(), relative_path)

    def test_certification_contract_markers(self):
        files = {
            "map": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-certification-map.js",
            "engine": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-certification-engine.js",
            "renderer": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-certification-renderer.js",
            "controller": ROOT / "ui/tabs/sanskrit/controller.js",
            "style": ROOT / "ui/tabs/sanskrit/style.css",
        }

        contents = {name: path.read_text(encoding="utf-8") for name, path in files.items()}

        self.assertIn("chandas-overlay-certification.v1", contents["map"])
        self.assertIn("chandas-overlay-verification.v1", contents["map"])
        self.assertIn("immutableCertificationSafe: true", contents["map"])
        self.assertIn("CHANDAS_OVERLAY_CERTIFICATION_LEVELS", contents["engine"])
        self.assertIn("certifyChandasOverlayVerification", contents["engine"])
        self.assertIn("isChandasOverlayCertificationReady", contents["engine"])
        self.assertIn("renderChandasOverlayCertification", contents["renderer"])
        self.assertIn("chandas-overlay-certification-host", contents["controller"])
        self.assertIn("chandas-overlay-certification-card", contents["style"])


if __name__ == "__main__":
    unittest.main()