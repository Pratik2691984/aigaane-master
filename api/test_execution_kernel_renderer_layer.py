import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KERNEL_RENDERER = ROOT / "ui" / "tabs" / "sanskrit" / "execution-kernel" / "execution-kernel-renderer.js"


class TestExecutionKernelRendererLayer(unittest.TestCase):
    def test_execution_kernel_renderer_file_is_syntax_valid(self):
        result = subprocess.run(
            ["node", "--check", str(KERNEL_RENDERER)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_renderer_builds_inspection_view_model(self):
        script = """
const engine = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js");
const renderer = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-renderer.js");
const snapshot = engine.createExecutionKernelSnapshot({
  mode: "GUARDED_RUNTIME",
  guard: "guard.snapshot.1",
  runtimeEnvironment: "runtime.snapshot.1",
  prakriyaPlan: "prakriya.snapshot.1",
  derivationGraph: "graph.snapshot.1",
  stages: [
    { id: "stage-init", type: "KERNEL_INITIALIZATION", order: 10, referenceId: "kernel.init.1" },
    { id: "stage-guard", type: "GUARD_VERIFICATION", order: 20, referenceId: "guard.snapshot.1" },
    { id: "stage-envelope", type: "EXECUTION_ENVELOPE", order: 40, referenceId: "execution.plan.1" }
  ]
});
const result = renderer.buildExecutionKernelInspectionViewModel(snapshot);
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

        self.assertEqual(payload["title"], "Controlled Sanskrit Execution Kernel")
        self.assertEqual(payload["subtitle"], "Inspection-only execution envelope")
        self.assertEqual(payload["mode"], "GUARDED_RUNTIME")
        self.assertTrue(payload["status"]["ready"])
        self.assertTrue(payload["status"]["inspectionOnly"])
        self.assertFalse(payload["status"]["executionAuthorized"])
        self.assertFalse(payload["status"]["executionPerformed"])
        self.assertFalse(payload["status"]["mutationPerformed"])
        self.assertFalse(payload["status"]["surfaceFormsProduced"])
        self.assertEqual(payload["diagnostics"]["stageCount"], 3)
        self.assertEqual(payload["diagnostics"]["blockedStageCount"], 3)
        self.assertEqual(payload["diagnostics"]["plannedStageCount"], 3)
        self.assertEqual(payload["diagnostics"]["executedStageCount"], 0)
        self.assertEqual(payload["diagnostics"]["authorizedStageCount"], 0)
        self.assertTrue(payload["diagnostics"]["replaySafe"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["executionBlocked"])
        self.assertTrue(payload["diagnostics"]["surfaceFormBlocked"])
        self.assertTrue(payload["diagnostics"]["rendererPure"])
        self.assertTrue(payload["diagnostics"]["staticPreviewCompatible"])
        self.assertTrue(
            all(stage["statusLabel"] == "PLANNED_ONLY" for stage in payload["stages"])
        )

    def test_renderer_text_output_is_deterministic_and_blocked(self):
        script = """
const engine = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js");
const renderer = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-renderer.js");
const snapshot = engine.createExecutionKernelSnapshot({
  mode: "GUARDED_RUNTIME",
  guard: "guard.snapshot.1",
  runtimeEnvironment: "runtime.snapshot.1",
  prakriyaPlan: "prakriya.snapshot.1",
  derivationGraph: "graph.snapshot.1",
  stages: [
    { id: "stage-envelope", type: "EXECUTION_ENVELOPE", order: 40, referenceId: "execution.plan.1" },
    { id: "stage-init", type: "KERNEL_INITIALIZATION", order: 10, referenceId: "kernel.init.1" },
    { id: "stage-guard", type: "GUARD_VERIFICATION", order: 20, referenceId: "guard.snapshot.1" }
  ]
});
const result = renderer.renderExecutionKernelInspectionText(snapshot);
console.log(result);
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
        text = result.stdout

        self.assertIn("Controlled Sanskrit Execution Kernel", text)
        self.assertIn("Schema: sanskrit-execution-kernel.v1", text)
        self.assertIn("Mode: GUARDED_RUNTIME", text)
        self.assertIn("Stages: 3", text)
        self.assertIn("Execution: BLOCKED", text)
        self.assertIn("Surface Forms: BLOCKED", text)
        self.assertIn("Mutation: BLOCKED", text)
        self.assertIn("[0] stage-init :: KERNEL_INITIALIZATION :: PLANNED_ONLY", text)
        self.assertIn("[1] stage-guard :: GUARD_VERIFICATION :: PLANNED_ONLY", text)
        self.assertIn("[2] stage-envelope :: EXECUTION_ENVELOPE :: PLANNED_ONLY", text)

    def test_renderer_diagnostics_are_safe(self):
        script = """
const engine = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js");
const renderer = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-renderer.js");
const snapshot = engine.createExecutionKernelSnapshot({
  mode: "GUARDED_RUNTIME",
  guard: "guard.snapshot.1",
  runtimeEnvironment: "runtime.snapshot.1",
  prakriyaPlan: "prakriya.snapshot.1",
  derivationGraph: "graph.snapshot.1",
  stages: [
    { id: "stage-init", type: "KERNEL_INITIALIZATION", order: 10, referenceId: "kernel.init.1" }
  ]
});
const result = renderer.getExecutionKernelRendererDiagnostics(snapshot);
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
        self.assertTrue(payload["rendererPure"])
        self.assertTrue(payload["inspectionOnly"])
        self.assertTrue(payload["executionBlocked"])
        self.assertTrue(payload["mutationFree"])
        self.assertTrue(payload["surfaceFormBlocked"])
        self.assertEqual(payload["stageCount"], 1)


if __name__ == "__main__":
    unittest.main()
