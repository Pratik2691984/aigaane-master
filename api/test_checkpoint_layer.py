import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT_MAP = ROOT / "ui" / "tabs" / "sanskrit" / "checkpoint" / "checkpoint-map.js"
CHECKPOINT_ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "checkpoint" / "checkpoint-engine.js"


class TestCheckpointLayer(unittest.TestCase):
    def test_checkpoint_files_are_syntax_valid(self):
        for path in (CHECKPOINT_MAP, CHECKPOINT_ENGINE):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_checkpoint_export_is_runtime_safe_and_normalized(self):
        script = """
const checkpoint = require("./ui/tabs/sanskrit/checkpoint/checkpoint-engine.js");
const result = checkpoint.buildCheckpointExport();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-checkpoint.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contracts"]["deterministic"])
        self.assertTrue(payload["contracts"]["immutable"])
        self.assertTrue(payload["contracts"]["inspectionOnly"])
        self.assertTrue(payload["contracts"]["nonPerformative"])
        self.assertTrue(payload["contracts"]["runtimeIsolated"])
        self.assertTrue(payload["contracts"]["schedulerLinked"])
        self.assertTrue(payload["contracts"]["irLinked"])
        self.assertTrue(payload["contracts"]["queueLinked"])
        self.assertTrue(payload["contracts"]["traceLinked"])
        self.assertTrue(payload["contracts"]["replaySafe"])
        self.assertTrue(payload["contracts"]["staticPreviewCompatible"])
        self.assertEqual(payload["fieldCount"], 6)

        self.assertTrue(payload["diagnostics"]["normalized"])
        self.assertTrue(payload["diagnostics"]["deterministic"])
        self.assertTrue(payload["diagnostics"]["immutable"])
        self.assertTrue(payload["diagnostics"]["runtimeSafe"])
        self.assertTrue(payload["diagnostics"]["replaySafe"])
        self.assertTrue(payload["diagnostics"]["schedulerLinked"])
        self.assertTrue(payload["diagnostics"]["irLinked"])
        self.assertTrue(payload["diagnostics"]["queueLinked"])
        self.assertTrue(payload["diagnostics"]["traceLinked"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])

        for field in payload["fields"]:
            self.assertIsInstance(field["id"], str)
            self.assertIsInstance(field["type"], str)
            self.assertIsInstance(field["summary"], str)
            self.assertIsInstance(field["required"], bool)
            self.assertIsInstance(field["diagnostics"], list)

    def test_create_checkpoint_snapshot_is_replay_safe(self):
        script = """
const checkpoint = require("./ui/tabs/sanskrit/checkpoint/checkpoint-engine.js");
const result = checkpoint.createCheckpointSnapshot({
  checkpoints: [
    { id: "checkpoint-1", type: "SCHEDULER_CHECKPOINT", referenceId: "scheduler.snapshot.1", summary: "scheduler state" },
    { id: "checkpoint-2", type: "IR_CHECKPOINT", referenceId: "ir.snapshot.1", summary: "ir state" },
    { id: "checkpoint-3", type: "TRACE_CHECKPOINT", referenceId: "trace.snapshot.1", summary: "trace state" }
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-checkpoint.v1")
        self.assertEqual(payload["kind"], "CHECKPOINT_SNAPSHOT")
        self.assertEqual(len(payload["checkpoints"]), 3)
        self.assertEqual(payload["checkpoints"][0]["id"], "checkpoint-1")
        self.assertEqual(payload["checkpoints"][0]["type"], "SCHEDULER_CHECKPOINT")
        self.assertTrue(payload["trace"]["replaySafe"])
        self.assertTrue(payload["trace"]["mutationFree"])
        self.assertEqual(payload["trace"]["checkpointCount"], 3)

    def test_checkpoint_diagnostics_contracts_are_satisfied(self):
        script = """
const checkpoint = require("./ui/tabs/sanskrit/checkpoint/checkpoint-engine.js");
const result = checkpoint.getCheckpointDiagnostics();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-checkpoint.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contractsSatisfied"])
        self.assertEqual(payload["fieldCount"], 6)


if __name__ == "__main__":
    unittest.main()