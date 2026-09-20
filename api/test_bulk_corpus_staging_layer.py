import json
import subprocess
import unittest


class BulkCorpusStagingTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_manifest_script_validates(self):
        result = subprocess.run(
            ["python", "scripts/validate_bulk_corpus_staging.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertTrue(data["previewOnly"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_preview_empty_manifest(self):
        data = self.run_json("""
const {
createCorpusStagingPreview
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-staging-engine.js");

console.log(JSON.stringify(createCorpusStagingPreview({})));
""")
        self.assertTrue(data["valid"])
        self.assertTrue(data["previewOnly"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_duplicate_detection(self):
        data = self.run_json("""
const {
findDuplicateCorpusRecordIds
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-staging-engine.js");

console.log(JSON.stringify(findDuplicateCorpusRecordIds({
batches:[
{batchId:"b1",records:[{id:"dhatu-1"},{id:"dhatu-1"}]}
]
})));
""")
        self.assertIn("dhatu-1", data)

    def test_limit_exceeded(self):
        data = self.run_json("""
const {
inspectCorpusStagingManifest
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-staging-engine.js");

const records = Array.from({length:2001}, (_, i) => ({id:"r-"+i}));

console.log(JSON.stringify(inspectCorpusStagingManifest({
batches:[{batchId:"b1",records}]
})));
""")
        self.assertFalse(data["valid"])
        self.assertIn("recordLimitExceeded", data["errors"])

    def test_renderer_escapes_html(self):
        data = self.run_json("""
const {
renderCorpusStagingPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-staging-renderer.js");

console.log(JSON.stringify(renderCorpusStagingPanel({
state:"<x>",
valid:false,
errors:["<bad>"],
duplicateIds:["<dup>"]
})));
""")
        self.assertIn("&lt;x&gt;", data["body"])
        self.assertIn("&lt;bad&gt;", data["body"])
        self.assertIn("&lt;dup&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()