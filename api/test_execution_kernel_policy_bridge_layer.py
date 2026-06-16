import json
import subprocess
import unittest


POLICY_BRIDGE = "ui/tabs/sanskrit/execution-kernel/execution-kernel-policy-bridge.js"


class ExecutionKernelPolicyBridgeLayerTests(unittest.TestCase):
    def run_node_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return json.loads(result.stdout)

    def test_policy_bridge_file_is_syntax_valid(self):
        subprocess.run(
            ["node", "--check", POLICY_BRIDGE],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_policy_reference_normalization_observation_only(self):
        data = self.run_node_json(
            """
            const { normalizeExecutionPolicyReference } = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-policy-bridge.js");
            const result = normalizeExecutionPolicyReference({
              id: "policy.snapshot.1",
              kind: "EXECUTION_POLICY_SNAPSHOT",
              schemaVersion: "sanskrit-policy.v1",
              status: "READY",
              executionPermitted: true,
              mutationPermitted: true,
              rollbackPermitted: true,
              replayPermitted: true
            });
            console.log(JSON.stringify(result));
            """
        )

        self.assertTrue(data["executionPermitted"])
        self.assertTrue(data["mutationPermitted"])
        self.assertTrue(data["rollbackPermitted"])
        self.assertTrue(data["replayPermitted"])
        self.assertFalse(data["diagnostics"]["bridgeExecutionGranted"])
        self.assertFalse(data["diagnostics"]["bridgeMutationGranted"])
        self.assertFalse(data["diagnostics"]["bridgeRollbackGranted"])
        self.assertFalse(data["diagnostics"]["bridgeReplayGranted"])

    def test_policy_bridge_blocks_execution(self):
        data = self.run_node_json(
            """
            const { createExecutionKernelSnapshot } = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js");
            const { createExecutionKernelPolicyBridge } = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-policy-bridge.js");

            const kernelSnapshot = createExecutionKernelSnapshot({
              mode: "INSPECTION",
              guard: "guard.snapshot.1",
              runtimeEnvironment: "runtime.snapshot.1",
              prakriyaPlan: "prakriya.snapshot.1",
              derivationGraph: "graph.snapshot.1",
              stages: [
                { id: "stage-init", type: "KERNEL_INITIALIZATION", order: 10, referenceId: "kernel.init.1" },
                { id: "stage-envelope", type: "EXECUTION_ENVELOPE", order: 40, referenceId: "execution.plan.1" }
              ]
            });

            const bridge = createExecutionKernelPolicyBridge({
              kernelSnapshot,
              policy: { id: "policy.snapshot.1", executionPermitted: true },
              audit: "audit.snapshot.1",
              trace: "trace.snapshot.1",
              scheduler: "scheduler.snapshot.1",
              queue: "queue.snapshot.1",
              replay: "replay.snapshot.1",
              checkpoint: "checkpoint.snapshot.1",
              runtimeEnvironment: "runtime.snapshot.1"
            });

            console.log(JSON.stringify(bridge));
            """
        )

        self.assertEqual(data["schemaVersion"], "sanskrit-execution-kernel-policy-bridge.v1")
        self.assertEqual(data["kind"], "EXECUTION_KERNEL_POLICY_BRIDGE")
        self.assertTrue(data["linkage"]["policyLinked"])
        self.assertTrue(data["linkage"]["auditLinked"])
        self.assertTrue(data["linkage"]["traceLinked"])
        self.assertTrue(data["linkage"]["schedulerLinked"])
        self.assertTrue(data["linkage"]["queueLinked"])
        self.assertTrue(data["linkage"]["replayLinked"])
        self.assertTrue(data["linkage"]["checkpointLinked"])
        self.assertTrue(data["linkage"]["runtimeLinked"])
        self.assertTrue(data["linkage"]["policyInspectionOnly"])
        self.assertTrue(data["linkage"]["executionBlocked"])
        self.assertTrue(data["linkage"]["mutationBlocked"])
        self.assertTrue(data["linkage"]["rollbackBlocked"])
        self.assertTrue(data["linkage"]["replayBlocked"])
        self.assertTrue(data["linkage"]["schedulingBlocked"])
        self.assertTrue(data["linkage"]["dispatchBlocked"])
        self.assertTrue(data["linkage"]["dequeueBlocked"])
        self.assertTrue(data["linkage"]["surfaceFormBlocked"])
        self.assertTrue(data["diagnostics"]["policyOnly"])
        self.assertTrue(data["diagnostics"]["auditCompatible"])
        self.assertTrue(data["diagnostics"]["traceCompatible"])
        self.assertTrue(data["diagnostics"]["schedulerCompatible"])
        self.assertTrue(data["diagnostics"]["queueCompatible"])
        self.assertTrue(data["diagnostics"]["checkpointCompatible"])
        self.assertTrue(data["diagnostics"]["replayCompatible"])
        self.assertTrue(data["diagnostics"]["runtimeCompatible"])
        self.assertEqual(data["diagnostics"]["stageCount"], 2)

    def test_policy_bridge_snapshot_and_diagnostics(self):
        data = self.run_node_json(
            """
            const {
              buildExecutionKernelPolicyBridgeSnapshot,
              getExecutionKernelPolicyBridgeDiagnostics
            } = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-policy-bridge.js");

            const bridge = buildExecutionKernelPolicyBridgeSnapshot({
              mode: "INSPECTION",
              policy: "policy.reference.1",
              audit: "audit.reference.1",
              trace: "trace.reference.1",
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

            console.log(JSON.stringify(getExecutionKernelPolicyBridgeDiagnostics(bridge)));
            """
        )

        self.assertTrue(data["ready"])
        self.assertTrue(data["policyLinked"])
        self.assertTrue(data["auditLinked"])
        self.assertTrue(data["traceLinked"])
        self.assertTrue(data["schedulerLinked"])
        self.assertTrue(data["queueLinked"])
        self.assertTrue(data["replayLinked"])
        self.assertTrue(data["checkpointLinked"])
        self.assertTrue(data["runtimeLinked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["mutationFree"])
        self.assertTrue(data["rollbackBlocked"])
        self.assertTrue(data["replayBlocked"])
        self.assertTrue(data["schedulingBlocked"])
        self.assertTrue(data["dispatchBlocked"])
        self.assertTrue(data["dequeueBlocked"])
        self.assertTrue(data["surfaceFormBlocked"])
        self.assertEqual(data["stageCount"], 1)


if __name__ == "__main__":
    unittest.main()