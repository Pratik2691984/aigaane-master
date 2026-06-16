import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRAKRIYA_MAP = ROOT / "ui" / "tabs" / "sanskrit" / "prakriya-planning" / "prakriya-planning-map.js"
PRAKRIYA_ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "prakriya-planning" / "prakriya-planning-engine.js"


class TestPrakriyaPlanningLayer(unittest.TestCase):
    def test_prakriya_planning_files_are_syntax_valid(self):
        for path in (PRAKRIYA_MAP, PRAKRIYA_ENGINE):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_prakriya_planning_export_is_runtime_safe_and_normalized(self):
        script = """
const prakriya = require("./ui/tabs/sanskrit/prakriya-planning/prakriya-planning-engine.js");
const result = prakriya.buildPrakriyaPlanningExport();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-prakriya-planning.v1")
        self.assertTrue(payload["ready"])
        self.assertEqual(payload["fieldCount"], 6)
        self.assertTrue(payload["contracts"]["deterministic"])
        self.assertTrue(payload["contracts"]["immutable"])
        self.assertTrue(payload["contracts"]["inspectionOnly"])
        self.assertTrue(payload["contracts"]["nonPerformative"])
        self.assertTrue(payload["contracts"]["nonMutating"])
        self.assertTrue(payload["contracts"]["runtimeIsolated"])
        self.assertTrue(payload["contracts"]["derivationGraphLinked"])

        self.assertTrue(payload["diagnostics"]["normalized"])
        self.assertTrue(payload["diagnostics"]["deterministic"])
        self.assertTrue(payload["diagnostics"]["replaySafe"])
        self.assertTrue(payload["diagnostics"]["derivationGraphLinked"])
        self.assertTrue(payload["diagnostics"]["sandhiPlanningLinked"])
        self.assertTrue(payload["diagnostics"]["morphologyPlanningLinked"])
        self.assertTrue(payload["diagnostics"]["lakaraPlanningLinked"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["planningOnly"])

        orders = [field["order"] for field in payload["fields"]]
        self.assertEqual(orders, sorted(orders))

    def test_create_prakriya_planning_snapshot_orders_stages(self):
        script = """
const prakriya = require("./ui/tabs/sanskrit/prakriya-planning/prakriya-planning-engine.js");
const result = prakriya.createPrakriyaPlanningSnapshot({
  stages: [
    { id: "sandhi-stage", type: "SANDHI_STAGE", order: 40, referenceId: "sandhi.snapshot.1" },
    { id: "dhatu-stage", type: "DHATU_STAGE", order: 10, referenceId: "dhatu.gam" },
    { id: "lakara-stage", type: "LAKARA_STAGE", order: 30, referenceId: "lakara.snapshot.1" },
    { id: "morphology-stage", type: "MORPHOLOGY_STAGE", order: 20, referenceId: "morphology.snapshot.1" }
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-prakriya-planning.v1")
        self.assertEqual(payload["kind"], "PRAKRIYA_PLANNING_SNAPSHOT")
        self.assertEqual(
            [stage["id"] for stage in payload["stages"]],
            ["dhatu-stage", "morphology-stage", "lakara-stage", "sandhi-stage"],
        )
        self.assertTrue(payload["stages"][0]["planned"])
        self.assertFalse(payload["stages"][0]["executed"])
        self.assertTrue(payload["trace"]["replaySafe"])
        self.assertTrue(payload["trace"]["mutationFree"])
        self.assertEqual(payload["trace"]["stageCount"], 4)

    def test_prakriya_planning_diagnostics_contracts_are_satisfied(self):
        script = """
const prakriya = require("./ui/tabs/sanskrit/prakriya-planning/prakriya-planning-engine.js");
const result = prakriya.getPrakriyaPlanningDiagnostics();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-prakriya-planning.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contractsSatisfied"])
        self.assertEqual(payload["fieldCount"], 6)


if __name__ == "__main__":
    unittest.main()