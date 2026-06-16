import json
import subprocess
import unittest


class RuntimeIndexTests(
    unittest.TestCase
):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )

        return json.loads(
            result.stdout
        )

    def test_create(self):

        data = self.run_json("""
const {
createRuntimeIndexRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-index-engine.js"
);

console.log(
JSON.stringify(
createRuntimeIndexRecord({})
));
""")

        self.assertEqual(
            data["state"],
            "INDEX_READY"
        )

    def test_entries(self):

        data = self.run_json("""
const {
deriveRuntimeIndexEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-index-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeIndexEntries({
warnings:["x"]
})
));
""")

        self.assertIn(
            "warning-reference-indexed",
            data
        )

    def test_read_only(self):

        data = self.run_json("""
const {
inspectRuntimeIndexRecord,
createRuntimeIndexRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-index-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeIndexRecord(
createRuntimeIndexRecord({})
)
));
""")

        self.assertTrue(
            data["readOnly"]
        )

    def test_renderer(self):

        data = self.run_json("""
const {
renderRuntimeIndexPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-index-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeIndexPanel({
indexStatus:"<a>",
indexMode:"<b>",
entries:["<c>"]
})
));
""")

        self.assertIn(
            "&lt;a&gt;",
            data["body"]
        )

    def test_compare(self):

        data = self.run_json("""
const {
compareRuntimeIndexRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-index-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeIndexRecords(
{},
{}
)
));
""")

        self.assertTrue(
            data["stable"]
        )


if __name__ == "__main__":
    unittest.main()