import json
import subprocess
import unittest


class RuntimeUiGovernanceTests(unittest.TestCase):

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
createRuntimeUiGovernanceRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-governance-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiGovernanceRecord({})
));
""")
        self.assertEqual(data["state"], "UI_GOVERNANCE_READY")

    def test_governance_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiGovernanceEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-governance-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiGovernanceEntries({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-ui-governance", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiGovernanceRecord,
createRuntimeUiGovernanceRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-governance-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiGovernanceRecord(
createRuntimeUiGovernanceRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["uiGovernanceBlocked"])
        self.assertTrue(data["governanceBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiGovernancePanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-governance-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiGovernancePanel({
uiGovernanceStatus:"<a>",
uiGovernanceMode:"<b>",
sourceUiCertificationStatus:"<c>",
sourceUiCertificationMode:"<d>",
sourceCertificate:"<e>",
governanceEntries:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiGovernanceRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-governance-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiGovernanceRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()