import json
import subprocess
import unittest


class BulkCorpusSimulationTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_simulation_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/simulate_bulk_corpus_execution.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["simulationCount"], 8)
        self.assertEqual(data["totalRecords"], 2000)
        self.assertEqual(data["totalEstimatedSeconds"], 100.0)
        self.assertEqual(data["finalCompletionPercent"], 100.0)
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["simulationExecutionAllowed"])

    def test_build_snapshots(self):
        data = self.run_json("""
const {
buildSimulationSnapshots
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-simulation-engine.js");

console.log(JSON.stringify(buildSimulationSnapshots([
{
timelineId:"timeline-001",
windowId:"window-001",
order:1,
recordCount:250,
endSecond:12.5,
completionPercent:12.5
}
])));
""")
        self.assertEqual(data[0]["snapshotId"], "simulation-001")
        self.assertEqual(data[0]["status"], "simulated-complete")
        self.assertEqual(data[0]["elapsedSecond"], 12.5)

    def test_throughput(self):
        data = self.run_json("""
const {
estimateSimulationThroughput
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-simulation-engine.js");

console.log(JSON.stringify({
value: estimateSimulationThroughput(2000, 100)
}));
""")
        self.assertEqual(data["value"], 20)

    def test_summary(self):
        data = self.run_json("""
const {
summarizeCorpusSimulation
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-simulation-engine.js");

console.log(JSON.stringify(summarizeCorpusSimulation({}, 250, 12.5)));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["simulationCount"], 8)
        self.assertEqual(data["totalRecords"], 2000)
        self.assertEqual(data["finalCompletionPercent"], 100)
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusSimulationPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-simulation-renderer.js");

console.log(JSON.stringify(renderCorpusSimulationPanel({
state:"<bad>",
valid:false
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()