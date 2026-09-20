import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-closeout-manifest.js"
)

class CloseoutManifestTests(
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

    def test_manifest_entry(self):

        result=self.run_json("""
const {
normalizeManifestEntry
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-closeout-manifest.js"
);

console.log(
JSON.stringify(
normalizeManifestEntry({
id:"x"
},0)
));
""")

        self.assertTrue(
            result["included"]
        )

        self.assertFalse(
            result["executed"]
        )

    def test_manifest(self):

        result=self.run_json("""
const {
createExecutionKernelCloseoutManifest
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-closeout-manifest.js"
);

console.log(
JSON.stringify(
createExecutionKernelCloseoutManifest({
entries:[
{id:"a"},
{id:"b"}
]
})
));
""")

        self.assertEqual(
            result["summary"]["manifestCount"],
            2
        )

    def test_manifest_diagnostics(self):

        result=self.run_json("""
const {
buildExecutionKernelCloseoutManifest,
getExecutionKernelCloseoutManifestDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-closeout-manifest.js"
);

console.log(
JSON.stringify(
getExecutionKernelCloseoutManifestDiagnostics(
buildExecutionKernelCloseoutManifest({})
)
));
""")

        self.assertTrue(
            result["ready"]
        )

if __name__=="__main__":
    unittest.main()