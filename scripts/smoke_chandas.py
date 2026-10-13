import sys
sys.path.insert(0, ".")
from engines.chandas.vidyut_chandas import VidyutChandas

c = VidyutChandas()
print("known vrttas:", len(c._c.vrttas), "jatis:", len(c._c.jatis))
print()

# An indravajra pada (known to match from probe 4)
text = "udbhidyate yasya na bhūtabhāvo jñānaṃ ca sarvatra samāsahāyam"
result = c.scan(text)
print("input:", text)
print("matched:", result["matched_meters"])
for p in result["padas"]:
    print("  pada", p["index"], "padya:", p["padya"], "aksharas:", p["akshara_count"])
    print("    weights:", p["weights"][:40])