import json
import subprocess
import unittest


class RuntimeSearchTests(unittest.TestCase):

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
createRuntimeSearchRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-search-engine.js"
);

console.log(
JSON.stringify(
createRuntimeSearchRecord({})
));
""")
        self.assertEqual(data["state"], "SEARCH_READY")

    def test_results(self):
        data = self.run_json("""
const {
deriveRuntimeSearchResults
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-search-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeSearchResults({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-search", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeSearchRecord,
createRuntimeSearchRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-search-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeSearchRecord(
createRuntimeSearchRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["searchBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeSearchPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-search-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeSearchPanel({
searchStatus:"<a>",
searchMode:"<b>",
sourceQueryStatus:"<c>",
sourceQueryMode:"<d>",
sourceCertificate:"<e>",
results:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeSearchRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-search-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeSearchRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()