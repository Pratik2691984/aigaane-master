import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from api.kernel_api import app


class TestChandasVrtta(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_indravajra_recognition(self):
        r = self.client.post(
            "/api/v3/chandas/vrtta",
            json={"text": "udbhidyate yasya na bhūtabhāvo jñānaṃ ca sarvatra samāsahāyam"},
        )
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertIn("indravajrA", data["matched_meters"])
        self.assertEqual(data["padas"][0]["padya"], "indravajrA")
        self.assertEqual(data["padas"][0]["akshara_count"], 22)

    def test_gibberish_response_shape(self):
        r = self.client.post(
            "/api/v3/chandas/vrtta",
            json={"text": "abcdefghij"},
        )
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertIsInstance(data["matched_meters"], list)
        self.assertGreaterEqual(data["pada_count"], 1)
        self.assertIn("padas", data)

    def test_multi_pada_split_on_pipe(self):
        r = self.client.post(
            "/api/v3/chandas/vrtta",
            json={"text": "udbhidyate yasya na bhūtabhāvo | jñānaṃ ca sarvatra samāsahāyam"},
        )
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertGreaterEqual(data["pada_count"], 2)

    def test_devanagari_input(self):
        r = self.client.post(
            "/api/v3/chandas/vrtta",
            json={"text": "उद्भिद्यते यस्य न भूतभावो", "script": "devanagari"},
        )
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertGreater(data["known_vrttas"], 100)

    def test_empty_text_returns_422(self):
        r = self.client.post("/api/v3/chandas/vrtta", json={"text": ""})
        self.assertEqual(r.status_code, 422)


if __name__ == "__main__":
    unittest.main()