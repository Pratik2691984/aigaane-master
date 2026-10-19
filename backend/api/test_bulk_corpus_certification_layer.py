import json
import subprocess
import unittest


class BulkCorpusCertificationTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_certification_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/build_bulk_corpus_certification.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["certificationStatus"], "certification-ready")
        self.assertEqual(data["certificationLedgerCount"], 3)
        self.assertEqual(data["acceptedRecordCount"], 2000)
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["promotionAllowed"])
        self.assertFalse(data["certificationExecutionAllowed"])

    def test_certification_summary(self):
        data = self.run_json("""
const {
summarizeCorpusCertification
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-certification-engine.js");

console.log(JSON.stringify(summarizeCorpusCertification({}, 250, 12.5)));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["certificationStatus"], "certification-ready")
        self.assertEqual(data["certificationLedgerCount"], 3)

    def test_status_ready(self):
        data = self.run_json("""
const {
deriveCertificationStatus
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-certification-engine.js");

console.log(JSON.stringify({
status: deriveCertificationStatus({
valid:true,
approvalStatus:"approval-ready",
recommendation:"manual-review-ready",
approvalExecutionAllowed:false,
canonicalWriteAllowed:false,
promotionAllowed:false
})
}));
""")
        self.assertEqual(data["status"], "certification-ready")

    def test_status_blocked(self):
        data = self.run_json("""
const {
deriveCertificationStatus
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-certification-engine.js");

console.log(JSON.stringify({
status: deriveCertificationStatus({
valid:false
})
}));
""")
        self.assertEqual(data["status"], "certification-blocked")

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusCertificationPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-certification-renderer.js");

console.log(JSON.stringify(renderCorpusCertificationPanel({
state:"<bad>",
valid:false,
certificationStatus:"<status>",
recommendation:"<recommendation>",
certificationLedger:[
{certificationId:"<id>",status:"<status>",message:"<msg>"}
]
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])
        self.assertIn("&lt;recommendation&gt;", data["body"])
        self.assertIn("&lt;msg&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()