import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-rollback-runtime.js"
)

class RollbackRuntimeTests(
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
createRollbackRuntime
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-rollback-runtime.js"
);

console.log(
JSON.stringify(
createRollbackRuntime({
stages:[
{id:"r1"},
{id:"r2"}
]
})
));
""")

        self.assertEqual(
            len(data["stages"]),
            2
        )

        self.assertFalse(
            data["capabilities"]["rollback"]
        )

    def test_restore_blocked(self):

        data=self.run_json("""
const {
createRollbackRuntime
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-rollback-runtime.js"
);

console.log(
JSON.stringify(
createRollbackRuntime({})
)
);
""")

        self.assertFalse(
            data["capabilities"]["restore"]
        )

        self.assertFalse(
            data["capabilities"]["execute"]
        )

    def test_diagnostics(self):

        data=self.run_json("""
const {
createRollbackRuntime,
getRollbackRuntimeDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-rollback-runtime.js"
);

console.log(
JSON.stringify(
getRollbackRuntimeDiagnostics(
createRollbackRuntime({})
)
));
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()