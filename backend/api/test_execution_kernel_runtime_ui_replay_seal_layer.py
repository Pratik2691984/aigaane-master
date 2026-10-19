import json
import subprocess
import unittest


class RuntimeUiReplaySealTests(unittest.TestCase):

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
createRuntimeUiReplaySealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-replay-seal-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiReplaySealRecord({})
));
""")
        self.assertEqual(data["state"], "UI_REPLAY_SEAL_READY")
        self.assertEqual(data["replaySealStatus"], "replay-seal-ready")
        self.assertEqual(data["replaySealMode"], "inspection-replay-seal")
        self.assertFalse(data["replaySealAllowed"])
        self.assertFalse(data["uiSnapshotSealAllowed"])
        self.assertFalse(data["uiSealAllowed"])
        self.assertFalse(data["controllerAllowed"])
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["mutationAllowed"])
        self.assertFalse(data["publicationAllowed"])
        self.assertFalse(data["rollbackAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_replay_seal_entries(self):
        data = self.run_json("""
const {
deriveRuntimeUiReplaySealEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-replay-seal-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiReplaySealEntries({
warnings:["x"]
})
));
""")
        self.assertIn("runtime-ui-replay-seal-surface", data)
        self.assertIn("runtime-ui-snapshot-seal-reference", data)
        self.assertIn("replay-seal-metadata-only", data)
        self.assertIn("replay-execution-denied", data)
        self.assertIn("canonical-write-denied", data)
        self.assertIn("warning-reference-ui-replay-seal", data)

    def test_read_only_blocked_diagnostics(self):
        data = self.run_json("""
const {
inspectRuntimeUiReplaySealRecord,
createRuntimeUiReplaySealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-replay-seal-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiReplaySealRecord(
createRuntimeUiReplaySealRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["replaySealBlocked"])
        self.assertTrue(data["replayExecutionBlocked"])
        self.assertTrue(data["snapshotSealBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["mutationBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer_escaping(self):
        data = self.run_json("""
const {
renderRuntimeUiReplaySealPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-replay-seal-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiReplaySealPanel({
replaySealStatus:"<a>",
replaySealMode:"<b>",
sourceUiSnapshotSealStatus:"<c>",
sourceUiSnapshotSealMode:"<d>",
sourceUiSealStatus:"<e>",
sourceCertificate:"<f>",
replaySealEntries:["<g>"],
warnings:["<h>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;g&gt;", data["body"])
        self.assertIn("&lt;h&gt;", data["body"])
        self.assertEqual(data["status"], "UI_REPLAY_SEAL_READY")

    def test_deterministic_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiReplaySealRecords,
createRuntimeUiReplaySealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-replay-seal-engine.js"
);

const a = createRuntimeUiReplaySealRecord({warnings:["x"]});
const b = createRuntimeUiReplaySealRecord({warnings:["x"]});

console.log(
JSON.stringify(
compareRuntimeUiReplaySealRecords(
a,
b
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()
