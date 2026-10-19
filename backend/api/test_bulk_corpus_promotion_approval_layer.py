import json
import subprocess
import unittest


class BulkCorpusPromotionApprovalTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_approval_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/build_bulk_corpus_promotion_approval.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["approvalStatus"], "approval-ready")
        self.assertEqual(data["approvalLedgerCount"], 3)
        self.assertEqual(data["recommendation"], "manual-review-ready")
        self.assertEqual(data["acceptedRecordCount"], 2000)
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["promotionAllowed"])
        self.assertFalse(data["approvalExecutionAllowed"])

    def test_approval_summary(self):
        data = self.run_json("""
const {
summarizeCorpusPromotionApproval
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-approval-engine.js");

console.log(JSON.stringify(summarizeCorpusPromotionApproval({}, 250, 12.5)));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["approvalStatus"], "approval-ready")
        self.assertEqual(data["approvalLedgerCount"], 3)
        self.assertEqual(data["recommendation"], "manual-review-ready")

    def test_status_ready(self):
        data = self.run_json("""
const {
deriveApprovalStatus
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-approval-engine.js");

console.log(JSON.stringify({
status: deriveApprovalStatus({
valid:true,
advisoryStatus:"advisory-ready",
recommendation:"manual-review-ready",
advisoryExecutionAllowed:false,
canonicalWriteAllowed:false,
promotionAllowed:false
})
}));
""")
        self.assertEqual(data["status"], "approval-ready")

    def test_status_blocked(self):
        data = self.run_json("""
const {
deriveApprovalStatus
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-approval-engine.js");

console.log(JSON.stringify({
status: deriveApprovalStatus({
valid:false
})
}));
""")
        self.assertEqual(data["status"], "approval-blocked")

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusApprovalPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-approval-renderer.js");

console.log(JSON.stringify(renderCorpusApprovalPanel({
state:"<bad>",
valid:false,
approvalStatus:"<status>",
recommendation:"<recommendation>",
approvalLedger:[
{approvalId:"<id>",status:"<status>",message:"<msg>"}
]
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])
        self.assertIn("&lt;recommendation&gt;", data["body"])
        self.assertIn("&lt;msg&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()