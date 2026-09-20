"""
engine/phonology/pratyahara.py
Pāṇinian Pratyāhāra Interval Generator (1.1.71) & Phonetic Distance (1.1.50)
"""
from typing import List, Set, Dict, Tuple

# Explicit tuples prevent Python string-slicing errors on Devanagari halant markers
MAHESHVARA_SUTRAS: List[Tuple[Tuple[str, ...], str]] = [
    (("अ", "इ", "उ"), "ण्"),
    (("ऋ", "ऌ"), "क्"),
    (("ए", "ओ"), "ङ्"),
    (("ऐ", "औ"), "च्"),
    (("ह", "य", "व", "र"), "ट्"),
    (("ल",), "ण्"),
    (("ञ", "म", "ङ", "ण", "न"), "म्"),
    (("झ", "भ"), "ञ्"),
    (("घ", "ढ", "ध"), "ष्"),
    (("ज", "ब", "ग", "ड", "द"), "श्"),
    (("ख", "फ", "छ", "ठ", "थ", "च", "ट", "त"), "व्"),
    (("क", "प"), "य्"),
    (("श", "ष", "स"), "र्"),
    (("ह",), "ल्")
]

# Coordinate System: (Sthāna, Ābhyantara-prayatna, Ghoṣa, Prāṇa)
# Sthāna: 1=Kantha, 2=Talu, 3=Murdha, 4=Danta, 5=Ostha
# Prayatna: 1=Vivrta, 2=Ishat-sprshta, 3=Sprshta
PHONETIC_COORDS: Dict[str, Tuple[int, int, int, int]] = {
    "अ": (1, 1, 1, 0), "आ": (1, 1, 1, 0),
    "इ": (2, 1, 1, 0), "ई": (2, 1, 1, 0),
    "उ": (5, 1, 1, 0), "ऊ": (5, 1, 1, 0),
    "ऋ": (3, 1, 1, 0), "ऌ": (4, 1, 1, 0),
    "ए": (2, 1, 1, 0), "ऐ": (2, 1, 1, 0),
    "ओ": (5, 1, 1, 0), "औ": (5, 1, 1, 0),
    "य": (2, 2, 1, 0), "व": (4, 2, 1, 0),
    "र": (3, 2, 1, 0), "ल": (4, 2, 1, 0),
    "क": (1, 3, 0, 0), "च": (2, 3, 0, 0), "ट": (3, 3, 0, 0), "त": (4, 3, 0, 0), "प": (5, 3, 0, 0)
}

def _build_registry() -> Tuple[List[str], Set[str]]:
    stream: List[str] = []
    it_markers: Set[str] = set()
    for phonemes, marker in MAHESHVARA_SUTRAS:
        stream.extend(phonemes)
        stream.append(f"MARKER_{marker}")
        it_markers.add(marker)
    return stream, it_markers

_STREAM, _MARKERS = _build_registry()

def interval(pratyahara: str) -> List[str]:
    """Generates the phoneme interval for a given pratyāhāra string (e.g., 'अच्', 'यण्', 'हल्')."""
    if len(pratyahara) < 2:
        raise ValueError("Pratyāhāra must be at least 2 characters.")

    start_char = pratyahara[0]
    end_marker = pratyahara[1:]

    if end_marker not in _MARKERS:
        raise ValueError(f"Invalid it-marker: {end_marker}")

    try:
        start_idx = _STREAM.index(start_char)
        target_marker = f"MARKER_{end_marker}"
        end_idx = _STREAM.index(target_marker, start_idx)
    except ValueError:
        raise ValueError(f"Could not resolve interval for {pratyahara}")

    # 1.3.9 tasya lopaḥ: exclude all markers
    return [char for char in _STREAM[start_idx:end_idx] if not char.startswith("MARKER_")]

def is_member(phoneme: str, pratyahara: str) -> bool:
    return phoneme in interval(pratyahara)

def sthane_antaratamah(target: str, candidates: List[str]) -> str:
    """Sūtra 1.1.50: Resolves closest phonetic substitute."""
    if target not in PHONETIC_COORDS:
        return candidates[0]

    target_c = PHONETIC_COORDS[target]

    def distance(candidate: str) -> Tuple[int, int, int]:
        if candidate not in PHONETIC_COORDS:
            return (99, 99, 99)
        cand_c = PHONETIC_COORDS[candidate]
        place_diff = abs(target_c[0] - cand_c[0])
        effort_diff = abs(target_c[1] - cand_c[1])
        ext_diff = abs(target_c[2] - cand_c[2]) + abs(target_c[3] - cand_c[3])
        return (place_diff, effort_diff, ext_diff)

    return min(candidates, key=distance)