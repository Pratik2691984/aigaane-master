"""
Aigaane v0.2.0 — Category G Chhandas Prosody Engine
"""

from typing import Optional, Dict

_CHHANDAS_TABLE: Dict[str, dict] = {
    "gāyatrī": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "gāyatrī 3x8",
    },
    "anuṣṭubh": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "anuṣṭubh 4x8",
    },
    "triṣṭubh": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "triṣṭubh 4x11",
    },
    "jagatī": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "jagatī 4x12",
    },
    "śārdūlavikrīḍita": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "śārdūlavikrīḍita 4x19",
    },
    "vasantatilakā": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "vasantatilakā 4x14",
    },
    "mandākrāntā": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "mandākrāntā 4x17",
    },
    "mālinī": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "mālinī 4x15",
    },
    "puṣpitāgrā": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "puṣpitāgrā 12+13",
    },
    "vaitālīya": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "vaitālīya 14+16",
    },
}

def lookup(surface: str) -> Optional[dict]:
    return _CHHANDAS_TABLE.get(surface)
