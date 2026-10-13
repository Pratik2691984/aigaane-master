import sys
sys.path.insert(0, ".")
from engines.morphology.tinanta_engine import TinantaEngine

e = TinantaEngine()
result = e.conjugate_grid(root="bhū", gana=1, lakara="lat", prayoga="kartari")

print("root:", result["root"], "| slp1:", result["root_slp1"])
print("gana:", result["gana"], "| lakara:", result["lakara"], "| prayoga:", result["prayoga"])
print()

for p in ("prathama", "madhyama", "uttama"):
    row = result["paradigm"][p]
    eka = row["eka"]
    dvi = row["dvi"]
    bahu = row["bahu"]
    print(p, "eka=", eka, " dvi=", dvi, " bahu=", bahu)

first = result["sutra_traces"]["prathama_eka"]
print()
print("trace for prathama_eka has", len(first), "steps")
for step in first[:5]:
    print("  ", step["code"], "->", step["result"])