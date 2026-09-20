import json
import subprocess
import unittest


class LedgerSealTests(unittest.TestCase):

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
createRuntimeUiLedgerSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-ledger-seal-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiLedgerSealRecord({})
)
);
""")
        self.assertEqual(
            data["state"],
            "UI_LEDGER_SEAL_READY"
        )
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["publicationAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiLedgerSealEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-ledger-seal-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiLedgerSealEntries({
warnings:["x"]
})
)
);
""")
        self.assertIn("runtime-ui-ledger-surface", data)
        self.assertIn("ledger-evidence-immutable", data)
        self.assertIn("ledger-metadata-only", data)
        self.assertIn("warning-reference-ui-ledger", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiLedgerSealRecord,
createRuntimeUiLedgerSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-ledger-seal-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiLedgerSealRecord(
createRuntimeUiLedgerSealRecord({})
)
)
);
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["ledgerSealBlocked"])
        self.assertTrue(data["archiveSealBlocked"])
        self.assertTrue(data["importSealBlocked"])
        self.assertTrue(data["exportSealBlocked"])
        self.assertTrue(data["ledgerExecutionBlocked"])
        self.assertTrue(data["publicationBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiLedgerSealPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-ledger-seal-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiLedgerSealPanel({
uiLedgerSealStatus:"<x>",
uiLedgerSealMode:"<mode>",
sourceArchiveSealId:"<archive>",
ledgerSealEntries:["<y>"]
})
)
);
""")
        self.assertIn("&lt;x&gt;", data["body"])
        self.assertIn("&lt;y&gt;", data["body"])
        self.assertEqual(data["status"], "UI_LEDGER_SEAL_READY")

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiLedgerSealRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-ledger-seal-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiLedgerSealRecords(
{},
{}
)
)
);
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()