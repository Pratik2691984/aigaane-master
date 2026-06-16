import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-closeout-renderer.js"
)

class CloseoutRendererTests(
unittest.TestCase
):

    def run_json(
        self,
        script
    ):
        r=subprocess.run(
            ["node","-e",script],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        return json.loads(
            r.stdout
        )

    def test_syntax(self):

        subprocess.run(
            ["node","--check",FILE],
            check=True
        )

    def test_render_entry(self):

        result=self.run_json("""
const {
normalizeRenderEntry
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-closeout-renderer.js"
);

console.log(
JSON.stringify(
normalizeRenderEntry({
id:"x"
},0)
));
""")

        self.assertTrue(
            result["visible"]
        )

        self.assertFalse(
            result["executed"]
        )

    def test_renderer(self):

        result=self.run_json("""
const {
createExecutionKernelCloseoutRenderer
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-closeout-renderer.js"
);

console.log(
JSON.stringify(
createExecutionKernelCloseoutRenderer({
entries:[
{id:"a"},
{id:"b"}
]
})
));
""")

        self.assertEqual(
            result["render"]["renderCount"],
            2
        )

    def test_renderer_diagnostics(self):

        result=self.run_json("""
const {
buildExecutionKernelCloseoutRenderer,
getExecutionKernelCloseoutRendererDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-closeout-renderer.js"
);

console.log(
JSON.stringify(
getExecutionKernelCloseoutRendererDiagnostics(
buildExecutionKernelCloseoutRenderer({})
)
));
""")

        self.assertTrue(
            result["ready"]
        )

if __name__=="__main__":
    unittest.main()