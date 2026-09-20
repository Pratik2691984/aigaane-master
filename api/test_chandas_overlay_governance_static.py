from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ChandasOverlayGovernanceStaticTests(unittest.TestCase):
    def test_governance_files_exist(self):
        expected = [
            "ui/tabs/sanskrit/chandas/chandas-overlay-governance-map.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-governance-engine.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-governance-renderer.js",
        ]

        for relative_path in expected:
            self.assertTrue((ROOT / relative_path).exists(), relative_path)

    def test_governance_contract_markers(self):
        files = {
            "map": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-governance-map.js",
            "engine": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-governance-engine.js",
            "renderer": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-governance-renderer.js",
            "controller": ROOT / "ui/tabs/sanskrit/controller.js",
            "style": ROOT / "ui/tabs/sanskrit/style.css",
        }

        contents = {name: path.read_text(encoding="utf-8") for name, path in files.items()}

        self.assertIn("chandas-overlay-governance.v1", contents["map"])
        self.assertIn("chandas-overlay-certification.v1", contents["map"])
        self.assertIn("immutableGovernanceSafe: true", contents["map"])
        self.assertIn("CHANDAS_OVERLAY_GOVERNANCE_POLICIES", contents["engine"])
        self.assertIn("governChandasOverlayCertification", contents["engine"])
        self.assertIn("isChandasOverlayGovernanceReady", contents["engine"])
        self.assertIn("renderChandasOverlayGovernance", contents["renderer"])
        self.assertIn("chandas-overlay-governance-host", contents["controller"])
        self.assertIn("chandas-overlay-governance-card", contents["style"])


if __name__ == "__main__":
    unittest.main()