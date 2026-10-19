import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_MAP = ROOT / "ui" / "tabs" / "sanskrit" / "runtime-environment" / "runtime-environment-map.js"
RUNTIME_ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "runtime-environment" / "runtime-environment-engine.js"


class TestRuntimeEnvironmentLayer(unittest.TestCase):
    def test_runtime_environment_files_are_syntax_valid(self):
        for path in (RUNTIME_MAP, RUNTIME_ENGINE):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_runtime_environment_export_is_runtime_safe_and_normalized(self):
        script = """
const runtime = require("./ui/tabs/sanskrit/runtime-environment/runtime-environment-engine.js");
const result = runtime.buildRuntimeEnvironmentExport();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-runtime-environment.v1")
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
        self.assertTrue(payload["contracts"]["checkpointLinked"])
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
        self.assertTrue(payload["diagnostics"]["checkpointLinked"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["guarded"])

        for field in payload["fields"]:
            self.assertIsInstance(field["id"], str)
            self.assertIsInstance(field["type"], str)
            self.assertIsInstance(field["summary"], str)
            self.assertIsInstance(field["required"], bool)
            self.assertIsInstance(field["diagnostics"], list)

    def test_create_runtime_environment_snapshot_is_guarded_and_replay_safe(self):
        script = """
const runtime = require("./ui/tabs/sanskrit/runtime-environment/runtime-environment-engine.js");
const result = runtime.createRuntimeEnvironmentSnapshot({
  mode: "GUARDED_RUNTIME",
  scheduler: "scheduler.snapshot.1",
  ir: "ir.snapshot.1",
  queue: "queue.snapshot.1",
  trace: "trace.snapshot.1",
  checkpoint: "checkpoint.snapshot.1"
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-runtime-environment.v1")
        self.assertEqual(payload["kind"], "RUNTIME_ENVIRONMENT_SNAPSHOT")
        self.assertEqual(payload["mode"], "GUARDED_RUNTIME")
        self.assertEqual(payload["references"]["scheduler"], "scheduler.snapshot.1")
        self.assertFalse(payload["capabilities"]["executeTransformations"])
        self.assertFalse(payload["capabilities"]["mutateSnapshots"])
        self.assertFalse(payload["capabilities"]["produceSurfaceForms"])
        self.assertTrue(payload["capabilities"]["inspectOnly"])
        self.assertTrue(payload["capabilities"]["rollbackSafe"])
        self.assertTrue(payload["trace"]["replaySafe"])
        self.assertTrue(payload["trace"]["mutationFree"])
        self.assertTrue(payload["trace"]["runtimeIsolated"])

    def test_runtime_environment_diagnostics_contracts_are_satisfied(self):
        script = """
const runtime = require("./ui/tabs/sanskrit/runtime-environment/runtime-environment-engine.js");
const result = runtime.getRuntimeEnvironmentDiagnostics();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-runtime-environment.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contractsSatisfied"])
        self.assertEqual(payload["fieldCount"], 6)


if __name__ == "__main__":
    unittest.main()