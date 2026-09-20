import json
import subprocess
import unittest


COMPLIANCE_BRIDGE = "ui/tabs/sanskrit/execution-kernel/execution-kernel-compliance-bridge.js"


class ExecutionKernelComplianceBridgeLayerTests(unittest.TestCase):
    def run_node_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return json.loads(result.stdout)

    def test_compliance_bridge_file_is_syntax_valid(self):
        subprocess.run(
            ["node", "--check", COMPLIANCE_BRIDGE],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_compliance_reference_normalization_observation_only(self):
        data = self.run_node_json(
            """
            const { normalizeExecutionComplianceReference } = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-compliance-bridge.js");
            const result = normalizeExecutionComplianceReference({
              id: "compliance.snapshot.1",
              kind: "EXECUTION_COMPLIANCE_SNAPSHOT",
              schemaVersion: "sanskrit-compliance.v1",
              status: "READY",
              compliant: true,
              enforcementAllowed: true,
              mutationAllowed: true
            });
            console.log(JSON.stringify(result));
            """
        )

        self.assertEqual(data["id"], "compliance.snapshot.1")
        self.assertTrue(data["compliant"])
        self.assertTrue(data["enforcementAllowed"])
        self.assertTrue(data["mutationAllowed"])
        self.assertTrue(data["diagnostics"]["normalized"])
        self.assertTrue(data["diagnostics"]["complianceLinked"])
        self.assertTrue(data["diagnostics"]["sourceCompliantObserved"])
        self.assertTrue(data["diagnostics"]["sourceEnforcementObserved"])
        self.assertTrue(data["diagnostics"]["sourceMutationObserved"])
        self.assertFalse(data["diagnostics"]["bridgeComplianceGranted"])
        self.assertFalse(data["diagnostics"]["bridgeEnforcementGranted"])
        self.assertFalse(data["diagnostics"]["bridgeMutationGranted"])
        self.assertFalse(data["diagnostics"]["bridgeExecutionGranted"])

    def test_compliance_bridge_blocks_enforcement_and_execution(self):
        data = self.run_node_json(
            """
            const { createExecutionKernelSnapshot } = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js");
            const { createExecutionKernelComplianceBridge } = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-compliance-bridge.js");

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

            const bridge = createExecutionKernelComplianceBridge({
              kernelSnapshot,
              compliance: { id: "compliance.snapshot.1", compliant: true, enforcementAllowed: true },
              policy: "policy.snapshot.1",
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

        self.assertEqual(data["schemaVersion"], "sanskrit-execution-kernel-compliance-bridge.v1")
        self.assertEqual(data["kind"], "EXECUTION_KERNEL_COMPLIANCE_BRIDGE")
        self.assertTrue(data["linkage"]["complianceLinked"])
        self.assertTrue(data["linkage"]["policyLinked"])
        self.assertTrue(data["linkage"]["auditLinked"])
        self.assertTrue(data["linkage"]["traceLinked"])
        self.assertTrue(data["linkage"]["schedulerLinked"])
        self.assertTrue(data["linkage"]["queueLinked"])
        self.assertTrue(data["linkage"]["replayLinked"])
        self.assertTrue(data["linkage"]["checkpointLinked"])
        self.assertTrue(data["linkage"]["runtimeLinked"])
        self.assertTrue(data["linkage"]["complianceInspectionOnly"])
        self.assertTrue(data["linkage"]["enforcementBlocked"])
        self.assertTrue(data["linkage"]["executionBlocked"])
        self.assertTrue(data["linkage"]["mutationBlocked"])
        self.assertTrue(data["linkage"]["rollbackBlocked"])
        self.assertTrue(data["linkage"]["replayBlocked"])
        self.assertTrue(data["linkage"]["schedulingBlocked"])
        self.assertTrue(data["linkage"]["dispatchBlocked"])
        self.assertTrue(data["linkage"]["dequeueBlocked"])
        self.assertTrue(data["linkage"]["surfaceFormBlocked"])
        self.assertTrue(data["diagnostics"]["complianceOnly"])
        self.assertTrue(data["diagnostics"]["policyCompatible"])
        self.assertTrue(data["diagnostics"]["auditCompatible"])
        self.assertTrue(data["diagnostics"]["traceCompatible"])
        self.assertTrue(data["diagnostics"]["schedulerCompatible"])
        self.assertTrue(data["diagnostics"]["queueCompatible"])
        self.assertTrue(data["diagnostics"]["checkpointCompatible"])
        self.assertTrue(data["diagnostics"]["replayCompatible"])
        self.assertTrue(data["diagnostics"]["runtimeCompatible"])
        self.assertEqual(data["diagnostics"]["stageCount"], 2)

    def test_compliance_bridge_snapshot_and_diagnostics(self):
        data = self.run_node_json(
            """
            const {
              buildExecutionKernelComplianceBridgeSnapshot,
              getExecutionKernelComplianceBridgeDiagnostics
            } = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-compliance-bridge.js");

            const bridge = buildExecutionKernelComplianceBridgeSnapshot({
              mode: "INSPECTION",
              compliance: "compliance.reference.1",
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

            console.log(JSON.stringify(getExecutionKernelComplianceBridgeDiagnostics(bridge)));
            """
        )

        self.assertTrue(data["ready"])
        self.assertTrue(data["complianceLinked"])
        self.assertTrue(data["policyLinked"])
        self.assertTrue(data["auditLinked"])
        self.assertTrue(data["traceLinked"])
        self.assertTrue(data["schedulerLinked"])
        self.assertTrue(data["queueLinked"])
        self.assertTrue(data["replayLinked"])
        self.assertTrue(data["checkpointLinked"])
        self.assertTrue(data["runtimeLinked"])
        self.assertTrue(data["enforcementBlocked"])
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