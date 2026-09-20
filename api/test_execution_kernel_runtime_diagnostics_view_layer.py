import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-diagnostics-view.js"
)

class RuntimeDiagnosticsViewTests(unittest.TestCase):

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

    def test_diagnostics_view(self):
        data=self.run_json("""
const {
createRuntimeDiagnosticsView
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-diagnostics-view.js"
);
console.log(JSON.stringify(createRuntimeDiagnosticsView({})));
""")
        self.assertTrue(data["view"]["visible"])
        self.assertTrue(data["diagnostics"]["ready"])

    def test_capabilities_blocked(self):
        data=self.run_json("""
const {
createRuntimeDiagnosticsView
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-diagnostics-view.js"
);
console.log(JSON.stringify(createRuntimeDiagnosticsView({})));
""")
        self.assertFalse(data["capabilities"]["execute"])
        self.assertFalse(data["capabilities"]["canonicalWrite"])

    def test_inspector(self):
        data=self.run_json("""
const {
createRuntimeDiagnosticsView,
inspectRuntimeDiagnosticsView
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-diagnostics-view.js"
);
console.log(JSON.stringify(
inspectRuntimeDiagnosticsView(createRuntimeDiagnosticsView({}))
));
""")
        self.assertTrue(data["ready"])
        self.assertTrue(data["visible"])

if __name__=="__main__":
    unittest.main()