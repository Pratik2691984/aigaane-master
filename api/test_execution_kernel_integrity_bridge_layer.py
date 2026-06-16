import json
import subprocess
import unittest


FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-integrity-bridge.js"
)


class IntegrityBridgeTests(
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
normalizeExecutionIntegrityReference
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-integrity-bridge.js"
);

console.log(
JSON.stringify(
normalizeExecutionIntegrityReference({
verified:true,
repairAllowed:true,
executionAllowed:true
})
));
""")

        self.assertTrue(
            result["verified"]
        )

        self.assertFalse(
            result["diagnostics"]["bridgeRepairGranted"]
        )

    def test_bridge(self):

        result=self.run_json("""
const {
createExecutionKernelSnapshot
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js"
);

const {
createExecutionKernelIntegrityBridge
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-integrity-bridge.js"
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
createExecutionKernelIntegrityBridge({
kernelSnapshot:kernel,
integrity:{
verified:true
}
})
));
""")

        self.assertTrue(
            result["linkage"]["integrityLinked"]
        )

        self.assertTrue(
            result["linkage"]["repairBlocked"]
        )

    def test_snapshot(self):

        result=self.run_json("""
const {
buildExecutionKernelIntegrityBridgeSnapshot,
getExecutionKernelIntegrityBridgeDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-integrity-bridge.js"
);

console.log(
JSON.stringify(
getExecutionKernelIntegrityBridgeDiagnostics(
buildExecutionKernelIntegrityBridgeSnapshot({})
)
));
""")

        self.assertTrue(
            result["ready"]
        )


if __name__=="__main__":
    unittest.main()