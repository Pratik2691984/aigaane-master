import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-publication-final-renderer.js"
)

class RuntimePublicationFinalRendererTests(
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

    def test_render(self):

        data=self.run_json("""
const {
renderRuntimePublicationFinal
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-final-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimePublicationFinal({})
)
);
""")

        self.assertTrue(
            data["diagnostics"]["rendered"]
        )

    def test_execution_block(self):

        data=self.run_json("""
const {
renderRuntimePublicationFinal
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-final-renderer.js"
);

console.log(
JSON.stringify(
renderRuntimePublicationFinal({})
)
);
""")

        self.assertFalse(
            data["capabilities"]["execute"]
        )

    def test_inspector(self):

        data=self.run_json("""
const {
renderRuntimePublicationFinal,
inspectRuntimePublicationRenderer
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-final-renderer.js"
);

console.log(
JSON.stringify(
inspectRuntimePublicationRenderer(
renderRuntimePublicationFinal({})
)
)
);
""")

        self.assertTrue(
            data["rendered"]
        )

if __name__=="__main__":
    unittest.main()