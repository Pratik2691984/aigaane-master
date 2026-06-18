import json
import subprocess
import unittest


class CertificationSealTests(unittest.TestCase):

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
createRuntimeUiCertificationSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-certification-seal-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiCertificationSealRecord({})
)
);
""")
        self.assertEqual(
            data["state"],
            "UI_CERTIFICATION_SEAL_READY"
        )
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiCertificationSealEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-certification-seal-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiCertificationSealEntries({
warnings:["x"]
})
)
);
""")
        self.assertIn("runtime-ui-certification-surface", data)
        self.assertIn("certification-evidence-immutable", data)
        self.assertIn("warning-reference-ui-certification", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiCertificationSealRecord,
createRuntimeUiCertificationSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-certification-seal-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiCertificationSealRecord(
createRuntimeUiCertificationSealRecord({})
)
)
);
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["certificationSealBlocked"])
        self.assertTrue(data["governanceSealBlocked"])
        self.assertTrue(data["auditSealBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["publicationBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiCertificationSealPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-certification-seal-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiCertificationSealPanel({
uiCertificationSealStatus:"<x>",
uiCertificationSealMode:"<mode>",
sourceGovernanceSealId:"<g>",
certificationSealEntries:["<y>"]
})
)
);
""")
        self.assertIn("&lt;x&gt;", data["body"])
        self.assertIn("&lt;y&gt;", data["body"])
        self.assertEqual(data["status"], "UI_CERTIFICATION_SEAL_READY")

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiCertificationSealRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-certification-seal-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiCertificationSealRecords(
{},
{}
)
)
);
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()