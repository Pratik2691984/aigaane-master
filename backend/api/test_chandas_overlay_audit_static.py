from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ChandasOverlayAuditStaticTests(unittest.TestCase):
    def test_audit_files_exist(self):
        expected = [
            "ui/tabs/sanskrit/chandas/chandas-overlay-audit-map.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-audit-engine.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-audit-renderer.js",
        ]

        for relative_path in expected:
            self.assertTrue((ROOT / relative_path).exists(), relative_path)

    def test_audit_contract_markers(self):
        files = {
            "map": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-audit-map.js",
            "engine": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-audit-engine.js",
            "renderer": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-audit-renderer.js",
            "controller": ROOT / "ui/tabs/sanskrit/controller.js",
            "style": ROOT / "ui/tabs/sanskrit/style.css",
        }

        contents = {name: path.read_text(encoding="utf-8") for name, path in files.items()}

        self.assertIn("chandas-overlay-audit.v1", contents["map"])
        self.assertIn("chandas-overlay-replay.v1", contents["map"])
        self.assertIn("immutableAuditSafe: true", contents["map"])
        self.assertIn("auditChandasOverlayReplay", contents["engine"])
        self.assertIn("isChandasOverlayAuditReady", contents["engine"])
        self.assertIn("buildCheckpoint", contents["engine"])
        self.assertIn("renderChandasOverlayAudit", contents["renderer"])
        self.assertIn("chandas-overlay-audit-host", contents["controller"])
        self.assertIn("chandas-overlay-audit-card", contents["style"])


if __name__ == "__main__":
    unittest.main()