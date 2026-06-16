import json
import subprocess
import unittest


FILE = (
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-assurance-bridge.js"
)


class AssuranceBridgeTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return json.loads(result.stdout)

    def test_syntax(self):
        subprocess.run(
            ["node", "--check", FILE],
            check=True,
        )

    def test_normalization(self):
        result = self.run_json("""
const {
normalizeExecutionAssuranceReference
}=require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-assurance-bridge.js");

console.log(JSON.stringify(
normalizeExecutionAssuranceReference({
id:"assurance.snapshot.1",
assured:true,
validationAllowed:true,
executionAllowed:true
})
));
""")

        self.assertTrue(
            result["assured"]
        )

        self.assertTrue(
            result["validationAllowed"]
        )

        self.assertTrue(
            result["executionAllowed"]
        )

        self.assertFalse(
            result["diagnostics"]["bridgeAssuranceGranted"]
        )

    def test_bridge(self):
        result = self.run_json("""
const {
createExecutionKernelSnapshot
}=require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js");

const {
createExecutionKernelAssuranceBridge
}=require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-assurance-bridge.js");

const kernel=createExecutionKernelSnapshot({
mode:"INSPECTION",
stages:[
{
id:"stage-init",
type:"KERNEL_INITIALIZATION",
order:10
}
]
});

console.log(JSON.stringify(
createExecutionKernelAssuranceBridge({
kernelSnapshot:kernel,
assurance:{
assured:true
},
compliance:"c",
policy:"p",
audit:"a"
})
));
""")

        self.assertTrue(
            result["linkage"]["assuranceLinked"]
        )

        self.assertTrue(
            result["linkage"]["validationBlocked"]
        )

        self.assertTrue(
            result["linkage"]["executionBlocked"]
        )

    def test_snapshot(self):
        result=self.run_json("""
const {
buildExecutionKernelAssuranceBridgeSnapshot,
getExecutionKernelAssuranceBridgeDiagnostics
}=require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-assurance-bridge.js");

console.log(JSON.stringify(
getExecutionKernelAssuranceBridgeDiagnostics(
buildExecutionKernelAssuranceBridgeSnapshot({})
)
));
""")

        self.assertTrue(
            result["ready"]
        )


if __name__=="__main__":
    unittest.main()