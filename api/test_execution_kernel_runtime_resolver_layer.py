import json
import subprocess
import unittest


class RuntimeResolverTests(unittest.TestCase):

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
createRuntimeResolverRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-resolver-engine.js"
);

console.log(
JSON.stringify(
createRuntimeResolverRecord({})
));
""")
        self.assertEqual(data["state"], "RESOLVER_READY")

    def test_resolutions(self):
        data = self.run_json("""
const {
deriveRuntimeResolverResolutions
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-resolver-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeResolverResolutions({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-resolver", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeResolverRecord,
createRuntimeResolverRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-resolver-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeResolverRecord(
createRuntimeResolverRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["resolverBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeResolverPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-resolver-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeResolverPanel({
resolverStatus:"<a>",
resolverMode:"<b>",
sourceSearchStatus:"<c>",
sourceSearchMode:"<d>",
sourceCertificate:"<e>",
resolutions:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeResolverRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-resolver-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeResolverRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()