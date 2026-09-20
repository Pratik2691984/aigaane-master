import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SANDHI_MAP = ROOT / "ui" / "tabs" / "sanskrit" / "sandhi-planning" / "sandhi-planning-map.js"
SANDHI_ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "sandhi-planning" / "sandhi-planning-engine.js"


class TestSandhiPlanningLayer(unittest.TestCase):
    def test_sandhi_planning_files_are_syntax_valid(self):
        for path in (SANDHI_MAP, SANDHI_ENGINE):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_sandhi_planning_export_is_runtime_safe_and_normalized(self):
        script = """
const sandhi = require("./ui/tabs/sanskrit/sandhi-planning/sandhi-planning-engine.js");
const result = sandhi.buildSandhiPlanningExport();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-sandhi-planning.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contracts"]["deterministic"])
        self.assertTrue(payload["contracts"]["immutable"])
        self.assertTrue(payload["contracts"]["inspectionOnly"])
        self.assertTrue(payload["contracts"]["nonPerformative"])
        self.assertTrue(payload["contracts"]["nonMutating"])
        self.assertTrue(payload["contracts"]["runtimeIsolated"])
        self.assertTrue(payload["contracts"]["schedulerLinked"])
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
        self.assertTrue(payload["diagnostics"]["queueLinked"])
        self.assertTrue(payload["diagnostics"]["traceLinked"])
        self.assertTrue(payload["diagnostics"]["checkpointLinked"])
        self.assertTrue(payload["diagnostics"]["executionGuardLinked"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["candidateOnly"])

    def test_classify_sandhi_boundary_is_deterministic(self):
        script = """
const sandhi = require("./ui/tabs/sanskrit/sandhi-planning/sandhi-planning-engine.js");
const result = [
  sandhi.classifySandhiBoundary("rāma", "iti"),
  sandhi.classifySandhiBoundary("namaḥ", "śiva"),
  sandhi.classifySandhiBoundary("saṃ", "kara"),
  sandhi.classifySandhiBoundary("tat", "tvam")
];
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

        self.assertEqual(
            payload,
            [
                "VOWEL_BOUNDARY",
                "VISARGA_BOUNDARY",
                "ANUSVARA_BOUNDARY",
                "CONSONANT_BOUNDARY",
            ],
        )

    def test_create_sandhi_planning_snapshot_is_candidate_only(self):
        script = """
const sandhi = require("./ui/tabs/sanskrit/sandhi-planning/sandhi-planning-engine.js");
const result = sandhi.createSandhiPlanningSnapshot({
  boundaries: [
    { id: "sandhi-1", left: "rāma", right: "iti" },
    { id: "sandhi-2", left: "namaḥ", right: "śiva" }
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-sandhi-planning.v1")
        self.assertEqual(payload["kind"], "SANDHI_PLANNING_SNAPSHOT")
        self.assertEqual(len(payload["boundaries"]), 2)
        self.assertEqual(payload["boundaries"][0]["type"], "VOWEL_BOUNDARY")
        self.assertTrue(payload["boundaries"][0]["planned"])
        self.assertFalse(payload["boundaries"][0]["executed"])
        self.assertTrue(payload["trace"]["replaySafe"])
        self.assertTrue(payload["trace"]["mutationFree"])
        self.assertEqual(payload["trace"]["boundaryCount"], 2)

    def test_sandhi_planning_diagnostics_contracts_are_satisfied(self):
        script = """
const sandhi = require("./ui/tabs/sanskrit/sandhi-planning/sandhi-planning-engine.js");
const result = sandhi.getSandhiPlanningDiagnostics();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-sandhi-planning.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contractsSatisfied"])
        self.assertEqual(payload["fieldCount"], 6)


if __name__ == "__main__":
    unittest.main()