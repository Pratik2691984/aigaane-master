import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTEGRITY_MAP = ROOT / "ui" / "tabs" / "sanskrit" / "chandas" / "integrity" / "chandas-overlay-integrity-map.js"
INTEGRITY_ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "chandas" / "integrity" / "chandas-overlay-integrity-engine.js"


class TestChandasOverlayIntegrityLayer(unittest.TestCase):
    def test_integrity_files_are_syntax_valid(self):
        for path in (INTEGRITY_MAP, INTEGRITY_ENGINE):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_integrity_export_is_runtime_safe_and_normalized(self):
        script = """
const integrity = require("./ui/tabs/sanskrit/chandas/integrity/chandas-overlay-integrity-engine.js");
const result = integrity.buildChandasOverlayIntegrityExport();
console.log(JSON.stringify(result));
"""
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["schemaVersion"], "chandas-overlay-integrity.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contracts"]["deterministic"])
        self.assertTrue(payload["contracts"]["inspectionOnly"])
        self.assertTrue(payload["contracts"]["nonAuthoritative"])
        self.assertTrue(payload["contracts"]["nonPerformative"])
        self.assertTrue(payload["contracts"]["runtimeIsolated"])
        self.assertTrue(payload["contracts"]["immutableAssuranceSafe"])
        self.assertTrue(payload["contracts"]["staticPreviewCompatible"])
        self.assertEqual(payload["integrityCount"], 4)

        self.assertTrue(payload["diagnostics"]["normalized"])
        self.assertTrue(payload["diagnostics"]["runtimeSafe"])
        self.assertTrue(payload["diagnostics"]["staticPreviewCompatible"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["assuranceSafe"])
        self.assertTrue(payload["diagnostics"]["replaySafe"])

        for rule in payload["rules"]:
            self.assertIsInstance(rule["id"], str)
            self.assertIsInstance(rule["state"], str)
            self.assertIsInstance(rule["summary"], str)
            self.assertIsInstance(rule["diagnostics"], list)

    def test_integrity_diagnostics_contracts_are_satisfied(self):
        script = """
const integrity = require("./ui/tabs/sanskrit/chandas/integrity/chandas-overlay-integrity-engine.js");
const result = integrity.getChandasOverlayIntegrityDiagnostics();
console.log(JSON.stringify(result));
"""
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["schemaVersion"], "chandas-overlay-integrity.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contractsSatisfied"])
        self.assertEqual(payload["integrityCount"], 4)


if __name__ == "__main__":
    unittest.main()