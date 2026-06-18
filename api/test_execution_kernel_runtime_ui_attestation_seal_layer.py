import json
import subprocess
import unittest


class AttestationSealTests(unittest.TestCase):

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
createRuntimeUiAttestationSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-attestation-seal-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiAttestationSealRecord({})
)
);
""")
        self.assertEqual(
            data["state"],
            "UI_ATTESTATION_SEAL_READY"
        )
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["publicationAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiAttestationSealEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-attestation-seal-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiAttestationSealEntries({
warnings:["x"]
})
)
);
""")
        self.assertIn("runtime-ui-attestation-surface", data)
        self.assertIn("attestation-evidence-immutable", data)
        self.assertIn("attestation-metadata-only", data)
        self.assertIn("warning-reference-ui-attestation", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiAttestationSealRecord,
createRuntimeUiAttestationSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-attestation-seal-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiAttestationSealRecord(
createRuntimeUiAttestationSealRecord({})
)
)
);
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["attestationSealBlocked"])
        self.assertTrue(data["provenanceSealBlocked"])
        self.assertTrue(data["integritySealBlocked"])
        self.assertTrue(data["registrySealBlocked"])
        self.assertTrue(data["attestationExecutionBlocked"])
        self.assertTrue(data["publicationBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiAttestationSealPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-attestation-seal-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiAttestationSealPanel({
uiAttestationSealStatus:"<x>",
uiAttestationSealMode:"<mode>",
sourceProvenanceSealId:"<provenance>",
attestationSealEntries:["<y>"]
})
)
);
""")
        self.assertIn("&lt;x&gt;", data["body"])
        self.assertIn("&lt;y&gt;", data["body"])
        self.assertEqual(data["status"], "UI_ATTESTATION_SEAL_READY")

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiAttestationSealRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-attestation-seal-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiAttestationSealRecords(
{},
{}
)
)
);
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()