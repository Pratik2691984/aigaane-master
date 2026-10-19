import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE_MAP = ROOT / "ui" / "tabs" / "sanskrit" / "transformation-queue" / "transformation-queue-map.js"
QUEUE_ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "transformation-queue" / "transformation-queue-engine.js"


class TestTransformationQueueLayer(unittest.TestCase):
    def test_transformation_queue_files_are_syntax_valid(self):
        for path in (QUEUE_MAP, QUEUE_ENGINE):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_transformation_queue_export_is_runtime_safe_and_normalized(self):
        script = """
const queue = require("./ui/tabs/sanskrit/transformation-queue/transformation-queue-engine.js");
const result = queue.buildTransformationQueueExport();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-transformation-queue.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contracts"]["deterministic"])
        self.assertTrue(payload["contracts"]["immutable"])
        self.assertTrue(payload["contracts"]["inspectionOnly"])
        self.assertTrue(payload["contracts"]["nonPerformative"])
        self.assertTrue(payload["contracts"]["runtimeIsolated"])
        self.assertTrue(payload["contracts"]["schedulerLinked"])
        self.assertTrue(payload["contracts"]["irCompatible"])
        self.assertTrue(payload["contracts"]["replaySafe"])
        self.assertTrue(payload["contracts"]["staticPreviewCompatible"])
        self.assertEqual(payload["fieldCount"], 6)

        self.assertTrue(payload["diagnostics"]["normalized"])
        self.assertTrue(payload["diagnostics"]["deterministic"])
        self.assertTrue(payload["diagnostics"]["immutable"])
        self.assertTrue(payload["diagnostics"]["runtimeSafe"])
        self.assertTrue(payload["diagnostics"]["replaySafe"])
        self.assertTrue(payload["diagnostics"]["schedulerLinked"])
        self.assertTrue(payload["diagnostics"]["irCompatible"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])

        for field in payload["fields"]:
            self.assertIsInstance(field["id"], str)
            self.assertIsInstance(field["type"], str)
            self.assertIsInstance(field["summary"], str)
            self.assertIsInstance(field["required"], bool)
            self.assertIsInstance(field["diagnostics"], list)

    def test_create_transformation_queue_snapshot_is_replay_safe(self):
        script = """
const queue = require("./ui/tabs/sanskrit/transformation-queue/transformation-queue-engine.js");
const result = queue.createTransformationQueueSnapshot({
  queueItems: [
    { id: "queue-1", type: "RULE_APPLICATION", ruleId: "sutra.1.4.2" },
    { id: "queue-2", type: "MORPHOLOGY_PLAN", ruleId: "sutra.3.1.placeholder" }
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-transformation-queue.v1")
        self.assertEqual(payload["kind"], "TRANSFORMATION_QUEUE_SNAPSHOT")
        self.assertEqual(len(payload["queueItems"]), 2)
        self.assertEqual(payload["queueItems"][0]["id"], "queue-1")
        self.assertTrue(payload["queueItems"][0]["planned"])
        self.assertTrue(payload["trace"]["replaySafe"])
        self.assertTrue(payload["trace"]["mutationFree"])
        self.assertEqual(payload["trace"]["queueLength"], 2)

    def test_transformation_queue_diagnostics_contracts_are_satisfied(self):
        script = """
const queue = require("./ui/tabs/sanskrit/transformation-queue/transformation-queue-engine.js");
const result = queue.getTransformationQueueDiagnostics();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-transformation-queue.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contractsSatisfied"])
        self.assertEqual(payload["fieldCount"], 6)


if __name__ == "__main__":
    unittest.main()