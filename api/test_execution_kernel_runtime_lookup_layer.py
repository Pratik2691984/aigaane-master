import json
import subprocess
import unittest


class RuntimeLookupTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_create(self):
        data = self.run_json("""
const {
createRuntimeLookupRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-lookup-engine.js"
);

console.log(
JSON.stringify(
createRuntimeLookupRecord({})
));
""")
        self.assertEqual(data["state"], "LOOKUP_READY")

    def test_entries(self):
        data = self.run_json("""
const {
deriveRuntimeLookupEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-lookup-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeLookupEntries({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-lookup", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeLookupRecord,
createRuntimeLookupRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-lookup-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeLookupRecord(
createRuntimeLookupRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeLookupPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-lookup-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeLookupPanel({
lookupStatus:"<a>",
lookupMode:"<b>",
sourceDirectoryStatus:"<c>",
sourceDirectoryMode:"<d>",
sourceCertificate:"<e>",
entries:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeLookupRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-lookup-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeLookupRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()