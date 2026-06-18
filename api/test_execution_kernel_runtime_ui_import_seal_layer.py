import json
import subprocess
import unittest


class ImportSealTests(unittest.TestCase):

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
createRuntimeUiImportSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-import-seal-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiImportSealRecord({})
)
);
""")
        self.assertEqual(
            data["state"],
            "UI_IMPORT_SEAL_READY"
        )
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["publicationAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiImportSealEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-import-seal-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiImportSealEntries({
warnings:["x"]
})
)
);
""")
        self.assertIn("runtime-ui-import-surface", data)
        self.assertIn("import-evidence-immutable", data)
        self.assertIn("import-metadata-only", data)
        self.assertIn("warning-reference-ui-import", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiImportSealRecord,
createRuntimeUiImportSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-import-seal-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiImportSealRecord(
createRuntimeUiImportSealRecord({})
)
)
);
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["importSealBlocked"])
        self.assertTrue(data["exportSealBlocked"])
        self.assertTrue(data["certificationSealBlocked"])
        self.assertTrue(data["governanceSealBlocked"])
        self.assertTrue(data["auditSealBlocked"])
        self.assertTrue(data["importExecutionBlocked"])
        self.assertTrue(data["publicationBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiImportSealPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-import-seal-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiImportSealPanel({
uiImportSealStatus:"<x>",
uiImportSealMode:"<mode>",
sourceExportSealId:"<export>",
importSealEntries:["<y>"]
})
)
);
""")
        self.assertIn("&lt;x&gt;", data["body"])
        self.assertIn("&lt;y&gt;", data["body"])
        self.assertEqual(data["status"], "UI_IMPORT_SEAL_READY")

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiImportSealRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-import-seal-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiImportSealRecords(
{},
{}
)
)
);
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()