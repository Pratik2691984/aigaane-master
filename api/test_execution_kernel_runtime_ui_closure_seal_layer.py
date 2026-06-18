import json
import subprocess
import unittest


class ClosureSealTests(unittest.TestCase):

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
createRuntimeUiClosureSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-closure-seal-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiClosureSealRecord({})
)
);
""")
        self.assertEqual(
            data["state"],
            "UI_CLOSURE_SEAL_READY"
        )
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["publicationAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiClosureSealEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-closure-seal-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiClosureSealEntries({
warnings:["x"]
})
)
);
""")
        self.assertIn("runtime-ui-closure-surface", data)
        self.assertIn("closure-evidence-immutable", data)
        self.assertIn("closure-metadata-only", data)
        self.assertIn("warning-reference-ui-closure", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiClosureSealRecord,
createRuntimeUiClosureSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-closure-seal-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiClosureSealRecord(
createRuntimeUiClosureSealRecord({})
)
)
);
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["closureSealBlocked"])
        self.assertTrue(data["attestationSealBlocked"])
        self.assertTrue(data["provenanceSealBlocked"])
        self.assertTrue(data["integritySealBlocked"])
        self.assertTrue(data["closureExecutionBlocked"])
        self.assertTrue(data["publicationBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiClosureSealPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-closure-seal-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiClosureSealPanel({
uiClosureSealStatus:"<x>",
uiClosureSealMode:"<mode>",
sourceAttestationSealId:"<attestation>",
closureSealEntries:["<y>"]
})
)
);
""")
        self.assertIn("&lt;x&gt;", data["body"])
        self.assertIn("&lt;y&gt;", data["body"])
        self.assertEqual(data["status"], "UI_CLOSURE_SEAL_READY")

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiClosureSealRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-closure-seal-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiClosureSealRecords(
{},
{}
)
)
);
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()