import json
import subprocess
import unittest


class BulkCorpusForecastTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_forecast_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/build_bulk_corpus_forecast.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["forecastStatus"], "forecast-ready")
        self.assertEqual(data["totalRecords"], 2000)
        self.assertEqual(data["projectedFinishSecond"], 100.0)
        self.assertEqual(data["projectedThroughputPerSecond"], 20.0)
        self.assertTrue(data["importReadinessForecast"])
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["forecastExecutionAllowed"])

    def test_forecast_summary(self):
        data = self.run_json("""
const {
summarizeCorpusForecast
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-forecast-engine.js");

console.log(JSON.stringify(summarizeCorpusForecast({}, 250, 12.5)));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["forecastStatus"], "forecast-ready")
        self.assertEqual(data["totalRecords"], 2000)
        self.assertEqual(data["projectedCompletionPercent"], 100)
        self.assertTrue(data["importReadinessForecast"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_status_ready(self):
        data = self.run_json("""
const {
deriveForecastStatus
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-forecast-engine.js");

console.log(JSON.stringify({
status: deriveForecastStatus({
valid:true,
finalCompletionPercent:100,
simulationExecutionAllowed:false,
canonicalWriteAllowed:false
})
}));
""")
        self.assertEqual(data["status"], "forecast-ready")

    def test_status_blocked(self):
        data = self.run_json("""
const {
deriveForecastStatus
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-forecast-engine.js");

console.log(JSON.stringify({
status: deriveForecastStatus({
valid:false
})
}));
""")
        self.assertEqual(data["status"], "forecast-blocked")

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusForecastPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-forecast-renderer.js");

console.log(JSON.stringify(renderCorpusForecastPanel({
state:"<bad>",
valid:false,
forecastStatus:"<status>"
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])
        self.assertIn("&lt;status&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()