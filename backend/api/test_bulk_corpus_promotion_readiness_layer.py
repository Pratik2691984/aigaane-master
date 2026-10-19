import json
import subprocess
import unittest


class BulkCorpusPromotionReadinessTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_promotion_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/build_bulk_corpus_promotion_readiness.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["promotionStatus"], "promotion-ready")
        self.assertEqual(data["promotionConfidence"], 100)
        self.assertEqual(data["acceptedRecordCount"], 2000)
        self.assertEqual(data["rejectedRecordCount"], 0)
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["promotionExecutionAllowed"])
        self.assertFalse(data["promotionAllowed"])

    def test_promotion_summary(self):
        data = self.run_json("""
const {
summarizeCorpusPromotionReadiness
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-promotion-engine.js");

console.log(JSON.stringify(summarizeCorpusPromotionReadiness({}, 250, 12.5)));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["promotionStatus"], "promotion-ready")
        self.assertEqual(data["promotionConfidence"], 100)
        self.assertIn("promotionPreviewReady", data["advisory"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_status_ready(self):
        data = self.run_json("""
const {
derivePromotionStatus
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-promotion-engine.js");

console.log(JSON.stringify({
status: derivePromotionStatus({
valid:true,
admissionStatus:"admission-ready",
acceptedRecordCount:2000,
rejectedRecordCount:0,
canonicalWriteAllowed:false,
promotionAllowed:false
})
}));
""")
        self.assertEqual(data["status"], "promotion-ready")

    def test_status_blocked(self):
        data = self.run_json("""
const {
derivePromotionStatus
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-promotion-engine.js");

console.log(JSON.stringify({
status: derivePromotionStatus({
valid:false
})
}));
""")
        self.assertEqual(data["status"], "promotion-blocked")

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusPromotionPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-promotion-renderer.js");

console.log(JSON.stringify(renderCorpusPromotionPanel({
state:"<bad>",
valid:false,
promotionStatus:"<status>",
advisory:["<advice>"],
blockers:["<blocker>"]
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])
        self.assertIn("&lt;status&gt;", data["body"])
        self.assertIn("&lt;advice&gt;", data["body"])
        self.assertIn("&lt;blocker&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()