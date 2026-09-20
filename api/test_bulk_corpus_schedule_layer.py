import json
import subprocess
import unittest


class BulkCorpusScheduleTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_schedule_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/plan_bulk_corpus_schedule.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["scheduleCount"], 8)
        self.assertEqual(data["totalEstimatedSeconds"], 100.0)
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["scheduleExecutionAllowed"])

    def test_build_schedule_from_windows(self):
        data = self.run_json("""
const {
buildScheduleFromWindows
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-schedule-engine.js");

console.log(JSON.stringify(buildScheduleFromWindows([
{windowId:"window-001",windowOrder:1,recordCount:250},
{windowId:"window-002",windowOrder:2,recordCount:250}
], 10)));
""")
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["scheduleId"], "schedule-001")
        self.assertEqual(data[0]["startSecond"], 0)
        self.assertEqual(data[0]["endSecond"], 10)
        self.assertEqual(data[1]["completionPercent"], 100)

    def test_summary(self):
        data = self.run_json("""
const {
summarizeCorpusSchedule
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-schedule-engine.js");

console.log(JSON.stringify(summarizeCorpusSchedule({}, 250, 12.5)));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["scheduleCount"], 8)
        self.assertEqual(data["totalEstimatedSeconds"], 100)
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_custom_window_seconds(self):
        data = self.run_json("""
const {
summarizeCorpusSchedule
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-schedule-engine.js");

console.log(JSON.stringify(summarizeCorpusSchedule({}, 500, 20)));
""")
        self.assertEqual(data["scheduleCount"], 4)
        self.assertEqual(data["totalEstimatedSeconds"], 80)

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusSchedulePanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-schedule-renderer.js");

console.log(JSON.stringify(renderCorpusSchedulePanel({
state:"<bad>",
valid:false
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()