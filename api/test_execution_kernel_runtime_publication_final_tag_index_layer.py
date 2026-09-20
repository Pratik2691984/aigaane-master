import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-publication-final-tag-index.js"
)

class RuntimePublicationFinalTagIndexTests(
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

    def test_index(self):

        data=self.run_json("""
const {
createRuntimePublicationFinalTagIndex
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-final-tag-index.js"
);

console.log(JSON.stringify(
createRuntimePublicationFinalTagIndex({})
));
""")

        self.assertTrue(
            data["diagnostics"]["indexed"]
        )

    def test_entries(self):

        data=self.run_json("""
const {
createRuntimePublicationFinalTagIndex
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-final-tag-index.js"
);

console.log(JSON.stringify(
createRuntimePublicationFinalTagIndex({})
));
""")

        self.assertGreaterEqual(
            len(data["tags"]),
            1
        )

    def test_inspector(self):

        data=self.run_json("""
const {
createRuntimePublicationFinalTagIndex,
inspectRuntimePublicationFinalTagIndex
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-final-tag-index.js"
);

console.log(JSON.stringify(
inspectRuntimePublicationFinalTagIndex(
createRuntimePublicationFinalTagIndex({})
)
));
""")

        self.assertTrue(
            data["indexed"]
        )

if __name__=="__main__":
    unittest.main()