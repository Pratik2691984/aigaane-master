import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-closeout-index.js"
)

class RuntimeCloseoutTests(
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

    def test_entry(self):

        result=self.run_json("""
const {
normalizeCloseoutEntry
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-closeout-index.js"
);

console.log(
JSON.stringify(
normalizeCloseoutEntry({
id:"x"
},0)
));
""")

        self.assertFalse(
            result["closed"]
        )

    def test_index(self):

        result=self.run_json("""
const {
createExecutionKernelRuntimeCloseoutIndex
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-closeout-index.js"
);

console.log(
JSON.stringify(
createExecutionKernelRuntimeCloseoutIndex({
entries:[
{id:"a"},
{id:"b"}
]
})
));
""")

        self.assertEqual(
            result["summary"]["entryCount"],
            2
        )

    def test_diagnostics(self):

        result=self.run_json("""
const {
buildExecutionKernelRuntimeCloseoutIndex,
getExecutionKernelRuntimeCloseoutDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-closeout-index.js"
);

console.log(
JSON.stringify(
getExecutionKernelRuntimeCloseoutDiagnostics(
buildExecutionKernelRuntimeCloseoutIndex({})
)
));
""")

        self.assertTrue(
            result["ready"]
        )

if __name__=="__main__":
    unittest.main()