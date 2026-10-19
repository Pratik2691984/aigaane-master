import json
import subprocess
import unittest

MAP_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-replay-map.js"
)

ENGINE_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-replay-engine.js"
)

RENDERER_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-replay-renderer.js"
)


class RuntimeReplayLayerTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        return json.loads(result.stdout)

    def test_syntax(self):
        subprocess.run(["node", "--check", MAP_FILE], check=True)
        subprocess.run(["node", "--check", ENGINE_FILE], check=True)
        subprocess.run(["node", "--check", RENDERER_FILE], check=True)

    def test_replay_plan_is_blocked(self):
        data = self.run_json("""
const {
createRuntimeReplayPlan
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-replay-engine.js"
);

console.log(JSON.stringify(
createRuntimeReplayPlan(
{snapshotId:"a", inspectionHash:"h1", pipelineStage:"one"},
{snapshotId:"b", inspectionHash:"h2", pipelineStage:"two"}
)
));
""")
        self.assertFalse(data["replayAllowed"])
        self.assertEqual(data["state"], "BLOCKED")

    def test_replay_detects_changes(self):
        data = self.run_json("""
const {
deriveRuntimeReplaySteps
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-replay-engine.js"
);

console.log(JSON.stringify(
deriveRuntimeReplaySteps(
{pipelineStage:"one", transformCount:1},
{pipelineStage:"two", transformCount:2}
)
));
""")
        fields = [step["field"] for step in data]
        self.assertIn("pipelineStage", fields)
        self.assertIn("transformCount", fields)

    def test_replay_is_read_only(self):
        data = self.run_json("""
const {
createRuntimeReplayPlan,
inspectRuntimeReplayPlan
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-replay-engine.js"
);

console.log(JSON.stringify(
inspectRuntimeReplayPlan(
createRuntimeReplayPlan(
{inspectionHash:"h1"},
{inspectionHash:"h2"}
)
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["mutationBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])
        self.assertFalse(data["replayAllowed"])

    def test_renderer_escapes_html(self):
        data = self.run_json("""
const {
renderRuntimeReplayPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-replay-renderer.js"
);

console.log(JSON.stringify(
renderRuntimeReplayPanel({
replayMode:"<script>",
sourceHash:"h1",
targetHash:"h2",
stepCount:1,
steps:[{
field:"pipelineStage",
from:"<old>",
to:"<new>",
action:"inspect-change"
}],
warnings:["<blocked>"]
})
));
""")
        self.assertIn("&lt;script&gt;", data["body"])
        self.assertIn("&lt;old&gt;", data["body"])
        self.assertIn("&lt;blocked&gt;", data["body"])
        self.assertNotIn("<script>", data["body"])


if __name__ == "__main__":
    unittest.main()