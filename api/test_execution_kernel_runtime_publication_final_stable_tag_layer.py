import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-publication-final-stable-tag.js"
)

class RuntimePublicationFinalStableTagTests(unittest.TestCase):

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
        subprocess.run(["node","--check",FILE],check=True)

    def test_tag(self):
        data=self.run_json("""
const {
createRuntimePublicationFinalStableTag
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-final-stable-tag.js"
);

console.log(JSON.stringify(
createRuntimePublicationFinalStableTag({})
));
""")

        self.assertTrue(data["tag"]["sealed"])
        self.assertFalse(data["capabilities"]["execute"])

    def test_no_writes(self):
        data=self.run_json("""
const {
createRuntimePublicationFinalStableTag
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-final-stable-tag.js"
);

console.log(JSON.stringify(
createRuntimePublicationFinalStableTag({})
));
""")

        self.assertFalse(
            data["capabilities"]["canonicalWrite"]
        )

    def test_inspector(self):

        data=self.run_json("""
const {
createRuntimePublicationFinalStableTag,
inspectRuntimePublicationFinalStableTag
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-final-stable-tag.js"
);

console.log(JSON.stringify(
inspectRuntimePublicationFinalStableTag(
createRuntimePublicationFinalStableTag({})
)
));
""")

        self.assertTrue(data["stable"])

if __name__=="__main__":
    unittest.main()