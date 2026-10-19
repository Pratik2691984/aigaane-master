import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-closeout-stable-tag.js"
)

class StableTagTests(
unittest.TestCase
):

    def run_json(
        self,
        script
    ):
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

    def test_stable_tag(self):

        result=self.run_json("""
const {
createExecutionKernelStableTag
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-closeout-stable-tag.js"
);

console.log(
JSON.stringify(
createExecutionKernelStableTag({})
)
);
""")

        self.assertTrue(
            result["closeout"]["sealed"]
        )

        self.assertFalse(
            result["closeout"]["executionEnabled"]
        )

    def test_diagnostics(self):

        result=self.run_json("""
const {
createExecutionKernelStableTag,
getExecutionKernelStableTagDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-closeout-stable-tag.js"
);

console.log(
JSON.stringify(
getExecutionKernelStableTagDiagnostics(
createExecutionKernelStableTag({})
)
));
""")

        self.assertTrue(
            result["ready"]
        )

    def test_renderer_link(self):

        result=self.run_json("""
const {
createExecutionKernelStableTag
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-closeout-stable-tag.js"
);

console.log(
JSON.stringify(
createExecutionKernelStableTag({})
)
);
""")

        self.assertIn(
            "renderer",
            result
        )

if __name__=="__main__":
    unittest.main()