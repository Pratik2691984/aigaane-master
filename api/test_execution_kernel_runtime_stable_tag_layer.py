import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-stable-tag.js"
)

class RuntimeStableTagTests(
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

    def test_tag(self):

        data=self.run_json("""
const {
createRuntimeStableTag
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-stable-tag.js"
);

console.log(
JSON.stringify(
createRuntimeStableTag({})
)
);
""")

        self.assertTrue(
            data["tag"]["deterministic"]
        )

    def test_execute_disabled(self):

        data=self.run_json("""
const {
createRuntimeStableTag
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-stable-tag.js"
);

console.log(
JSON.stringify(
createRuntimeStableTag({})
)
);
""")

        self.assertFalse(
            data["capabilities"]["execute"]
        )

    def test_diagnostics(self):

        data=self.run_json("""
const {
createRuntimeStableTag,
getRuntimeStableDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-stable-tag.js"
);

console.log(
JSON.stringify(
getRuntimeStableDiagnostics(
createRuntimeStableTag({})
)
));
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()