import json
import subprocess
import unittest


class RuntimePanelTests(unittest.TestCase):

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
createRuntimePanelRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-panel-engine.js"
);

console.log(
JSON.stringify(
createRuntimePanelRecord({})
));
""")
        self.assertEqual(data["state"], "PANEL_READY")

    def test_sections(self):
        data = self.run_json("""
const {
deriveRuntimePanelSections
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-panel-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimePanelSections({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-panel", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimePanelRecord,
createRuntimePanelRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-panel-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimePanelRecord(
createRuntimePanelRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["panelBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimePanelPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-panel-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimePanelPanel({
panelStatus:"<a>",
panelMode:"<b>",
sourceViewStatus:"<c>",
sourceViewMode:"<d>",
sourceCertificate:"<e>",
sections:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimePanelRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-panel-engine.js"
);

console.log(
JSON.stringify(
compareRuntimePanelRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()