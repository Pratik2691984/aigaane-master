import json
import subprocess
import unittest


class BulkCorpusImportPreviewTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_import_preview_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/preview_bulk_corpus_import.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertTrue(data["previewOnly"])
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["importAllowed"])

    def test_ready_import_preview(self):
        data = self.run_json("""
const {
summarizeCorpusImportPreview
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-import-preview-engine.js");

console.log(JSON.stringify(summarizeCorpusImportPreview({
batches:[{
batchId:"b1",
lineage:"lineage-1",
records:[
{id:"d1",type:"dhatu",text:"भू",source:"source-1"},
{id:"s1",type:"sutra",text:"अदर्शनं लोपः",source:"source-2"}
]
}]
})));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["recordCount"], 2)
        self.assertEqual(data["estimatedInsertCount"], 2)
        self.assertEqual(data["estimatedSkipCount"], 0)
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["importAllowed"])

    def test_duplicate_import_preview(self):
        data = self.run_json("""
const {
summarizeCorpusImportPreview
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-import-preview-engine.js");

console.log(JSON.stringify(summarizeCorpusImportPreview({
batches:[{
batchId:"b1",
records:[
{id:"x",type:"dhatu",text:"भू",source:"source-1"},
{id:"x",type:"sutra",text:"सूत्र",source:"source-2"}
]
}]
})));
""")
        self.assertEqual(data["estimatedInsertCount"], 1)
        self.assertEqual(data["estimatedSkipCount"], 1)
        self.assertIn("x", data["duplicateIds"])
        self.assertFalse(data["importAllowed"])

    def test_missing_id_skips(self):
        data = self.run_json("""
const {
summarizeCorpusImportPreview
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-import-preview-engine.js");

console.log(JSON.stringify(summarizeCorpusImportPreview({
batches:[{
batchId:"b1",
records:[
{type:"dhatu",text:"भू",source:"source-1"}
]
}]
})));
""")
        self.assertEqual(data["estimatedInsertCount"], 0)
        self.assertEqual(data["estimatedSkipCount"], 1)

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusImportPreviewPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-import-preview-renderer.js");

console.log(JSON.stringify(renderCorpusImportPreviewPanel({
state:"<bad>",
valid:false,
duplicateIds:["<dup>"]
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])
        self.assertIn("&lt;dup&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()