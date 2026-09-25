"""
scripts/transliterate.py
Devanagari → IAST transliteration.

Handles standard classical Sanskrit orthography:
  - Independent vowels (अ आ इ ...)
  - Consonants (क ख ग ...)
  - Vowel matras (ा ि ी ...)
  - Virama (्) — conjunct clusters
  - Anusvara (ं), Visarga (ः), Candrabindu (ँ)
  - Nukta (़) for loan consonants

Not handled (rare/edge cases):
  - Vedic svara marks (Udatta/Anudatta/Svarita) — stripped
  - Vedic-specific characters (॒ ॑ ᳚)
  - Regional variants beyond standard Hindi/Sanskrit

Usage:
    from scripts.transliterate import devanagari_to_iast
    iast = devanagari_to_iast("धर्मक्षेत्रे")
    # → "dharmakṣetre"
"""

import re
from typing import Optional

# --- Vowels (independent) ---
INDEPENDENT_VOWELS = {
    'अ': 'a',   'आ': 'ā',   'इ': 'i',   'ई': 'ī',
    'उ': 'u',   'ऊ': 'ū',   'ऋ': 'ṛ',   'ॠ': 'ṝ',
    'ऌ': 'ḷ',   'ॡ': 'ḹ',   'ए': 'e',   'ऐ': 'ai',
    'ओ': 'o',   'औ': 'au',  'ऍ': 'ê',   'ऑ': 'ô',
    'ॐ': 'oṃ',  # Om — single character, treated as a complete syllable
}

# --- Vowel matras (dependent) ---
MATRAS = {
    'ा': 'ā',   'ि': 'i',   'ी': 'ī',
    'ु': 'u',   'ू': 'ū',   'ृ': 'ṛ',
    'ॄ': 'ṝ',   'ॢ': 'ḷ',   'ॣ': 'ḹ',
    'े': 'e',   'ै': 'ai',  'ो': 'o',
    'ौ': 'au',
}

# --- Consonants ---
CONSONANTS = {
    # Velar (kaṇṭhya)
    'क': 'k',   'ख': 'kh',  'ग': 'g',   'घ': 'gh',  'ङ': 'ṅ',
    # Palatal (tālavya)
    'च': 'c',   'छ': 'ch',  'ज': 'j',   'झ': 'jh',  'ञ': 'ñ',
    # Retroflex (mūrdhanya)
    'ट': 'ṭ',   'ठ': 'ṭh',  'ड': 'ḍ',   'ढ': 'ḍh',  'ण': 'ṇ',
    # Dental (dantya)
    'त': 't',   'थ': 'th',  'द': 'd',   'ध': 'dh',  'न': 'n',
    # Labial (oṣṭhya)
    'प': 'p',   'फ': 'ph',  'ब': 'b',   'भ': 'bh',  'म': 'm',
    # Semivowels (antastha)
    'य': 'y',   'र': 'r',   'ल': 'l',   'व': 'v',
    # Sibilants (ūṣman)
    'श': 'ś',   'ष': 'ṣ',   'स': 's',
    # Aspirate
    'ह': 'h',
    # Retroflex lateral (Vedic)
    'ळ': 'ḻ',
    # Common with nukta
    'क़': 'q',  'ख़': 'x',  'ग़': 'ġ',  'ज़': 'z',
    'ड़': 'ṛ',  'ढ़': 'ṛh', 'फ़': 'f',
}

# --- Modifiers ---
MODIFIERS = {
    'ं': 'ṃ',   # anusvara
    'ँ': 'm̐',   # candrabindu (may not render)
    'ः': 'ḥ',   # visarga
    '्': '',    # virama — drops inherent vowel
    'ऽ': "'",   # avagraha
    '़': '',    # nukta — handled by consonant map
}

# --- Vedic svara marks (stripped) ---
SVARA_MARKS = '॒॑᳚'

# --- Punctuation that should be preserved ---
PRESERVE = set(' \t\n।॥|.,;:!?()[]{}"\'–—-')

# --- Pre-compile the classifier ---
_DEVA_RANGE = re.compile(r'[\u0900-\u097F]')


def devanagari_to_iast(text: str) -> str:
    """
    Convert Devanagari to IAST. Handles conjuncts via virama.

    Returns the IAST string, or the original if input isn't Devanagari.
    """
    if not text or not isinstance(text, str):
        return text or ''

    # If there's no Devanagari, return as-is
    if not _DEVA_RANGE.search(text):
        return text

    out = []
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]

        # Skip Vedic svara marks
        if ch in SVARA_MARKS:
            i += 1
            continue

        # Preserve whitespace and punctuation
        if ch in PRESERVE:
            out.append(ch)
            i += 1
            continue

        # Independent vowel
        if ch in INDEPENDENT_VOWELS:
            out.append(INDEPENDENT_VOWELS[ch])
            i += 1
            continue

        # Consonant
        if ch in CONSONANTS:
            consonant = CONSONANTS[ch]
            i += 1

            # Look ahead for a matra or virama
            if i < n:
                nxt = text[i]

                # Virama → suppress inherent vowel
                if nxt == '्':
                    out.append(consonant)
                    i += 1
                    continue

                # Matra → replace inherent vowel
                if nxt in MATRAS:
                    out.append(consonant + MATRAS[nxt])
                    i += 1
                    continue

            # No matra → inherent 'a'
            out.append(consonant + 'a')
            continue

        # Modifier (anusvara, visarga)
        if ch in MODIFIERS:
            out.append(MODIFIERS[ch])
            i += 1
            continue

        # Anything else — append as-is (unknown character)
        out.append(ch)
        i += 1

    # Post-process: clean up double vowels from virama + matra edge cases
    result = ''.join(out)
    # Fix ā after consonant (shouldn't happen, but defensive)
    result = re.sub(r'([^aeiouāīūṛṝḷḹ])a(?=[aāiīuūṛṝḷḹeaiou])', r'\1', result)
    return result


def transliterate_line(line: str) -> str:
    """Alias for readability."""
    return devanagari_to_iast(line)


# --- Self-test ---
if __name__ == '__main__':
    tests = [
        ('धर्मक्षेत्रे', 'dharmakṣetre'),
        ('कुरुक्षेत्रे', 'kurukṣetre'),
        ('समवेता', 'samavetā'),
        ('युयुत्सवः', 'yuyutsavaḥ'),
        ('कर्मण्येवाधिकारस्ते', 'karmaṇyevādhikāraste'),
        ('श्रीमद्भगवद्गीता', 'śrīmadbhagavadgītā'),
        ('ॐ', 'oṃ'),
        ('संस्कृतम्', 'saṃskṛtam'),
    ]
    pass_count = 0
    for deva, expected in tests:
        got = devanagari_to_iast(deva)
        ok = got == expected
        status = 'PASS' if ok else 'FAIL'
        print(f'  [{status}] {deva} → {got} (expected {expected})')
        if ok:
            pass_count += 1
    print(f'\n{pass_count}/{len(tests)} passed')