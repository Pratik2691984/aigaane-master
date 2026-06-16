import json
import subprocess
import unittest

MAP_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-catalog-map.js"
)

ENGINE_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-catalog-engine.js"
)

RENDERER_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-catalog-renderer.js"
)


class RuntimeCatalogLayerTests(unittest.TestCase):

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

    def test_catalog_ready(self):
        data = self.run_json("""
const {
createRuntimeCatalogRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-catalog-engine.js"
);

console.log(JSON.stringify(
createRuntimeCatalogRecord({
manifestId:"m1",
manifestStatus:"manifest-ready",
manifestMode:"inspection-manifest",
sourceCertificate:"controlled-runtime-inspection-only"
})
));
""")
        self.assertEqual(data["catalogStatus"], "catalog-ready")
        self.assertEqual(data["catalogMode"], "inspection-catalog")
        self.assertEqual(data["state"], "CATALOG_READY")
        self.assertFalse(data["catalogAllowed"])
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_catalog_records_present(self):
        data = self.run_json("""
const {
deriveRuntimeCatalogRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-catalog-engine.js"
);

console.log(JSON.stringify(
deriveRuntimeCatalogRecords({
warnings:["review"]
})
));
""")
        self.assertIn("runtime-lineage-catalog", data)
        self.assertIn("runtime-export-catalog", data)
        self.assertIn("runtime-import-catalog", data)
        self.assertIn("runtime-archive-catalog", data)
        self.assertIn("runtime-manifest-catalog", data)
        self.assertIn("runtime-readonly-catalog", data)
        self.assertIn("execution-denied", data)
        self.assertIn("mutation-denied", data)
        self.assertIn("publication-denied", data)
        self.assertIn("rollback-denied", data)
        self.assertIn("canonical-write-denied", data)
        self.assertIn("warning-reference-catalogued", data)

    def test_catalog_is_read_only(self):
        data = self.run_json("""
const {
createRuntimeCatalogRecord,
inspectRuntimeCatalogRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-catalog-engine.js"
);

console.log(JSON.stringify(
inspectRuntimeCatalogRecord(
createRuntimeCatalogRecord({
warnings:["review"]
})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["catalogBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["mutationBlocked"])
        self.assertTrue(data["publicationBlocked"])
        self.assertTrue(data["rollbackBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])
        self.assertFalse(data["catalogAllowed"])
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_renderer_escapes_html(self):
        data = self.run_json("""
const {
renderRuntimeCatalogPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-catalog-renderer.js"
);

console.log(JSON.stringify(
renderRuntimeCatalogPanel({
catalogStatus:"<catalog>",
catalogMode:"<mode>",
sourceManifestStatus:"<manifest>",
sourceManifestMode:"<manifest-mode>",
sourceCertificate:"<certificate>",
recordCount:1,
warningCount:1,
records:["<record>"],
warnings:["<warning>"]
})
));
""")
        self.assertIn("&lt;catalog&gt;", data["body"])
        self.assertIn("&lt;mode&gt;", data["body"])
        self.assertIn("&lt;manifest&gt;", data["body"])
        self.assertIn("&lt;manifest-mode&gt;", data["body"])
        self.assertIn("&lt;certificate&gt;", data["body"])
        self.assertIn("&lt;record&gt;", data["body"])
        self.assertIn("&lt;warning&gt;", data["body"])
        self.assertNotIn("<catalog>", data["body"])


if __name__ == "__main__":
    unittest.main()