import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAKARA_MAP = ROOT / "ui" / "tabs" / "sanskrit" / "lakara-planning" / "lakara-planning-map.js"
LAKARA_ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "lakara-planning" / "lakara-planning-engine.js"


class TestLakaraPlanningLayer(unittest.TestCase):
    def test_lakara_planning_files_are_syntax_valid(self):
        for path in (LAKARA_MAP, LAKARA_ENGINE):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_lakara_planning_export_is_runtime_safe_and_normalized(self):
        script = """
const lakara = require("./ui/tabs/sanskrit/lakara-planning/lakara-planning-engine.js");
const result = lakara.buildLakaraPlanningExport();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-lakara-planning.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contracts"]["deterministic"])
        self.assertTrue(payload["contracts"]["immutable"])
        self.assertTrue(payload["contracts"]["inspectionOnly"])
        self.assertTrue(payload["contracts"]["nonPerformative"])
        self.assertTrue(payload["contracts"]["nonMutating"])
        self.assertTrue(payload["contracts"]["runtimeIsolated"])
        self.assertTrue(payload["contracts"]["schedulerLinked"])
        self.assertTrue(payload["contracts"]["irLinked"])
        self.assertTrue(payload["contracts"]["queueLinked"])
        self.assertTrue(payload["contracts"]["traceLinked"])
        self.assertTrue(payload["contracts"]["checkpointLinked"])
        self.assertTrue(payload["contracts"]["executionGuardLinked"])
        self.assertTrue(payload["contracts"]["morphologyPlanningLinked"])
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
        self.assertTrue(payload["diagnostics"]["executionGuardLinked"])
        self.assertTrue(payload["diagnostics"]["morphologyPlanningLinked"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["candidateOnly"])

    def test_create_lakara_planning_snapshot_is_candidate_only(self):
        script = """
const lakara = require("./ui/tabs/sanskrit/lakara-planning/lakara-planning-engine.js");
const result = lakara.createLakaraPlanningSnapshot({
  candidates: [
    { id: "lakara-1", type: "DHATU_LAKARA_CANDIDATE", root: "gam", lakara: "lat", purusha: "prathama", vacana: "ekavacana", pada: "parasmaipada" },
    { id: "lakara-2", type: "CONJUGATION_STATE", root: "bhū", lakara: "lot", purusha: "madhyama", vacana: "ekavacana", pada: "parasmaipada" }
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-lakara-planning.v1")
        self.assertEqual(payload["kind"], "LAKARA_PLANNING_SNAPSHOT")
        self.assertEqual(len(payload["candidates"]), 2)
        self.assertEqual(payload["candidates"][0]["root"], "gam")
        self.assertEqual(payload["candidates"][0]["lakara"], "lat")
        self.assertEqual(payload["candidates"][0]["type"], "DHATU_LAKARA_CANDIDATE")
        self.assertTrue(payload["candidates"][0]["planned"])
        self.assertFalse(payload["candidates"][0]["executed"])
        self.assertTrue(payload["trace"]["replaySafe"])
        self.assertTrue(payload["trace"]["mutationFree"])
        self.assertEqual(payload["trace"]["candidateCount"], 2)

    def test_lakara_planning_diagnostics_contracts_are_satisfied(self):
        script = """
const lakara = require("./ui/tabs/sanskrit/lakara-planning/lakara-planning-engine.js");
const result = lakara.getLakaraPlanningDiagnostics();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-lakara-planning.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contractsSatisfied"])
        self.assertEqual(payload["fieldCount"], 6)


if __name__ == "__main__":
    unittest.main()