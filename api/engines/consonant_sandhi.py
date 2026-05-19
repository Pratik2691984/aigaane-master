from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import unicodedata

from engines.trace_graph import DerivationStep, DerivationTraceGraph


VIRAMA = "\u094d"
CONSONANTS = set("\u0915\u0916\u0917\u0918\u0919\u091a\u091b\u091c\u091d\u091e\u091f\u0920\u0921\u0922\u0923\u0924\u0925\u0926\u0927\u0928\u092a\u092b\u092c\u092d\u092e\u092f\u0930\u0932\u0935\u0936\u0937\u0938\u0939")


class ConsonantSandhiException(Exception):
    status_code = 400
    code = "sandhi_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


@dataclass(frozen=True)
class ConsonantBoundary:
    left_token: str
    right_token: str
    rule_key: str


RULES = {
    "\u0924\u094d+\u091a": {
        "replacement": "\u091a\u094d\u091a",
        "sutra": "8.4.40",
        "sutra_name": "\u0938\u094d\u0924\u094b\u0903 \u0936\u094d\u091a\u0941\u0928\u093e \u0936\u094d\u091a\u0941\u0903",
        "operation": "dental_to_palatal_assimilation",
    }
}


def normalize_word(value: str, field_name: str) -> str:
    if value is None or not isinstance(value, str):
        raise ConsonantSandhiException(f"{field_name} is required.")
    normalized = unicodedata.normalize("NFC", value.strip())
    if not normalized:
        raise ConsonantSandhiException(f"{field_name} must not be empty.")
    return normalized


def is_devanagari(text: str) -> bool:
    return any("\u0900" <= char <= "\u097f" for char in text)


def is_consonant(char: str) -> bool:
    return char in CONSONANTS


def normalize_halant_token(token: str) -> str:
    normalized = unicodedata.normalize("NFC", token.strip())
    if not normalized:
        return normalized
    if normalized.endswith(VIRAMA):
        return normalized
    if len(normalized) == 1 and is_consonant(normalized):
        return normalized + VIRAMA
    return normalized


def final_consonant_token(word: str) -> Optional[str]:
    if len(word) >= 2 and word[-1] == VIRAMA and is_consonant(word[-2]):
        return word[-2:]
    if word and is_consonant(word[-1]):
        return word[-1] + VIRAMA
    return None


def initial_consonant_token(word: str) -> Optional[str]:
    for char in word:
        if char.isspace():
            continue
        if is_consonant(char):
            return char
        return None
    return None


def build_rule_key(left_token: str, right_token: str) -> str:
    return f"{normalize_halant_token(left_token)}+{right_token}"


def trace(rule: str, word1: str, word2: str, boundary: ConsonantBoundary, merged: str) -> List[Dict[str, Any]]:
    return [
        {"layer": "orthographic_input", "word1": word1, "word2": word2},
        {
            "layer": "phonological_representation",
            "left_consonant": boundary.left_token,
            "right_consonant": boundary.right_token,
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
                engine_node="Node 2C Consonant Sandhi",
            )
        ]
    ).to_list()


def substitute_boundary(word1: str, word2: str, boundary: ConsonantBoundary, replacement: str) -> str:
    left_base = word1[: -len(boundary.left_token)]
    right_remainder = word2[len(boundary.right_token) :]
    return left_base + replacement + right_remainder


def analyze_consonant_sandhi(word1: str, word2: str) -> Dict[str, Any]:
    left_word = normalize_word(word1, "word1")
    right_word = normalize_word(word2, "word2")
    if not (is_devanagari(left_word) and is_devanagari(right_word)):
        raise ConsonantSandhiException("Only Devanagari consonant sandhi is enabled in this phase.")

    left_token = final_consonant_token(left_word)
    right_token = initial_consonant_token(right_word)
    if left_token is None or right_token is None:
        raise ConsonantSandhiException("Both words must expose consonant boundaries.")

    boundary = ConsonantBoundary(
        left_token=normalize_halant_token(left_token),
        right_token=right_token,
        rule_key=build_rule_key(left_token, right_token),
    )
    rule = RULES.get(boundary.rule_key)
    if rule is None:
        raise ConsonantSandhiException("No supported consonant sandhi rule matched.")

    merged = substitute_boundary(left_word, right_word, boundary, rule["replacement"])
    return {
        "merged": merged,
        "sutra": rule["sutra"],
        "sutra_name": rule["sutra_name"],
        "type": "consonant_sandhi",
        "trace": trace(rule["sutra"], left_word, right_word, boundary, merged),
        "derivation_path": derivation_path(
            rule["sutra"],
            rule["sutra_name"],
            rule["operation"],
            left_word,
            right_word,
            merged,
        ),
    }
