"""
engines/phonology/pratyahara.py
Śiva Sūtra Interval Indexer — Aṣṭādhyāyī 1.1.71, 1.3.9
"""

from typing import Dict, FrozenSet, List, Tuple

SIVA_SUTRAS: List[Tuple[str, ...]] = [
    ("a", "i", "u", "ṇ"),
    ("ṛ", "ḷ", "k"),
    ("e", "o", "ṅ"),
    ("ai", "au", "c"),
    ("ha", "ya", "va", "ra", "ṭ"),
    ("la", "ṇ"),
    ("ña", "ma", "ṅa", "ṇa", "na", "m"),
    ("jha", "bha", "ñ"),
    ("gha", "ḍha", "dha", "ṣ"),
    ("ja", "ba", "ga", "ḍa", "da", "ś"),
    ("kha", "pha", "cha", "ṭha", "tha", "ca", "ṭa", "ta", "v"),
    ("ka", "pa", "y"),
    ("śa", "ṣa", "sa", "r"),
    ("ha", "l"),
]


class PratyaharaEngine:
    def __init__(self, sutras: List[Tuple[str, ...]] = SIVA_SUTRAS):
        self.sutras = sutras
        self._stream: List[Tuple[str, bool]] = []
        self._it_markers: FrozenSet[str] = frozenset()
        self._cache: Dict[str, FrozenSet[str]] = {}
        self._compile()

    def _compile(self) -> None:
        markers = set()
        for sutra in self.sutras:
            *phonemes, it_marker = sutra
            for ph in phonemes:
                self._stream.append((ph, False))
            self._stream.append((it_marker, True))
            markers.add(it_marker)
        self._it_markers = frozenset(markers)

    def _find_interval(self, start: str, end_marker: str) -> Tuple[int, int]:
        starts = [i for i, (ph, is_it) in enumerate(self._stream)
                  if not is_it and ph == start]
        if not starts:
            raise ValueError(f"Phoneme '{start}' not found in Śiva Sūtras.")
        ends = [j for j, (ph, is_it) in enumerate(self._stream)
                if is_it and ph == end_marker]
        if not ends:
            raise ValueError(f"'{end_marker}' is not a valid it-sañjñā.")
        for i in starts:
            for j in ends:
                if i < j:
                    return i, j
        raise ValueError(f"No valid interval for '{start}{end_marker}'.")

    @staticmethod
    def _strip_inherent_a(token: str) -> str:
        """Strip trailing 'a' from a consonant syllable (ya -> y, ka -> k)."""
        if len(token) > 1 and token.endswith("a"):
            return token[:-1]
        return token

    def generate(self, pratyahara: str) -> FrozenSet[str]:
        if pratyahara in self._cache:
            return self._cache[pratyahara]
        if len(pratyahara) < 2:
            raise ValueError(f"Invalid pratyāhāra: '{pratyahara}'")

        # Try 2-character start first (ya, va, ra, la, ka, ...),
        # then fall back to 1-character (a, i, u, ṛ, ḷ, e, o, ...).
        last_error = None
        for start_len in (2, 1):
            start = pratyahara[:start_len]
            end_marker = pratyahara[start_len:]
            if not end_marker:
                continue
            try:
                i, j = self._find_interval(start, end_marker)
                result = frozenset(
                    self._strip_inherent_a(ph)
                    for ph, is_it in self._stream[i:j]
                    if not is_it
                )
                self._cache[pratyahara] = result
                return result
            except ValueError as e:
                last_error = e
                continue
        raise last_error or ValueError(f"No valid interval for '{pratyahara}'.")

    @property
    def stream(self) -> List[Tuple[str, bool]]:
        return list(self._stream)

    @property
    def it_markers(self) -> FrozenSet[str]:
        return self._it_markers


if __name__ == "__main__":
    pe = PratyaharaEngine()
    assert pe.generate("ac") == frozenset(
        {"a", "i", "u", "ṛ", "ḷ", "e", "o", "ai", "au"}
    )
    assert pe.generate("yaṇ") == frozenset({"y", "v", "r", "l"}), pe.generate("yaṇ")
    assert pe.generate("laṇ") == frozenset({"l"}), pe.generate("laṇ")
    assert pe.generate("ac").isdisjoint(pe.generate("hal"))
    print("✓ pratyahara.py OK")
