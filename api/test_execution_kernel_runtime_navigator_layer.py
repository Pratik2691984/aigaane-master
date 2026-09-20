import json
import subprocess
import unittest


class RuntimeNavigatorTests(unittest.TestCase):

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
createRuntimeNavigatorRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-navigator-engine.js"
);

console.log(
JSON.stringify(
createRuntimeNavigatorRecord({})
));
""")
        self.assertEqual(data["state"], "NAVIGATOR_READY")

    def test_routes(self):
        data = self.run_json("""
const {
deriveRuntimeNavigatorRoutes
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-navigator-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeNavigatorRoutes({
warnings:["x"]
})
));
""")
        self.assertIn("warning-reference-navigator", data)

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeNavigatorRecord,
createRuntimeNavigatorRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-navigator-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeNavigatorRecord(
createRuntimeNavigatorRecord({})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["navigatorBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeNavigatorPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-navigator-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeNavigatorPanel({
navigatorStatus:"<a>",
navigatorMode:"<b>",
sourceResolverStatus:"<c>",
sourceResolverMode:"<d>",
sourceCertificate:"<e>",
routes:["<f>"]
})
));
""")
        self.assertIn("&lt;a&gt;", data["body"])
        self.assertIn("&lt;f&gt;", data["body"])

    def test_compare(self):
        data = self.run_json("""
const {
compareRuntimeNavigatorRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-navigator-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeNavigatorRecords(
{},
{}
)
));
""")
        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()