import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-permission-bridge.js"
)

class PermissionBridgeTests(
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
        return json.loads(r.stdout)

    def test_syntax(self):
        subprocess.run(
            ["node","--check",FILE],
            check=True
        )

    def test_normalization(self):

        result=self.run_json("""
const {
normalizeExecutionPermissionReference
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-permission-bridge.js"
);

console.log(
JSON.stringify(
normalizeExecutionPermissionReference({
permitted:true,
grantAllowed:true,
executionAllowed:true
})
));
""")

        self.assertTrue(
            result["permitted"]
        )

        self.assertFalse(
            result["diagnostics"]["bridgeGrantGranted"]
        )

    def test_bridge(self):

        result=self.run_json("""
const {
createExecutionKernelSnapshot
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js"
);

const {
createExecutionKernelPermissionBridge
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-permission-bridge.js"
);

const kernel=
createExecutionKernelSnapshot({
stages:[
{id:"s"}
]
});

console.log(
JSON.stringify(
createExecutionKernelPermissionBridge({
kernelSnapshot:kernel,
permission:{
permitted:true
}
})
));
""")

        self.assertTrue(
            result["linkage"]["permissionLinked"]
        )

        self.assertTrue(
            result["linkage"]["grantBlocked"]
        )

    def test_snapshot(self):

        result=self.run_json("""
const {
buildExecutionKernelPermissionBridgeSnapshot,
getExecutionKernelPermissionBridgeDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-permission-bridge.js"
);

console.log(
JSON.stringify(
getExecutionKernelPermissionBridgeDiagnostics(
buildExecutionKernelPermissionBridgeSnapshot({})
)
));
""")

        self.assertTrue(
            result["ready"]
        )

if __name__=="__main__":
    unittest.main()