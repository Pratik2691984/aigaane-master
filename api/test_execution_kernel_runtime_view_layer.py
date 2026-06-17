import json
import subprocess
import unittest


class RuntimeViewTests(unittest.TestCase):

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
createRuntimeViewRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-view-engine.js"
);

console.log(
JSON.stringify(
createRuntimeViewRecord({})
));
""")
        self.assertEqual(data["state"], "VIEW_READY")

    def test_views(self):
        data = self.run_json("""
const {
deriveRuntimeViews
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-view-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeViews({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-view", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeViewRecord,
createRuntimeViewRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-view-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeViewRecord(
createRuntimeViewRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["viewBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeViewPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-view-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeViewPanel({
viewStatus:"<a>",
viewMode:"<b>",
sourceSessionStatus:"<c>",
sourceSessionMode:"<d>",
sourceCertificate:"<e>",
views:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeViewRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-view-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeViewRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()