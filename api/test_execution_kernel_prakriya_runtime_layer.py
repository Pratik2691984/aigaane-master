import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-prakriya-runtime.js"
)

class PrakriyaRuntimeTests(
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
createPrakriyaRuntime
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-prakriya-runtime.js"
);

console.log(
JSON.stringify(
createPrakriyaRuntime({
stages:[
{id:"p1"},
{id:"p2"}
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

    def test_execution_blocked(self):

        data=self.run_json("""
const {
createPrakriyaRuntime
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-prakriya-runtime.js"
);

console.log(
JSON.stringify(
createPrakriyaRuntime({})
)
);
""")

        self.assertFalse(
            data["capabilities"]["applySandhi"]
        )

        self.assertFalse(
            data["capabilities"]["applyMorphology"]
        )

        self.assertFalse(
            data["capabilities"]["runSutras"]
        )

    def test_diagnostics(self):

        data=self.run_json("""
const {
createPrakriyaRuntime,
getPrakriyaRuntimeDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-prakriya-runtime.js"
);

console.log(
JSON.stringify(
getPrakriyaRuntimeDiagnostics(
createPrakriyaRuntime({})
)
));
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()