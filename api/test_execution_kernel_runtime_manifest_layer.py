import json
import subprocess
import unittest

MAP_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-manifest-map.js"
)

ENGINE_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-manifest-engine.js"
)

RENDERER_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-manifest-renderer.js"
)


class RuntimeManifestLayerTests(unittest.TestCase):

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

    def test_manifest_ready(self):
        data = self.run_json("""
const {
createRuntimeManifestRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-manifest-engine.js"
);

console.log(JSON.stringify(
createRuntimeManifestRecord({
archiveId:"a1",
archiveStatus:"archive-ready",
archiveMode:"inspection-archive",
sourceCertificate:"controlled-runtime-inspection-only"
})
));
""")
        self.assertEqual(data["manifestStatus"], "manifest-ready")
        self.assertEqual(data["manifestMode"], "inspection-manifest")
        self.assertEqual(data["state"], "MANIFEST_READY")
        self.assertFalse(data["manifestAllowed"])
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_manifest_entries_present(self):
        data = self.run_json("""
const {
deriveRuntimeManifestEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-manifest-engine.js"
);

console.log(JSON.stringify(
deriveRuntimeManifestEntries({
warnings:["review"]
})
));
""")
        self.assertIn("runtime-inspection-lineage", data)
        self.assertIn("runtime-export-reference", data)
        self.assertIn("runtime-import-reference", data)
        self.assertIn("runtime-archive-reference", data)
        self.assertIn("runtime-readonly-reference", data)
        self.assertIn("execution-denied", data)
        self.assertIn("mutation-denied", data)
        self.assertIn("publication-denied", data)
        self.assertIn("rollback-denied", data)
        self.assertIn("canonical-write-denied", data)
        self.assertIn("warning-reference-added", data)

    def test_manifest_is_read_only(self):
        data = self.run_json("""
const {
createRuntimeManifestRecord,
inspectRuntimeManifestRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-manifest-engine.js"
);

console.log(JSON.stringify(
inspectRuntimeManifestRecord(
createRuntimeManifestRecord({
warnings:["review"]
})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["manifestBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["mutationBlocked"])
        self.assertTrue(data["publicationBlocked"])
        self.assertTrue(data["rollbackBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])
        self.assertFalse(data["manifestAllowed"])
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_renderer_escapes_html(self):
        data = self.run_json("""
const {
renderRuntimeManifestPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-manifest-renderer.js"
);

console.log(JSON.stringify(
renderRuntimeManifestPanel({
manifestStatus:"<manifest>",
manifestMode:"<mode>",
sourceArchiveStatus:"<archive>",
sourceArchiveMode:"<archive-mode>",
sourceCertificate:"<certificate>",
entryCount:1,
warningCount:1,
entries:["<entry>"],
warnings:["<warning>"]
})
));
""")
        self.assertIn("&lt;manifest&gt;", data["body"])
        self.assertIn("&lt;mode&gt;", data["body"])
        self.assertIn("&lt;archive&gt;", data["body"])
        self.assertIn("&lt;archive-mode&gt;", data["body"])
        self.assertIn("&lt;certificate&gt;", data["body"])
        self.assertIn("&lt;entry&gt;", data["body"])
        self.assertIn("&lt;warning&gt;", data["body"])
        self.assertNotIn("<manifest>", data["body"])


if __name__ == "__main__":
    unittest.main()