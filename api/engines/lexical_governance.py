from dataclasses import dataclass
from typing import Any, Dict, List
import unicodedata


DEVANAGARI_START = "\u0900"
DEVANAGARI_END = "\u097f"
SANSKRIT_PUNCTUATION = {"\u0964", "\u0965", "\u093d"}
API_SEPARATORS = {"|"}
SAFE_ANALYZE_CONTROLS = {"\n", "\r", "\t"}


class LexicalGovernanceException(Exception):
    status_code = 400
    code = "lexical_governance_error"

    def __init__(self, message: str, invalid_characters: List[Dict[str, str]]):
        super().__init__(message)
        self.message = message
        self.invalid_characters = invalid_characters


@dataclass(frozen=True)
class GovernanceMetadata:
    normalization: str
    script_policy: str
    source: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "normalization": self.normalization,
            "script_policy": self.script_policy,
            "source": self.source,
        }


SANDHI_GOVERNANCE = GovernanceMetadata(
    normalization="NFC",
    script_policy="devanagari_only",
    source="sandhi_rule_registry",
)

MORPHOLOGY_GOVERNANCE = GovernanceMetadata(
    normalization="NFC",
    script_policy="devanagari_only",
    source="classical_paradigm_registry",
)

ANALYZE_GOVERNANCE = GovernanceMetadata(
    normalization="NFC",
    script_policy="mixed_chandas_ingress",
    source="classical_paradigm_registry",
)


def normalize_nfc(value: str, field_name: str) -> str:
    if value is None or not isinstance(value, str):
        raise LexicalGovernanceException(
            f"{field_name} must be a string.",
            [{"character": "", "codepoint": "", "name": "non-string input"}],
        )
    try:
        return unicodedata.normalize("NFC", value)
    except UnicodeError as exc:
        raise LexicalGovernanceException(
            f"{field_name} contains malformed Unicode.",
            [{"character": "", "codepoint": "", "name": "malformed Unicode"}],
        ) from exc


def invalid_character_record(char: str) -> Dict[str, str]:
    return {
        "character": char,
        "codepoint": f"U+{ord(char):04X}",
        "name": unicodedata.name(char, "UNKNOWN"),
    }


def is_allowed_devanagari_endpoint_char(char: str) -> bool:
    return (
        DEVANAGARI_START <= char <= DEVANAGARI_END
        or char.isspace()
        or char in SANSKRIT_PUNCTUATION
        or char in API_SEPARATORS
    )


def validate_devanagari_only(value: str, field_name: str) -> str:
    normalized = normalize_nfc(value, field_name).strip()
    invalid = [invalid_character_record(char) for char in normalized if not is_allowed_devanagari_endpoint_char(char)]
    if invalid:
        raise LexicalGovernanceException(
            f"{field_name} must use Devanagari input for this endpoint.",
            invalid,
        )
    return normalized


def sanitize_mixed_chandas_input(value: str, field_name: str) -> str:
    normalized = normalize_nfc(value, field_name)
    invalid = [
        invalid_character_record(char)
        for char in normalized
        if unicodedata.category(char).startswith("C") and char not in SAFE_ANALYZE_CONTROLS
    ]
    if invalid:
        raise LexicalGovernanceException(
            f"{field_name} contains unsupported control characters.",
            invalid,
        )
    return normalized


def attach_governance(payload: Dict[str, Any], metadata: GovernanceMetadata) -> Dict[str, Any]:
    governed = dict(payload)
    governed["governance"] = metadata.to_dict()
    return governed
