import json
import subprocess
import unittest


class BulkCorpusReadinessTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_readiness_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/compute_bulk_corpus_readiness.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertTrue(data["promotionEligible"])
        self.assertTrue(data["previewOnly"])
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["promotionAllowed"])

    def test_ready_manifest(self):
        data = self.run_json("""
const {
summarizeCorpusReadiness
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-readiness-engine.js");

console.log(JSON.stringify(summarizeCorpusReadiness({
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
        self.assertTrue(data["promotionEligible"])
        self.assertEqual(data["readinessScore"], 100)
        self.assertEqual(data["recordCount"], 2)

    def test_blocked_duplicate(self):
        data = self.run_json("""
const {
summarizeCorpusReadiness
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-readiness-engine.js");

console.log(JSON.stringify(summarizeCorpusReadiness({
batches:[{
batchId:"b1",
records:[
{id:"x",type:"dhatu",text:"भू",source:"source-1"},
{id:"x",type:"sutra",text:"सूत्र",source:"source-2"}
]
}]
})));
""")
        self.assertFalse(data["valid"])
        self.assertFalse(data["promotionEligible"])
        self.assertIn("validator:duplicateRecordIds", data["errors"])

    def test_blocked_missing_source(self):
        data = self.run_json("""
const {
summarizeCorpusReadiness
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-readiness-engine.js");

console.log(JSON.stringify(summarizeCorpusReadiness({
batches:[{
batchId:"b1",
records:[
{id:"x",type:"dhatu",text:"भू"}
]
}]
})));
""")
        self.assertFalse(data["valid"])
        self.assertFalse(data["promotionEligible"])
        self.assertIn("validator:b1:0:missingSource", data["errors"])

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusReadinessPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-readiness-renderer.js");

console.log(JSON.stringify(renderCorpusReadinessPanel({
state:"<bad>",
valid:false,
promotionEligible:false,
errors:["<err>"],
warnings:["<warn>"]
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])
        self.assertIn("&lt;err&gt;", data["body"])
        self.assertIn("&lt;warn&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()