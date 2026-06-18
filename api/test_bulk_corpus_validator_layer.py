import json
import subprocess
import unittest


class BulkCorpusValidatorTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_validator_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/validate_bulk_corpus_records.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertTrue(data["previewOnly"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_valid_manifest(self):
        data = self.run_json("""
const {
validateBulkCorpusManifest
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-validator-engine.js");

console.log(JSON.stringify(validateBulkCorpusManifest({
batches:[{
batchId:"b1",
records:[
{id:"d1",type:"dhatu",text:"भू",source:"manual"},
{id:"s1",type:"sutra",text:"अदर्शनं लोपः",source:"manual"},
{id:"st1",type:"stotra",text:"शिवं शान्तम्",source:"manual"}
]
}]
})));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["recordCount"], 3)
        self.assertEqual(data["readinessScore"], 100)

    def test_missing_fields(self):
        data = self.run_json("""
const {
validateBulkCorpusManifest
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-validator-engine.js");

console.log(JSON.stringify(validateBulkCorpusManifest({
batches:[{batchId:"b1",records:[{id:"x"}]}]
})));
""")
        self.assertFalse(data["valid"])
        self.assertIn("b1:0:invalidType", data["errors"])
        self.assertIn("b1:0:missingText", data["errors"])
        self.assertIn("b1:0:missingSource", data["errors"])

    def test_duplicate_ids(self):
        data = self.run_json("""
const {
validateBulkCorpusManifest
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-validator-engine.js");

console.log(JSON.stringify(validateBulkCorpusManifest({
batches:[{batchId:"b1",records:[
{id:"x",type:"dhatu",text:"भू",source:"manual"},
{id:"x",type:"sutra",text:"x",source:"manual"}
]}]
})));
""")
        self.assertFalse(data["valid"])
        self.assertIn("x", data["duplicateIds"])
        self.assertIn("duplicateRecordIds", data["errors"])

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusValidatorPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-validator-renderer.js");

console.log(JSON.stringify(renderCorpusValidatorPanel({
state:"<bad>",
valid:false,
errors:["<err>"],
duplicateIds:["<dup>"]
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])
        self.assertIn("&lt;err&gt;", data["body"])
        self.assertIn("&lt;dup&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()