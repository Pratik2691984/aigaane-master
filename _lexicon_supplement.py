"""
Supplement lexicon — loaded by _lexicon.py to extend _STATIC_LEXICON.
Contains proper nouns from epics and common compound parts not in the
base 2,500-stem lexicon.
"""

SUPPLEMENT_STEMS = {
    # Devas
    "indra": {"stem": "indra", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "agni": {"stem": "agni", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "varuṇa": {"stem": "varuṇa", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "soma": {"stem": "soma", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "yama": {"stem": "yama", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "kṛṣṇa": {"stem": "kṛṣṇa", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "sūrya": {"stem": "sūrya", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "candra": {"stem": "candra", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "viṣṇu": {"stem": "viṣṇu", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "śiva": {"stem": "śiva", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},

    # Epic heroes
    "arjuna": {"stem": "arjuna", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "bhīma": {"stem": "bhīma", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "yudhiṣṭhira": {"stem": "yudhiṣṭhira", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "nakula": {"stem": "nakula", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "sahadeva": {"stem": "sahadeva", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "lakṣmaṇa": {"stem": "lakṣmaṇa", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "sītā": {"stem": "sītā", "pos": "subhanta", "linga": "strilinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "hanumān": {"stem": "hanumān", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "rāvaṇa": {"stem": "rāvaṇa", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "karṇa": {"stem": "karṇa", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "bhīṣma": {"stem": "bhīṣma", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "duryodhana": {"stem": "duryodhana", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},

    # Compound decomposition parts (CRITICAL for recursion)
    "manuSya": {"stem": "manuSya", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "manuṣya": {"stem": "manuṣya", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "nAga": {"stem": "nAga", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "nāga": {"stem": "nāga", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "gandharva": {"stem": "gandharva", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "rākṣasa": {"stem": "rākṣasa", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "kinnara": {"stem": "kinnara", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "yakṣa": {"stem": "yakṣa", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},

    # Places/factions
    "kuru": {"stem": "kuru", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "pāṇḍava": {"stem": "pāṇḍava", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
}