import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-sandhi-runtime.js"
)

class SandhiRuntimeTests(
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

    def test_runtime(self):

        data=self.run_json("""
const {
createSandhiRuntime
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-sandhi-runtime.js"
);

console.log(
JSON.stringify(
createSandhiRuntime({
stages:[
{id:"s1"},
{id:"s2"}
]
})
));
""")

        self.assertEqual(
            len(data["stages"]),
            2
        )

        self.assertFalse(
            data["capabilities"]["execute"]
        )

    def test_stage_blocked(self):

        data=self.run_json("""
const {
createSandhiRuntime
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-sandhi-runtime.js"
);

console.log(
JSON.stringify(
createSandhiRuntime({
stages:[
{id:"a"}
]
})
));
""")

        self.assertFalse(
            data["stages"][0]["executed"]
        )

    def test_diagnostics(self):

        data=self.run_json("""
const {
createSandhiRuntime,
getSandhiRuntimeDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-sandhi-runtime.js"
);

console.log(
JSON.stringify(
getSandhiRuntimeDiagnostics(
createSandhiRuntime({})
)
));
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()