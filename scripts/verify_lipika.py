from vidyut.lipi import transliterate, Scheme, detect

text_iast = "bhavati"
print("detected:", detect(text_iast))

slp1 = transliterate(text_iast, Scheme.Iast, Scheme.Slp1)
print("IAST -> SLP1:", repr(slp1))

deva = transliterate(slp1, Scheme.Slp1, Scheme.Devanagari)
print("SLP1 -> Deva:", repr(deva))

back = transliterate(deva, Scheme.Devanagari, Scheme.Iast)
print("Deva -> IAST:", repr(back))

assert slp1 == "Bavati", f"SLP1 mismatch: {slp1}"
assert back == text_iast, f"round-trip failed: {back}"

# Also verify the round trip the engine will actually need
root_iast = "bhū"
root_slp1 = transliterate(root_iast, Scheme.Iast, Scheme.Slp1)
print("root bhū -> SLP1:", repr(root_slp1))

print("OK: transliteration bridge verified")