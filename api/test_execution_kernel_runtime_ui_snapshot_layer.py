import json
import subprocess
import unittest


class RuntimeUiSnapshotTests(unittest.TestCase):

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
createRuntimeUiSnapshotRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-snapshot-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiSnapshotRecord({})
));
""")
        self.assertEqual(data["state"], "UI_SNAPSHOT_READY")

    def test_snapshots(self):
        data = self.run_json("""
const {
deriveRuntimeUiSnapshots
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-snapshot-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiSnapshots({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-ui-snapshot", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiSnapshotRecord,
createRuntimeUiSnapshotRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-snapshot-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiSnapshotRecord(
createRuntimeUiSnapshotRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["uiSnapshotBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiSnapshotPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-snapshot-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiSnapshotPanel({
uiSnapshotStatus:"<a>",
uiSnapshotMode:"<b>",
sourceControllerStatus:"<c>",
sourceControllerMode:"<d>",
sourceCertificate:"<e>",
snapshots:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiSnapshotRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-snapshot-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiSnapshotRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()