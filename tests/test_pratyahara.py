"""
tests/test_pratyahara.py
Native unittest suite for Paninian Pratyahara Engine
"""
import unittest
from engine.phonology.pratyahara import is_member, interval, sthane_antaratamah

class TestPratyaharaEngine(unittest.TestCase):

    def test_memberships(self):
        self.assertTrue(is_member("इ", "अच्"))
        self.assertFalse(is_member("क्", "अच्"))
        self.assertTrue(is_member("य", "यण्"))
        self.assertTrue(is_member("ल", "यण्"))
        self.assertFalse(is_member("ह", "यण्"))

    def test_intervals(self):
        ac_set = set(interval("अच्"))
        self.assertEqual(ac_set, {"अ", "इ", "उ", "ऋ", "ऌ", "ए", "ओ", "ऐ", "औ"})
        
        yan_set = set(interval("यण्"))
        self.assertEqual(yan_set, {"य", "व", "र", "ल"})

    def test_hal_edge_case(self):
        hal_list = interval("हल्")
        self.assertIn("ह", hal_list)
        self.assertIn("य", hal_list)
        self.assertIn("ल", hal_list)
        self.assertEqual(len(hal_list), 34)

    def test_sthane_antaratamah(self):
        self.assertEqual(sthane_antaratamah("इ", ["य", "व", "र", "ल"]), "य")
        self.assertEqual(sthane_antaratamah("उ", ["य", "व", "र", "ल"]), "व")
        self.assertEqual(sthane_antaratamah("ऋ", ["उ", "र"]), "र")

if __name__ == "__main__":
    unittest.main()