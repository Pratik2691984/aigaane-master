import json
import subprocess
import unittest


class RuntimeUiAssuranceTests(unittest.TestCase):

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
createRuntimeUiAssuranceRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-assurance-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiAssuranceRecord({})
));
""")
        self.assertEqual(data["state"], "UI_ASSURANCE_READY")

    def test_assurance_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiAssuranceEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-assurance-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiAssuranceEntries({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-ui-assurance", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiAssuranceRecord,
createRuntimeUiAssuranceRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-assurance-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiAssuranceRecord(
createRuntimeUiAssuranceRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["uiAssuranceBlocked"])
        self.assertTrue(data["assuranceBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiAssurancePanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-assurance-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiAssurancePanel({
uiAssuranceStatus:"<a>",
uiAssuranceMode:"<b>",
sourceUiIntegrityStatus:"<c>",
sourceUiIntegrityMode:"<d>",
sourceCertificate:"<e>",
assuranceEntries:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiAssuranceRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-assurance-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiAssuranceRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()