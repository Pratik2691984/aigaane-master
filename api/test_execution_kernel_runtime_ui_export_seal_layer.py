import json
import subprocess
import unittest


class ExportSealTests(unittest.TestCase):

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
createRuntimeUiExportSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-export-seal-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiExportSealRecord({})
)
);
""")
        self.assertEqual(
            data["state"],
            "UI_EXPORT_SEAL_READY"
        )
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["publicationAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiExportSealEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-export-seal-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiExportSealEntries({
warnings:["x"]
})
)
);
""")
        self.assertIn("runtime-ui-export-surface", data)
        self.assertIn("export-evidence-immutable", data)
        self.assertIn("export-metadata-only", data)
        self.assertIn("warning-reference-ui-export", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiExportSealRecord,
createRuntimeUiExportSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-export-seal-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiExportSealRecord(
createRuntimeUiExportSealRecord({})
)
)
);
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["exportSealBlocked"])
        self.assertTrue(data["certificationSealBlocked"])
        self.assertTrue(data["governanceSealBlocked"])
        self.assertTrue(data["auditSealBlocked"])
        self.assertTrue(data["exportExecutionBlocked"])
        self.assertTrue(data["publicationBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiExportSealPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-export-seal-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiExportSealPanel({
uiExportSealStatus:"<x>",
uiExportSealMode:"<mode>",
sourceCertificationSealId:"<cert>",
exportSealEntries:["<y>"]
})
)
);
""")
        self.assertIn("&lt;x&gt;", data["body"])
        self.assertIn("&lt;y&gt;", data["body"])
        self.assertEqual(data["status"], "UI_EXPORT_SEAL_READY")

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiExportSealRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-export-seal-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiExportSealRecords(
{},
{}
)
)
);
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()