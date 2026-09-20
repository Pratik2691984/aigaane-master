from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import unicodedata

from engines.trace_graph import DerivationStep, DerivationTraceGraph


VISARGA = "\u0903"
VIRAMA = "\u094d"
O_SIGN = "\u094b"
AVAGRAHA = "\u093d"

VOWELS = {
    "\u0905",
    "\u0906",
    "\u0907",
    "\u0908",
    "\u0909",
    "\u090a",
    "\u090b",
    "\u0960",
    "\u090f",
    "\u0910",
    "\u0913",
    "\u0914",
}

KHAR = {
    "\u0915",
    "\u0916",
    "\u091a",
    "\u091b",
    "\u091f",
    "\u0920",
    "\u0924",
    "\u0925",
    "\u092a",
    "\u092b",
    "\u0936",
    "\u0937",
    "\u0938",
}

HASH = {
    "\u0917",
    "\u0918",
    "\u0919",
    "\u091c",
    "\u091d",
    "\u091e",
    "\u0921",
    "\u0922",
    "\u0923",
    "\u0926",
    "\u0927",
    "\u0928",
    "\u092c",
    "\u092d",
    "\u092e",
    "\u092f",
    "\u0930",
    "\u0932",
    "\u0935",
    "\u0939",
}


class VisargaSandhiException(Exception):
    status_code = 400
    code = "sandhi_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


@dataclass(frozen=True)
class VisargaBoundary:
    base: str
    preceding_vowel: Optional[str]
    right_initial: str
    right_class: str


def normalize_word(value: str, field_name: str) -> str:
    if value is None or not isinstance(value, str):
        raise VisargaSandhiException(f"{field_name} is required.")
    normalized = unicodedata.normalize("NFC", value.strip())
    if not normalized:
        raise VisargaSandhiException(f"{field_name} must not be empty.")
    return normalized


def is_devanagari(text: str) -> bool:
    return any("\u0900" <= char <= "\u097f" for char in text)


def first_phonological_char(word: str) -> str:
    for char in word:
        if not char.isspace():
            return char
    return ""


def phonological_class(char: str) -> str:
    if char in VOWELS:
        return "VOWEL"
    if char in KHAR:
        return "KHAR"
    if char in HASH:
        return "HASH"
    return "UNKNOWN"


def preceding_vowel_before_visarga(word: str) -> Optional[str]:
    if not word.endswith(VISARGA) or len(word) < 2:
        return None
    index = len(word) - 2
    if word[index] == VIRAMA:
        return None
    return "a"


def add_o_to_final_inherent_a(base: str) -> str:
    if not base or base.endswith(VIRAMA):
        raise VisargaSandhiException("Visarga sandhi requires a final inherent-a base in this phase.")
    return base + O_SIGN


def build_trace(rule: str, word1: str, word2: str, boundary: VisargaBoundary, merged: str) -> List[Dict[str, Any]]:
    return [
        {"layer": "orthographic_input", "word1": word1, "word2": word2},
        {
            "layer": "phonological_representation",
            "left_visarga": VISARGA,
            "preceding_vowel": boundary.preceding_vowel,
            "right_initial": boundary.right_initial,
            "right_class": boundary.right_class,
        },
        {"layer": "sandhi_rule_engine", "sutra": rule},
        {"layer": "orthographic_recomposition", "merged": merged},
    ]


def derivation_path(
    rule: str,
    sutra_name: str,
    operation: str,
    word1: str,
    word2: str,
    merged: str,
) -> List[Dict[str, str]]:
    return DerivationTraceGraph(
        steps=[
            DerivationStep(
                sutra=rule,
                sutra_name=sutra_name,
                operation=operation,
                input_state=f"{word1} + {word2}",
                output_state=merged,
                engine_node="Node 2B Visarga Sandhi",
            )
        ]
    ).to_list()


def analyze_visarga_sandhi(word1: str, word2: str) -> Dict[str, Any]:
    left_word = normalize_word(word1, "word1")
    right_word = normalize_word(word2, "word2")
    if not (is_devanagari(left_word) and is_devanagari(right_word)):
        raise VisargaSandhiException("Only Devanagari visarga sandhi is enabled in this phase.")
    if not left_word.endswith(VISARGA):
        raise VisargaSandhiException("word1 must end in visarga for visarga sandhi.")

    base = left_word[:-1]
    right_initial = first_phonological_char(right_word)
    right_class = phonological_class(right_initial)
    boundary = VisargaBoundary(
        base=base,
        preceding_vowel=preceding_vowel_before_visarga(left_word),
        right_initial=right_initial,
        right_class=right_class,
    )
    if boundary.preceding_vowel != "a":
        raise VisargaSandhiException("Only final a-visarga is enabled in this phase.")

    if right_initial == "\u0905":
        merged = add_o_to_final_inherent_a(base) + AVAGRAHA + right_word[1:]
        sutra_name = "\u0939\u0936\u093f \u091a"
        return {
            "merged": merged,
            "sutra": "6.1.114",
            "sutra_name": sutra_name,
            "type": "visarga_sandhi",
            "trace": build_trace("6.1.114", left_word, right_word, boundary, merged),
            "derivation_path": derivation_path("6.1.114", sutra_name, "visarga_to_o_avagraha", left_word, right_word, merged),
        }

    if right_class == "HASH":
        merged = f"{add_o_to_final_inherent_a(base)} {right_word}"
        sutra_name = "\u0938\u0938\u091c\u0941\u0937\u094b \u0930\u0941\u0903 / \u0905\u0924\u094b \u0930\u094b\u0930\u092a\u094d\u0932\u0941\u0924\u093e\u0926\u092a\u094d\u0932\u0941\u0924\u0947"
        return {
            "merged": merged,
            "sutra": "8.2.66 / 6.1.113",
            "sutra_name": sutra_name,
            "type": "visarga_sandhi",
            "trace": build_trace("8.2.66 / 6.1.113", left_word, right_word, boundary, merged),
            "derivation_path": derivation_path("8.2.66 / 6.1.113", sutra_name, "visarga_to_o_before_hash", left_word, right_word, merged),
        }

    if right_initial == "\u091a":
        merged = base + "\u0936" + VIRAMA + right_word
        sutra_name = "\u0935\u093f\u0938\u0930\u094d\u091c\u0928\u0940\u092f\u0938\u094d\u092f \u0938\u0903"
        return {
            "merged": merged,
            "sutra": "8.3.34",
            "sutra_name": sutra_name,
            "type": "visarga_sandhi",
            "trace": build_trace("8.3.34", left_word, right_word, boundary, merged),
            "derivation_path": derivation_path("8.3.34", sutra_name, "visarga_to_sh_before_ca", left_word, right_word, merged),
        }

    raise VisargaSandhiException("No supported visarga sandhi rule matched.")
