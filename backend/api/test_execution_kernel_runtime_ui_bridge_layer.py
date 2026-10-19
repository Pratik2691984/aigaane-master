import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-ui-bridge.js"
)

class RuntimeUiBridgeTests(unittest.TestCase):

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

    def test_ui_bridge(self):
        data=self.run_json("""
const {
createRuntimeUiBridge
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-bridge.js"
);
console.log(JSON.stringify(createRuntimeUiBridge({})));
""")
        self.assertTrue(data["ui"]["visible"])
        self.assertTrue(data["ui"]["readOnly"])

    def test_capabilities_blocked(self):
        data=self.run_json("""
const {
createRuntimeUiBridge
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-bridge.js"
);
console.log(JSON.stringify(createRuntimeUiBridge({})));
""")
        self.assertFalse(data["capabilities"]["execute"])
        self.assertFalse(data["capabilities"]["canonicalWrite"])

    def test_inspector(self):
        data=self.run_json("""
const {
createRuntimeUiBridge,
inspectRuntimeUiBridge
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-bridge.js"
);
console.log(JSON.stringify(
inspectRuntimeUiBridge(createRuntimeUiBridge({}))
));
""")
        self.assertTrue(data["ready"])
        self.assertTrue(data["readOnly"])

if __name__=="__main__":
    unittest.main()