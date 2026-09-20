import json
import subprocess
import unittest


class BulkCorpusIntakeTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_intake_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/prepare_bulk_corpus_intake.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertTrue(data["previewOnly"])
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["importAllowed"])

    def test_ready_intake(self):
        data = self.run_json("""
const {
summarizeCorpusIntake
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-intake-engine.js");

console.log(JSON.stringify(summarizeCorpusIntake({
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
        self.assertEqual(data["sourceRecordCount"], 2)
        self.assertEqual(data["intakeRecordCount"], 2)
        self.assertEqual(data["skippedRecordCount"], 0)
        self.assertEqual(data["intakeBatchCount"], 2)

    def test_duplicate_is_skipped(self):
        data = self.run_json("""
const {
prepareCorpusIntake
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-intake-engine.js");

console.log(JSON.stringify(prepareCorpusIntake({
batches:[{
batchId:"b1",
records:[
{id:"x",type:"dhatu",text:"भू",source:"source-1"},
{id:"x",type:"sutra",text:"सूत्र",source:"source-2"}
]
}]
})));
""")
        self.assertEqual(data["intakeRecordCount"], 1)
        self.assertEqual(data["skippedRecordCount"], 1)
        self.assertEqual(data["skippedRecords"][0]["skipReason"], "duplicateId")

    def test_missing_id_is_skipped(self):
        data = self.run_json("""
const {
prepareCorpusIntake
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-intake-engine.js");

console.log(JSON.stringify(prepareCorpusIntake({
batches:[{
batchId:"b1",
records:[
{type:"dhatu",text:"भू",source:"source-1"}
]
}]
})));
""")
        self.assertEqual(data["intakeRecordCount"], 0)
        self.assertEqual(data["skippedRecordCount"], 1)
        self.assertEqual(data["skippedRecords"][0]["skipReason"], "missingId")

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusIntakePanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-intake-renderer.js");

console.log(JSON.stringify(renderCorpusIntakePanel({
state:"<bad>",
valid:false
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()