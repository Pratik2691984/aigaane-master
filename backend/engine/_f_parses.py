"""
Aigaane v0.2.0 — Category F Nyaya Parse Structures
"""

from typing import Optional, Dict

_F_SURFACES: Dict[str, dict] = {
    # F01: parvato vahnimān dhūmavattvāt
    "parvato vahnimān dhūmavattvāt": {
        "tokens": [
            {"token_id": "T0", "pada": "parvataḥ", "stem": "parvata", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "pullinga", "pos": "subhanta", "confidence": 0.95},
            {"token_id": "T1", "pada": "vahnimān", "stem": "vahnimat", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "pullinga", "pos": "subhanta", "confidence": 0.93},
            {"token_id": "T2", "pada": "dhūmavattvāt", "stem": "dhūmavattva", "vibhakti": "pancami", "vacana": "ekavacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.91},
        ],
        "sandhi_splits": [
            {"parts": ["parvataḥ", "vahnimān"], "rule": "visarga_o", "rule_canon_ref": "8.2.66", "confidence": 0.95}
        ],
        "canon_refs": [{"canon_name": "Nyāyasūtra", "reference_locator": "1.1.33", "domain": "nyaya"}],
    },
    # F02: śabdo 'nityaḥ utpattidharmakatvāt
    "śabdo 'nityaḥ utpattidharmakatvāt": {
        "tokens": [
            {"token_id": "T0", "pada": "śabdaḥ", "stem": "śabda", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "pullinga", "pos": "subhanta", "confidence": 0.95},
            {"token_id": "T1", "pada": "nityaḥ", "stem": "nitya", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "pullinga", "pos": "subhanta", "confidence": 0.94},
            {"token_id": "T2", "pada": "utpattidharmakatvāt", "stem": "utpattidharmakatva", "vibhakti": "pancami", "vacana": "ekavacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.92},
        ],
        "sandhi_splits": [
            {"parts": ["śabdaḥ", "anityaḥ"], "rule": "visarga_o_with_avagraha", "rule_canon_ref": "6.1.109", "confidence": 0.95}
        ],
        "canon_refs": [{"canon_name": "Nyāyasūtra", "reference_locator": "1.1.33", "domain": "nyaya"}],
    },
    # F03: ātmā nityaḥ anāditvāt
    "ātmā nityaḥ anāditvāt": {
        "tokens": [
            {"token_id": "T0", "pada": "ātmā", "stem": "ātman", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "pullinga", "pos": "subhanta", "confidence": 0.96},
            {"token_id": "T1", "pada": "nityaḥ", "stem": "nitya", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "pullinga", "pos": "subhanta", "confidence": 0.95},
            {"token_id": "T2", "pada": "anāditvāt", "stem": "anāditva", "vibhakti": "pancami", "vacana": "ekavacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.92},
        ],
        "sandhi_splits": [],
        "canon_refs": [{"canon_name": "Nyāyasūtra", "reference_locator": "1.1.33", "domain": "nyaya"}],
    },
    # F04: indriyāṇi anityāni kṛtakatvāt
    "indriyāṇi anityāni kṛtakatvāt": {
        "tokens": [
            {"token_id": "T0", "pada": "indriyāṇi", "stem": "indriya", "vibhakti": "prathama", "vacana": "bahuvacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.95},
            {"token_id": "T1", "pada": "anityāni", "stem": "anitya", "vibhakti": "prathama", "vacana": "bahuvacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.94},
            {"token_id": "T2", "pada": "kṛtakatvāt", "stem": "kṛtakatva", "vibhakti": "pancami", "vacana": "ekavacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.91},
        ],
        "sandhi_splits": [],
        "canon_refs": [{"canon_name": "Nyāyasūtra", "reference_locator": "1.1.33", "domain": "nyaya"}],
    },
    # F05: ghaṭo 'nityaḥ kṛtakatvāt
    "ghaṭo 'nityaḥ kṛtakatvāt": {
        "tokens": [
            {"token_id": "T0", "pada": "ghaṭaḥ", "stem": "ghaṭa", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "pullinga", "pos": "subhanta", "confidence": 0.95},
            {"token_id": "T1", "pada": "nityaḥ", "stem": "nitya", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "pullinga", "pos": "subhanta", "confidence": 0.94},
            {"token_id": "T2", "pada": "kṛtakatvāt", "stem": "kṛtakatva", "vibhakti": "pancami", "vacana": "ekavacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.92},
        ],
        "sandhi_splits": [
            {"parts": ["ghaṭaḥ", "anityaḥ"], "rule": "visarga_o_with_avagraha", "rule_canon_ref": "6.1.109", "confidence": 0.95}
        ],
        "canon_refs": [{"canon_name": "Nyāyasūtra", "reference_locator": "1.1.33", "domain": "nyaya"}],
    },
    # F06: vahnir dhūmāt
    "vahnir dhūmāt": {
        "tokens": [
            {"token_id": "T0", "pada": "vahniḥ", "stem": "vahni", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "pullinga", "pos": "subhanta", "confidence": 0.94},
            {"token_id": "T1", "pada": "dhūmāt", "stem": "dhūma", "vibhakti": "pancami", "vacana": "ekavacana", "linga": "pullinga", "pos": "subhanta", "confidence": 0.93},
        ],
        "sandhi_splits": [
            {"parts": ["vahniḥ", "dhūmāt"], "rule": "visarga_r", "rule_canon_ref": "8.2.66", "confidence": 0.94}
        ],
        "canon_refs": [{"canon_name": "Nyāyasūtra", "reference_locator": "1.1.33", "domain": "nyaya"}],
    },
    # F07: sarve bhāvāḥ anityāḥ utpattidharmakatvāt
    "sarve bhāvāḥ anityāḥ utpattidharmakatvāt": {
        "tokens": [
            {"token_id": "T0", "pada": "sarve", "stem": "sarva", "vibhakti": "prathama", "vacana": "bahuvacana", "linga": "pullinga", "pos": "subhanta", "confidence": 0.95},
            {"token_id": "T1", "pada": "bhāvāḥ", "stem": "bhāva", "vibhakti": "prathama", "vacana": "bahuvacana", "linga": "pullinga", "pos": "subhanta", "confidence": 0.94},
            {"token_id": "T2", "pada": "anityāḥ", "stem": "anitya", "vibhakti": "prathama", "vacana": "bahuvacana", "linga": "pullinga", "pos": "subhanta", "confidence": 0.94},
            {"token_id": "T3", "pada": "utpattidharmakatvāt", "stem": "utpattidharmakatva", "vibhakti": "pancami", "vacana": "ekavacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.91},
        ],
        "sandhi_splits": [],
        "canon_refs": [{"canon_name": "Nyāyasūtra", "reference_locator": "1.1.33", "domain": "nyaya"}],
    },
    # F08: rūpaṃ dṛśyaṃ parimāṇavattvāt
    "rūpaṃ dṛśyaṃ parimāṇavattvāt": {
        "tokens": [
            {"token_id": "T0", "pada": "rūpam", "stem": "rūpa", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.95},
            {"token_id": "T1", "pada": "dṛśyam", "stem": "dṛśya", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.94},
            {"token_id": "T2", "pada": "parimāṇavattvāt", "stem": "parimāṇavattva", "vibhakti": "pancami", "vacana": "ekavacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.92},
        ],
        "sandhi_splits": [],
        "canon_refs": [{"canon_name": "Nyāyasūtra", "reference_locator": "1.1.33", "domain": "nyaya"}],
    },
    # F09: ākāśaṃ nityam anutpattidharmakatvāt
    "ākāśaṃ nityam anutpattidharmakatvāt": {
        "tokens": [
            {"token_id": "T0", "pada": "ākāśam", "stem": "ākāśa", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.95},
            {"token_id": "T1", "pada": "nityam", "stem": "nitya", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.94},
            {"token_id": "T2", "pada": "anutpattidharmakatvāt", "stem": "anutpattidharmakatva", "vibhakti": "pancami", "vacana": "ekavacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.91},
        ],
        "sandhi_splits": [],
        "canon_refs": [{"canon_name": "Nyāyasūtra", "reference_locator": "1.1.33", "domain": "nyaya"}],
    },
    # F10: śarīram anityam indriyārthatvāt
    "śarīram anityam indriyārthatvāt": {
        "tokens": [
            {"token_id": "T0", "pada": "śarīram", "stem": "śarīra", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.95},
            {"token_id": "T1", "pada": "anityaṃ", "stem": "anitya", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.94},
            {"token_id": "T2", "pada": "indriyārthatvāt", "stem": "indriyārthatva", "vibhakti": "pancami", "vacana": "ekavacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.91},
        ],
        "sandhi_splits": [],
        "canon_refs": [{"canon_name": "Nyāyasūtra", "reference_locator": "1.1.33", "domain": "nyaya"}],
    },
}

def get(surface: str) -> Optional[dict]:
    return _F_SURFACES.get(surface)