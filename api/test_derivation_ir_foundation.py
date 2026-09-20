import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IR_MAP = ROOT / "ui" / "tabs" / "sanskrit" / "derivation-ir" / "derivation-ir-map.js"
IR_ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "derivation-ir" / "derivation-ir-engine.js"


class TestDerivationIrFoundation(unittest.TestCase):
    def test_derivation_ir_files_are_syntax_valid(self):
        for path in (IR_MAP, IR_ENGINE):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_derivation_ir_export_is_runtime_safe_and_normalized(self):
        script = """
const ir = require("./ui/tabs/sanskrit/derivation-ir/derivation-ir-engine.js");
const result = ir.buildDerivationIrExport();
console.log(JSON.stringify(result));
"""
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["schemaVersion"], "sanskrit-derivation-ir.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contracts"]["deterministic"])
        self.assertTrue(payload["contracts"]["immutable"])
        self.assertTrue(payload["contracts"]["inspectionOnly"])
        self.assertTrue(payload["contracts"]["nonPerformative"])
        self.assertTrue(payload["contracts"]["runtimeIsolated"])
        self.assertTrue(payload["contracts"]["schedulerCompatible"])
        self.assertTrue(payload["contracts"]["replaySafe"])
        self.assertTrue(payload["contracts"]["staticPreviewCompatible"])
        self.assertEqual(payload["fieldCount"], 7)

        self.assertTrue(payload["diagnostics"]["normalized"])
        self.assertTrue(payload["diagnostics"]["deterministic"])
        self.assertTrue(payload["diagnostics"]["immutable"])
        self.assertTrue(payload["diagnostics"]["runtimeSafe"])
        self.assertTrue(payload["diagnostics"]["replaySafe"])
        self.assertTrue(payload["diagnostics"]["schedulerCompatible"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])

        for field in payload["fields"]:
            self.assertIsInstance(field["id"], str)
            self.assertIsInstance(field["type"], str)
            self.assertIsInstance(field["summary"], str)
            self.assertIsInstance(field["required"], bool)
            self.assertIsInstance(field["diagnostics"], list)

    def test_create_derivation_ir_snapshot_is_replay_safe(self):
        script = """
const ir = require("./ui/tabs/sanskrit/derivation-ir/derivation-ir-engine.js");
const result = ir.createDerivationIrSnapshot({
  environment: { mode: "inspection", schedulerVersion: "sanskrit-rule-precedence.v1" },
  intent: { root: "gam", lakara: "lat" },
  plannedSteps: [
    { id: "step-1", ruleId: "sutra.1.4.2", description: "precedence arbitration" },
    { id: "step-2", ruleId: "sutra.8.2.1", description: "asiddhatva placeholder" }
  ]
});
console.log(JSON.stringify(result));
"""
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["schemaVersion"], "sanskrit-derivation-ir.v1")
        self.assertEqual(payload["kind"], "DERIVATION_IR_SNAPSHOT")
        self.assertEqual(payload["environment"]["mode"], "inspection")
        self.assertEqual(payload["intent"]["root"], "gam")
        self.assertEqual(len(payload["plannedSteps"]), 2)
        self.assertTrue(payload["trace"]["replaySafe"])
        self.assertTrue(payload["trace"]["mutationFree"])
        self.assertEqual(payload["trace"]["stepCount"], 2)

    def test_derivation_ir_diagnostics_contracts_are_satisfied(self):
        script = """
const ir = require("./ui/tabs/sanskrit/derivation-ir/derivation-ir-engine.js");
const result = ir.getDerivationIrDiagnostics();
console.log(JSON.stringify(result));
"""
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["schemaVersion"], "sanskrit-derivation-ir.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contractsSatisfied"])
        self.assertEqual(payload["fieldCount"], 7)


if __name__ == "__main__":
    unittest.main()