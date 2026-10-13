import sys
sys.path.insert(0, ".")
from engines.phonology.sandhi_splitter import SandhiSplitter

s = SandhiSplitter()
for text in ("rāmaśca", "tacchrutvā", "rāmo'pi", "so 'bravīt"):
    result = s.split(text)
    print("==", text, "==")
    for r in result["splits"][:3]:
        tag = " (via expansion)" if r.get("from_expansion") else ""
        print("  %-12s + %-12s known=%s/%s%s" % (
            r["first"], r["second"], r["first_known"], r["second_known"], tag
        ))
    print()