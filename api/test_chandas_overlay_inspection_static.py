from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ChandasOverlayInspectionStaticTests(unittest.TestCase):
    def test_inspection_files_exist(self):
        expected = [
            "ui/tabs/sanskrit/chandas/chandas-overlay-inspection-map.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-inspection-engine.js",
            "ui/tabs/sanskrit/chandas/chandas-overlay-inspection-renderer.js",
        ]

        for relative_path in expected:
            self.assertTrue((ROOT / relative_path).exists(), relative_path)

    def test_inspection_contract_markers(self):
        files = {
            "map": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-inspection-map.js",
            "engine": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-inspection-engine.js",
            "renderer": ROOT / "ui/tabs/sanskrit/chandas/chandas-overlay-inspection-renderer.js",
            "controller": ROOT / "ui/tabs/sanskrit/controller.js",
        }

        contents = {name: path.read_text(encoding="utf-8") for name, path in files.items()}

        self.assertIn("chandas-overlay-inspection.v1", contents["map"])
        self.assertIn("runtimeIsolated: true", contents["map"])
        self.assertIn("staticPreviewCompatible: true", contents["map"])
        self.assertIn("inspectChandasOverlayRegistry", contents["engine"])
        self.assertIn("isChandasOverlayInspectionReady", contents["engine"])
        self.assertIn("renderChandasOverlayInspection", contents["renderer"])
        self.assertIn("inspectChandasOverlayRegistry", contents["controller"])
        self.assertIn("renderChandasOverlayInspection", contents["controller"])
        self.assertIn("chandas-overlay-inspection-host", contents["controller"])


if __name__ == "__main__":
    unittest.main()