import json
import subprocess
import unittest

MAP_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-registry-map.js"
)

ENGINE_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-registry-engine.js"
)

RENDERER_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-registry-renderer.js"
)


class RuntimeRegistryLayerTests(unittest.TestCase):

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

    def test_registry_ready(self):
        data = self.run_json("""
const {
createRuntimeRegistryRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-registry-engine.js"
);

console.log(JSON.stringify(
createRuntimeRegistryRecord({
catalogId:"c1",
catalogStatus:"catalog-ready",
catalogMode:"inspection-catalog",
sourceCertificate:"controlled-runtime-inspection-only"
})
));
""")
        self.assertEqual(data["registryStatus"], "registry-ready")
        self.assertEqual(data["registryMode"], "inspection-registry")
        self.assertEqual(data["state"], "REGISTRY_READY")
        self.assertFalse(data["registryAllowed"])
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_registry_entries_present(self):
        data = self.run_json("""
const {
deriveRuntimeRegistryEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-registry-engine.js"
);

console.log(JSON.stringify(
deriveRuntimeRegistryEntries({
warnings:["review"]
})
));
""")
        self.assertIn("runtime-registry-index", data)
        self.assertIn("runtime-catalog-reference", data)
        self.assertIn("runtime-manifest-reference", data)
        self.assertIn("runtime-archive-reference", data)
        self.assertIn("runtime-import-reference", data)
        self.assertIn("runtime-export-reference", data)
        self.assertIn("runtime-readonly-reference", data)
        self.assertIn("execution-denied", data)
        self.assertIn("mutation-denied", data)
        self.assertIn("publication-denied", data)
        self.assertIn("rollback-denied", data)
        self.assertIn("canonical-write-denied", data)
        self.assertIn("warning-reference-registered", data)

    def test_registry_is_read_only(self):
        data = self.run_json("""
const {
createRuntimeRegistryRecord,
inspectRuntimeRegistryRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-registry-engine.js"
);

console.log(JSON.stringify(
inspectRuntimeRegistryRecord(
createRuntimeRegistryRecord({
warnings:["review"]
})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["registryBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["mutationBlocked"])
        self.assertTrue(data["publicationBlocked"])
        self.assertTrue(data["rollbackBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])
        self.assertFalse(data["registryAllowed"])
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_renderer_escapes_html(self):
        data = self.run_json("""
const {
renderRuntimeRegistryPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-registry-renderer.js"
);

console.log(JSON.stringify(
renderRuntimeRegistryPanel({
registryStatus:"<registry>",
registryMode:"<mode>",
sourceCatalogStatus:"<catalog>",
sourceCatalogMode:"<catalog-mode>",
sourceCertificate:"<certificate>",
entryCount:1,
warningCount:1,
entries:["<entry>"],
warnings:["<warning>"]
})
));
""")
        self.assertIn("&lt;registry&gt;", data["body"])
        self.assertIn("&lt;mode&gt;", data["body"])
        self.assertIn("&lt;catalog&gt;", data["body"])
        self.assertIn("&lt;catalog-mode&gt;", data["body"])
        self.assertIn("&lt;certificate&gt;", data["body"])
        self.assertIn("&lt;entry&gt;", data["body"])
        self.assertIn("&lt;warning&gt;", data["body"])
        self.assertNotIn("<registry>", data["body"])


if __name__ == "__main__":
    unittest.main()