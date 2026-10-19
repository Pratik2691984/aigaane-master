import json
import subprocess
import unittest

MAP_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-archive-map.js"
)

ENGINE_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-archive-engine.js"
)

RENDERER_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-archive-renderer.js"
)


class RuntimeArchiveLayerTests(unittest.TestCase):

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

    def test_archive_ready(self):
        data = self.run_json("""
const {
createRuntimeArchiveRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-archive-engine.js"
);

console.log(JSON.stringify(
createRuntimeArchiveRecord({
importId:"i1",
importStatus:"review-only",
importMode:"inspection-import",
sourceCertificate:"controlled-runtime-inspection-only"
})
));
""")
        self.assertEqual(data["archiveStatus"], "archive-ready")
        self.assertEqual(data["archiveMode"], "inspection-archive")
        self.assertEqual(data["state"], "ARCHIVE_READY")
        self.assertFalse(data["archiveAllowed"])
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_archive_attestations_present(self):
        data = self.run_json("""
const {
deriveRuntimeArchiveAttestations
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-archive-engine.js"
);

console.log(JSON.stringify(
deriveRuntimeArchiveAttestations({
warnings:["review"]
})
));
""")
        self.assertIn("inspection-archive-reviewed", data)
        self.assertIn("source-import-readonly-accepted", data)
        self.assertIn("archive-metadata-only", data)
        self.assertIn("execution-denied", data)
        self.assertIn("mutation-denied", data)
        self.assertIn("publication-denied", data)
        self.assertIn("rollback-denied", data)
        self.assertIn("canonical-write-denied", data)
        self.assertIn("warning-carry-forward-archived", data)

    def test_archive_is_read_only(self):
        data = self.run_json("""
const {
createRuntimeArchiveRecord,
inspectRuntimeArchiveRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-archive-engine.js"
);

console.log(JSON.stringify(
inspectRuntimeArchiveRecord(
createRuntimeArchiveRecord({
warnings:["review"]
})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["archiveBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["mutationBlocked"])
        self.assertTrue(data["publicationBlocked"])
        self.assertTrue(data["rollbackBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])
        self.assertFalse(data["archiveAllowed"])
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_renderer_escapes_html(self):
        data = self.run_json("""
const {
renderRuntimeArchivePanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-archive-renderer.js"
);

console.log(JSON.stringify(
renderRuntimeArchivePanel({
archiveStatus:"<archive>",
archiveMode:"<mode>",
sourceImportStatus:"<review>",
sourceImportMode:"<import>",
sourceCertificate:"<certificate>",
attestationCount:1,
warningCount:1,
attestations:["<attestation>"],
warnings:["<warning>"]
})
));
""")
        self.assertIn("&lt;archive&gt;", data["body"])
        self.assertIn("&lt;mode&gt;", data["body"])
        self.assertIn("&lt;review&gt;", data["body"])
        self.assertIn("&lt;import&gt;", data["body"])
        self.assertIn("&lt;certificate&gt;", data["body"])
        self.assertIn("&lt;attestation&gt;", data["body"])
        self.assertIn("&lt;warning&gt;", data["body"])
        self.assertNotIn("<archive>", data["body"])


if __name__ == "__main__":
    unittest.main()