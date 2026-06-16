import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-certification-bridge.js"
)

class CertificationBridgeTests(unittest.TestCase):

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
normalizeExecutionCertificationReference
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-certification-bridge.js"
);

console.log(JSON.stringify(
normalizeExecutionCertificationReference({
certified:true,
issuanceAllowed:true,
executionAllowed:true
})
));
""")

        self.assertTrue(
            result["certified"]
        )

        self.assertFalse(
            result["diagnostics"]["bridgeIssuanceGranted"]
        )

    def test_bridge(self):

        result=self.run_json("""
const {
createExecutionKernelSnapshot
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js"
);

const {
createExecutionKernelCertificationBridge
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-certification-bridge.js"
);

const kernel=
createExecutionKernelSnapshot({
stages:[
{id:"s"}
]
});

console.log(JSON.stringify(
createExecutionKernelCertificationBridge({
kernelSnapshot:kernel,
certification:{
certified:true
}
})
));
""")

        self.assertTrue(
            result["linkage"]["certificationLinked"]
        )

        self.assertTrue(
            result["linkage"]["issuanceBlocked"]
        )

    def test_snapshot(self):

        result=self.run_json("""
const {
buildExecutionKernelCertificationBridgeSnapshot,
getExecutionKernelCertificationBridgeDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-certification-bridge.js"
);

console.log(JSON.stringify(
getExecutionKernelCertificationBridgeDiagnostics(
buildExecutionKernelCertificationBridgeSnapshot({})
)
));
""")

        self.assertTrue(
            result["ready"]
        )

if __name__=="__main__":
    unittest.main()