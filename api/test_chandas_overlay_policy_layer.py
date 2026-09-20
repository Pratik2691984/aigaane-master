import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_MAP = ROOT / "ui" / "tabs" / "sanskrit" / "chandas" / "policy" / "chandas-overlay-policy-map.js"
POLICY_ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "chandas" / "policy" / "chandas-overlay-policy-engine.js"


class TestChandasOverlayPolicyLayer(unittest.TestCase):
    def test_policy_files_are_syntax_valid(self):
        for path in (POLICY_MAP, POLICY_ENGINE):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_policy_export_is_runtime_safe_and_normalized(self):
        script = """
const policy = require("./ui/tabs/sanskrit/chandas/policy/chandas-overlay-policy-engine.js");
const result = policy.buildChandasOverlayPolicyExport();
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

        self.assertEqual(payload["schemaVersion"], "chandas-overlay-policy.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contracts"]["deterministic"])
        self.assertTrue(payload["contracts"]["inspectionOnly"])
        self.assertTrue(payload["contracts"]["nonAuthoritative"])
        self.assertTrue(payload["contracts"]["nonPerformative"])
        self.assertTrue(payload["contracts"]["runtimeIsolated"])
        self.assertTrue(payload["contracts"]["immutableGovernanceSafe"])
        self.assertTrue(payload["contracts"]["staticPreviewCompatible"])
        self.assertEqual(payload["policyCount"], 4)

        self.assertTrue(payload["diagnostics"]["normalized"])
        self.assertTrue(payload["diagnostics"]["runtimeSafe"])
        self.assertTrue(payload["diagnostics"]["staticPreviewCompatible"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])

        for rule in payload["rules"]:
            self.assertIsInstance(rule["id"], str)
            self.assertIsInstance(rule["level"], str)
            self.assertIsInstance(rule["summary"], str)
            self.assertIsInstance(rule["diagnostics"], list)

    def test_policy_diagnostics_contracts_are_satisfied(self):
        script = """
const policy = require("./ui/tabs/sanskrit/chandas/policy/chandas-overlay-policy-engine.js");
const result = policy.getChandasOverlayPolicyDiagnostics();
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

        self.assertEqual(payload["schemaVersion"], "chandas-overlay-policy.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contractsSatisfied"])
        self.assertEqual(payload["policyCount"], 4)


if __name__ == "__main__":
    unittest.main()