import json
import subprocess
import unittest


class RuntimeUiIntegrityTests(unittest.TestCase):

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
createRuntimeUiIntegrityRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-integrity-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiIntegrityRecord({})
));
""")
        self.assertEqual(data["state"], "UI_INTEGRITY_READY")

    def test_integrity_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiIntegrityEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-integrity-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiIntegrityEntries({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-ui-integrity", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiIntegrityRecord,
createRuntimeUiIntegrityRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-integrity-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiIntegrityRecord(
createRuntimeUiIntegrityRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["uiIntegrityBlocked"])
        self.assertTrue(data["integrityBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiIntegrityPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-integrity-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiIntegrityPanel({
uiIntegrityStatus:"<a>",
uiIntegrityMode:"<b>",
sourceUiGovernanceStatus:"<c>",
sourceUiGovernanceMode:"<d>",
sourceCertificate:"<e>",
integrityEntries:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiIntegrityRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-integrity-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiIntegrityRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()