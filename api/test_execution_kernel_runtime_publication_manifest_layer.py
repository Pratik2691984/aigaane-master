import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-publication-manifest.js"
)

class RuntimePublicationManifestTests(
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

    def test_manifest(self):

        data=self.run_json("""
const {
createRuntimePublicationManifest
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-manifest.js"
);

console.log(
JSON.stringify(
createRuntimePublicationManifest({})
)
);
""")

        self.assertTrue(
            data["manifest"]["immutable"]
        )

    def test_capabilities(self):

        data=self.run_json("""
const {
createRuntimePublicationManifest
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-manifest.js"
);

console.log(
JSON.stringify(
createRuntimePublicationManifest({})
)
);
""")

        self.assertFalse(
            data["capabilities"]["execute"]
        )

        self.assertFalse(
            data["capabilities"]["canonicalWrite"]
        )

    def test_diagnostics(self):

        data=self.run_json("""
const {
createRuntimePublicationManifest,
getRuntimePublicationManifestDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-manifest.js"
);

console.log(
JSON.stringify(
getRuntimePublicationManifestDiagnostics(
createRuntimePublicationManifest({})
)
));
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()