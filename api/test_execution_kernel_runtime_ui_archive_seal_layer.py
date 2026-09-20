import json
import subprocess
import unittest


class ArchiveSealTests(
unittest.TestCase
):

    def run_json(
        self,
        script
    ):

        result=subprocess.run(
            ["node","-e",script],
            capture_output=True,
            text=True,
            check=True
        )

        return json.loads(
            result.stdout
        )

    def test_create(self):

        data=self.run_json("""

const {
createRuntimeUiArchiveSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-archive-seal-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiArchiveSealRecord({})
)
);

""")

        self.assertEqual(
            data["state"],
            "UI_ARCHIVE_SEAL_READY"
        )

    def test_entries(self):

        data=self.run_json("""

const {
deriveRuntimeUiArchiveSealEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-archive-seal-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiArchiveSealEntries({
warnings:["x"]
})
)
);

""")

        self.assertIn(
            "runtime-ui-archive-surface",
            data
        )

    def test_read_only(self):

        data=self.run_json("""

const {
inspectRuntimeUiArchiveSealRecord,
createRuntimeUiArchiveSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-archive-seal-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiArchiveSealRecord(
createRuntimeUiArchiveSealRecord({})
)
)
);

""")

        self.assertTrue(
            data["readOnly"]
        )

        self.assertTrue(
            data["canonicalWriteBlocked"]
        )

    def test_renderer(self):

        data=self.run_json("""

const {
renderRuntimeUiArchiveSealPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-archive-seal-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiArchiveSealPanel({
uiArchiveSealStatus:"<x>",
archiveSealEntries:["<y>"]
})
)
);

""")

        self.assertIn(
            "&lt;x&gt;",
            data["body"]
        )

    def test_compare(self):

        data=self.run_json("""

const {
compareRuntimeUiArchiveSealRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-archive-seal-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiArchiveSealRecords(
{},
{}
)
)
);

""")

        self.assertTrue(
            data["stable"]
        )


if __name__=="__main__":
    unittest.main()