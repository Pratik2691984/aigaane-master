import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-publication-stable-git-tag.js"
)

class RuntimePublicationStableGitTagTests(
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

    def test_ready(self):

        data=self.run_json("""
const {
createRuntimePublicationStableGitTag
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-stable-git-tag.js"
);

console.log(
JSON.stringify(
createRuntimePublicationStableGitTag({})
)
);
""")

        self.assertTrue(
            data["tag"]["ready"]
        )

    def test_no_publish(self):

        data=self.run_json("""
const {
createRuntimePublicationStableGitTag
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-stable-git-tag.js"
);

console.log(
JSON.stringify(
createRuntimePublicationStableGitTag({})
)
);
""")

        self.assertFalse(
            data["capabilities"]["push"]
        )

    def test_inspector(self):

        data=self.run_json("""
const {
createRuntimePublicationStableGitTag,
inspectRuntimePublicationStableGitTag
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-stable-git-tag.js"
);

console.log(
JSON.stringify(
inspectRuntimePublicationStableGitTag(
createRuntimePublicationStableGitTag({})
)
)
);
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()