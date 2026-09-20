import json
import subprocess
import unittest


class RuntimeExplorerTests(unittest.TestCase):

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
createRuntimeExplorerRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-explorer-engine.js"
);

console.log(
JSON.stringify(
createRuntimeExplorerRecord({})
));
""")
        self.assertEqual(
            data["state"],
            "EXPLORER_READY"
        )

    def test_warning(self):
        data = self.run_json("""
const {
deriveRuntimeExplorerItems
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-explorer-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeExplorerItems({
warnings:["x"]
})
));
""")

        self.assertIn(
            "warning-reference-explorer",
            data
        )

    def test_read_only(self):
        data = self.run_json("""
const {
inspectRuntimeExplorerRecord,
createRuntimeExplorerRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-explorer-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeExplorerRecord(
createRuntimeExplorerRecord({})
)
));
""")

        self.assertTrue(data["readOnly"])

    def test_renderer(self):
        data = self.run_json("""
const {
renderRuntimeExplorerPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-explorer-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeExplorerPanel({
explorerStatus:"<a>",
items:["<b>"]
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
compareRuntimeExplorerRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-explorer-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeExplorerRecords(
{},
{}
)
));
""")

        self.assertTrue(data["stable"])


if __name__ == "__main__":
    unittest.main()