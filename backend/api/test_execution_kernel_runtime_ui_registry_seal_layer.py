import json
import subprocess
import unittest


class RegistrySealTests(
    unittest.TestCase
):

    def run_json(
        self,
        script
    ):
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
createRuntimeUiRegistrySealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-registry-seal-engine.js"
);

console.log(
JSON.stringify(
createRuntimeUiRegistrySealRecord({})
)
);

""")

        self.assertEqual(
            data["state"],
            "UI_REGISTRY_SEAL_READY"
        )

    def test_entries(self):

        data = self.run_json("""

const {
deriveRuntimeUiRegistrySealEntries
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-registry-seal-engine.js"
);

console.log(
JSON.stringify(
deriveRuntimeUiRegistrySealEntries({
warnings:["x"]
})
)
);

""")

        self.assertIn(
            "runtime-ui-registry-surface",
            data
        )

    def test_read_only(self):

        data = self.run_json("""

const {
inspectRuntimeUiRegistrySealRecord,
createRuntimeUiRegistrySealRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-registry-seal-engine.js"
);

console.log(
JSON.stringify(
inspectRuntimeUiRegistrySealRecord(
createRuntimeUiRegistrySealRecord({})
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

        data = self.run_json("""

const {
renderRuntimeUiRegistrySealPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-registry-seal-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimeUiRegistrySealPanel({
uiRegistrySealStatus:"<x>",
registrySealEntries:["<y>"]
})
)
);

""")

        self.assertIn(
            "&lt;x&gt;",
            data["body"]
        )

    def test_compare(self):

        data = self.run_json("""

const {
compareRuntimeUiRegistrySealRecords
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-ui-registry-seal-engine.js"
);

console.log(
JSON.stringify(
compareRuntimeUiRegistrySealRecords(
{},
{}
)
)
);

""")

        self.assertTrue(
            data["stable"]
        )


if __name__ == "__main__":
    unittest.main()