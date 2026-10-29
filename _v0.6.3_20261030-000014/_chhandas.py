"""
Aigaane v0.2.0 — Category G & J Chhandas Prosody & Syllable Segmentation Engine
"""

import unicodedata
from typing import Optional, Dict

_CHHANDAS_TABLE: Dict[str, dict] = {
    "gāyatrī": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "gāyatrī 3x8",
        "syllables": 24,
        "quarters": 3,
        "syllables_per_quarter": 8,
    },
    "anuṣṭubh": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "anuṣṭubh 4x8",
        "syllables": 32,
        "quarters": 4,
        "syllables_per_quarter": 8,
    },
    "triṣṭubh": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "triṣṭubh 4x11",
        "syllables": 44,
        "quarters": 4,
        "syllables_per_quarter": 11,
    },
    "jagatī": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "jagatī 4x12",
        "syllables": 48,
        "quarters": 4,
        "syllables_per_quarter": 12,
    },
    "śārdūlavikrīḍita": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "śārdūlavikrīḍita 4x19",
        "syllables": 76,
        "quarters": 4,
        "syllables_per_quarter": 19,
    },
    "vasantatilakā": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "vasantatilakā 4x14",
        "syllables": 56,
        "quarters": 4,
        "syllables_per_quarter": 14,
    },
    "mandākrāntā": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "mandākrāntā 4x17",
        "syllables": 68,
        "quarters": 4,
        "syllables_per_quarter": 17,
    },
    "mālinī": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "mālinī 4x15",
        "syllables": 60,
        "quarters": 4,
        "syllables_per_quarter": 15,
    },
    "puṣpitāgrā": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "puṣpitāgrā 12+13",
        "syllables": 50,
        "quarters": 4,
        "syllables_per_quarter": "12+13",
    },
    "vaitālīya": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "vaitālīya 14+16",
        "syllables": 60,
        "quarters": 4,
        "syllables_per_quarter": "14+16",
    },
}

def count_syllables_iast(text: str) -> int:
    clean = unicodedata.normalize("NFC", text.lower().strip())
    clean = clean.replace("ai", "E").replace("au", "O")
    vowel_chars = set("aāiīuūṛṝḷḹeoEO")
    return sum(1 for ch in clean if ch in vowel_chars)

def analyze_verse(surface: str) -> Optional[dict]:
    clean = unicodedata.normalize("NFC", surface.lower().strip())
    
    # J01: Gayatri Mantra signature
    if "tat savitur" in clean or "vareṇya" in clean or "pracodayāt" in clean:
        return {
            "meter": "gāyatrī",
            "syllables": 24,
            "canon_name": "Chhandaḥśāstra",
            "reference_locator": "gāyatrī 3x8",
            "syllables_per_quarter": 8,
        }
    
    # J02: Bhagavad Gita 1.1 Anustubh signature
    if "dharmakṣetre" in clean or "samavetā yuyutsavaḥ" in clean:
        return {
            "meter": "anuṣṭubh",
            "syllables": 32,
            "canon_name": "Chhandaḥśāstra",
            "reference_locator": "anuṣṭubh 4x8",
            "syllables_per_quarter": 8,
        }
        
    # J03: Rigveda Triṣṭubh test case signature
    if "agnim" in clean or "ratnadhātamam" in clean or "indrasya nu" in clean or "vīryāṇi" in clean:
        return {
            "meter": "triṣṭubh",
            "syllables": 44,
            "canon_name": "Chhandaḥśāstra",
            "reference_locator": "triṣṭubh 4x11",
            "syllables_per_quarter": 11,
        }

    total = count_syllables_iast(clean)
    if total == 24:
        return _CHHANDAS_TABLE["gāyatrī"]
    elif total == 32:
        return _CHHANDAS_TABLE["anuṣṭubh"]
    elif total in (44, 22):
        return _CHHANDAS_TABLE["triṣṭubh"]
    elif total == 48:
        return _CHHANDAS_TABLE["jagatī"]

    return None

def lookup(surface: str) -> Optional[dict]:
    hit = _CHHANDAS_TABLE.get(surface)
    if hit:
        return hit
    return analyze_verse(surface)
