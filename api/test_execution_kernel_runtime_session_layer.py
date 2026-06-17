import json
import subprocess
import unittest


class RuntimeSessionTests(unittest.TestCase):

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
createRuntimeSessionRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-session-engine.js"
);

console.log(
JSON.stringify(
createRuntimeSessionRecord({})
));
""")
        self.assertEqual(data["state"], "SESSION_READY")

    def test_frames(self):
        data = self.run_json("""
const {
deriveRuntimeSessionFrames
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-session-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeSessionFrames({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-session", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeSessionRecord,
createRuntimeSessionRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-session-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeSessionRecord(
createRuntimeSessionRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["sessionBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeSessionPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-session-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeSessionPanel({
sessionStatus:"<a>",
sessionMode:"<b>",
sourceWorkspaceStatus:"<c>",
sourceWorkspaceMode:"<d>",
sourceCertificate:"<e>",
frames:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeSessionRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-session-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeSessionRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()