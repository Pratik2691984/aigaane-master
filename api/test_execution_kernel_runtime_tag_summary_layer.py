import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-tag-summary.js"
)

class RuntimeSummaryTests(
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

    def test_summary(self):

        data=self.run_json("""
const {
createRuntimeTagSummary
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-tag-summary.js"
);

console.log(
JSON.stringify(
createRuntimeTagSummary({})
)
);
""")

        self.assertTrue(
            data["summary"]["deterministic"]
        )

    def test_execution_disabled(self):

        data=self.run_json("""
const {
createRuntimeTagSummary
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-tag-summary.js"
);

console.log(
JSON.stringify(
createRuntimeTagSummary({})
)
);
""")

        self.assertFalse(
            data["capabilities"]["execute"]
        )

    def test_diagnostics(self):

        data=self.run_json("""
const {
createRuntimeTagSummary,
getRuntimeTagSummaryDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-tag-summary.js"
);

console.log(
JSON.stringify(
getRuntimeTagSummaryDiagnostics(
createRuntimeTagSummary({})
)
));
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()