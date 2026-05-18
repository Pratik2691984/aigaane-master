from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import re
import time
import unicodedata


MAX_INPUT_CHARS = 2000
MAX_CANDIDATES = 96
MAX_SYLLABLES = 256
MAX_DERIVATION_STEPS = 64
PIPELINE_TIMEOUT_SECONDS = 1.5

LONG_VOWELS = {"a", "i", "u", "r", "l", "e", "o", "ai", "au"}
SHORT_VOWELS = {"a", "i", "u", "r", "l"}
VOWEL_PATTERN = r"(?:ai|au|[aeiou]|r|l)"
TOKEN_PATTERN = re.compile(r"[a-zA-Z]+")

LEXICON = {
    "agnim": ("agni", "fire; sacred fire"),
    "ile": ("id", "I praise"),
    "purohitam": ("purohita", "house priest; placed in front"),
    "yajnasya": ("yajna", "of the sacrifice"),
    "devam": ("deva", "shining one; deity"),
    "rtvijam": ("rtvij", "seasonal officiating priest"),
    "hotaram": ("hotr", "invoking priest"),
    "ratnadhatamam": ("ratnadhatama", "bestower of treasures"),
    "ramah": ("rama", "Rama"),
    "avadat": ("vad", "spoke"),
}

LEXICAL_SOURCE_GOVERNANCE = {
    "monier_williams": {"enabled": False, "license": None, "source_uri": None},
    "dcs": {"enabled": False, "license": None, "source_uri": None},
    "sanskrit_library": {"enabled": False, "license": None, "source_uri": None},
    "inria_corpus": {"enabled": False, "license": None, "source_uri": None},
    "structured_dhatu_datasets": {"enabled": False, "license": None, "source_uri": None},
}

INDEPENDENT_VOWELS = {
    "\u0905": "a", "\u0906": "a", "\u0907": "i", "\u0908": "i", "\u0909": "u",
    "\u090a": "u", "\u090b": "r", "\u0960": "r", "\u090c": "l", "\u090f": "e",
    "\u0910": "ai", "\u0913": "o", "\u0914": "au",
}

VOWEL_SIGNS = {
    "\u093e": "a", "\u093f": "i", "\u0940": "i", "\u0941": "u", "\u0942": "u",
    "\u0943": "r", "\u0944": "r", "\u0947": "e", "\u0948": "ai", "\u094b": "o",
    "\u094c": "au",
}

CONSONANTS = {
    "\u0915": "k", "\u0916": "kh", "\u0917": "g", "\u0918": "gh", "\u0919": "n",
    "\u091a": "c", "\u091b": "ch", "\u091c": "j", "\u091d": "jh", "\u091e": "n",
    "\u091f": "t", "\u0920": "th", "\u0921": "d", "\u0922": "dh", "\u0923": "n",
    "\u0924": "t", "\u0925": "th", "\u0926": "d", "\u0927": "dh", "\u0928": "n",
    "\u092a": "p", "\u092b": "ph", "\u092c": "b", "\u092d": "bh", "\u092e": "m",
    "\u092f": "y", "\u0930": "r", "\u0932": "l", "\u0933": "l", "\u0935": "v", "\u0936": "s",
    "\u0937": "s", "\u0938": "s", "\u0939": "h",
}

ANUSVARA = "\u0902"
VISARGA = "\u0903"
VIRAMA = "\u094d"
AVAGRAHA = "\u093d"


class SanskritTabException(Exception):
    status_code = 400
    code = "sanskrit_tab_error"

    def __init__(self, message: str, diagnostics: Optional[List[Dict[str, str]]] = None):
        super().__init__(message)
        self.message = message
        self.diagnostics = diagnostics or []


class SanskritInputException(SanskritTabException):
    code = "invalid_sanskrit_input"


class SanskritTimeoutException(SanskritTabException):
    status_code = 408
    code = "sanskrit_pipeline_timeout"


class SanskritPipelineException(SanskritTabException):
    status_code = 500
    code = "sanskrit_pipeline_error"


@dataclass
class UnicodeClusterNode:
    index: int
    text: str
    codepoints: List[str]


@dataclass
class PhonologicalSyllableNode:
    index: int
    text: str
    weight: str
    matra_count: int
    cluster_start: int
    cluster_end: int


@dataclass
class SyllableUnit:
    text: str
    vowel: str
    is_long: bool = False
    has_visarga: bool = False
    has_anusvara: bool = False
    has_halanta_coda: bool = False


def enforce_timeout(started_at: float) -> None:
    if time.monotonic() - started_at > PIPELINE_TIMEOUT_SECONDS:
        raise SanskritTimeoutException("Sanskrit analysis exceeded the deterministic time budget.")


def normalize_input(text: str) -> Tuple[str, List[Dict[str, str]]]:
    diagnostics: List[Dict[str, str]] = []
    if text is None:
        raise SanskritInputException("input_text is required.")
    if not isinstance(text, str):
        raise SanskritInputException("input_text must be a string.")
    if len(text) > MAX_INPUT_CHARS:
        raise SanskritInputException(f"input_text exceeds {MAX_INPUT_CHARS} characters.")

    try:
        normalized = unicodedata.normalize("NFC", text)
    except (TypeError, ValueError) as exc:
        raise SanskritInputException("input_text contains malformed Unicode.") from exc

    if any(0xD800 <= ord(char) <= 0xDFFF for char in normalized):
        diagnostics.append({"level": "warning", "message": "Malformed Unicode surrogate codepoint ignored."})
        normalized = "".join(char for char in normalized if not 0xD800 <= ord(char) <= 0xDFFF)

    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = "\n".join(re.sub(r"[ \t\f\v]+", " ", line).strip() for line in normalized.strip().split("\n"))
    normalized = re.sub(r"\n{2,}", "\n", normalized)
    if not normalized:
        diagnostics.append({"level": "warning", "message": "Empty input; no linguistic analysis performed."})
    return normalized, diagnostics


def is_devanagari(text: str) -> bool:
    return any("\u0900" <= char <= "\u097F" for char in text)


def transliterate_devanagari(text: str) -> Tuple[str, List[Dict[str, str]]]:
    output: List[str] = []
    diagnostics: List[Dict[str, str]] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char in CONSONANTS:
            base = CONSONANTS[char]
            next_char = text[index + 1] if index + 1 < len(text) else ""
            following = text[index + 2] if index + 2 < len(text) else ""
            if next_char in VOWEL_SIGNS:
                output.append(base + VOWEL_SIGNS[next_char])
                index += 2
                continue
            if next_char == VIRAMA:
                output.append(base)
                index += 2
                continue
            if next_char in (ANUSVARA, VISARGA):
                output.append(base + "a" + ("m" if next_char == ANUSVARA else "h"))
                index += 2
                continue
            if next_char in VOWEL_SIGNS and following in (ANUSVARA, VISARGA):
                output.append(base + VOWEL_SIGNS[next_char] + ("m" if following == ANUSVARA else "h"))
                index += 3
                continue
            output.append(base + "a")
        elif char in INDEPENDENT_VOWELS:
            output.append(INDEPENDENT_VOWELS[char])
        elif char in (ANUSVARA, VISARGA):
            output.append("m" if char == ANUSVARA else "h")
        elif char == AVAGRAHA:
            pass
        elif char.isspace() or char in {"|", "\u0964", "\u0965", ",", ".", ";", ":", "-", "\n", "\t"}:
            output.append(" ")
        elif char in VOWEL_SIGNS or char == VIRAMA:
            diagnostics.append({"level": "warning", "message": "Detached Devanagari mark ignored."})
        else:
            diagnostics.append({"level": "warning", "message": f"Unsupported character ignored: U+{ord(char):04X}"})
        index += 1
    return re.sub(r"\s+", " ", "".join(output)).strip(), diagnostics


def transliterate(text: str) -> Tuple[str, List[Dict[str, str]]]:
    if not is_devanagari(text):
        ascii_iast = (
            text.replace("\u0101", "a")
            .replace("\u012b", "i")
            .replace("\u016b", "u")
            .replace("\u1e5b", "r")
            .replace("\u1e5d", "r")
            .replace("\u1e37", "l")
            .replace("\u1e39", "l")
            .replace("\u1e45", "n")
            .replace("\u00f1", "n")
            .replace("\u1e6d", "t")
            .replace("\u1e0d", "d")
            .replace("\u1e47", "n")
            .replace("\u015b", "s")
            .replace("\u1e63", "s")
            .replace("\u1e43", "m")
            .replace("\u1e25", "h")
        )
        return re.sub(r"\s+", " ", ascii_iast).strip(), []
    return transliterate_devanagari(text)


def build_unicode_clusters(text: str, limit: int = MAX_CANDIDATES) -> List[UnicodeClusterNode]:
    clusters: List[UnicodeClusterNode] = []
    current = ""
    for char in text:
        if len(clusters) >= limit:
            break
        category = unicodedata.category(char)
        if not current or category.startswith("M"):
            current += char
        else:
            clusters.append(UnicodeClusterNode(len(clusters), current, [f"U+{ord(c):04X}" for c in current]))
            current = char
    if current and len(clusters) < limit:
        clusters.append(UnicodeClusterNode(len(clusters), current, [f"U+{ord(c):04X}" for c in current]))
    return clusters


def validate_transliteration(text: str) -> List[Dict[str, str]]:
    diagnostics: List[Dict[str, str]] = []
    invalid = re.findall(r"[^a-zA-Z\s|.,;:-]", text)
    if invalid:
        diagnostics.append({"level": "warning", "message": "Unsupported transliteration characters were ignored for syllable parsing."})
    if re.search(r"[aeiou]{4,}", text.lower()):
        diagnostics.append({"level": "warning", "message": "Unusually long vowel sequence detected."})
    return diagnostics


def split_syllables(text: str, started_at: float) -> List[str]:
    tokens = TOKEN_PATTERN.findall(text.lower())
    syllables: List[str] = []
    for token in tokens[:MAX_CANDIDATES]:
        enforce_timeout(started_at)
        parts = re.findall(rf"[^aeiourl]*?{VOWEL_PATTERN}(?:m|h|[kgcjtdnpbmyrlvsh]{{0,2}})?", token)
        for part in parts:
            if part:
                syllables.append(part)
                if len(syllables) >= MAX_SYLLABLES:
                    return syllables
    return syllables


def syllable_weight(syllable: str, is_long: bool = False, has_marker: bool = False, has_halanta_coda: bool = False) -> str:
    vowel = next((v for v in ("ai", "au", "e", "o", "a", "i", "u", "r", "l") if v in syllable.lower()), "a")
    if is_long or has_marker or has_halanta_coda or vowel in {"e", "o", "ai", "au"}:
        return "Guru"
    if re.search(r"[aeiourl][kgcjtdnpbmyrlvsh]{2,}$", syllable):
        return "Guru"
    return "Laghu"


def append_marker_to_previous(units: List[SyllableUnit], marker: str) -> None:
    if not units:
        return
    units[-1].text += marker
    if marker == VISARGA:
        units[-1].has_visarga = True
    if marker == ANUSVARA:
        units[-1].has_anusvara = True


def devanagari_syllable_units(text: str, limit: int = MAX_SYLLABLES) -> List[SyllableUnit]:
    units: List[SyllableUnit] = []
    index = 0
    while index < len(text) and len(units) < limit:
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        following = text[index + 2] if index + 2 < len(text) else ""

        if char in INDEPENDENT_VOWELS:
            units.append(SyllableUnit(char, INDEPENDENT_VOWELS[char], char in {"\u0906", "\u0908", "\u090a", "\u0960", "\u090f", "\u0910", "\u0913", "\u0914"}))
        elif char in CONSONANTS:
            if next_char == VIRAMA:
                if units:
                    units[-1].text += char + VIRAMA
                    units[-1].has_halanta_coda = True
                index += 2
                continue
            if next_char in VOWEL_SIGNS:
                vowel = VOWEL_SIGNS[next_char]
                is_long = next_char in {"\u093e", "\u0940", "\u0942", "\u0944", "\u0947", "\u0948", "\u094b", "\u094c"}
                unit = SyllableUnit(char + next_char, vowel, is_long)
                if following in (ANUSVARA, VISARGA):
                    unit.text += following
                    unit.has_anusvara = following == ANUSVARA
                    unit.has_visarga = following == VISARGA
                    index += 3
                    units.append(unit)
                    continue
                units.append(unit)
                index += 2
                continue
            unit = SyllableUnit(char, "a", False)
            if next_char in (ANUSVARA, VISARGA):
                unit.text += next_char
                unit.has_anusvara = next_char == ANUSVARA
                unit.has_visarga = next_char == VISARGA
                index += 2
                units.append(unit)
                continue
            units.append(unit)
        elif char in (ANUSVARA, VISARGA):
            append_marker_to_previous(units, char)
        index += 1
    return units


LATIN_WORD_PATTERN = re.compile(r"[a-zA-Zāīūṛṝḷḹṅñṭḍṇśṣṃṁḥ]+")
LATIN_VOWELS = {"a", "i", "u", "ṛ", "ḷ", "ā", "ī", "ū", "ṝ", "ḹ", "e", "o"}
LATIN_LONG_VOWELS = {"ā", "ī", "ū", "ṝ", "ḹ", "e", "o", "ai", "au"}
IAST_DISPLAY_MAP: Dict[str, str] = {}


def latin_vowel_at(token: str, index: int) -> Optional[str]:
    pair = token[index:index + 2]
    if pair in {"ai", "au"}:
        return pair
    char = token[index]
    if char in LATIN_VOWELS:
        return char
    return None


def latin_vowel_positions(token: str) -> List[Tuple[int, int, str]]:
    positions: List[Tuple[int, int, str]] = []
    index = 0
    while index < len(token):
        vowel = latin_vowel_at(token, index)
        if vowel:
            positions.append((index, index + len(vowel), vowel))
            index += len(vowel)
        else:
            index += 1
    return positions


def latin_display_text(clean: str) -> str:
    return IAST_DISPLAY_MAP.get(clean, clean)


def is_single_latin_consonant_span(consonants: str) -> bool:
    return len(consonants) == 1 or consonants in {"kh", "gh", "ch", "jh", "\u1e6dh", "\u1e0dh", "th", "dh", "ph", "bh"}


def latin_syllable_units(text: str, limit: int = MAX_SYLLABLES) -> List[SyllableUnit]:
    units: List[SyllableUnit] = []
    for token in LATIN_WORD_PATTERN.findall(text.lower())[:MAX_CANDIDATES]:
        normalized = token.replace("ṁ", "ṃ")
        if normalized.startswith(("rtv", "ṛtv")):
            units.append(SyllableUnit("ṛ", "ṛ", False, False, False, False))
            normalized = normalized[1:] if normalized.startswith("rtv") else normalized[1:]
            if len(units) >= limit:
                return units
        vowels = latin_vowel_positions(normalized)
        if not vowels:
            continue

        pending_onset = normalized[:vowels[0][0]]
        for index, (start, end, vowel) in enumerate(vowels):
            next_start = vowels[index + 1][0] if index + 1 < len(vowels) else len(normalized)
            consonants = normalized[end:next_start]
            coda = ""

            if index + 1 < len(vowels):
                if is_single_latin_consonant_span(consonants):
                    next_onset = consonants
                elif len(consonants) > 1:
                    coda = consonants[0]
                    next_onset = consonants[1:]
                else:
                    next_onset = ""
            else:
                coda = consonants
                next_onset = ""

            clean = pending_onset + vowel + coda
            has_visarga = clean.endswith("ḥ")
            has_anusvara = clean.endswith(("ṃ", "m")) and len(clean) > 1
            has_final_coda = bool(coda) or has_visarga or has_anusvara
            units.append(SyllableUnit(
                latin_display_text(clean),
                vowel,
                vowel in LATIN_LONG_VOWELS,
                has_visarga,
                has_anusvara,
                has_final_coda,
            ))
            if len(units) >= limit:
                return units
            pending_onset = next_onset
    return promote_vocalic_r_before_conjunct(units)


def starts_with_conjunct(text: str) -> bool:
    lowered = text.lower()
    return lowered.startswith(("tvi", "tv", "k\u1e63", "ks", "tr", "dhv", "j\u00f1", "jn", "gn"))


def promote_vocalic_r_before_conjunct(units: List[SyllableUnit]) -> List[SyllableUnit]:
    for index, unit in enumerate(units[:-1]):
        if unit.text in {"\u1e5b", "r"} and starts_with_conjunct(units[index + 1].text):
            unit.is_long = True
    return units


def iast_syllable_units(text: str, limit: int = MAX_SYLLABLES) -> List[SyllableUnit]:
    return merge_iast_edge_syllables(latin_syllable_units(text, limit))


def merge_iast_edge_syllables(units: List[SyllableUnit]) -> List[SyllableUnit]:
    merged: List[SyllableUnit] = []
    index = 0
    while index < len(units):
        current = units[index]
        next_unit = units[index + 1] if index + 1 < len(units) else None
        if next_unit and current.text in {"\u1e37", "l\u0323"} and next_unit.text == "e":
            merged.append(SyllableUnit("\u1e37e", "e", True, False, False, False))
            index += 2
            continue
        merged.append(current)
        index += 1
    return merged


def source_syllable_units(source_text: str, transliterated: str, started_at: float) -> List[SyllableUnit]:
    enforce_timeout(started_at)
    if is_devanagari(source_text):
        return devanagari_syllable_units(source_text)
    if any(char in source_text for char in "āīūṛṝḷḹṅñṭḍṇśṣṃṁḥ"):
        return iast_syllable_units(source_text)
    return latin_syllable_units(transliterated)


def build_phonological_syllables(source_text: str, transliterated: str, started_at: float) -> List[PhonologicalSyllableNode]:
    nodes: List[PhonologicalSyllableNode] = []
    cluster_cursor = 0
    for index, unit in enumerate(source_syllable_units(source_text, transliterated, started_at)):
        enforce_timeout(started_at)
        weight = syllable_weight(unit.text, unit.is_long, unit.has_visarga or unit.has_anusvara, unit.has_halanta_coda)
        matra_count = 2 if weight == "Guru" else 1
        end = cluster_cursor + max(len(unit.text) - 1, 0)
        nodes.append(PhonologicalSyllableNode(index, unit.text, weight, matra_count, cluster_cursor, end))
        cluster_cursor = end + 1
    return nodes


def derive_pada_meter(nodes: List[PhonologicalSyllableNode]) -> str:
    count = len(nodes)
    if count == 8:
        return "8-syllable pada"
    if count == 11:
        return "tristubh pada candidate"
    if count == 12:
        return "jagati pada candidate"
    if count < 8:
        return "partial pada"
    return "unclassified pada"


def derive_stanza_meter(padas: List[Dict[str, Any]]) -> str:
    counts = [pada.get("syllable_count", 0) for pada in padas]
    if not counts or max(counts, default=0) < 8:
        return "Fragment / partial pada - meter not determined"
    if len(padas) == 1 and counts[0] == 8:
        if padas[0].get("guru_laghu_pattern") == "G G G G G G G G":
            return "Vidyunm\u0101l\u0101 p\u0101da candidate"
        return "8-syllable p\u0101da candidate"
    if len(padas) == 3 and all(count == 8 for count in counts):
        return "G\u0101yatr\u012b \u2014 24-syllable Vedic matrix"
    if len(padas) == 3:
        return "G\u0101yatr\u012b candidate incomplete \u2014 mixed p\u0101da matrix"
    if len(padas) == 4 and all(count == 8 for count in counts):
        if all(pada.get("guru_laghu_pattern") == "G G G G G G G G" for pada in padas):
            return "Vidyunm\u0101l\u0101 candidate"
        return "Anu\u1e63\u1e6dubh / \u015aloka \u2014 32-syllable matrix"
    if all(count == 8 for count in counts):
        return "Partial 8-syllable pada matrix - meter not determined"
    return "Meter not determined for mixed pada matrix"


def split_pada_segments(text: str) -> List[str]:
    return [segment.strip() for segment in re.split(r"\s*(?:\|\||\||\u0965|\u0964|\r?\n)+\s*", text) if segment.strip()]


def pada_display_from_nodes(nodes: List[PhonologicalSyllableNode]) -> str:
    return " ".join(node.text for node in nodes)


def make_pada(
    label_index: int,
    text: str,
    nodes: List[PhonologicalSyllableNode],
    source_segment: Optional[str] = None,
) -> Dict[str, Any]:
    record = {
        "label": f"pada {label_index}",
        "text": text,
        "display_text": text,
        "meter": derive_pada_meter(nodes),
        "syllable_count": len(nodes),
        "matra_count": sum(node.matra_count for node in nodes),
        "guru_laghu_pattern": " ".join("G" if node.weight == "Guru" else "L" for node in nodes),
        "phonological_syllables": [node.__dict__ for node in nodes],
    }
    if source_segment is not None:
        record["source_segment"] = source_segment
    return record


def split_16_syllable_half_verse(
    label_index: int,
    segment: str,
    nodes: List[PhonologicalSyllableNode],
) -> List[Dict[str, Any]]:
    padas: List[Dict[str, Any]] = []
    for half in (nodes[:8], nodes[8:16]):
        padas.append(make_pada(label_index, pada_display_from_nodes(half), half, segment))
        label_index += 1
    return padas


def make_pada_segment(index: int, text: str, nodes: List[PhonologicalSyllableNode]) -> Dict[str, Any]:
    return {
        "label": f"segment {index}",
        "text": text,
        "syllable_count": len(nodes),
        "matra_count": sum(node.matra_count for node in nodes),
        "guru_laghu_pattern": " ".join("G" if node.weight == "Guru" else "L" for node in nodes),
    }


def build_pada_segments(source_text: str, started_at: float) -> List[Dict[str, Any]]:
    segments = split_pada_segments(source_text) or ([source_text] if source_text else [])
    records: List[Dict[str, Any]] = []
    for index, segment in enumerate(segments[:MAX_CANDIDATES], start=1):
        segment_transliterated, _ = transliterate(segment)
        segment_nodes = build_phonological_syllables(segment, segment_transliterated, started_at)
        records.append(make_pada_segment(index, segment, segment_nodes))
    return records


def build_padas(source_text: str, transliterated: str, nodes: List[PhonologicalSyllableNode], started_at: float) -> List[Dict[str, Any]]:
    segments = split_pada_segments(source_text) or ([source_text] if source_text else [])
    padas: List[Dict[str, Any]] = []
    label_index = 1

    for segment in segments[:MAX_CANDIDATES]:
        enforce_timeout(started_at)
        segment_transliterated, _ = transliterate(segment)
        segment_nodes = build_phonological_syllables(segment, segment_transliterated, started_at)

        if len(segment_nodes) == 16:
            split_padas = split_16_syllable_half_verse(label_index, segment, segment_nodes)
            padas.extend(split_padas)
            label_index += len(split_padas)
        else:
            padas.append(make_pada(label_index, segment, segment_nodes))
            label_index += 1

    if not padas and nodes:
        padas.append(make_pada(1, transliterated, nodes))
    return padas


def apply_sandhi(text: str) -> List[Dict[str, str]]:
    if not text:
        return []
    steps: List[Dict[str, str]] = []
    collapsed = re.sub(r"\ba a\b", "a", text, count=MAX_CANDIDATES)
    if collapsed != text:
        steps.append({"rule": "savarna-dirgha candidate", "before": text, "after": collapsed})
    if not steps:
        steps.append({"rule": "no external sandhi applied", "before": text, "after": text})
    return steps[:MAX_CANDIDATES]


def final_form_cleanup(current_state: str) -> str:
    cleaned = re.sub(r"\s+", " ", current_state).strip()
    return cleaned.rstrip(" ,;")


def build_derivation_history(text: str, transliterated: str, sandhi_steps: List[Dict[str, str]]) -> List[Dict[str, str]]:
    current_state = text
    history = [{"stage": "input", "rule": "Unicode NFC normalization", "input": text, "output": current_state}]
    history.append({"stage": "transliteration", "rule": "orthography ingress normalization", "input": current_state, "output": transliterated})
    current_state = transliterated
    for step in sandhi_steps[:MAX_DERIVATION_STEPS]:
        before = current_state
        after = step.get("after", before)
        history.append({"stage": "sandhi", "rule": step.get("rule", "unknown"), "input": before, "output": after})
        current_state = after
    cleaned = final_form_cleanup(current_state)
    history.append({"stage": "final-form cleanup", "rule": "trim punctuation and spacing", "input": current_state, "output": cleaned})
    return history[:MAX_DERIVATION_STEPS]


def build_prakriya_graph(history: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    nodes = [{"id": f"n{index}", "label": step["stage"]} for index, step in enumerate(history)]
    edges = [{"from": f"n{index}", "to": f"n{index + 1}", "rule": history[index + 1]["rule"]} for index in range(len(history) - 1)]
    return {"nodes": nodes, "edges": edges}


def lexical_lookup(text: str) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for token in TOKEN_PATTERN.findall(text.lower())[:MAX_CANDIDATES]:
        lemma, gloss = LEXICON.get(token, (token, "unresolved lexical item"))
        entries.append({
            "token": token,
            "lemma": lemma,
            "gloss": gloss,
            "gender": None,
            "source": None,
        })
    return entries


def experimental_projection(nodes: List[PhonologicalSyllableNode]) -> Dict[str, Any]:
    return {
        "label": "Experimental Symbolic Structural Projection Field Map",
        "field_map": [
            {
                "index": node.index,
                "symbol": "G" if node.weight == "Guru" else "L",
                "weight": node.matra_count,
            }
            for node in nodes[:49]
        ],
    }


def empty_payload(input_text: str, diagnostics: List[Dict[str, str]]) -> Dict[str, Any]:
    return {
        "input_text": input_text,
        "unicode_clusters": [],
        "transliteration": "",
        "sandhi": [],
        "overall_stanza_meter": "Fragment / partial pada - meter not determined",
        "total_matra_count": 0,
        "pada_segments": [],
        "padas": [],
        "phonological_syllables": [],
        "derivation_history": [],
        "prakriya_graph": {"nodes": [], "edges": []},
        "lexical_lookup": [],
        "parser_diagnostics": diagnostics,
        "lexical_source_governance": LEXICAL_SOURCE_GOVERNANCE,
        "experimental_payload": experimental_projection([]),
    }


def analyze_sanskrit(input_text: str) -> Dict[str, Any]:
    started_at = time.monotonic()
    try:
        normalized, diagnostics = normalize_input(input_text)
        if not normalized:
            return empty_payload(normalized, diagnostics)

        enforce_timeout(started_at)
        transliterated, transliteration_diagnostics = transliterate(normalized)
        diagnostics.extend(transliteration_diagnostics)
        diagnostics.extend(validate_transliteration(transliterated))

        unicode_clusters = build_unicode_clusters(normalized)
        phonological_syllables = build_phonological_syllables(normalized, transliterated, started_at)
        sandhi_steps = apply_sandhi(transliterated)
        derivation_history = build_derivation_history(normalized, transliterated, sandhi_steps)
        pada_segments = build_pada_segments(normalized, started_at)
        padas = build_padas(normalized, transliterated, phonological_syllables, started_at)

        if not phonological_syllables:
            diagnostics.append({"level": "warning", "message": "No phonological syllables were detected."})
        else:
            diagnostics.append({"level": "info", "message": "Deterministic Sanskrit pipeline completed."})

        return {
            "input_text": normalized,
            "unicode_clusters": [node.__dict__ for node in unicode_clusters],
            "transliteration": transliterated,
            "sandhi": sandhi_steps,
            "overall_stanza_meter": derive_stanza_meter(padas),
            "total_matra_count": sum(node.matra_count for node in phonological_syllables),
            "pada_segments": pada_segments,
            "padas": padas,
            "phonological_syllables": [node.__dict__ for node in phonological_syllables],
            "derivation_history": derivation_history,
            "prakriya_graph": build_prakriya_graph(derivation_history),
            "lexical_lookup": lexical_lookup(transliterated),
            "parser_diagnostics": diagnostics,
            "lexical_source_governance": LEXICAL_SOURCE_GOVERNANCE,
            "experimental_payload": experimental_projection(phonological_syllables),
        }
    except SanskritTabException:
        raise
    except Exception as exc:
        raise SanskritPipelineException("Sanskrit analysis failed safely.") from exc
