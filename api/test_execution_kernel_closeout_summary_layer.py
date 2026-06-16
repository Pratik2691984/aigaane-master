import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-closeout-summary.js"
)

class CloseoutSummaryTests(
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

    def test_summary_entry(self):

        result=self.run_json("""
const {
normalizeSummaryEntry
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-closeout-summary.js"
);

console.log(
JSON.stringify(
normalizeSummaryEntry({
id:"x"
},0)
));
""")

        self.assertTrue(
            result["included"]
        )

        self.assertFalse(
            result["executed"]
        )

    def test_summary(self):

        result=self.run_json("""
const {
createExecutionKernelCloseoutSummary
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-closeout-summary.js"
);

console.log(
JSON.stringify(
createExecutionKernelCloseoutSummary({
entries:[
{id:"a"},
{id:"b"}
]
})
));
""")

        self.assertEqual(
            result["summary"]["summaryCount"],
            2
        )

    def test_summary_diagnostics(self):

        result=self.run_json("""
const {
buildExecutionKernelCloseoutSummary,
getExecutionKernelCloseoutSummaryDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-closeout-summary.js"
);

console.log(
JSON.stringify(
getExecutionKernelCloseoutSummaryDiagnostics(
buildExecutionKernelCloseoutSummary({})
)
));
""")

        self.assertTrue(
            result["ready"]
        )

if __name__=="__main__":
    unittest.main()