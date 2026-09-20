import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRACE_MAP = ROOT / "ui" / "tabs" / "sanskrit" / "replay-trace" / "replay-trace-map.js"
TRACE_ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "replay-trace" / "replay-trace-engine.js"


class TestReplayTraceLayer(unittest.TestCase):
    def test_replay_trace_files_are_syntax_valid(self):
        for path in (TRACE_MAP, TRACE_ENGINE):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_replay_trace_export_is_runtime_safe_and_normalized(self):
        script = """
const trace = require("./ui/tabs/sanskrit/replay-trace/replay-trace-engine.js");
const result = trace.buildReplayTraceExport();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-replay-trace.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contracts"]["deterministic"])
        self.assertTrue(payload["contracts"]["immutable"])
        self.assertTrue(payload["contracts"]["inspectionOnly"])
        self.assertTrue(payload["contracts"]["nonPerformative"])
        self.assertTrue(payload["contracts"]["runtimeIsolated"])
        self.assertTrue(payload["contracts"]["schedulerLinked"])
        self.assertTrue(payload["contracts"]["irLinked"])
        self.assertTrue(payload["contracts"]["queueLinked"])
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
        self.assertTrue(payload["diagnostics"]["mutationFree"])

        for field in payload["fields"]:
            self.assertIsInstance(field["id"], str)
            self.assertIsInstance(field["type"], str)
            self.assertIsInstance(field["summary"], str)
            self.assertIsInstance(field["required"], bool)
            self.assertIsInstance(field["diagnostics"], list)

    def test_create_replay_trace_snapshot_is_replay_safe(self):
        script = """
const trace = require("./ui/tabs/sanskrit/replay-trace/replay-trace-engine.js");
const result = trace.createReplayTraceSnapshot({
  events: [
    { id: "event-1", type: "SCHEDULER_DECISION", referenceId: "rule.1.4.2", summary: "precedence decision" },
    { id: "event-2", type: "IR_SNAPSHOT", referenceId: "ir.snapshot.1", summary: "snapshot reference" },
    { id: "event-3", type: "QUEUE_ITEM", referenceId: "queue.item.1", summary: "queue reference" }
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-replay-trace.v1")
        self.assertEqual(payload["kind"], "REPLAY_TRACE_SNAPSHOT")
        self.assertEqual(len(payload["events"]), 3)
        self.assertEqual(payload["events"][0]["id"], "event-1")
        self.assertEqual(payload["events"][0]["type"], "SCHEDULER_DECISION")
        self.assertTrue(payload["trace"]["replaySafe"])
        self.assertTrue(payload["trace"]["mutationFree"])
        self.assertEqual(payload["trace"]["eventCount"], 3)

    def test_replay_trace_diagnostics_contracts_are_satisfied(self):
        script = """
const trace = require("./ui/tabs/sanskrit/replay-trace/replay-trace-engine.js");
const result = trace.getReplayTraceDiagnostics();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-replay-trace.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contractsSatisfied"])
        self.assertEqual(payload["fieldCount"], 6)


if __name__ == "__main__":
    unittest.main()