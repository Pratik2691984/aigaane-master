import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUARD_MAP = ROOT / "ui" / "tabs" / "sanskrit" / "execution-guard" / "execution-guard-map.js"
GUARD_ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "execution-guard" / "execution-guard-engine.js"


class TestExecutionGuardLayer(unittest.TestCase):
    def test_execution_guard_files_are_syntax_valid(self):
        for path in (GUARD_MAP, GUARD_ENGINE):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_execution_guard_export_is_runtime_safe_and_normalized(self):
        script = """
const guard = require("./ui/tabs/sanskrit/execution-guard/execution-guard-engine.js");
const result = guard.buildExecutionGuardExport();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-execution-guard.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contracts"]["deterministic"])
        self.assertTrue(payload["contracts"]["immutable"])
        self.assertTrue(payload["contracts"]["inspectionOnly"])
        self.assertTrue(payload["contracts"]["nonPerformative"])
        self.assertTrue(payload["contracts"]["runtimeIsolated"])
        self.assertTrue(payload["contracts"]["runtimeEnvironmentLinked"])
        self.assertTrue(payload["contracts"]["schedulerLinked"])
        self.assertTrue(payload["contracts"]["irLinked"])
        self.assertTrue(payload["contracts"]["queueLinked"])
        self.assertTrue(payload["contracts"]["traceLinked"])
        self.assertTrue(payload["contracts"]["checkpointLinked"])
        self.assertTrue(payload["contracts"]["replaySafe"])
        self.assertTrue(payload["contracts"]["staticPreviewCompatible"])
        self.assertEqual(payload["fieldCount"], 6)

        self.assertTrue(payload["diagnostics"]["normalized"])
        self.assertTrue(payload["diagnostics"]["deterministic"])
        self.assertTrue(payload["diagnostics"]["immutable"])
        self.assertTrue(payload["diagnostics"]["runtimeSafe"])
        self.assertTrue(payload["diagnostics"]["replaySafe"])
        self.assertTrue(payload["diagnostics"]["runtimeEnvironmentLinked"])
        self.assertTrue(payload["diagnostics"]["schedulerLinked"])
        self.assertTrue(payload["diagnostics"]["irLinked"])
        self.assertTrue(payload["diagnostics"]["queueLinked"])
        self.assertTrue(payload["diagnostics"]["traceLinked"])
        self.assertTrue(payload["diagnostics"]["checkpointLinked"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["guarded"])

        for field in payload["fields"]:
            self.assertIsInstance(field["id"], str)
            self.assertIsInstance(field["type"], str)
            self.assertIsInstance(field["summary"], str)
            self.assertIsInstance(field["required"], bool)
            self.assertIsInstance(field["diagnostics"], list)

    def test_create_execution_guard_snapshot_blocks_mutation_and_execution(self):
        script = """
const guard = require("./ui/tabs/sanskrit/execution-guard/execution-guard-engine.js");
const result = guard.createExecutionGuardSnapshot({
  mode: "GUARDED_RUNTIME",
  runtimeEnvironment: "runtime.snapshot.1",
  scheduler: "scheduler.snapshot.1",
  ir: "ir.snapshot.1",
  queue: "queue.snapshot.1",
  trace: "trace.snapshot.1",
  checkpoint: "checkpoint.snapshot.1"
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-execution-guard.v1")
        self.assertEqual(payload["kind"], "EXECUTION_GUARD_SNAPSHOT")
        self.assertEqual(payload["mode"], "GUARDED_RUNTIME")
        self.assertEqual(payload["references"]["runtimeEnvironment"], "runtime.snapshot.1")
        self.assertFalse(payload["permissions"]["executeTransformations"])
        self.assertFalse(payload["permissions"]["mutateSnapshots"])
        self.assertFalse(payload["permissions"]["produceSurfaceForms"])
        self.assertTrue(payload["permissions"]["authorizeRollback"])
        self.assertTrue(payload["permissions"]["inspectOnly"])
        self.assertTrue(payload["trace"]["replaySafe"])
        self.assertTrue(payload["trace"]["mutationFree"])
        self.assertTrue(payload["trace"]["runtimeIsolated"])
        self.assertTrue(payload["trace"]["guarded"])

    def test_execution_guard_diagnostics_contracts_are_satisfied(self):
        script = """
const guard = require("./ui/tabs/sanskrit/execution-guard/execution-guard-engine.js");
const result = guard.getExecutionGuardDiagnostics();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-execution-guard.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contractsSatisfied"])
        self.assertEqual(payload["fieldCount"], 6)


if __name__ == "__main__":
    unittest.main()