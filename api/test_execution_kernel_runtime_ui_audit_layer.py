import json
import subprocess
import unittest


class RuntimeUiAuditTests(unittest.TestCase):

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
createRuntimeUiAuditRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-audit-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiAuditRecord({})
));
""")
        self.assertEqual(data["state"], "UI_AUDIT_READY")

    def test_audit_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiAuditEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-audit-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiAuditEntries({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-ui-audit", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiAuditRecord,
createRuntimeUiAuditRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-audit-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiAuditRecord(
createRuntimeUiAuditRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["uiAuditBlocked"])
        self.assertTrue(data["auditBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiAuditPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-audit-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiAuditPanel({
uiAuditStatus:"<a>",
uiAuditMode:"<b>",
sourceUiReplayStatus:"<c>",
sourceUiReplayMode:"<d>",
sourceCertificate:"<e>",
auditEntries:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiAuditRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-audit-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiAuditRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()