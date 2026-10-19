import json
import subprocess
import unittest


class IntegritySealTests(
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
createRuntimeUiIntegritySealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-integrity-seal-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiIntegritySealRecord({})
)
);

""")

        self.assertEqual(
            data["state"],
            "UI_INTEGRITY_SEAL_READY"
        )

    def test_entries(self):

        data=self.run_json("""

const {
deriveRuntimeUiIntegritySealEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-integrity-seal-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiIntegritySealEntries({
warnings:["x"]
})
)
);

""")

        self.assertIn(
            "runtime-ui-integrity-surface",
            data
        )

    def test_read_only(self):

        data=self.run_json("""

const {
inspectRuntimeUiIntegritySealRecord,
createRuntimeUiIntegritySealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-integrity-seal-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiIntegritySealRecord(
createRuntimeUiIntegritySealRecord({})
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
renderRuntimeUiIntegritySealPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-integrity-seal-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiIntegritySealPanel({
uiIntegritySealStatus:"<x>",
integritySealEntries:["<y>"]
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
compareRuntimeUiIntegritySealRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-integrity-seal-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiIntegritySealRecords(
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