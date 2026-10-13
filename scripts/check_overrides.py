import sys
sys.path.insert(0, ".")
from engines.morphology.tinanta_engine import TinantaEngine

e = TinantaEngine()

cases = [
    ("bhū", 1, "bhavati"),
    ("gam", 1, "gacchati"),
    ("dā", 3, "dadāti"),
    ("dhā", 3, "dadhāti"),
    ("sthā", 1, "tiṣṭhati"),
]

for root, gana, expected in cases:
    r = e.conjugate_grid(root=root, gana=gana, lakara="lat")
    got = r["paradigm"]["prathama"]["eka"]
    ok = "OK" if got == expected else "MISMATCH"
    print("%-6s gana=%d  expected=%-10s got=%-10s %s" % (root, gana, expected, got, ok))