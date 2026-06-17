import json
import subprocess
import unittest


class RuntimeControllerTests(unittest.TestCase):

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
createRuntimeControllerRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-controller-engine.js"
);

console.log(
JSON.stringify(
createRuntimeControllerRecord({})
));
""")
        self.assertEqual(data["state"], "CONTROLLER_READY")

    def test_bindings(self):
        data = self.run_json("""
const {
deriveRuntimeControllerBindings
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-controller-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeControllerBindings({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-controller", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeControllerRecord,
createRuntimeControllerRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-controller-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeControllerRecord(
createRuntimeControllerRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["controllerBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeControllerPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-controller-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeControllerPanel({
controllerStatus:"<a>",
controllerMode:"<b>",
sourcePanelStatus:"<c>",
sourcePanelMode:"<d>",
sourceCertificate:"<e>",
bindings:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeControllerRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-controller-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeControllerRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()