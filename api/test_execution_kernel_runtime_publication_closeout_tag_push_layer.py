import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-publication-closeout-tag-push.js"
)

class RuntimePublicationCloseoutTagPushTests(
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

        return json.loads(r.stdout)

    def test_syntax(self):
        subprocess.run(
            ["node","--check",FILE],
            check=True
        )

    def test_closeout(self):

        data=self.run_json("""
const {
createRuntimePublicationCloseoutTagPush
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-closeout-tag-push.js"
);

console.log(JSON.stringify(
createRuntimePublicationCloseoutTagPush({})
));
""")

        self.assertTrue(
            data["closeout"]["prepared"]
        )

    def test_capabilities(self):

        data=self.run_json("""
const {
createRuntimePublicationCloseoutTagPush
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-closeout-tag-push.js"
);

console.log(JSON.stringify(
createRuntimePublicationCloseoutTagPush({})
));
""")

        self.assertFalse(
            data["capabilities"]["publish"]
        )

    def test_inspection(self):

        data=self.run_json("""
const {
createRuntimePublicationCloseoutTagPush,
inspectRuntimePublicationCloseoutTagPush
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-closeout-tag-push.js"
);

console.log(JSON.stringify(
inspectRuntimePublicationCloseoutTagPush(
createRuntimePublicationCloseoutTagPush({})
)
));
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()