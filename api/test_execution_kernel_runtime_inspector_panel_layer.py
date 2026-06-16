import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-inspector-panel.js"
)

class RuntimeInspectorPanelTests(unittest.TestCase):

    def run_json(self,script):
        r=subprocess.run(
            ["node","-e",script],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        return json.loads(r.stdout)

    def test_syntax(self):
        subprocess.run(["node","--check",FILE],check=True)

    def test_panel(self):
        data=self.run_json("""
const {
createRuntimeInspectorPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-inspector-panel.js"
);
console.log(JSON.stringify(createRuntimeInspectorPanel({})));
""")
        self.assertTrue(data["panel"]["visible"])
        self.assertTrue(data["panel"]["readOnly"])

    def test_capabilities_blocked(self):
        data=self.run_json("""
const {
createRuntimeInspectorPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-inspector-panel.js"
);
console.log(JSON.stringify(createRuntimeInspectorPanel({})));
""")
        self.assertFalse(data["capabilities"]["execute"])
        self.assertFalse(data["capabilities"]["canonicalWrite"])

    def test_inspector(self):
        data=self.run_json("""
const {
createRuntimeInspectorPanel,
inspectRuntimeInspectorPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-inspector-panel.js"
);
console.log(JSON.stringify(
inspectRuntimeInspectorPanel(createRuntimeInspectorPanel({}))
));
""")
        self.assertTrue(data["ready"])
        self.assertTrue(data["visible"])
        self.assertTrue(data["readOnly"])

if __name__=="__main__":
    unittest.main()