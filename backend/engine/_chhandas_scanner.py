import sys
from pathlib import Path
from typing import Dict, Any, List

# Ensure backend path is on sys.path if needed
backend_dir = Path(__file__).resolve().parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

try:
    from aigaane.chandas import scan_iast
except ImportError:
    # Direct fallback implementation matching Piṅgala rules
    SHORT_VOWELS = {'a', 'i', 'u', 'ṛ', 'ḷ'}
    LONG_VOWELS  = {'ā', 'ī', 'ū', 'ṝ', 'e', 'o'}
    DIPHTHONGS   = {'ai', 'au'}
    SIGNS        = {'ṃ', 'ḥ'}
    VOWELS       = SHORT_VOWELS | LONG_VOWELS | DIPHTHONGS

    def scan_iast(text: str) -> List[str]:
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


def scan_text(text: str) -> Dict[str, Any]:
    """
    Performs deterministic Piṅgala Chandas scansion on Sanskrit IAST text.
    Returns meter identification, syllable count, and weight vector.
    """
    weights = scan_iast(text)
    n = len(weights)
    pattern = "".join(weights)

    if n in (8, 16, 24, 32):
        meter_name = "anuṣṭubh"
    elif n in (11, 22, 33, 44):
        meter_name = "triṣṭubh"
    elif n in (12, 24, 36, 48):
        meter_name = "jagatī"
    elif n in (7, 14, 21):
        meter_name = "gāyatrī"
    else:
        meter_name = "anuṣṭubh" if n >= 8 else "classical_vrtta"

    return {
        "meter": meter_name,
        "syllables": n,
        "pattern": pattern,
        "syllable_weights": weights,
        "matras": [2 if w == "G" else 1 for w in weights],
        "total_matras": sum(2 if w == "G" else 1 for w in weights)
    }
