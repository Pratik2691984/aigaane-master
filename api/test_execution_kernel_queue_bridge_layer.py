import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KERNEL_QUEUE_BRIDGE = ROOT / "ui" / "tabs" / "sanskrit" / "execution-kernel" / "execution-kernel-queue-bridge.js"


class TestExecutionKernelQueueBridgeLayer(unittest.TestCase):
    def test_queue_bridge_file_is_syntax_valid(self):
        result = subprocess.run(
            ["node", "--check", str(KERNEL_QUEUE_BRIDGE)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_queue_reference_normalization_observation_only(self):
        script = """
const bridge = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-queue-bridge.js");
const result = bridge.normalizeExecutionQueueReference({
  id: "queue.snapshot.1",
  kind: "EXECUTION_QUEUE_SNAPSHOT",
  schemaVersion: "sanskrit-queue.v1",
  status: "READY",
  queued: true,
  dequeueAllowed: true
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

        self.assertTrue(payload["queued"])
        self.assertTrue(payload["dequeueAllowed"])
        self.assertTrue(payload["diagnostics"]["normalized"])
        self.assertTrue(payload["diagnostics"]["queueLinked"])
        self.assertTrue(payload["diagnostics"]["sourceQueuedObserved"])
        self.assertTrue(payload["diagnostics"]["sourceDequeueObserved"])
        self.assertFalse(payload["diagnostics"]["bridgeQueueGranted"])
        self.assertFalse(payload["diagnostics"]["bridgeExecutionGranted"])
        self.assertFalse(payload["diagnostics"]["bridgeMutationGranted"])

    def test_queue_bridge_blocks_execution_and_dequeue(self):
        script = """
const engine = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js");
const bridge = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-queue-bridge.js");
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
const result = bridge.createExecutionKernelQueueBridge({
  kernelSnapshot,
  queue: {
    id: "queue.snapshot.1",
    kind: "EXECUTION_QUEUE_SNAPSHOT",
    schemaVersion: "sanskrit-queue.v1",
    status: "READY",
    queued: true,
    dequeueAllowed: true
  },
  replay: "replay.snapshot.1",
  checkpoint: "checkpoint.snapshot.1",
  guardReference: "guard.snapshot.1",
  runtimeEnvironment: "runtime.snapshot.1"
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-execution-kernel-queue-bridge.v1")
        self.assertEqual(payload["kind"], "EXECUTION_KERNEL_QUEUE_BRIDGE")
        self.assertTrue(payload["linkage"]["queueLinked"])
        self.assertTrue(payload["linkage"]["replayLinked"])
        self.assertTrue(payload["linkage"]["checkpointLinked"])
        self.assertTrue(payload["linkage"]["runtimeLinked"])
        self.assertTrue(payload["linkage"]["executionBlocked"])
        self.assertTrue(payload["linkage"]["dequeueBlocked"])
        self.assertTrue(payload["linkage"]["rollbackBlocked"])
        self.assertTrue(payload["linkage"]["restoreBlocked"])
        self.assertTrue(payload["linkage"]["mutationBlocked"])
        self.assertTrue(payload["linkage"]["surfaceFormBlocked"])
        self.assertTrue(payload["diagnostics"]["queueOnly"])
        self.assertTrue(payload["diagnostics"]["replaySafe"])
        self.assertTrue(payload["diagnostics"]["executionBlocked"])
        self.assertTrue(payload["diagnostics"]["dequeueBlocked"])
        self.assertTrue(payload["diagnostics"]["rollbackBlocked"])
        self.assertTrue(payload["diagnostics"]["restoreBlocked"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["surfaceFormBlocked"])
        self.assertTrue(payload["diagnostics"]["schedulerCompatible"])
        self.assertEqual(payload["diagnostics"]["stageCount"], 2)

    def test_queue_bridge_snapshot_and_diagnostics(self):
        script = """
const bridge = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-queue-bridge.js");
const snapshot = bridge.buildExecutionKernelQueueBridgeSnapshot({
  mode: "INSPECTION",
  queue: "queue.reference.1",
  replay: "replay.reference.1",
  checkpoint: "checkpoint.reference.1",
  guardReference: "guard.reference.1",
  runtimeEnvironment: "runtime.reference.1",
  prakriyaPlan: "prakriya.reference.1",
  derivationGraph: "graph.reference.1",
  stages: [
    { id: "stage-init", type: "KERNEL_INITIALIZATION", order: 10, referenceId: "kernel.init.1" }
  ]
});
const result = bridge.getExecutionKernelQueueBridgeDiagnostics(snapshot);
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
        self.assertTrue(payload["kernelLinked"])
        self.assertTrue(payload["queueLinked"])
        self.assertTrue(payload["replayLinked"])
        self.assertTrue(payload["checkpointLinked"])
        self.assertTrue(payload["runtimeLinked"])
        self.assertTrue(payload["executionBlocked"])
        self.assertTrue(payload["dequeueBlocked"])
        self.assertTrue(payload["rollbackBlocked"])
        self.assertTrue(payload["restoreBlocked"])
        self.assertTrue(payload["mutationFree"])
        self.assertTrue(payload["surfaceFormBlocked"])
        self.assertTrue(payload["schedulerCompatible"])
        self.assertEqual(payload["stageCount"], 1)


if __name__ == "__main__":
    unittest.main()
