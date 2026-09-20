import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-finalization-seal.js"
)

class FinalizationSealTests(unittest.TestCase):

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
normalizeExecutionFinalizationSeal
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-finalization-seal.js"
);

console.log(JSON.stringify(
normalizeExecutionFinalizationSeal({
sealed:true,
finalizationAllowed:true,
surfaceFormsAllowed:true
})
));
""")
        self.assertTrue(result["sealed"])
        self.assertTrue(result["finalizationAllowed"])
        self.assertTrue(result["surfaceFormsAllowed"])
        self.assertFalse(result["diagnostics"]["bridgeFinalizationGranted"])
        self.assertFalse(result["diagnostics"]["bridgeSurfaceFormsGranted"])

    def test_bridge_blocks_finalization_and_surface_forms(self):
        result=self.run_json("""
const {
createExecutionKernelSnapshot
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-engine.js"
);

const {
createExecutionKernelFinalizationSeal
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-finalization-seal.js"
);

const kernel=createExecutionKernelSnapshot({
stages:[{id:"s"}]
});

console.log(JSON.stringify(
createExecutionKernelFinalizationSeal({
kernelSnapshot:kernel,
finalizationSeal:{sealed:true},
authorizationSeal:"authorization-seal.snapshot.1",
permission:"permission.snapshot.1",
authority:"authority.snapshot.1"
})
));
""")
        self.assertTrue(result["linkage"]["finalizationSealLinked"])
        self.assertTrue(result["linkage"]["authorizationSealLinked"])
        self.assertTrue(result["linkage"]["permissionLinked"])
        self.assertTrue(result["linkage"]["authorityLinked"])
        self.assertTrue(result["linkage"]["finalizationBlocked"])
        self.assertTrue(result["linkage"]["surfaceFormBlocked"])
        self.assertTrue(result["linkage"]["executionBlocked"])
        self.assertTrue(result["diagnostics"]["finalizationSealOnly"])
        self.assertEqual(result["diagnostics"]["stageCount"], 1)

    def test_snapshot_diagnostics(self):
        result=self.run_json("""
const {
buildExecutionKernelFinalizationSealSnapshot,
getExecutionKernelFinalizationSealDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-finalization-seal.js"
);

console.log(JSON.stringify(
getExecutionKernelFinalizationSealDiagnostics(
buildExecutionKernelFinalizationSealSnapshot({})
)
));
""")
        self.assertTrue(result["ready"])
        self.assertTrue(result["finalizationSealLinked"])
        self.assertTrue(result["finalizationBlocked"])
        self.assertTrue(result["surfaceFormBlocked"])
        self.assertTrue(result["executionBlocked"])

if __name__=="__main__":
    unittest.main()