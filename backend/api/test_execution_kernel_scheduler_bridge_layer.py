import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KERNEL_SCHEDULER_BRIDGE = ROOT / "ui" / "tabs" / "sanskrit" / "execution-kernel" / "execution-kernel-scheduler-bridge.js"


class TestExecutionKernelSchedulerBridgeLayer(unittest.TestCase):
    def test_scheduler_bridge_file_is_syntax_valid(self):
        result = subprocess.run(
            ["node", "--check", str(KERNEL_SCHEDULER_BRIDGE)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_scheduler_reference_normalization_observation_only(self):
        script = """
const bridge = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-scheduler-bridge.js");
const result = bridge.normalizeExecutionSchedulerReference({
  id: "scheduler.snapshot.1",
  kind: "EXECUTION_SCHEDULER_SNAPSHOT",
  schemaVersion: "sanskrit-scheduler.v1",
  status: "READY",
  scheduled: true,
  dispatchAllowed: true
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

        self.assertTrue(payload["scheduled"])
        self.assertTrue(payload["dispatchAllowed"])
        self.assertTrue(payload["diagnostics"]["normalized"])
        self.assertTrue(payload["diagnostics"]["schedulerLinked"])
        self.assertTrue(payload["diagnostics"]["sourceScheduledObserved"])
        self.assertTrue(payload["diagnostics"]["sourceDispatchObserved"])
        self.assertFalse(payload["diagnostics"]["bridgeScheduleGranted"])
        self.assertFalse(payload["diagnostics"]["bridgeDispatchGranted"])
        self.assertFalse(payload["diagnostics"]["bridgeExecutionGranted"])

    def test_scheduler_bridge_blocks_scheduling_and_dispatch(self):
        script = """
const engine = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js");
const bridge = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-scheduler-bridge.js");
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
const result = bridge.createExecutionKernelSchedulerBridge({
  kernelSnapshot,
  scheduler: {
    id: "scheduler.snapshot.1",
    kind: "EXECUTION_SCHEDULER_SNAPSHOT",
    schemaVersion: "sanskrit-scheduler.v1",
    status: "READY",
    scheduled: true,
    dispatchAllowed: true
  },
  queue: "queue.snapshot.1",
  replay: "replay.snapshot.1",
  checkpoint: "checkpoint.snapshot.1",
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-execution-kernel-scheduler-bridge.v1")
        self.assertEqual(payload["kind"], "EXECUTION_KERNEL_SCHEDULER_BRIDGE")
        self.assertTrue(payload["linkage"]["schedulerLinked"])
        self.assertTrue(payload["linkage"]["queueLinked"])
        self.assertTrue(payload["linkage"]["replayLinked"])
        self.assertTrue(payload["linkage"]["checkpointLinked"])
        self.assertTrue(payload["linkage"]["runtimeLinked"])
        self.assertTrue(payload["linkage"]["executionBlocked"])
        self.assertTrue(payload["linkage"]["schedulingBlocked"])
        self.assertTrue(payload["linkage"]["dispatchBlocked"])
        self.assertTrue(payload["linkage"]["rollbackBlocked"])
        self.assertTrue(payload["linkage"]["restoreBlocked"])
        self.assertTrue(payload["linkage"]["mutationBlocked"])
        self.assertTrue(payload["linkage"]["surfaceFormBlocked"])
        self.assertTrue(payload["diagnostics"]["schedulerOnly"])
        self.assertTrue(payload["diagnostics"]["replaySafe"])
        self.assertTrue(payload["diagnostics"]["executionBlocked"])
        self.assertTrue(payload["diagnostics"]["schedulingBlocked"])
        self.assertTrue(payload["diagnostics"]["dispatchBlocked"])
        self.assertTrue(payload["diagnostics"]["rollbackBlocked"])
        self.assertTrue(payload["diagnostics"]["restoreBlocked"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["surfaceFormBlocked"])
        self.assertTrue(payload["diagnostics"]["queueCompatible"])
        self.assertEqual(payload["diagnostics"]["stageCount"], 2)

    def test_scheduler_bridge_snapshot_and_diagnostics(self):
        script = """
const bridge = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-scheduler-bridge.js");
const snapshot = bridge.buildExecutionKernelSchedulerBridgeSnapshot({
  mode: "INSPECTION",
  scheduler: "scheduler.reference.1",
  queue: "queue.reference.1",
  replay: "replay.reference.1",
  checkpoint: "checkpoint.reference.1",
  runtimeEnvironment: "runtime.reference.1",
  prakriyaPlan: "prakriya.reference.1",
  derivationGraph: "graph.reference.1",
  stages: [
    { id: "stage-init", type: "KERNEL_INITIALIZATION", order: 10, referenceId: "kernel.init.1" }
  ]
});
const result = bridge.getExecutionKernelSchedulerBridgeDiagnostics(snapshot);
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
        self.assertTrue(payload["schedulerLinked"])
        self.assertTrue(payload["queueLinked"])
        self.assertTrue(payload["replayLinked"])
        self.assertTrue(payload["checkpointLinked"])
        self.assertTrue(payload["runtimeLinked"])
        self.assertTrue(payload["executionBlocked"])
        self.assertTrue(payload["schedulingBlocked"])
        self.assertTrue(payload["dispatchBlocked"])
        self.assertTrue(payload["rollbackBlocked"])
        self.assertTrue(payload["restoreBlocked"])
        self.assertTrue(payload["mutationFree"])
        self.assertTrue(payload["surfaceFormBlocked"])
        self.assertTrue(payload["queueCompatible"])
        self.assertEqual(payload["stageCount"], 1)


if __name__ == "__main__":
    unittest.main()
