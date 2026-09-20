import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-execution-renderer.js"
)

class ExecutionRendererTests(
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

    def test_renderer(self):

        data=self.run_json("""
const {
createExecutionRenderer
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-execution-renderer.js"
);

console.log(
JSON.stringify(
createExecutionRenderer({
inspector:{
inspections:[
{id:"i1"},
{id:"i2"}
],
diagnostics:{
ready:true
}
}
})
));
""")

        self.assertEqual(
            len(data["panels"]),
            2
        )

    def test_render_blocked(self):

        data=self.run_json("""
const {
createExecutionRenderer
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-execution-renderer.js"
);

console.log(
JSON.stringify(
createExecutionRenderer({})
)
);
""")

        self.assertTrue(
            data["renderState"]["executionBlocked"]
        )

    def test_diagnostics(self):

        data=self.run_json("""
const {
createExecutionRenderer,
getExecutionRendererDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-execution-renderer.js"
);

console.log(
JSON.stringify(
getExecutionRendererDiagnostics(
createExecutionRenderer({})
)
));
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()