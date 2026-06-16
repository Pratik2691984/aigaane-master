import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-transformation-commit.js"
)

class TransformationCommitTests(
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

    def test_layer(self):

        data=self.run_json("""
const {
createTransformationCommit
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-transformation-commit.js"
);

console.log(
JSON.stringify(
createTransformationCommit({
stages:[
{id:"c1"},
{id:"c2"}
]
})
));
""")

        self.assertEqual(
            len(data["stages"]),
            2
        )

        self.assertFalse(
            data["capabilities"]["commit"]
        )

    def test_commit_blocked(self):

        data=self.run_json("""
const {
createTransformationCommit
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-transformation-commit.js"
);

console.log(
JSON.stringify(
createTransformationCommit({})
)
);
""")

        self.assertFalse(
            data["capabilities"]["execute"]
        )

        self.assertFalse(
            data["capabilities"]["mutate"]
        )

    def test_diagnostics(self):

        data=self.run_json("""
const {
createTransformationCommit,
getTransformationCommitDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-transformation-commit.js"
);

console.log(
JSON.stringify(
getTransformationCommitDiagnostics(
createTransformationCommit({})
)
));
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()