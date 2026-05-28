import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH_MAP = ROOT / "ui" / "tabs" / "sanskrit" / "derivation-graph-planning" / "derivation-graph-planning-map.js"
GRAPH_ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "derivation-graph-planning" / "derivation-graph-planning-engine.js"


class TestDerivationGraphPlanningLayer(unittest.TestCase):
    def test_derivation_graph_planning_files_are_syntax_valid(self):
        for path in (GRAPH_MAP, GRAPH_ENGINE):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_derivation_graph_planning_export_is_runtime_safe_and_normalized(self):
        script = """
const graph = require("./ui/tabs/sanskrit/derivation-graph-planning/derivation-graph-planning-engine.js");
const result = graph.buildDerivationGraphPlanningExport();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-derivation-graph-planning.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contracts"]["deterministic"])
        self.assertTrue(payload["contracts"]["immutable"])
        self.assertTrue(payload["contracts"]["inspectionOnly"])
        self.assertTrue(payload["contracts"]["nonPerformative"])
        self.assertTrue(payload["contracts"]["nonMutating"])
        self.assertTrue(payload["contracts"]["schedulerLinked"])
        self.assertTrue(payload["contracts"]["queueLinked"])
        self.assertTrue(payload["contracts"]["traceLinked"])
        self.assertTrue(payload["contracts"]["checkpointLinked"])
        self.assertTrue(payload["contracts"]["sandhiPlanningLinked"])
        self.assertTrue(payload["contracts"]["morphologyPlanningLinked"])
        self.assertTrue(payload["contracts"]["lakaraPlanningLinked"])
        self.assertTrue(payload["contracts"]["executionGuardLinked"])
        self.assertTrue(payload["contracts"]["replaySafe"])
        self.assertTrue(payload["contracts"]["runtimeIsolated"])
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
        self.assertTrue(payload["diagnostics"]["sandhiPlanningLinked"])
        self.assertTrue(payload["diagnostics"]["morphologyPlanningLinked"])
        self.assertTrue(payload["diagnostics"]["lakaraPlanningLinked"])
        self.assertTrue(payload["diagnostics"]["executionGuardLinked"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["graphOnly"])

    def test_create_derivation_graph_planning_snapshot_is_graph_only(self):
        script = """
const graph = require("./ui/tabs/sanskrit/derivation-graph-planning/derivation-graph-planning-engine.js");
const result = graph.createDerivationGraphPlanningSnapshot({
  nodes: [
    { id: "node-dhatu", type: "DHATU", referenceId: "dhatu.gam" },
    { id: "node-morphology", type: "MORPHOLOGY", referenceId: "morphology.snapshot.1" },
    { id: "node-lakara", type: "LAKARA", referenceId: "lakara.snapshot.1" },
    { id: "node-sandhi", type: "SANDHI", referenceId: "sandhi.snapshot.1" }
  ],
  edges: [
    { id: "edge-1", from: "node-dhatu", to: "node-morphology", relation: "PLANS" },
    { id: "edge-2", from: "node-morphology", to: "node-lakara", relation: "PLANS" },
    { id: "edge-3", from: "node-lakara", to: "node-sandhi", relation: "PLANS" }
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-derivation-graph-planning.v1")
        self.assertEqual(payload["kind"], "DERIVATION_GRAPH_PLANNING_SNAPSHOT")
        self.assertEqual(len(payload["nodes"]), 4)
        self.assertEqual(len(payload["edges"]), 3)
        self.assertEqual(payload["nodes"][0]["type"], "DHATU")
        self.assertEqual(payload["edges"][0]["from"], "node-dhatu")
        self.assertTrue(payload["nodes"][0]["planned"])
        self.assertFalse(payload["nodes"][0]["executed"])
        self.assertTrue(payload["edges"][0]["planned"])
        self.assertFalse(payload["edges"][0]["executed"])
        self.assertTrue(payload["trace"]["replaySafe"])
        self.assertTrue(payload["trace"]["mutationFree"])
        self.assertEqual(payload["trace"]["nodeCount"], 4)
        self.assertEqual(payload["trace"]["edgeCount"], 3)

    def test_derivation_graph_planning_diagnostics_contracts_are_satisfied(self):
        script = """
const graph = require("./ui/tabs/sanskrit/derivation-graph-planning/derivation-graph-planning-engine.js");
const result = graph.getDerivationGraphPlanningDiagnostics();
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

        self.assertEqual(payload["schemaVersion"], "sanskrit-derivation-graph-planning.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contractsSatisfied"])
        self.assertEqual(payload["fieldCount"], 6)


if __name__ == "__main__":
    unittest.main()