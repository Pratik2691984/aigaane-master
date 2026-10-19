import json
import subprocess
import unittest


class RuntimeQueryTests(unittest.TestCase):

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
createRuntimeQueryRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-query-engine.js"
);

console.log(
JSON.stringify(
createRuntimeQueryRecord({})
));
""")
        self.assertEqual(data["state"], "QUERY_READY")

    def test_entries(self):
        data = self.run_json("""
const {
deriveRuntimeQueryEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-query-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeQueryEntries({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-query", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeQueryRecord,
createRuntimeQueryRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-query-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeQueryRecord(
createRuntimeQueryRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["queryBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeQueryPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-query-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeQueryPanel({
queryStatus:"<a>",
queryMode:"<b>",
sourceLookupStatus:"<c>",
sourceLookupMode:"<d>",
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
compareRuntimeQueryRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-query-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeQueryRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()