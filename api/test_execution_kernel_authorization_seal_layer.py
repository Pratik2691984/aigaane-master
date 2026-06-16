import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-authorization-seal.js"
)

class AuthorizationSealTests(unittest.TestCase):

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
normalizeExecutionAuthorizationSeal
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-authorization-seal.js"
);

console.log(JSON.stringify(
normalizeExecutionAuthorizationSeal({
sealed:true,
authorizationAllowed:true,
executionAllowed:true
})
));
""")
        self.assertTrue(result["sealed"])
        self.assertFalse(result["diagnostics"]["bridgeAuthorizationGranted"])
        self.assertFalse(result["diagnostics"]["bridgeExecutionGranted"])

    def test_bridge_blocks_authorization_and_execution(self):
        result=self.run_json("""
const {
createExecutionKernelSnapshot
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js"
);

const {
createExecutionKernelAuthorizationSeal
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-authorization-seal.js"
);

const kernel=createExecutionKernelSnapshot({
stages:[{id:"s"}]
});

console.log(JSON.stringify(
createExecutionKernelAuthorizationSeal({
kernelSnapshot:kernel,
authorizationSeal:{sealed:true},
permission:"permission.snapshot.1",
authority:"authority.snapshot.1",
governance:"governance.snapshot.1"
})
));
""")
        self.assertTrue(result["linkage"]["authorizationSealLinked"])
        self.assertTrue(result["linkage"]["permissionLinked"])
        self.assertTrue(result["linkage"]["authorityLinked"])
        self.assertTrue(result["linkage"]["governanceLinked"])
        self.assertTrue(result["linkage"]["authorizationBlocked"])
        self.assertTrue(result["linkage"]["executionBlocked"])
        self.assertTrue(result["diagnostics"]["sealOnly"])
        self.assertEqual(result["diagnostics"]["stageCount"], 1)

    def test_snapshot_diagnostics(self):
        result=self.run_json("""
const {
buildExecutionKernelAuthorizationSealSnapshot,
getExecutionKernelAuthorizationSealDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-authorization-seal.js"
);

console.log(JSON.stringify(
getExecutionKernelAuthorizationSealDiagnostics(
buildExecutionKernelAuthorizationSealSnapshot({})
)
));
""")
        self.assertTrue(result["ready"])
        self.assertTrue(result["authorizationSealLinked"])
        self.assertTrue(result["authorizationBlocked"])
        self.assertTrue(result["executionBlocked"])

if __name__=="__main__":
    unittest.main()