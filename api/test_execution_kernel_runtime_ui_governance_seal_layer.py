import json
import subprocess
import unittest


class GovernanceSealTests(
unittest.TestCase
):

    def run_json(self,script):

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
createRuntimeUiGovernanceSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-governance-seal-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiGovernanceSealRecord({})
)
);

""")

        self.assertEqual(
            data["state"],
            "UI_GOVERNANCE_SEAL_READY"
        )

    def test_entries(self):

        data=self.run_json("""

const {
deriveRuntimeUiGovernanceSealEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-governance-seal-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiGovernanceSealEntries({})
)
);

""")

        self.assertIn(
            "runtime-ui-governance-surface",
            data
        )

    def test_read_only(self):

        data=self.run_json("""

const {
inspectRuntimeUiGovernanceSealRecord,
createRuntimeUiGovernanceSealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-governance-seal-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiGovernanceSealRecord(
createRuntimeUiGovernanceSealRecord({})
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
renderRuntimeUiGovernanceSealPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-governance-seal-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiGovernanceSealPanel({
uiGovernanceSealStatus:"<x>",
governanceSealEntries:["<y>"]
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
compareRuntimeUiGovernanceSealRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-governance-seal-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiGovernanceSealRecords(
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