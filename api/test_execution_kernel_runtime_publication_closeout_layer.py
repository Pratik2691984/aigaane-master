import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-publication-closeout.js"
)

class RuntimePublicationCloseoutTests(unittest.TestCase):

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
        subprocess.run(["node","--check",FILE],check=True)

    def test_publication_closeout(self):
        data=self.run_json("""
const {
createRuntimePublicationCloseout
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-closeout.js"
);
console.log(JSON.stringify(createRuntimePublicationCloseout({})));
""")
        self.assertTrue(data["publication"]["closed"])
        self.assertTrue(data["publication"]["deterministic"])

    def test_capabilities_blocked(self):
        data=self.run_json("""
const {
createRuntimePublicationCloseout
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-closeout.js"
);
console.log(JSON.stringify(createRuntimePublicationCloseout({})));
""")
        self.assertFalse(data["capabilities"]["execute"])
        self.assertFalse(data["capabilities"]["canonicalWrite"])
        self.assertFalse(data["capabilities"]["rollback"])

    def test_diagnostics(self):
        data=self.run_json("""
const {
createRuntimePublicationCloseout,
getRuntimePublicationCloseoutDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-closeout.js"
);
console.log(JSON.stringify(
getRuntimePublicationCloseoutDiagnostics(
createRuntimePublicationCloseout({})
)
));
""")
        self.assertTrue(data["ready"])
        self.assertTrue(data["canonicalWriteBlocked"])

if __name__=="__main__":
    unittest.main()