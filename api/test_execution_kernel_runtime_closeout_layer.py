import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-closeout.js"
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

    def test_closeout(self):

        data=self.run_json("""
const {
createRuntimeCloseout
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-closeout.js"
);

console.log(
JSON.stringify(
createRuntimeCloseout({})
)
);
""")

        self.assertTrue(
            data["summary"]["closed"]
        )

    def test_execution_blocked(self):

        data=self.run_json("""
const {
createRuntimeCloseout
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-closeout.js"
);

console.log(
JSON.stringify(
createRuntimeCloseout({})
)
);
""")

        self.assertFalse(
            data["capabilities"]["execute"]
        )

    def test_diagnostics(self):

        data=self.run_json("""
const {
createRuntimeCloseout,
getRuntimeCloseoutDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-closeout.js"
);

console.log(
JSON.stringify(
getRuntimeCloseoutDiagnostics(
createRuntimeCloseout({})
)
));
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()