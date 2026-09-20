import json
import subprocess
import unittest


class RuntimeUiAuditSealTests(unittest.TestCase):

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
createRuntimeUiAuditSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-audit-seal-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiAuditSealRecord({})
));
""")
        self.assertEqual(data["state"], "UI_AUDIT_SEAL_READY")
        self.assertEqual(data["uiAuditSealStatus"], "ui-audit-seal-ready")
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_audit_seal_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiAuditSealEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-audit-seal-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiAuditSealEntries({
warnings:["x"]
})
));
""")
        self.assertIn("runtime-ui-audit-seal-surface", data)
        self.assertIn("runtime-audit-evidence-reference", data)
        self.assertIn("warning-reference-ui-audit-seal", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiAuditSealRecord,
createRuntimeUiAuditSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-audit-seal-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiAuditSealRecord(
createRuntimeUiAuditSealRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["immutableAuditSeal"])
        self.assertTrue(data["auditSealBlocked"])
        self.assertTrue(data["replaySealBlocked"])
        self.assertTrue(data["snapshotSealBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiAuditSealPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-audit-seal-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiAuditSealPanel({
uiAuditSealStatus:"<a>",
uiAuditSealMode:"<b>",
sourceUiReplaySealStatus:"<c>",
sourceUiReplaySealId:"<d>",
sourceUiSnapshotSealId:"<e>",
sourceUiSealId:"<f>",
auditSealEntries:["<g>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;g&gt;", data["body"])
        self.assertEqual(data["status"], "UI_AUDIT_SEAL_READY")

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiAuditSealRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-audit-seal-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiAuditSealRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()