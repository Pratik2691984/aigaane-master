import json
import subprocess
import unittest


class EvidenceSealTests(unittest.TestCase):

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
createRuntimeUiEvidenceSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-evidence-seal-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiEvidenceSealRecord({})
)
);
""")
        self.assertEqual(
            data["state"],
            "UI_EVIDENCE_SEAL_READY"
        )
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["publicationAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiEvidenceSealEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-evidence-seal-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiEvidenceSealEntries({
warnings:["x"]
})
)
);
""")
        self.assertIn("runtime-ui-evidence-surface", data)
        self.assertIn("evidence-chain-immutable", data)
        self.assertIn("evidence-metadata-only", data)
        self.assertIn("warning-reference-ui-evidence", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiEvidenceSealRecord,
createRuntimeUiEvidenceSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-evidence-seal-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiEvidenceSealRecord(
createRuntimeUiEvidenceSealRecord({})
)
)
);
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["evidenceSealBlocked"])
        self.assertTrue(data["ledgerSealBlocked"])
        self.assertTrue(data["archiveSealBlocked"])
        self.assertTrue(data["importSealBlocked"])
        self.assertTrue(data["evidenceExecutionBlocked"])
        self.assertTrue(data["publicationBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiEvidenceSealPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-evidence-seal-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiEvidenceSealPanel({
uiEvidenceSealStatus:"<x>",
uiEvidenceSealMode:"<mode>",
sourceLedgerSealId:"<ledger>",
evidenceSealEntries:["<y>"]
})
)
);
""")
        self.assertIn("&lt;x&gt;", data["body"])
        self.assertIn("&lt;y&gt;", data["body"])
        self.assertEqual(data["status"], "UI_EVIDENCE_SEAL_READY")

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiEvidenceSealRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-evidence-seal-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiEvidenceSealRecords(
{},
{}
)
)
);
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()