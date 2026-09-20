import json
import subprocess
import unittest


class BulkCorpusIntakeQueueTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_queue_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/build_bulk_corpus_intake_queue.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertTrue(data["previewOnly"])
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["queueExecutionAllowed"])

    def test_ready_queue(self):
        data = self.run_json("""
const {
summarizeCorpusIntakeQueue
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-intake-queue-engine.js");

console.log(JSON.stringify(summarizeCorpusIntakeQueue({
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
        self.assertFalse(data["queueExecutionAllowed"])

    def test_queue_items_have_order(self):
        data = self.run_json("""
const {
buildCorpusIntakeQueue
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-intake-queue-engine.js");

console.log(JSON.stringify(buildCorpusIntakeQueue({
batches:[{
batchId:"b1",
lineage:"lineage-1",
records:[
{id:"d1",type:"dhatu",text:"भू",source:"source-1"}
]
}]
})));
""")
        self.assertEqual(data["queueItems"][0]["queueId"], "queue-0001")
        self.assertEqual(data["queueItems"][0]["queueOrder"], 1)

    def test_duplicate_skips_queue_item(self):
        data = self.run_json("""
const {
buildCorpusIntakeQueue
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-intake-queue-engine.js");

console.log(JSON.stringify(buildCorpusIntakeQueue({
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
renderCorpusIntakeQueuePanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-intake-queue-renderer.js");

console.log(JSON.stringify(renderCorpusIntakeQueuePanel({
state:"<bad>",
valid:false
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()