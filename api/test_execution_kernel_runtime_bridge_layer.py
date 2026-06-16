import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KERNEL_RUNTIME_BRIDGE = ROOT / "ui" / "tabs" / "sanskrit" / "execution-kernel" / "execution-kernel-runtime-bridge.js"


class TestExecutionKernelRuntimeBridgeLayer(unittest.TestCase):
    def test_runtime_bridge_file_is_syntax_valid(self):
        result = subprocess.run(
            ["node", "--check", str(KERNEL_RUNTIME_BRIDGE)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_runtime_environment_normalization_preserves_observation_only(self):
        script = """
const bridge = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-bridge.js");
const result = bridge.normalizeRuntimeEnvironment({
  id: "runtime.snapshot.1",
  kind: "RUNTIME_ENVIRONMENT_SNAPSHOT",
  schemaVersion: "sanskrit-runtime.v1",
  status: "READY",
  ready: true,
  executionAllowed: true,
  mutationAllowed: true,
  rollbackAllowed: true
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

        self.assertEqual(payload["id"], "runtime.snapshot.1")
        self.assertEqual(payload["kind"], "RUNTIME_ENVIRONMENT_SNAPSHOT")
        self.assertEqual(payload["schemaVersion"], "sanskrit-runtime.v1")
        self.assertEqual(payload["status"], "READY")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["executionAllowed"])
        self.assertTrue(payload["mutationAllowed"])
        self.assertTrue(payload["rollbackAllowed"])
        self.assertFalse(payload["diagnostics"]["bridgeExecutionGranted"])
        self.assertFalse(payload["diagnostics"]["bridgeMutationGranted"])
        self.assertFalse(payload["diagnostics"]["bridgeRollbackGranted"])

    def test_runtime_bridge_blocks_runtime_forwarding(self):
        script = """
const engine = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js");
const bridge = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-bridge.js");
const kernelSnapshot = engine.createExecutionKernelSnapshot({
  mode: "GUARDED_RUNTIME",
  guard: "guard.snapshot.1",
  runtimeEnvironment: "runtime.snapshot.1",
  prakriyaPlan: "prakriya.snapshot.1",
  derivationGraph: "graph.snapshot.1",
  stages: [
    { id: "stage-init", type: "KERNEL_INITIALIZATION", order: 10, referenceId: "kernel.init.1" },
    { id: "stage-envelope", type: "EXECUTION_ENVELOPE", order: 40, referenceId: "execution.plan.1" }
  ]
});
const result = bridge.createExecutionKernelRuntimeBridge({
  kernelSnapshot,
  runtimeEnvironment: {
    id: "runtime.snapshot.1",
    kind: "RUNTIME_ENVIRONMENT_SNAPSHOT",
    schemaVersion: "sanskrit-runtime.v1",
    status: "READY",
    ready: true,
    executionAllowed: true,
    mutationAllowed: true,
    rollbackAllowed: true
  },
  guardReference: "guard.snapshot.1"
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-execution-kernel-runtime-bridge.v1")
        self.assertEqual(payload["kind"], "EXECUTION_KERNEL_RUNTIME_BRIDGE")
        self.assertTrue(payload["linkage"]["kernelLinked"])
        self.assertTrue(payload["linkage"]["runtimeLinked"])
        self.assertTrue(payload["linkage"]["guardLinked"])
        self.assertTrue(payload["linkage"]["executionBlocked"])
        self.assertTrue(payload["linkage"]["mutationBlocked"])
        self.assertTrue(payload["linkage"]["rollbackBlocked"])
        self.assertFalse(payload["linkage"]["authorizationForwarded"])
        self.assertFalse(payload["linkage"]["executionForwarded"])
        self.assertFalse(payload["linkage"]["mutationForwarded"])
        self.assertTrue(payload["diagnostics"]["runtimeSafe"])
        self.assertTrue(payload["diagnostics"]["inspectionOnly"])
        self.assertTrue(payload["diagnostics"]["replaySafe"])
        self.assertTrue(payload["diagnostics"]["executionBlocked"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["rollbackBlocked"])
        self.assertTrue(payload["diagnostics"]["queueCompatible"])
        self.assertTrue(payload["diagnostics"]["schedulerCompatible"])
        self.assertTrue(payload["diagnostics"]["checkpointCompatible"])
        self.assertEqual(payload["diagnostics"]["stageCount"], 2)

    def test_runtime_bridge_snapshot_and_diagnostics(self):
        script = """
const bridge = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-bridge.js");
const snapshot = bridge.buildExecutionKernelRuntimeBridgeSnapshot({
  mode: "INSPECTION",
  guardReference: "guard.reference.1",
  runtimeEnvironment: "runtime.reference.1",
  prakriyaPlan: "prakriya.reference.1",
  derivationGraph: "graph.reference.1",
  stages: [
    { id: "stage-init", type: "KERNEL_INITIALIZATION", order: 10, referenceId: "kernel.init.1" }
  ]
});
const result = bridge.getExecutionKernelRuntimeBridgeDiagnostics(snapshot);
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

        self.assertTrue(payload["ready"])
        self.assertTrue(payload["runtimeLinked"])
        self.assertTrue(payload["guardLinked"])
        self.assertTrue(payload["kernelLinked"])
        self.assertTrue(payload["executionBlocked"])
        self.assertTrue(payload["mutationFree"])
        self.assertTrue(payload["rollbackBlocked"])
        self.assertEqual(payload["stageCount"], 1)


if __name__ == "__main__":
    unittest.main()
