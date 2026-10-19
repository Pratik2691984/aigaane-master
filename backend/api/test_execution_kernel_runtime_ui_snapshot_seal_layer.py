import json
import subprocess
import unittest


class RuntimeUiSnapshotSealTests(unittest.TestCase):

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
createRuntimeUiSnapshotSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-snapshot-seal-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiSnapshotSealRecord({})
));
""")
        self.assertEqual(data["state"], "UI_SNAPSHOT_SEAL_READY")
        self.assertEqual(data["uiSnapshotSealStatus"], "ui-snapshot-seal-ready")
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_snapshot_seal_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiSnapshotSealEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-snapshot-seal-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiSnapshotSealEntries({
warnings:["x"]
})
));
""")
        self.assertIn("runtime-ui-snapshot-seal-surface", data)
        self.assertIn("ui-snapshot-seal-immutable", data)
        self.assertIn("warning-reference-ui-snapshot-seal", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiSnapshotSealRecord,
createRuntimeUiSnapshotSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-snapshot-seal-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiSnapshotSealRecord(
createRuntimeUiSnapshotSealRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["immutableSnapshotSeal"])
        self.assertTrue(data["uiSnapshotSealBlocked"])
        self.assertTrue(data["uiSealBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiSnapshotSealPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-snapshot-seal-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiSnapshotSealPanel({
uiSnapshotSealStatus:"<a>",
uiSnapshotSealMode:"<b>",
sourceUiSealStatus:"<c>",
sourceUiSealMode:"<d>",
sourceCertificate:"<e>",
snapshotSealEntries:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])
        self.assertEqual(data["status"], "UI_SNAPSHOT_SEAL_READY")

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiSnapshotSealRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-snapshot-seal-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiSnapshotSealRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()