import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-tag-publisher.js"
)

class RuntimePublisherTests(
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

    def test_publish(self):

        data=self.run_json("""
const {
publishRuntimeTag
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-tag-publisher.js"
);

console.log(
JSON.stringify(
publishRuntimeTag({})
)
);
""")

        self.assertTrue(
            data["publication"]["published"]
        )

    def test_execute_disabled(self):

        data=self.run_json("""
const {
publishRuntimeTag
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-tag-publisher.js"
);

console.log(
JSON.stringify(
publishRuntimeTag({})
)
);
""")

        self.assertFalse(
            data["capabilities"]["execute"]
        )

    def test_diagnostics(self):

        data=self.run_json("""
const {
publishRuntimeTag,
getPublisherDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-tag-publisher.js"
);

console.log(
JSON.stringify(
getPublisherDiagnostics(
publishRuntimeTag({})
)
));
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()