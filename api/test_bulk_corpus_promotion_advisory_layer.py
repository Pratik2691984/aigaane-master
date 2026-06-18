import json
import subprocess
import unittest


class BulkCorpusPromotionAdvisoryTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_advisory_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/build_bulk_corpus_promotion_advisory.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["advisoryStatus"], "advisory-ready")
        self.assertEqual(data["recommendation"], "manual-review-ready")
        self.assertEqual(data["advisoryPacketCount"], 3)
        self.assertEqual(data["promotionConfidence"], 100)
        self.assertEqual(data["acceptedRecordCount"], 2000)
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["promotionAllowed"])
        self.assertFalse(data["advisoryExecutionAllowed"])

    def test_advisory_summary(self):
        data = self.run_json("""
const {
summarizeCorpusPromotionAdvisory
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-advisory-engine.js");

console.log(JSON.stringify(summarizeCorpusPromotionAdvisory({}, 250, 12.5)));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["advisoryStatus"], "advisory-ready")
        self.assertEqual(data["recommendation"], "manual-review-ready")
        self.assertEqual(data["advisoryPacketCount"], 3)

    def test_status_ready(self):
        data = self.run_json("""
const {
deriveAdvisoryStatus
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-advisory-engine.js");

console.log(JSON.stringify({
status: deriveAdvisoryStatus({
valid:true,
promotionStatus:"promotion-ready",
promotionConfidence:100,
promotionExecutionAllowed:false,
canonicalWriteAllowed:false,
promotionAllowed:false
})
}));
""")
        self.assertEqual(data["status"], "advisory-ready")

    def test_recommendation_hold(self):
        data = self.run_json("""
const {
derivePromotionRecommendation
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-advisory-engine.js");

console.log(JSON.stringify({
recommendation: derivePromotionRecommendation("advisory-blocked")
}));
""")
        self.assertEqual(data["recommendation"], "hold")

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusAdvisoryPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-advisory-renderer.js");

console.log(JSON.stringify(renderCorpusAdvisoryPanel({
state:"<bad>",
valid:false,
advisoryStatus:"<status>",
recommendation:"<recommendation>",
advisoryPackets:[
{packetId:"<id>",severity:"<sev>",message:"<msg>"}
]
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])
        self.assertIn("&lt;status&gt;", data["body"])
        self.assertIn("&lt;recommendation&gt;", data["body"])
        self.assertIn("&lt;msg&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()