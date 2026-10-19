import json
import subprocess
import unittest


class BulkCorpusAllocationTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_allocation_script_empty_manifest(self):
        import sys
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root / "scripts"))
        from plan_bulk_corpus_allocation import plan_bulk_corpus_allocation
        fixture = json.loads(
            (root / "data" / "sanskrit" / "corpus-staging" / "fixtures" / "empty_bulk_corpus_manifest.v1.json").read_text(encoding="utf-8")
        )
        if isinstance(fixture.get("batches"), dict):
            fixture = dict(fixture)
            fixture["batches"] = []
        data = plan_bulk_corpus_allocation(fixture)
        self.assertEqual(data["totalUsed"], 0)
        self.assertEqual(data["freeCapacity"], 2000)
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["allocationWriteAllowed"])
        self.assertFalse(data["promotionAllowed"])
        self.assertFalse(data["importAllowed"])
        self.assertFalse(data["executionAllowed"])

    def test_allocation_ready(self):
        data = self.run_json("""
const {
summarizeCorpusAllocation
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-allocation-engine.js");

console.log(JSON.stringify(summarizeCorpusAllocation({
batches:[{
batchId:"b1",
lineage:"lineage-1",
records:[
{id:"d1",type:"dhatu",text:"भू",source:"source-1"},
{id:"s1",type:"sutra",text:"अदर्शनं लोपः",source:"source-2"},
{id:"st1",type:"stotra",text:"शिवं शान्तम्",source:"source-3"}
]
}]
})));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["typeCounts"]["dhatu"], 1)
        self.assertEqual(data["typeCounts"]["sutra"], 1)
        self.assertEqual(data["typeCounts"]["stotra"], 1)
        self.assertEqual(data["freeCapacity"], 1997)

    def test_quota_warning(self):
        data = self.run_json("""
const {
summarizeCorpusAllocation
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-allocation-engine.js");

console.log(JSON.stringify(summarizeCorpusAllocation({
batches:[{
batchId:"b1",
records:[
{id:"d1",type:"dhatu",text:"भू",source:"source-1"},
{id:"d2",type:"dhatu",text:"गम्",source:"source-2"}
]
}]
}, {dhatu:1,sutra:1,stotra:1})));
""")
        self.assertTrue(data["valid"])
        self.assertIn("dhatu:quotaExceeded", data["warnings"])

    def test_allocation_exceeds_capacity(self):
        data = self.run_json("""
const {
summarizeCorpusAllocation
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-allocation-engine.js");

console.log(JSON.stringify(summarizeCorpusAllocation({}, {
dhatu:2000,
sutra:1,
stotra:1
})));
""")
        self.assertFalse(data["valid"])
        self.assertIn("allocationExceedsCapacity", data["errors"])

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusAllocationPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-allocation-renderer.js");

console.log(JSON.stringify(renderCorpusAllocationPanel({
state:"<bad>",
valid:false,
warnings:["<warn>"],
errors:["<err>"]
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])
        self.assertIn("&lt;warn&gt;", data["body"])
        self.assertIn("&lt;err&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()
