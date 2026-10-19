import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-ui-renderer.js"
)

class RuntimeUiRendererTests(unittest.TestCase):

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

    def test_renderer(self):
        data=self.run_json("""
const {
renderRuntimeUi
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-renderer.js"
);
console.log(JSON.stringify(renderRuntimeUi({})));
""")
        self.assertTrue(data["view"]["visible"])
        self.assertTrue(data["view"]["readOnly"])
        self.assertEqual(len(data["sections"]),2)

    def test_blocked_capabilities(self):
        data=self.run_json("""
const {
renderRuntimeUi
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-renderer.js"
);
console.log(JSON.stringify(renderRuntimeUi({})));
""")
        self.assertFalse(data["capabilities"]["execute"])
        self.assertFalse(data["capabilities"]["canonicalWrite"])

    def test_inspector(self):
        data=self.run_json("""
const {
renderRuntimeUi,
inspectRuntimeUiRenderer
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-renderer.js"
);
console.log(JSON.stringify(
inspectRuntimeUiRenderer(renderRuntimeUi({}))
));
""")
        self.assertTrue(data["ready"])
        self.assertEqual(data["sectionCount"],2)
        self.assertTrue(data["readOnly"])

if __name__=="__main__":
    unittest.main()