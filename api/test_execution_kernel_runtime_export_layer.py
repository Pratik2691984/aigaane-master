import json
import subprocess
import unittest


class RuntimeExportTests(
unittest.TestCase
):

    def run_json(
        self,
        script
    ):
        r=subprocess.run(
            [
                "node",
                "-e",
                script
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        return json.loads(
            r.stdout
        )

    def test_syntax(self):

        subprocess.run([
            "node",
            "--check",
            "ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-export-map.js"
        ],check=True)

    def test_export_ready(self):

        data=self.run_json("""
const {
createRuntimeExportRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-export-engine.js"
);

console.log(
JSON.stringify(
createRuntimeExportRecord({})
)
);
""")

        self.assertEqual(
            data["state"],
            "EXPORT_READY"
        )

    def test_export_attestations(self):

        data=self.run_json("""
const {
deriveRuntimeExportAttestations
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-export-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeExportAttestations({})
)
);
""")

        self.assertIn(
            "inspection-export-certified",
            data
        )

    def test_export_is_read_only(self):

        data=self.run_json("""
const {
inspectRuntimeExportRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-export-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeExportRecord({})
)
);
""")

        self.assertTrue(
            data["readOnly"]
        )

    def test_renderer_escapes_html(self):

        data=self.run_json("""
const {
renderRuntimeExportPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-export-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeExportPanel({
exportStatus:"<x>"
})
)
);
""")

        self.assertIn(
            "&lt;x&gt;",
            data["body"]
        )


if __name__=="__main__":
    unittest.main()