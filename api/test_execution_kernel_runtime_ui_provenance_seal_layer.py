import json
import subprocess
import unittest


class ProvenanceSealTests(unittest.TestCase):

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
createRuntimeUiProvenanceSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-provenance-seal-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiProvenanceSealRecord({})
)
);
""")
        self.assertEqual(
            data["state"],
            "UI_PROVENANCE_SEAL_READY"
        )
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["publicationAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiProvenanceSealEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-provenance-seal-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiProvenanceSealEntries({
warnings:["x"]
})
)
);
""")
        self.assertIn("runtime-ui-provenance-surface", data)
        self.assertIn("provenance-evidence-immutable", data)
        self.assertIn("provenance-metadata-only", data)
        self.assertIn("warning-reference-ui-provenance", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiProvenanceSealRecord,
createRuntimeUiProvenanceSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-provenance-seal-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiProvenanceSealRecord(
createRuntimeUiProvenanceSealRecord({})
)
)
);
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["provenanceSealBlocked"])
        self.assertTrue(data["integritySealBlocked"])
        self.assertTrue(data["registrySealBlocked"])
        self.assertTrue(data["evidenceSealBlocked"])
        self.assertTrue(data["provenanceExecutionBlocked"])
        self.assertTrue(data["publicationBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiProvenanceSealPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-provenance-seal-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiProvenanceSealPanel({
uiProvenanceSealStatus:"<x>",
uiProvenanceSealMode:"<mode>",
sourceIntegritySealId:"<integrity>",
provenanceSealEntries:["<y>"]
})
)
);
""")
        self.assertIn("&lt;x&gt;", data["body"])
        self.assertIn("&lt;y&gt;", data["body"])
        self.assertEqual(data["status"], "UI_PROVENANCE_SEAL_READY")

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiProvenanceSealRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-provenance-seal-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiProvenanceSealRecords(
{},
{}
)
)
);
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()