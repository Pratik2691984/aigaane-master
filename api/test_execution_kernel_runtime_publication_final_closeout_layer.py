import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-publication-final-closeout.js"
)

class RuntimePublicationFinalCloseoutTests(unittest.TestCase):

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

    def test_closeout(self):
        data=self.run_json("""
const {
createRuntimePublicationFinalCloseout
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-final-closeout.js"
);

console.log(JSON.stringify(
createRuntimePublicationFinalCloseout({})
));
""")
        self.assertTrue(data["closeout"]["sealed"])
        self.assertTrue(data["closeout"]["closed"])

    def test_capabilities_blocked(self):
        data=self.run_json("""
const {
createRuntimePublicationFinalCloseout
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-final-closeout.js"
);

console.log(JSON.stringify(
createRuntimePublicationFinalCloseout({})
));
""")
        self.assertFalse(data["capabilities"]["execute"])
        self.assertFalse(data["capabilities"]["publish"])
        self.assertFalse(data["capabilities"]["canonicalWrite"])

    def test_inspector(self):
        data=self.run_json("""
const {
createRuntimePublicationFinalCloseout,
inspectRuntimePublicationFinalCloseout
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-final-closeout.js"
);

console.log(JSON.stringify(
inspectRuntimePublicationFinalCloseout(
createRuntimePublicationFinalCloseout({})
)
));
""")
        self.assertTrue(data["ready"])
        self.assertTrue(data["sealed"])
        self.assertTrue(data["closed"])

if __name__=="__main__":
    unittest.main()