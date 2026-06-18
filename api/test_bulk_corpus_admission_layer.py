import json
import subprocess
import unittest


class BulkCorpusAdmissionTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_admission_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/build_bulk_corpus_admission.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["admissionStatus"], "admission-ready")
        self.assertEqual(data["acceptedRecordCount"], 2000)
        self.assertEqual(data["rejectedRecordCount"], 0)
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["admissionExecutionAllowed"])

    def test_admission_summary(self):
        data = self.run_json("""
const {
summarizeCorpusAdmission
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-admission-engine.js");

console.log(JSON.stringify(summarizeCorpusAdmission({}, 250, 12.5)));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["admissionStatus"], "admission-ready")
        self.assertEqual(data["acceptedRecordCount"], 2000)
        self.assertIn("forecastReady", data["admissionReasons"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_status_ready(self):
        data = self.run_json("""
const {
deriveAdmissionStatus
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-admission-engine.js");

console.log(JSON.stringify({
status: deriveAdmissionStatus({
valid:true,
importReadinessForecast:true,
forecastExecutionAllowed:false,
canonicalWriteAllowed:false
})
}));
""")
        self.assertEqual(data["status"], "admission-ready")

    def test_status_blocked(self):
        data = self.run_json("""
const {
deriveAdmissionStatus
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-admission-engine.js");

console.log(JSON.stringify({
status: deriveAdmissionStatus({
valid:false
})
}));
""")
        self.assertEqual(data["status"], "admission-blocked")

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusAdmissionPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-admission-renderer.js");

console.log(JSON.stringify(renderCorpusAdmissionPanel({
state:"<bad>",
valid:false,
admissionStatus:"<status>",
admissionReasons:["<reason>"],
rejectionReasons:["<reject>"]
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])
        self.assertIn("&lt;status&gt;", data["body"])
        self.assertIn("&lt;reason&gt;", data["body"])
        self.assertIn("&lt;reject&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()