import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-morphology-runtime.js"
)

class MorphologyRuntimeTests(
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
createMorphologyRuntime
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-morphology-runtime.js"
);

console.log(
JSON.stringify(
createMorphologyRuntime({
stages:[
{id:"m1"},
{id:"m2"}
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

    def test_generation_blocked(self):

        data=self.run_json("""
const {
createMorphologyRuntime
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-morphology-runtime.js"
);

console.log(
JSON.stringify(
createMorphologyRuntime({})
)
);
""")

        self.assertFalse(
            data["capabilities"]["generateSubanta"]
        )

        self.assertFalse(
            data["capabilities"]["generateTinanta"]
        )

    def test_diagnostics(self):

        data=self.run_json("""
const {
createMorphologyRuntime,
getMorphologyRuntimeDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-morphology-runtime.js"
);

console.log(
JSON.stringify(
getMorphologyRuntimeDiagnostics(
createMorphologyRuntime({})
)
));
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()