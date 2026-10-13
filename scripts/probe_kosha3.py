from vidyut.kosha import Kosha
from vidyut.lipi import transliterate, Scheme

k = Kosha("C:/aigaane-master/data/vidyut/kosha")

for word_iast in ["rāma", "rāmaḥ", "bhavati", "gam", "rāmo'pi", "dharma", "xyzzy"]:
    slp1 = transliterate(word_iast, Scheme.Iast, Scheme.Slp1)
    entries = k.get(slp1)
    print(f"== {word_iast} (SLP1: {slp1}) ==")
    if not entries:
        print("  (no entries)")
    else:
        for e in entries[:4]:
            print("  type:", type(e).__name__)
            print("  lemma:", e.lemma)
            print("  is_avyaya:", e.is_avyaya)
            try:
                sub = e.Subanta
                print("  Subanta:", sub)
            except Exception as ex:
                print("  Subanta accessor failed:", ex)
            try:
                tin = e.Tinanta
                print("  Tinanta:", tin)
            except Exception as ex:
                print("  Tinanta accessor failed:", ex)
            print()
    print()