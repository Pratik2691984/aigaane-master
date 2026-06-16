import json
import subprocess
import unittest

MAP_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-import-map.js"
)

ENGINE_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-import-engine.js"
)

RENDERER_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-import-renderer.js"
)


class RuntimeImportLayerTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        return json.loads(result.stdout)

    def test_syntax(self):
        subprocess.run(["node", "--check", MAP_FILE], check=True)
        subprocess.run(["node", "--check", ENGINE_FILE], check=True)
        subprocess.run(["node", "--check", RENDERER_FILE], check=True)

    def test_import_review_only(self):
        data = self.run_json("""
const {
createRuntimeImportRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-import-engine.js"
);

console.log(JSON.stringify(
createRuntimeImportRecord({
exportId:"e1",
exportStatus:"export-ready",
exportMode:"inspection-export",
certificate:"controlled-runtime-inspection-only"
})
));
""")
        self.assertEqual(data["importStatus"], "review-only")
        self.assertEqual(data["importMode"], "inspection-import")
        self.assertEqual(data["state"], "REVIEW_ONLY")
        self.assertFalse(data["importAllowed"])
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_import_attestations_present(self):
        data = self.run_json("""
const {
deriveRuntimeImportFindings
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-import-engine.js"
);

console.log(JSON.stringify(
deriveRuntimeImportFindings({
warnings:["review"]
})
));
""")
        self.assertIn("inspection-import-reviewed", data)
        self.assertIn("source-export-readonly-accepted", data)
        self.assertIn("execution-denied", data)
        self.assertIn("mutation-denied", data)
        self.assertIn("publication-denied", data)
        self.assertIn("rollback-denied", data)
        self.assertIn("canonical-write-denied", data)
        self.assertIn("warning-review-required", data)

    def test_import_is_read_only(self):
        data = self.run_json("""
const {
createRuntimeImportRecord,
inspectRuntimeImportRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-import-engine.js"
);

console.log(JSON.stringify(
inspectRuntimeImportRecord(
createRuntimeImportRecord({
warnings:["review"]
})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["importBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["mutationBlocked"])
        self.assertTrue(data["publicationBlocked"])
        self.assertTrue(data["rollbackBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])
        self.assertFalse(data["importAllowed"])
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_renderer_escapes_html(self):
        data = self.run_json("""
const {
renderRuntimeImportPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-import-renderer.js"
);

console.log(JSON.stringify(
renderRuntimeImportPanel({
importStatus:"<review>",
importMode:"<import>",
sourceExportStatus:"<export>",
sourceExportMode:"<mode>",
sourceCertificate:"<certificate>",
attestationCount:1,
warningCount:1,
attestations:["<attestation>"],
warnings:["<warning>"]
})
));
""")
        self.assertIn("&lt;review&gt;", data["body"])
        self.assertIn("&lt;import&gt;", data["body"])
        self.assertIn("&lt;export&gt;", data["body"])
        self.assertIn("&lt;mode&gt;", data["body"])
        self.assertIn("&lt;certificate&gt;", data["body"])
        self.assertIn("&lt;attestation&gt;", data["body"])
        self.assertIn("&lt;warning&gt;", data["body"])
        self.assertNotIn("<review>", data["body"])


if __name__ == "__main__":
    unittest.main()