import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from api.kernel_api import app


class TestTinantaRouter(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_conjugate_bhu_lat_returns_200(self):
        r = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"root": "bhū", "gana": 1, "lakara": "lat"},
        )
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertEqual(data["root_slp1"], "BU")
        self.assertEqual(data["paradigm"]["prathama"]["eka"], "bhavati")
        self.assertEqual(data["paradigm"]["madhyama"]["eka"], "bhavasi")
        self.assertEqual(data["paradigm"]["uttama"]["eka"], "bhavāmi")
        self.assertEqual(data["paradigm"]["prathama"]["bahu"], "bhavanti")

    def test_unknown_lakara_returns_422(self):
        r = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"root": "bhū", "gana": 1, "lakara": "bogus"},
        )
        self.assertEqual(r.status_code, 422)

    def test_unknown_gana_returns_422(self):
        r = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"root": "bhū", "gana": 99},
        )
        self.assertEqual(r.status_code, 422)

    def test_traces_included_when_requested(self):
        r = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"root": "bhū", "gana": 1, "lakara": "lat", "include_traces": True},
        )
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertIn("prathama_eka", data["sutra_traces"])
        trace = data["sutra_traces"]["prathama_eka"]
        self.assertGreater(len(trace), 0)
        for step in trace:
            self.assertIn("code", step)

    def test_devanagari_output(self):
        r = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"root": "bhū", "gana": 1, "lakara": "lat", "script": "devanagari"},
        )
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertEqual(data["paradigm"]["prathama"]["eka"], "भवति")


if __name__ == "__main__":
    unittest.main()