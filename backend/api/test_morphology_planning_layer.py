import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MORPHOLOGY_MAP = ROOT / "ui" / "tabs" / "sanskrit" / "morphology-planning" / "morphology-planning-map.js"
MORPHOLOGY_ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "morphology-planning" / "morphology-planning-engine.js"


class TestMorphologyPlanningLayer(unittest.TestCase):
    def test_morphology_planning_files_are_syntax_valid(self):
        for path in (MORPHOLOGY_MAP, MORPHOLOGY_ENGINE):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_morphology_planning_export_is_runtime_safe_and_normalized(self):
        script = """
const morphology = require("./ui/tabs/sanskrit/morphology-planning/morphology-planning-engine.js");
const result = morphology.buildMorphologyPlanningExport();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-morphology-planning.v1")
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
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["candidateOnly"])

    def test_create_morphology_planning_snapshot_is_candidate_only(self):
        script = """
const morphology = require("./ui/tabs/sanskrit/morphology-planning/morphology-planning-engine.js");
const result = morphology.createMorphologyPlanningSnapshot({
  candidates: [
    { id: "morph-1", type: "ROOT_PLAN", root: "gam", gana: "bhvadi", pada: "parasmaipada" },
    { id: "morph-2", type: "AFFIX_PLAN", affix: "lat", stem: "gaccha" }
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-morphology-planning.v1")
        self.assertEqual(payload["kind"], "MORPHOLOGY_PLANNING_SNAPSHOT")
        self.assertEqual(len(payload["candidates"]), 2)
        self.assertEqual(payload["candidates"][0]["root"], "gam")
        self.assertEqual(payload["candidates"][0]["type"], "ROOT_PLAN")
        self.assertTrue(payload["candidates"][0]["planned"])
        self.assertFalse(payload["candidates"][0]["executed"])
        self.assertTrue(payload["trace"]["replaySafe"])
        self.assertTrue(payload["trace"]["mutationFree"])
        self.assertEqual(payload["trace"]["candidateCount"], 2)

    def test_morphology_planning_diagnostics_contracts_are_satisfied(self):
        script = """
const morphology = require("./ui/tabs/sanskrit/morphology-planning/morphology-planning-engine.js");
const result = morphology.getMorphologyPlanningDiagnostics();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-morphology-planning.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contractsSatisfied"])
        self.assertEqual(payload["fieldCount"], 6)


if __name__ == "__main__":
    unittest.main()