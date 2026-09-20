import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-closeout-seal.js"
)

class CloseoutSealTests(unittest.TestCase):

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

    def test_normalization(self):

        result=self.run_json("""
const {
normalizeExecutionCloseoutSeal
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-closeout-seal.js"
);

console.log(JSON.stringify(
normalizeExecutionCloseoutSeal({
closed:true,
closeoutAllowed:true,
releaseAllowed:true
})
));
""")

        self.assertTrue(
            result["closed"]
        )

        self.assertFalse(
            result["diagnostics"]["bridgeCloseoutGranted"]
        )

    def test_bridge(self):

        result=self.run_json("""
const {
createExecutionKernelSnapshot
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js"
);

const {
createExecutionKernelCloseoutSeal
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-closeout-seal.js"
);

const kernel=
createExecutionKernelSnapshot({
stages:[
{id:"s"}
]
});

console.log(JSON.stringify(
createExecutionKernelCloseoutSeal({
kernelSnapshot:kernel,
closeoutSeal:{
closed:true
}
})
));
""")

        self.assertTrue(
            result["linkage"]["closeoutSealLinked"]
        )

        self.assertTrue(
            result["linkage"]["closeoutBlocked"]
        )

    def test_snapshot(self):

        result=self.run_json("""
const {
buildExecutionKernelCloseoutSealSnapshot,
getExecutionKernelCloseoutSealDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-closeout-seal.js"
);

console.log(JSON.stringify(
getExecutionKernelCloseoutSealDiagnostics(
buildExecutionKernelCloseoutSealSnapshot({})
)
));
""")

        self.assertTrue(
            result["ready"]
        )

if __name__=="__main__":
    unittest.main()