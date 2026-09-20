import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-rule-executor.js"
)

class RuleExecutorTests(
unittest.TestCase
):

    def run_json(
        self,
        script
    ):
        result=subprocess.run(
            ["node","-e",script],
            capture_output=True,
            check=True,
            text=True,
            encoding="utf-8"
        )

        return json.loads(
            result.stdout
        )

    def test_syntax(self):

        subprocess.run(
            ["node","--check",FILE],
            check=True
        )

    def test_executor(self):

        data=self.run_json("""
const {
createRuleExecutionEnvelope
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-rule-executor.js"
);

console.log(
JSON.stringify(
createRuleExecutionEnvelope({
rules:[
{id:"r1"},
{id:"r2"}
]
})
));
""")

        self.assertEqual(
            len(data["rules"]),
            2
        )

        self.assertFalse(
            data["capabilities"]["execute"]
        )

    def test_diagnostics(self):

        data=self.run_json("""
const {
createRuleExecutionEnvelope,
getRuleExecutorDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-rule-executor.js"
);

console.log(
JSON.stringify(
getRuleExecutorDiagnostics(
createRuleExecutionEnvelope({})
)
));
""")

        self.assertTrue(
            data["ready"]
        )

    def test_execution_stays_blocked(self):

        data=self.run_json("""
const {
createRuleExecutionEnvelope
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-rule-executor.js"
);

console.log(
JSON.stringify(
createRuleExecutionEnvelope({})
)
);
""")

        self.assertFalse(
            data["capabilities"]["mutate"]
        )

if __name__=="__main__":
    unittest.main()