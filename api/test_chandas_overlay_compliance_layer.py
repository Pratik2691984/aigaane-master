import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPLIANCE_MAP = ROOT / "ui" / "tabs" / "sanskrit" / "chandas" / "compliance" / "chandas-overlay-compliance-map.js"
COMPLIANCE_ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "chandas" / "compliance" / "chandas-overlay-compliance-engine.js"


class TestChandasOverlayComplianceLayer(unittest.TestCase):
    def test_compliance_files_are_syntax_valid(self):
        for path in (COMPLIANCE_MAP, COMPLIANCE_ENGINE):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_compliance_export_is_runtime_safe_and_normalized(self):
        script = """
const compliance = require("./ui/tabs/sanskrit/chandas/compliance/chandas-overlay-compliance-engine.js");
const result = compliance.buildChandasOverlayComplianceExport();
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

        self.assertEqual(payload["schemaVersion"], "chandas-overlay-compliance.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contracts"]["deterministic"])
        self.assertTrue(payload["contracts"]["inspectionOnly"])
        self.assertTrue(payload["contracts"]["nonAuthoritative"])
        self.assertTrue(payload["contracts"]["nonPerformative"])
        self.assertTrue(payload["contracts"]["runtimeIsolated"])
        self.assertTrue(payload["contracts"]["immutablePolicySafe"])
        self.assertTrue(payload["contracts"]["staticPreviewCompatible"])
        self.assertEqual(payload["complianceCount"], 4)

        self.assertTrue(payload["diagnostics"]["normalized"])
        self.assertTrue(payload["diagnostics"]["runtimeSafe"])
        self.assertTrue(payload["diagnostics"]["staticPreviewCompatible"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["policySafe"])

        for rule in payload["rules"]:
            self.assertIsInstance(rule["id"], str)
            self.assertIsInstance(rule["state"], str)
            self.assertIsInstance(rule["summary"], str)
            self.assertIsInstance(rule["diagnostics"], list)

    def test_compliance_diagnostics_contracts_are_satisfied(self):
        script = """
const compliance = require("./ui/tabs/sanskrit/chandas/compliance/chandas-overlay-compliance-engine.js");
const result = compliance.getChandasOverlayComplianceDiagnostics();
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

        self.assertEqual(payload["schemaVersion"], "chandas-overlay-compliance.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contractsSatisfied"])
        self.assertEqual(payload["complianceCount"], 4)


if __name__ == "__main__":
    unittest.main()