import json
import subprocess
import unittest


class RuntimeWorkspaceTests(unittest.TestCase):

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
createRuntimeWorkspaceRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-workspace-engine.js"
);

console.log(
JSON.stringify(
createRuntimeWorkspaceRecord({})
));
""")
        self.assertEqual(data["state"], "WORKSPACE_READY")

    def test_panels(self):
        data = self.run_json("""
const {
deriveRuntimeWorkspacePanels
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-workspace-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeWorkspacePanels({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-workspace", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeWorkspaceRecord,
createRuntimeWorkspaceRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-workspace-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeWorkspaceRecord(
createRuntimeWorkspaceRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["workspaceBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeWorkspacePanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-workspace-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeWorkspacePanel({
workspaceStatus:"<a>",
workspaceMode:"<b>",
sourceExplorerStatus:"<c>",
sourceExplorerMode:"<d>",
sourceCertificate:"<e>",
panels:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeWorkspaceRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-workspace-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeWorkspaceRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()