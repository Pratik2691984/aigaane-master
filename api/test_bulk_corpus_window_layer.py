import json
import subprocess
import unittest


class BulkCorpusWindowTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_window_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/plan_bulk_corpus_windows.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["windowSize"], 250)
        self.assertEqual(data["windowCount"], 8)
        self.assertEqual(data["totalReserved"], 2000)
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["windowExecutionAllowed"])

    def test_build_windows(self):
        data = self.run_json("""
const {
buildCorpusWindows
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-window-engine.js");

console.log(JSON.stringify(buildCorpusWindows(2000, 250)));
""")
        self.assertEqual(len(data), 8)
        self.assertEqual(data[0]["windowId"], "window-001")
        self.assertEqual(data[0]["startIndex"], 0)
        self.assertEqual(data[0]["endIndex"], 250)
        self.assertEqual(data[7]["endIndex"], 2000)

    def test_partial_window(self):
        data = self.run_json("""
const {
buildCorpusWindows
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-window-engine.js");

console.log(JSON.stringify(buildCorpusWindows(501, 250)));
""")
        self.assertEqual(len(data), 3)
        self.assertEqual(data[2]["recordCount"], 1)

    def test_summary(self):
        data = self.run_json("""
const {
summarizeCorpusWindows
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-window-engine.js");

console.log(JSON.stringify(summarizeCorpusWindows({}, 250)));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["windowCount"], 8)
        self.assertEqual(data["totalReserved"], 2000)
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusWindowPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-window-renderer.js");

console.log(JSON.stringify(renderCorpusWindowPanel({
state:"<bad>",
valid:false
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()