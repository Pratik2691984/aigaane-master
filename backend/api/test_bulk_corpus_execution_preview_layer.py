import json
import subprocess
import unittest


class BulkCorpusExecutionPreviewTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_execution_preview_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/preview_bulk_corpus_execution.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertTrue(data["previewOnly"])
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["queueExecutionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_ready_execution_preview(self):
        data = self.run_json("""
const {
summarizeCorpusExecutionPreview
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-execution-preview-engine.js");

console.log(JSON.stringify(summarizeCorpusExecutionPreview({
batches:[{
batchId:"b1",
lineage:"lineage-1",
records:[
{id:"d1",type:"dhatu",text:"भू",source:"source-1"},
{id:"s1",type:"sutra",text:"अदर्शनं लोपः",source:"source-2"}
]
}]
}, 1)));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["queueItemCount"], 2)
        self.assertEqual(data["estimatedSeconds"], 0.1)
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["queueExecutionAllowed"])

    def test_timeline_order(self):
        data = self.run_json("""
const {
previewCorpusExecution
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-execution-preview-engine.js");

console.log(JSON.stringify(previewCorpusExecution({
batches:[{
batchId:"b1",
lineage:"lineage-1",
records:[
{id:"d1",type:"dhatu",text:"भू",source:"source-1"}
]
}]
})));
""")
        self.assertEqual(data["timeline"][0]["queueId"], "queue-0001")
        self.assertEqual(data["timeline"][0]["queueOrder"], 1)
        self.assertEqual(data["timeline"][0]["startSecond"], 0)
        self.assertEqual(data["timeline"][0]["endSecond"], 0.05)

    def test_duplicate_skips_execution_item(self):
        data = self.run_json("""
const {
previewCorpusExecution
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-execution-preview-engine.js");

console.log(JSON.stringify(previewCorpusExecution({
batches:[{
batchId:"b1",
records:[
{id:"x",type:"dhatu",text:"भू",source:"source-1"},
{id:"x",type:"sutra",text:"सूत्र",source:"source-2"}
]
}]
})));
""")
        self.assertEqual(data["queueItemCount"], 1)

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusExecutionPreviewPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-execution-preview-renderer.js");

console.log(JSON.stringify(renderCorpusExecutionPreviewPanel({
state:"<bad>",
valid:false
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()