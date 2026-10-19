import json
import subprocess
import unittest


class RuntimeUiCertificationTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_create(self):
        data = self.run_json("""
const {
createRuntimeUiCertificationRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-certification-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiCertificationRecord({})
));
""")
        self.assertEqual(data["state"], "UI_CERTIFICATION_READY")

    def test_certification_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiCertificationEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-certification-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiCertificationEntries({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-ui-certification", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiCertificationRecord,
createRuntimeUiCertificationRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-certification-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiCertificationRecord(
createRuntimeUiCertificationRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["uiCertificationBlocked"])
        self.assertTrue(data["certificationBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiCertificationPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-certification-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiCertificationPanel({
uiCertificationStatus:"<a>",
uiCertificationMode:"<b>",
sourceUiAuditStatus:"<c>",
sourceUiAuditMode:"<d>",
sourceCertificate:"<e>",
certificationEntries:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiCertificationRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-certification-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiCertificationRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()