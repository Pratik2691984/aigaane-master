import json
import subprocess
import unittest


class BulkCorpusCapacityTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_capacity_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/plan_bulk_corpus_capacity.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["recordCount"], 0)
        self.assertEqual(data["remainingCapacity"], 2000)
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_capacity_ready(self):
        data = self.run_json("""
const {
summarizeCorpusCapacity
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-capacity-engine.js");

console.log(JSON.stringify(summarizeCorpusCapacity({
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
        self.assertEqual(data["recordCount"], 2)
        self.assertEqual(data["remainingCapacity"], 1998)
        self.assertEqual(data["projectedBatchCount"], 2)
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_utilization_percent(self):
        data = self.run_json("""
const {
computeUtilizationPercent
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-capacity-engine.js");

console.log(JSON.stringify({
value: computeUtilizationPercent(1000, 2000)
}));
""")
        self.assertEqual(data["value"], 50)

    def test_projected_batches(self):
        data = self.run_json("""
const {
computeProjectedBatchCount
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-capacity-engine.js");

console.log(JSON.stringify({
value: computeProjectedBatchCount(501, 250)
}));
""")
        self.assertEqual(data["value"], 3)

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusCapacityPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-capacity-renderer.js");

console.log(JSON.stringify(renderCorpusCapacityPanel({
state:"<bad>",
valid:false
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()