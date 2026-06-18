import json
import subprocess
import unittest


class RuntimeUiSealTests(unittest.TestCase):

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
createRuntimeUiSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-seal-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiSealRecord({})
));
""")
        self.assertEqual(data["state"], "UI_SEAL_READY")

    def test_seal_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiSealEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-seal-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiSealEntries({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-ui-seal", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiSealRecord,
createRuntimeUiSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-seal-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiSealRecord(
createRuntimeUiSealRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["uiSealBlocked"])
        self.assertTrue(data["sealBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiSealPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-seal-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiSealPanel({
uiSealStatus:"<a>",
uiSealMode:"<b>",
sourceUiAssuranceStatus:"<c>",
sourceUiAssuranceMode:"<d>",
sourceCertificate:"<e>",
sealEntries:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiSealRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-seal-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiSealRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()