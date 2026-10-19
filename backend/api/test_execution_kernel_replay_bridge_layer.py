import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KERNEL_REPLAY_BRIDGE = ROOT / "ui" / "tabs" / "sanskrit" / "execution-kernel" / "execution-kernel-replay-bridge.js"


class TestExecutionKernelReplayBridgeLayer(unittest.TestCase):
    def test_replay_bridge_file_is_syntax_valid(self):
        result = subprocess.run(
            ["node", "--check", str(KERNEL_REPLAY_BRIDGE)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_replay_reference_normalization_observation_only(self):
        script = """
const bridge = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-replay-bridge.js");
const result = bridge.normalizeExecutionReplayReference({
  id: "replay.snapshot.1",
  kind: "EXECUTION_REPLAY_SNAPSHOT",
  schemaVersion: "sanskrit-replay.v1",
  status: "READY",
  replayable: true,
  deterministicReplay: true
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

        self.assertEqual(payload["id"], "replay.snapshot.1")
        self.assertEqual(payload["kind"], "EXECUTION_REPLAY_SNAPSHOT")
        self.assertEqual(payload["schemaVersion"], "sanskrit-replay.v1")
        self.assertEqual(payload["status"], "READY")
        self.assertTrue(payload["replayable"])
        self.assertTrue(payload["deterministicReplay"])
        self.assertTrue(payload["diagnostics"]["normalized"])
        self.assertTrue(payload["diagnostics"]["replayLinked"])
        self.assertTrue(payload["diagnostics"]["sourceReplayableObserved"])
        self.assertTrue(payload["diagnostics"]["sourceDeterministicReplayObserved"])
        self.assertFalse(payload["diagnostics"]["bridgeReplayGranted"])
        self.assertFalse(payload["diagnostics"]["bridgeExecutionGranted"])
        self.assertFalse(payload["diagnostics"]["bridgeMutationGranted"])

    def test_replay_bridge_blocks_replay_and_execution(self):
        script = """
const engine = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js");
const bridge = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-replay-bridge.js");
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
const result = bridge.createExecutionKernelReplayBridge({
  kernelSnapshot,
  replay: {
    id: "replay.snapshot.1",
    kind: "EXECUTION_REPLAY_SNAPSHOT",
    schemaVersion: "sanskrit-replay.v1",
    status: "READY",
    replayable: true,
    deterministicReplay: true
  },
  checkpoint: "checkpoint.snapshot.1",
  trace: "trace.snapshot.1",
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-execution-kernel-replay-bridge.v1")
        self.assertEqual(payload["kind"], "EXECUTION_KERNEL_REPLAY_BRIDGE")
        self.assertEqual(payload["kernel"]["stageCount"], 2)
        self.assertTrue(payload["replay"]["replayable"])
        self.assertTrue(payload["replay"]["deterministicReplay"])
        self.assertTrue(payload["linkage"]["kernelLinked"])
        self.assertTrue(payload["linkage"]["replayLinked"])
        self.assertTrue(payload["linkage"]["checkpointLinked"])
        self.assertTrue(payload["linkage"]["traceLinked"])
        self.assertTrue(payload["linkage"]["guardLinked"])
        self.assertTrue(payload["linkage"]["runtimeLinked"])
        self.assertTrue(payload["linkage"]["replaySafe"])
        self.assertTrue(payload["linkage"]["replayBlocked"])
        self.assertTrue(payload["linkage"]["restoreBlocked"])
        self.assertTrue(payload["linkage"]["rollbackBlocked"])
        self.assertTrue(payload["linkage"]["executionBlocked"])
        self.assertTrue(payload["linkage"]["mutationBlocked"])
        self.assertTrue(payload["linkage"]["surfaceFormBlocked"])
        self.assertTrue(payload["diagnostics"]["ready"])
        self.assertTrue(payload["diagnostics"]["inspectionOnly"])
        self.assertTrue(payload["diagnostics"]["replayOnly"])
        self.assertTrue(payload["diagnostics"]["replaySafe"])
        self.assertTrue(payload["diagnostics"]["replayBlocked"])
        self.assertTrue(payload["diagnostics"]["restoreBlocked"])
        self.assertTrue(payload["diagnostics"]["rollbackBlocked"])
        self.assertTrue(payload["diagnostics"]["executionBlocked"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["surfaceFormBlocked"])
        self.assertEqual(payload["diagnostics"]["stageCount"], 2)

    def test_replay_bridge_snapshot_and_diagnostics(self):
        script = """
const bridge = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-replay-bridge.js");
const snapshot = bridge.buildExecutionKernelReplayBridgeSnapshot({
  mode: "INSPECTION",
  replay: "replay.reference.1",
  checkpoint: "checkpoint.reference.1",
  trace: "trace.reference.1",
  guardReference: "guard.reference.1",
  runtimeEnvironment: "runtime.reference.1",
  prakriyaPlan: "prakriya.reference.1",
  derivationGraph: "graph.reference.1",
  stages: [
    { id: "stage-init", type: "KERNEL_INITIALIZATION", order: 10, referenceId: "kernel.init.1" }
  ]
});
const result = bridge.getExecutionKernelReplayBridgeDiagnostics(snapshot);
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-execution-kernel-replay-bridge.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["kernelLinked"])
        self.assertTrue(payload["replayLinked"])
        self.assertTrue(payload["checkpointLinked"])
        self.assertTrue(payload["traceLinked"])
        self.assertTrue(payload["guardLinked"])
        self.assertTrue(payload["runtimeLinked"])
        self.assertTrue(payload["replaySafe"])
        self.assertTrue(payload["replayBlocked"])
        self.assertTrue(payload["restoreBlocked"])
        self.assertTrue(payload["rollbackBlocked"])
        self.assertTrue(payload["executionBlocked"])
        self.assertTrue(payload["mutationFree"])
        self.assertTrue(payload["surfaceFormBlocked"])
        self.assertEqual(payload["stageCount"], 1)


if __name__ == "__main__":
    unittest.main()
