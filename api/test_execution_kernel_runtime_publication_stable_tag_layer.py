import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-publication-stable-tag.js"
)

class RuntimePublicationStableTagTests(
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

    def test_tag(self):

        data=self.run_json("""
const {
createRuntimePublicationStableTag
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-stable-tag.js"
);

console.log(
JSON.stringify(
createRuntimePublicationStableTag({})
)
);
""")

        self.assertTrue(
            data["tag"]["immutable"]
        )

    def test_capabilities(self):

        data=self.run_json("""
const {
createRuntimePublicationStableTag
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-stable-tag.js"
);

console.log(
JSON.stringify(
createRuntimePublicationStableTag({})
)
);
""")

        self.assertFalse(
            data["capabilities"]["execute"]
        )

        self.assertFalse(
            data["capabilities"]["canonicalWrite"]
        )

    def test_diagnostics(self):

        data=self.run_json("""
const {
createRuntimePublicationStableTag,
getRuntimePublicationStableTagDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-stable-tag.js"
);

console.log(
JSON.stringify(
getRuntimePublicationStableTagDiagnostics(
createRuntimePublicationStableTag({})
)
));
""")

        self.assertTrue(
            data["ready"]
        )

if __name__=="__main__":
    unittest.main()