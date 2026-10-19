import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-panel-adapter.js"
)

class RuntimePanelAdapterTests(
unittest.TestCase
):

    def run_json(self,script):

        r=subprocess.run(
            ["node","-e",script],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        return json.loads(
            r.stdout
        )

    def test_syntax(self):

        subprocess.run(
            ["node","--check",FILE],
            check=True
        )

    def test_panel(self):

        data=self.run_json("""
const {
createRuntimePanelAdapter
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-panel-adapter.js"
);

console.log(
JSON.stringify(
createRuntimePanelAdapter({})
)
);
""")

        self.assertTrue(
            data["panel"]["visible"]
        )

    def test_blocked(self):

        data=self.run_json("""
const {
createRuntimePanelAdapter
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-panel-adapter.js"
);

console.log(
JSON.stringify(
createRuntimePanelAdapter({})
)
);
""")

        self.assertFalse(
            data["capabilities"]["execute"]
        )

    def test_inspection(self):

        data=self.run_json("""
const {
createRuntimePanelAdapter,
inspectRuntimePanelAdapter
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-panel-adapter.js"
);

console.log(
JSON.stringify(
inspectRuntimePanelAdapter(
createRuntimePanelAdapter({})
)
)
);
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()