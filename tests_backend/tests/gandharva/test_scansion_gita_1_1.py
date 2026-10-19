import unittest
from aigaane.chandas import scan_iast

class TestGandharvaScansion(unittest.TestCase):
    def test_gita_1_1_pada_1(self):
        self.assertEqual(scan_iast("dharmakṣetre kurukṣetre"), list("GGGGLGGG"))
    def test_gita_1_1_pada_2(self):
        self.assertEqual(scan_iast("samavetā yuyutsavaḥ"), list("LLGGLGLG"))
    def test_negative_input_sensitivity(self):
        self.assertNotEqual(scan_iast("dharmakṣetre"), scan_iast("rāmaḥ"))
    def test_half_verse_classification(self):
        weights = scan_iast("dharmakṣetre kurukṣetre samavetā yuyutsavaḥ")
        self.assertEqual(len(weights), 16)
        self.assertEqual("".join(weights), "GGGGLGGGLLGGLGLG")
