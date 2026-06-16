import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-authority-bridge.js"
)

class AuthorityBridgeTests(unittest.TestCase):

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
normalizeExecutionAuthorityReference
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-authority-bridge.js"
);

console.log(
JSON.stringify(
normalizeExecutionAuthorityReference({
authorized:true,
delegationAllowed:true,
executionAllowed:true
})
));
""")

        self.assertTrue(
            result["authorized"]
        )

        self.assertFalse(
            result["diagnostics"]["bridgeDelegationGranted"]
        )

    def test_bridge(self):

        result=self.run_json("""
const {
createExecutionKernelSnapshot
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js"
);

const {
createExecutionKernelAuthorityBridge
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-authority-bridge.js"
);

const kernel=
createExecutionKernelSnapshot({
stages:[
{id:"s"}
]
});

console.log(
JSON.stringify(
createExecutionKernelAuthorityBridge({
kernelSnapshot:kernel,
authority:{
authorized:true
}
})
));
""")

        self.assertTrue(
            result["linkage"]["authorityLinked"]
        )

        self.assertTrue(
            result["linkage"]["delegationBlocked"]
        )

    def test_snapshot(self):

        result=self.run_json("""
const {
buildExecutionKernelAuthorityBridgeSnapshot,
getExecutionKernelAuthorityBridgeDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-authority-bridge.js"
);

console.log(
JSON.stringify(
getExecutionKernelAuthorityBridgeDiagnostics(
buildExecutionKernelAuthorityBridgeSnapshot({})
)
));
""")

        self.assertTrue(
            result["ready"]
        )

if __name__=="__main__":
    unittest.main()