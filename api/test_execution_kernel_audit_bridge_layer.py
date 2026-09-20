import json
import subprocess
import unittest


AUDIT_BRIDGE = "ui/tabs/sanskrit/execution-kernel/execution-kernel-audit-bridge.js"


class ExecutionKernelAuditBridgeLayerTests(unittest.TestCase):
    def run_node_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return json.loads(result.stdout)

    def test_audit_bridge_file_is_syntax_valid(self):
        subprocess.run(
            ["node", "--check", AUDIT_BRIDGE],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_audit_reference_normalization_observation_only(self):
        data = self.run_node_json(
            """
            const { normalizeExecutionAuditReference } = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-audit-bridge.js");
            const result = normalizeExecutionAuditReference({
              id: "audit.snapshot.1",
              kind: "EXECUTION_AUDIT_SNAPSHOT",
              schemaVersion: "sanskrit-audit.v1",
              status: "READY",
              auditable: true,
              auditMutationAllowed: true
            });
            console.log(JSON.stringify(result));
            """
        )

        self.assertEqual(data["id"], "audit.snapshot.1")
        self.assertEqual(data["kind"], "EXECUTION_AUDIT_SNAPSHOT")
        self.assertEqual(data["schemaVersion"], "sanskrit-audit.v1")
        self.assertEqual(data["status"], "READY")
        self.assertTrue(data["auditable"])
        self.assertTrue(data["auditMutationAllowed"])
        self.assertTrue(data["diagnostics"]["normalized"])
        self.assertTrue(data["diagnostics"]["auditLinked"])
        self.assertTrue(data["diagnostics"]["sourceAuditableObserved"])
        self.assertTrue(data["diagnostics"]["sourceAuditMutationObserved"])
        self.assertFalse(data["diagnostics"]["bridgeAuditGranted"])
        self.assertFalse(data["diagnostics"]["bridgeAuditMutationGranted"])
        self.assertFalse(data["diagnostics"]["bridgeExecutionGranted"])

    def test_audit_bridge_blocks_audit_mutation_and_execution(self):
        data = self.run_node_json(
            """
            const { createExecutionKernelSnapshot } = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js");
            const { createExecutionKernelAuditBridge } = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-audit-bridge.js");

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

            const bridge = createExecutionKernelAuditBridge({
              kernelSnapshot,
              audit: {
                id: "audit.snapshot.1",
                kind: "EXECUTION_AUDIT_SNAPSHOT",
                schemaVersion: "sanskrit-audit.v1",
                status: "READY",
                auditable: true,
                auditMutationAllowed: true
              },
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

        self.assertEqual(data["schemaVersion"], "sanskrit-execution-kernel-audit-bridge.v1")
        self.assertEqual(data["kind"], "EXECUTION_KERNEL_AUDIT_BRIDGE")
        self.assertEqual(data["kernel"]["stageCount"], 2)

        self.assertTrue(data["linkage"]["kernelLinked"])
        self.assertTrue(data["linkage"]["auditLinked"])
        self.assertTrue(data["linkage"]["traceLinked"])
        self.assertTrue(data["linkage"]["schedulerLinked"])
        self.assertTrue(data["linkage"]["queueLinked"])
        self.assertTrue(data["linkage"]["replayLinked"])
        self.assertTrue(data["linkage"]["checkpointLinked"])
        self.assertTrue(data["linkage"]["runtimeLinked"])

        self.assertTrue(data["linkage"]["auditInspectionOnly"])
        self.assertTrue(data["linkage"]["auditMutationBlocked"])
        self.assertTrue(data["linkage"]["replaySafe"])
        self.assertTrue(data["linkage"]["executionBlocked"])
        self.assertTrue(data["linkage"]["schedulingBlocked"])
        self.assertTrue(data["linkage"]["dispatchBlocked"])
        self.assertTrue(data["linkage"]["dequeueBlocked"])
        self.assertTrue(data["linkage"]["replayBlocked"])
        self.assertTrue(data["linkage"]["rollbackBlocked"])
        self.assertTrue(data["linkage"]["restoreBlocked"])
        self.assertTrue(data["linkage"]["mutationBlocked"])
        self.assertTrue(data["linkage"]["surfaceFormBlocked"])

        self.assertTrue(data["diagnostics"]["ready"])
        self.assertTrue(data["diagnostics"]["inspectionOnly"])
        self.assertTrue(data["diagnostics"]["auditOnly"])
        self.assertTrue(data["diagnostics"]["replaySafe"])
        self.assertTrue(data["diagnostics"]["auditMutationBlocked"])
        self.assertTrue(data["diagnostics"]["executionBlocked"])
        self.assertTrue(data["diagnostics"]["mutationFree"])
        self.assertTrue(data["diagnostics"]["surfaceFormBlocked"])
        self.assertTrue(data["diagnostics"]["traceCompatible"])
        self.assertTrue(data["diagnostics"]["schedulerCompatible"])
        self.assertTrue(data["diagnostics"]["queueCompatible"])
        self.assertTrue(data["diagnostics"]["checkpointCompatible"])
        self.assertTrue(data["diagnostics"]["replayCompatible"])
        self.assertTrue(data["diagnostics"]["runtimeCompatible"])
        self.assertEqual(data["diagnostics"]["stageCount"], 2)

    def test_audit_bridge_snapshot_and_diagnostics(self):
        data = self.run_node_json(
            """
            const {
              buildExecutionKernelAuditBridgeSnapshot,
              getExecutionKernelAuditBridgeDiagnostics
            } = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-audit-bridge.js");

            const bridge = buildExecutionKernelAuditBridgeSnapshot({
              mode: "INSPECTION",
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

            console.log(JSON.stringify(getExecutionKernelAuditBridgeDiagnostics(bridge)));
            """
        )

        self.assertEqual(data["schemaVersion"], "sanskrit-execution-kernel-audit-bridge.v1")
        self.assertTrue(data["ready"])
        self.assertTrue(data["kernelLinked"])
        self.assertTrue(data["auditLinked"])
        self.assertTrue(data["traceLinked"])
        self.assertTrue(data["schedulerLinked"])
        self.assertTrue(data["queueLinked"])
        self.assertTrue(data["replayLinked"])
        self.assertTrue(data["checkpointLinked"])
        self.assertTrue(data["runtimeLinked"])
        self.assertTrue(data["auditInspectionOnly"])
        self.assertTrue(data["auditMutationBlocked"])
        self.assertTrue(data["replaySafe"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["schedulingBlocked"])
        self.assertTrue(data["dispatchBlocked"])
        self.assertTrue(data["dequeueBlocked"])
        self.assertTrue(data["replayBlocked"])
        self.assertTrue(data["rollbackBlocked"])
        self.assertTrue(data["restoreBlocked"])
        self.assertTrue(data["mutationFree"])
        self.assertTrue(data["surfaceFormBlocked"])
        self.assertEqual(data["stageCount"], 1)


if __name__ == "__main__":
    unittest.main()