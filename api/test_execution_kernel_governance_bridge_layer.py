import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-governance-bridge.js"
)

class GovernanceBridgeTests(
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

    def test_normalization(self):

        result=self.run_json("""
const {
normalizeExecutionGovernanceReference
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-governance-bridge.js"
);

console.log(
JSON.stringify(
normalizeExecutionGovernanceReference({
governed:true,
authorizationAllowed:true,
executionAllowed:true
})
));
""")

        self.assertTrue(
            result["governed"]
        )

        self.assertFalse(
            result["diagnostics"]["bridgeAuthorizationGranted"]
        )

    def test_bridge(self):

        result=self.run_json("""
const {
createExecutionKernelSnapshot
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js"
);

const {
createExecutionKernelGovernanceBridge
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-governance-bridge.js"
);

const kernel=
createExecutionKernelSnapshot({
stages:[
{
id:"s"
}
]
});

console.log(
JSON.stringify(
createExecutionKernelGovernanceBridge({
kernelSnapshot:kernel,
governance:{
governed:true
}
})
));
""")

        self.assertTrue(
            result["linkage"]["governanceLinked"]
        )

        self.assertTrue(
            result["linkage"]["authorizationBlocked"]
        )

    def test_snapshot(self):

        result=self.run_json("""
const {
buildExecutionKernelGovernanceBridgeSnapshot,
getExecutionKernelGovernanceBridgeDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-governance-bridge.js"
);

console.log(
JSON.stringify(
getExecutionKernelGovernanceBridgeDiagnostics(
buildExecutionKernelGovernanceBridgeSnapshot({})
)
));
""")

        self.assertTrue(
            result["ready"]
        )


if __name__=="__main__":
    unittest.main()