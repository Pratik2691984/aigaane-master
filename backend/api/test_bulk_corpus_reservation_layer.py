import json
import subprocess
import unittest


class BulkCorpusReservationTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def test_reservation_script_empty_manifest(self):
        result = subprocess.run(
            ["python", "scripts/reserve_bulk_corpus_capacity.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["totalRequested"], 2000)
        self.assertEqual(data["totalReserved"], 2000)
        self.assertFalse(data["canonicalWriteAllowed"])
        self.assertFalse(data["reservationWriteAllowed"])

    def test_reservation_ready(self):
        data = self.run_json("""
const {
summarizeCorpusReservation
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-reservation-engine.js");

console.log(JSON.stringify(summarizeCorpusReservation({
batches:[{
batchId:"b1",
lineage:"lineage-1",
records:[
{id:"d1",type:"dhatu",text:"भू",source:"source-1"},
{id:"s1",type:"sutra",text:"अदर्शनं लोपः",source:"source-2"}
]
}]
})));
""")
        self.assertTrue(data["valid"])
        self.assertEqual(data["totalRequested"], 2000)
        self.assertEqual(data["totalReserved"], 1998)
        self.assertEqual(data["totalUnreserved"], 2)

    def test_limited_reservation_warning(self):
        data = self.run_json("""
const {
buildReservations
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-reservation-engine.js");

console.log(JSON.stringify(buildReservations({
dhatu:{remaining:1},
sutra:{remaining:0},
stotra:{remaining:0}
}, {
dhatu:2,
sutra:1,
stotra:1
})));
""")
        self.assertIn("dhatu:reservationLimited", data["warnings"])
        self.assertIn("sutra:reservationLimited", data["warnings"])
        self.assertIn("stotra:reservationLimited", data["warnings"])

    def test_custom_reservation(self):
        data = self.run_json("""
const {
summarizeCorpusReservation
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-reservation-engine.js");

console.log(JSON.stringify(summarizeCorpusReservation({}, {
dhatu:10,
sutra:5,
stotra:2
})));
""")
        self.assertEqual(data["totalRequested"], 17)
        self.assertEqual(data["totalReserved"], 17)
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_renderer_escapes(self):
        data = self.run_json("""
const {
renderCorpusReservationPanel
}=require("./ui/tabs/sanskrit/corpus-staging/corpus-reservation-renderer.js");

console.log(JSON.stringify(renderCorpusReservationPanel({
state:"<bad>",
valid:false,
warnings:["<warn>"],
errors:["<err>"]
})));
""")
        self.assertIn("&lt;bad&gt;", data["body"])
        self.assertIn("&lt;warn&gt;", data["body"])
        self.assertIn("&lt;err&gt;", data["body"])


if __name__ == "__main__":
    unittest.main()