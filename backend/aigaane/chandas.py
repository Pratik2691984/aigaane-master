SHORT_VOWELS = {'a', 'i', 'u', 'ṛ', 'ḷ'}
LONG_VOWELS  = {'ā', 'ī', 'ū', 'ṝ', 'e', 'o'}
DIPHTHONGS   = {'ai', 'au'}
SIGNS        = {'ṃ', 'ḥ'}
VOWELS       = SHORT_VOWELS | LONG_VOWELS | DIPHTHONGS

def scan_iast(text: str) -> list[str]:
    s = text.strip().lower()
    phonemes = []
    i = 0
    while i < len(s):
        if s[i:i + 2] in DIPHTHONGS:
            phonemes.append(s[i:i + 2]); i += 2; continue
        ch = s[i]
        if ch in VOWELS or ch in SIGNS:
            phonemes.append(ch)
        elif ch.isalpha():
            phonemes.append(ch)
        i += 1

    weights = []
    for idx, p in enumerate(phonemes):
        if p not in VOWELS:
            continue
        if p in LONG_VOWELS or p in DIPHTHONGS:
            weights.append("G"); continue
        consonants = []
        for q in phonemes[idx + 1:]:
            if q in VOWELS:
                break
            consonants.append(q)
        if consonants and consonants[0] in SIGNS:
            weights.append("G"); continue
        if len(consonants) >= 2:
            weights.append("G"); continue
        weights.append("L")
    return weights
