import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KERNEL_MAP = ROOT / "ui" / "tabs" / "sanskrit" / "execution-kernel" / "execution-kernel-map.js"
KERNEL_ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "execution-kernel" / "execution-kernel-engine.js"


class TestExecutionKernelLayer(unittest.TestCase):
    def test_execution_kernel_files_are_syntax_valid(self):
        for path in (KERNEL_MAP, KERNEL_ENGINE):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_execution_kernel_export_is_runtime_safe_and_normalized(self):
        script = """
const kernel = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js");
const result = kernel.buildExecutionKernelExport();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-execution-kernel.v1")
        self.assertTrue(payload["ready"])
        self.assertEqual(payload["fieldCount"], 6)
        self.assertTrue(payload["contracts"]["deterministic"])
        self.assertTrue(payload["contracts"]["immutable"])
        self.assertTrue(payload["contracts"]["inspectionOnly"])
        self.assertTrue(payload["contracts"]["nonPerformative"])
        self.assertTrue(payload["contracts"]["nonMutating"])
        self.assertTrue(payload["contracts"]["runtimeIsolated"])
        self.assertTrue(payload["contracts"]["executionGuardLinked"])
        self.assertTrue(payload["contracts"]["runtimeEnvironmentLinked"])
        self.assertTrue(payload["contracts"]["prakriyaPlanningLinked"])
        self.assertTrue(payload["contracts"]["derivationGraphLinked"])
        self.assertTrue(payload["contracts"]["schedulerLinked"])
        self.assertTrue(payload["contracts"]["queueLinked"])
        self.assertTrue(payload["contracts"]["traceLinked"])
        self.assertTrue(payload["contracts"]["checkpointLinked"])
        self.assertTrue(payload["contracts"]["replaySafe"])
        self.assertTrue(payload["contracts"]["staticPreviewCompatible"])
        self.assertTrue(payload["diagnostics"]["normalized"])
        self.assertTrue(payload["diagnostics"]["deterministic"])
        self.assertTrue(payload["diagnostics"]["immutable"])
        self.assertTrue(payload["diagnostics"]["runtimeSafe"])
        self.assertTrue(payload["diagnostics"]["replaySafe"])
        self.assertTrue(payload["diagnostics"]["executionGuardLinked"])
        self.assertTrue(payload["diagnostics"]["runtimeEnvironmentLinked"])
        self.assertTrue(payload["diagnostics"]["prakriyaPlanningLinked"])
        self.assertTrue(payload["diagnostics"]["derivationGraphLinked"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["executionBlocked"])
        self.assertTrue(payload["diagnostics"]["kernelOnly"])

        orders = [field["order"] for field in payload["fields"]]
        self.assertEqual(orders, sorted(orders))

    def test_create_execution_kernel_snapshot_blocks_execution(self):
        script = """
const kernel = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js");
const result = kernel.createExecutionKernelSnapshot({
  mode: "GUARDED_RUNTIME",
  guard: "guard.snapshot.1",
  runtimeEnvironment: "runtime.snapshot.1",
  prakriyaPlan: "prakriya.snapshot.1",
  derivationGraph: "graph.snapshot.1",
  stages: [
    { id: "stage-sandhi", type: "EXECUTION_ENVELOPE", order: 40, referenceId: "sandhi.plan.1" },
    { id: "stage-init", type: "KERNEL_INITIALIZATION", order: 10, referenceId: "kernel.init.1" },
    { id: "stage-guard", type: "GUARD_VERIFICATION", order: 20, referenceId: "guard.snapshot.1" }
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-execution-kernel.v1")
        self.assertEqual(payload["kind"], "EXECUTION_KERNEL_SNAPSHOT")
        self.assertEqual(payload["mode"], "GUARDED_RUNTIME")
        self.assertEqual(payload["references"]["guard"], "guard.snapshot.1")
        self.assertEqual(
            [stage["id"] for stage in payload["stages"]],
            ["stage-init", "stage-guard", "stage-sandhi"],
        )
        self.assertTrue(all(stage["planned"] for stage in payload["stages"]))
        self.assertTrue(all(not stage["authorized"] for stage in payload["stages"]))
        self.assertTrue(all(not stage["executed"] for stage in payload["stages"]))
        self.assertFalse(payload["capabilities"]["executeTransformations"])
        self.assertFalse(payload["capabilities"]["mutateSnapshots"])
        self.assertFalse(payload["capabilities"]["produceSurfaceForms"])
        self.assertTrue(payload["capabilities"]["authorizeRollback"])
        self.assertTrue(payload["capabilities"]["inspectOnly"])
        self.assertTrue(payload["trace"]["replaySafe"])
        self.assertTrue(payload["trace"]["mutationFree"])
        self.assertTrue(payload["trace"]["executionBlocked"])
        self.assertEqual(payload["trace"]["stageCount"], 3)

    def test_execution_kernel_diagnostics_contracts_are_satisfied(self):
        script = """
const kernel = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js");
const result = kernel.getExecutionKernelDiagnostics();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-execution-kernel.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contractsSatisfied"])
        self.assertEqual(payload["fieldCount"], 6)


if __name__ == "__main__":
    unittest.main()
