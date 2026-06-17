import json
import subprocess
import unittest


class RuntimeUiReplayTests(unittest.TestCase):

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
createRuntimeUiReplayRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-replay-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiReplayRecord({})
));
""")
        self.assertEqual(data["state"], "UI_REPLAY_READY")

    def test_replay_frames(self):
        data = self.run_json("""
const {
deriveRuntimeUiReplayFrames
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-replay-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiReplayFrames({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-ui-replay", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeUiReplayRecord,
createRuntimeUiReplayRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-replay-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiReplayRecord(
createRuntimeUiReplayRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["uiReplayBlocked"])
        self.assertTrue(data["replayBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeUiReplayPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-replay-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiReplayPanel({
uiReplayStatus:"<a>",
uiReplayMode:"<b>",
sourceUiSnapshotStatus:"<c>",
sourceUiSnapshotMode:"<d>",
sourceCertificate:"<e>",
replayFrames:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeUiReplayRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-replay-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiReplayRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()