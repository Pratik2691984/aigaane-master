import json
import subprocess
import unittest


class BulkCorpusCanonicalTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_canonical_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/preview_bulk_corpus_canonical.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["canonicalStatus"], "canonical-preview-ready")
        self.assertEqual(data["canonicalLedgerCount"], 3)
        self.assertEqual(data["acceptedRecordCount"], 2000)
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["promotionAllowed"])
        self.assertFalse(data["canonicalExecutionAllowed"])

    def test_canonical_summary(self):
        data = self.run_json("""
const {
summarizeCorpusCanonicalPreview
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-canonical-engine.js");

console.log(JSON.stringify(summarizeCorpusCanonicalPreview({}, 250, 12.5)));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["canonicalStatus"], "canonical-preview-ready")
        self.assertEqual(data["canonicalLedgerCount"], 3)

    def test_status_ready(self):
        data = self.run_json("""
const {
deriveCanonicalStatus
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-canonical-engine.js");

console.log(JSON.stringify({
status: deriveCanonicalStatus({
valid:true,
certificationStatus:"certification-ready",
certificationExecutionAllowed:false,
canonicalWriteAllowed:false,
promotionAllowed:false
})
}));
""")
        self.assertEqual(data["status"], "canonical-preview-ready")

    def test_status_blocked(self):
        data = self.run_json("""
const {
deriveCanonicalStatus
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-canonical-engine.js");

console.log(JSON.stringify({
status: deriveCanonicalStatus({
valid:false
})
}));
""")
        self.assertEqual(data["status"], "canonical-preview-blocked")

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusCanonicalPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-canonical-renderer.js");

console.log(JSON.stringify(renderCorpusCanonicalPanel({
state:"<bad>",
valid:false,
canonicalStatus:"<status>",
recommendation:"<recommendation>",
canonicalLedger:[
{canonicalId:"<id>",status:"<status>",message:"<msg>"}
]
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])
        self.assertIn("&lt;recommendation&gt;", data["body"])
        self.assertIn("&lt;msg&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()