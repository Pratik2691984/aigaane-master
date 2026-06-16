import json
import subprocess
import unittest

ENGINE_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-snapshot-engine.js"
)

MAP_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-snapshot-map.js"
)

RENDERER_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-snapshot-renderer.js"
)


class RuntimeSnapshotTests(unittest.TestCase):

    def run_json(self, script):
        r = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        return json.loads(r.stdout)

    def test_syntax(self):
        subprocess.run(["node", "--check", MAP_FILE], check=True)
        subprocess.run(["node", "--check", ENGINE_FILE], check=True)
        subprocess.run(["node", "--check", RENDERER_FILE], check=True)

    def test_snapshot(self):
        data = self.run_json("""
const {
captureExecutionRuntimeSnapshot
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-snapshot-engine.js"
);

console.log(
JSON.stringify(
captureExecutionRuntimeSnapshot({})
)
);
""")
        self.assertEqual(data["executionMode"], "controlled")
        self.assertEqual(data["pipelineStage"], "unresolved")
        self.assertTrue(data["inspectionHash"])

    def test_compare(self):
        data = self.run_json("""
const {
compareExecutionRuntimeSnapshots
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-snapshot-engine.js"
);

console.log(
JSON.stringify(
compareExecutionRuntimeSnapshots(
{a:1},
{a:1}
)
)
);
""")
        self.assertTrue(data["stable"])

    def test_renderer_escapes_html(self):
        data = self.run_json("""
const {
renderExecutionRuntimeSnapshotPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-snapshot-renderer.js"
);

console.log(
JSON.stringify(
renderExecutionRuntimeSnapshotPanel({
executionMode:"<script>",
pipelineStage:"ready",
inspectionHash:"hash"
})
)
);
""")
        self.assertIn("&lt;script&gt;", data["body"])
        self.assertNotIn("<script>", data["body"])


if __name__ == "__main__":
    unittest.main()