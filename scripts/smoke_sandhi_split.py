import sys
sys.path.insert(0, ".")
from engines.phonology.sandhi_splitter import SandhiSplitter

s = SandhiSplitter()
for text in ("rāmaśca", "tacchrutvā", "rāmo'pi"):
    result = s.split(text)
    print("==", text, "==")
    for r in result["splits"][:5]:
        print("  %-10s + %-10s valid=%s" % (r["first"], r["second"], r["valid"]))
    print()