import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-publication-final-summary.js"
)

class RuntimePublicationFinalSummaryTests(
unittest.TestCase
):

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
        subprocess.run(
            ["node","--check",FILE],
            check=True
        )

    def test_summary(self):

        data=self.run_json("""
const {
createRuntimePublicationFinalSummary
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-final-summary.js"
);

console.log(JSON.stringify(
createRuntimePublicationFinalSummary({})
));
""")

        self.assertEqual(
            data["summary"]["status"],
            "READY"
        )

    def test_execution_block(self):

        data=self.run_json("""
const {
createRuntimePublicationFinalSummary
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-final-summary.js"
);

console.log(JSON.stringify(
createRuntimePublicationFinalSummary({})
));
""")

        self.assertFalse(
            data["capabilities"]["execute"]
        )

    def test_inspector(self):

        data=self.run_json("""
const {
createRuntimePublicationFinalSummary,
inspectRuntimePublicationFinalSummary
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-final-summary.js"
);

console.log(JSON.stringify(
inspectRuntimePublicationFinalSummary(
createRuntimePublicationFinalSummary({})
)
));
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()