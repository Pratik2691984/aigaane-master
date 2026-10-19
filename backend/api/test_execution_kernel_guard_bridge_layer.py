import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KERNEL_GUARD_BRIDGE = ROOT / "ui" / "tabs" / "sanskrit" / "execution-kernel" / "execution-kernel-guard-bridge.js"


class TestExecutionKernelGuardBridgeLayer(unittest.TestCase):
    def test_execution_kernel_guard_bridge_file_is_syntax_valid(self):
        result = subprocess.run(
            ["node", "--check", str(KERNEL_GUARD_BRIDGE)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_guard_bridge_normalizes_guard_without_authorizing_kernel(self):
        script = """
const bridge = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-guard-bridge.js");
const result = bridge.normalizeExecutionGuardReference({
  id: "guard.snapshot.1",
  kind: "EXECUTION_GUARD_SNAPSHOT",
  schemaVersion: "sanskrit-execution-guard.v1",
  status: "READY",
  authorized: true,
  executionBlocked: false,
  mutationAllowed: true,
  surfaceFormsAllowed: true
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

        self.assertEqual(payload["id"], "guard.snapshot.1")
        self.assertEqual(payload["kind"], "EXECUTION_GUARD_SNAPSHOT")
        self.assertEqual(payload["schemaVersion"], "sanskrit-execution-guard.v1")
        self.assertEqual(payload["status"], "READY")
        self.assertTrue(payload["authorized"])
        self.assertTrue(payload["mutationAllowed"])
        self.assertTrue(payload["surfaceFormsAllowed"])
        self.assertTrue(payload["diagnostics"]["normalized"])
        self.assertTrue(payload["diagnostics"]["guardLinked"])
        self.assertTrue(payload["diagnostics"]["sourceAuthorizedObserved"])
        self.assertFalse(payload["diagnostics"]["sourceExecutionBlocked"])
        self.assertFalse(payload["diagnostics"]["bridgeAuthorizationGranted"])
        self.assertFalse(payload["diagnostics"]["bridgeMutationGranted"])
        self.assertFalse(payload["diagnostics"]["bridgeSurfaceFormsGranted"])

    def test_guard_bridge_blocks_forwarding_even_with_authorized_source(self):
        script = """
const engine = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js");
const bridge = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-guard-bridge.js");
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
const result = bridge.createExecutionKernelGuardBridge({
  kernelSnapshot,
  guardSnapshot: {
    id: "guard.snapshot.1",
    kind: "EXECUTION_GUARD_SNAPSHOT",
    schemaVersion: "sanskrit-execution-guard.v1",
    status: "READY",
    authorized: true,
    executionBlocked: false,
    mutationAllowed: true,
    surfaceFormsAllowed: true
  },
  runtimeEnvironment: {
    id: "runtime.snapshot.1",
    kind: "RUNTIME_ENVIRONMENT_SNAPSHOT",
    schemaVersion: "sanskrit-runtime-environment.v1",
    status: "READY"
  }
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-execution-kernel-guard-bridge.v1")
        self.assertEqual(payload["kind"], "EXECUTION_KERNEL_GUARD_BRIDGE")
        self.assertEqual(payload["kernel"]["stageCount"], 2)
        self.assertTrue(payload["guard"]["authorized"])
        self.assertTrue(payload["linkage"]["kernelLinked"])
        self.assertTrue(payload["linkage"]["guardLinked"])
        self.assertTrue(payload["linkage"]["runtimeLinked"])
        self.assertTrue(payload["linkage"]["executionBlocked"])
        self.assertFalse(payload["linkage"]["authorizationForwarded"])
        self.assertFalse(payload["linkage"]["mutationForwarded"])
        self.assertFalse(payload["linkage"]["surfaceFormForwarded"])
        self.assertTrue(payload["diagnostics"]["ready"])
        self.assertTrue(payload["diagnostics"]["inspectionOnly"])
        self.assertTrue(payload["diagnostics"]["bridgeOnly"])
        self.assertTrue(payload["diagnostics"]["executionBlocked"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["surfaceFormBlocked"])
        self.assertEqual(payload["diagnostics"]["stageCount"], 2)

    def test_guard_bridge_convenience_snapshot_and_diagnostics(self):
        script = """
const bridge = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-guard-bridge.js");
const snapshot = bridge.buildExecutionKernelGuardBridgeSnapshot({
  mode: "INSPECTION",
  guard: "guard.reference.1",
  runtimeEnvironment: "runtime.reference.1",
  prakriyaPlan: "prakriya.reference.1",
  derivationGraph: "graph.reference.1",
  stages: [
    { id: "stage-init", type: "KERNEL_INITIALIZATION", order: 10, referenceId: "kernel.init.1" }
  ]
});
const result = bridge.getExecutionKernelGuardBridgeDiagnostics(snapshot);
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-execution-kernel-guard-bridge.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["guardLinked"])
        self.assertTrue(payload["runtimeLinked"])
        self.assertTrue(payload["kernelLinked"])
        self.assertTrue(payload["executionBlocked"])
        self.assertTrue(payload["mutationFree"])
        self.assertTrue(payload["surfaceFormBlocked"])
        self.assertFalse(payload["authorizationForwarded"])
        self.assertEqual(payload["stageCount"], 1)


if __name__ == "__main__":
    unittest.main()
