import json
import subprocess
import unittest


class BulkCorpusProvenanceTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_audit_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/audit_bulk_corpus_provenance.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertTrue(data["previewOnly"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_valid_provenance(self):
        data = self.run_json("""
const {
auditCorpusProvenanceManifest
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-provenance-engine.js");

console.log(JSON.stringify(auditCorpusProvenanceManifest({
batches:[{
batchId:"b1",
source:"manual",
lineage:"lineage-1",
records:[
{id:"d1",type:"dhatu",text:"भू",source:"dhatu-source-1"},
{id:"s1",type:"sutra",text:"अदर्शनं लोपः",source:"sutra-source-1"}
]
}]
})));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["recordCount"], 2)
        self.assertEqual(data["confidenceScore"], 100)

    def test_duplicate_record_ids(self):
        data = self.run_json("""
const {
auditCorpusProvenanceManifest
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-provenance-engine.js");

console.log(JSON.stringify(auditCorpusProvenanceManifest({
batches:[{
batchId:"b1",
records:[
{id:"x",type:"dhatu",text:"भू",source:"src1"},
{id:"x",type:"sutra",text:"सूत्र",source:"src2"}
]
}]
})));
""")
        self.assertFalse(data["valid"])
        self.assertIn("x", data["duplicateRecordIds"])
        self.assertIn("duplicateRecordIds", data["errors"])

    def test_missing_provenance_source(self):
        data = self.run_json("""
const {
auditCorpusProvenanceManifest
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-provenance-engine.js");

console.log(JSON.stringify(auditCorpusProvenanceManifest({
batches:[{
batchId:"b1",
records:[
{id:"x",type:"dhatu",text:"भू"}
]
}]
})));
""")
        self.assertFalse(data["valid"])
        self.assertIn("b1:0:missingSource", data["errors"])

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusProvenancePanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-provenance-renderer.js");

console.log(JSON.stringify(renderCorpusProvenancePanel({
state:"<bad>",
valid:false,
errors:["<err>"],
warnings:["<warn>"],
duplicateRecordIds:["<dup>"]
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])
        self.assertIn("&lt;err&gt;", data["body"])
        self.assertIn("&lt;warn&gt;", data["body"])
        self.assertIn("&lt;dup&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()