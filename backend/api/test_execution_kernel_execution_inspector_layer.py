import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-execution-inspector.js"
)

class ExecutionInspectorTests(
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

    def test_build(self):

        data=self.run_json("""
const {
createExecutionInspector
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-execution-inspector.js"
);

console.log(
JSON.stringify(
createExecutionInspector({
inspections:[
{id:"i1"},
{id:"i2"}
]
})
));
""")

        self.assertEqual(
            len(data["inspections"]),
            2
        )

        self.assertFalse(
            data["capabilities"]["execute"]
        )

    def test_mutation_blocked(self):

        data=self.run_json("""
const {
createExecutionInspector
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-execution-inspector.js"
);

console.log(
JSON.stringify(
createExecutionInspector({})
)
);
""")

        self.assertFalse(
            data["capabilities"]["mutate"]
        )

    def test_diagnostics(self):

        data=self.run_json("""
const {
createExecutionInspector,
getExecutionInspectorDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-execution-inspector.js"
);

console.log(
JSON.stringify(
getExecutionInspectorDiagnostics(
createExecutionInspector({})
)
));
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()