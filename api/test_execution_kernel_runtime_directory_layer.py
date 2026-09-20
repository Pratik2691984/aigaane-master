import json
import subprocess
import unittest


class RuntimeDirectoryTests(
    unittest.TestCase
):

    def run_json(
        self,
        script
    ):
        result = subprocess.run(
            [
                "node",
                "-e",
                script
            ],
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
createRuntimeDirectoryRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-directory-engine.js"
);

console.log(
JSON.stringify(
createRuntimeDirectoryRecord({})
));
""")

        self.assertEqual(
            data["state"],
            "DIRECTORY_READY"
        )

    def test_entries(self):

        data = self.run_json("""
const {
deriveRuntimeDirectoryEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-directory-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeDirectoryEntries({
warnings:["x"]
})
));
""")

        self.assertIn(
            "warning-reference-directory",
            data
        )

    def test_read_only(self):

        data = self.run_json("""
const {
inspectRuntimeDirectoryRecord,
createRuntimeDirectoryRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-directory-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeDirectoryRecord(
createRuntimeDirectoryRecord({})
)
));
""")

        self.assertTrue(
            data["readOnly"]
        )

    def test_renderer(self):

        data = self.run_json("""
const {
renderRuntimeDirectoryPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-directory-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeDirectoryPanel({
directoryStatus:"<a>",
directoryMode:"<b>",
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
compareRuntimeDirectoryRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-directory-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeDirectoryRecords(
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