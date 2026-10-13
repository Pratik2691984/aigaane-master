import sys
sys.path.insert(0, ".")
from engines.lexicon.vidyut_kosha import VidyutKosha

print("loading kosha (this may take a few seconds)...")
k = VidyutKosha()
print("loaded. dhatu count:", k.dhatu_count)
print()

for word in ["rāma", "bhavati", "dharma", "rāmaḥ", "xyzzy"]:
    result = k.lookup(word)
    print("%-10s found=%-5s count=%d" % (word, result["found"], result["count"]))
    for e in result["entries"][:3]:
        gloss = e.get("gloss", {}).get("en", "")
        print("    lemma: %-10s avyaya=%-5s gloss=%s" % (
            e["lemma"], e["is_avyaya"], gloss[:50]
        ))
    print()

print("exists rāma:  ", k.exists("rāma"))
print("exists xyzzy: ", k.exists("xyzzy"))
print("exists rāmaḥ: ", k.exists("rāmaḥ"))
print("exists bhavati:", k.exists("bhavati"))
print()
print("gloss BU (en):", k.dhatu_gloss("BU", "en"))
print("gloss BU (sa):", k.dhatu_gloss("BU", "sa"))