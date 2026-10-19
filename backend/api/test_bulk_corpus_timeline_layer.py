import json
import subprocess
import unittest


class BulkCorpusTimelineTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_timeline_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/build_bulk_corpus_timeline.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["timelineCount"], 8)
        self.assertEqual(data["totalEstimatedSeconds"], 100.0)
        self.assertEqual(data["finalCompletionPercent"], 100.0)
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["timelineExecutionAllowed"])

    def test_build_timeline_from_schedule(self):
        data = self.run_json("""
const {
buildTimelineFromSchedule
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-timeline-engine.js");

console.log(JSON.stringify(buildTimelineFromSchedule([
{
scheduleId:"schedule-001",
windowId:"window-001",
windowOrder:1,
recordCount:250,
startSecond:0,
endSecond:12.5,
completionPercent:12.5
}
])));
""")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["timelineId"], "timeline-001")
        self.assertEqual(data[0]["durationSecond"], 12.5)

    def test_markers(self):
        data = self.run_json("""
const {
buildTimelineMarkers
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-timeline-engine.js");

console.log(JSON.stringify(buildTimelineMarkers([
{
timelineId:"timeline-001",
order:1,
endSecond:12.5,
completionPercent:12.5
}
])));
""")
        self.assertEqual(data[0]["markerId"], "marker-001")
        self.assertEqual(data[0]["atSecond"], 12.5)

    def test_summary(self):
        data = self.run_json("""
const {
summarizeCorpusTimeline
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-timeline-engine.js");

console.log(JSON.stringify(summarizeCorpusTimeline({}, 250, 12.5)));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["timelineCount"], 8)
        self.assertEqual(data["finalCompletionPercent"], 100)
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusTimelinePanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-timeline-renderer.js");

console.log(JSON.stringify(renderCorpusTimelinePanel({
state:"<bad>",
valid:false
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()