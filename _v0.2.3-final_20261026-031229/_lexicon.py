"""
Aigaane v0.2.0 — Verified Pada & Stem Lexicon
"""

WORDS = {
    # Category A & Sandhi Components
    "rāmaḥ": {
        "stem": "rāma", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.98
    },
    "rāma": {
        "stem": "rāma", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95
    },
    "rāmāya": {
        "stem": "rāma", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "caturthi", "vacana": "ekavacana", "confidence": 0.98
    },
    "gacchati": {
        "stem": "gam", "pos": "tinanta", "linga": "na",
        "vibhakti": "na", "vacana": "ekavacana", "dhatu": "gam", "gana": 1,
        "confidence": 0.97
    },
    "api": {
        "stem": "api", "pos": "nipata", "linga": "na",
        "vibhakti": "na", "vacana": "na", "confidence": 0.99
    },
    "hima": {
        "stem": "hima", "pos": "subhanta", "linga": "napumsakalinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95
    },
    "alayaḥ": {
        "stem": "ālaya", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95
    },
    "ālayaḥ": {
        "stem": "ālaya", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.96
    },
    "na": {
        "stem": "na", "pos": "avyaya", "linga": "na",
        "vibhakti": "na", "vacana": "na", "confidence": 0.99
    },
    "asti": {
        "stem": "as", "pos": "tinanta", "linga": "na",
        "vibhakti": "na", "vacana": "ekavacana", "dhatu": "as", "gana": 2,
        "confidence": 0.98
    },
    "vāk": {
        "stem": "vāc", "pos": "subhanta", "linga": "strilinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.96
    },
    "īśaḥ": {
        "stem": "īśa", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.96
    },
    "tat": {
        "stem": "tad", "pos": "subhanta", "linga": "napumsakalinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.97
    },
    "ca": {
        "stem": "ca", "pos": "nipata", "linga": "na",
        "vibhakti": "na", "vacana": "na", "confidence": 0.99
    },
    "sat": {
        "stem": "sat", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95
    },
    "janaḥ": {
        "stem": "jana", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.97
    },
    "iti": {
        "stem": "iti", "pos": "nipata", "linga": "na",
        "vibhakti": "na", "vacana": "na", "confidence": 0.99
    },
    "madhu": {
        "stem": "madhu", "pos": "subhanta", "linga": "napumsakalinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.96
    },
    "ari": {
        "stem": "ari", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95
    },
    "deva": {
        "stem": "deva", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.96
    },
    "indraḥ": {
        "stem": "indra", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.97
    },
    "gaṇa": {
        "stem": "gaṇa", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.96
    },
    "pitṛ": {
        "stem": "pitṛ", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.96
    },
    "ājñā": {
        "stem": "ājñā", "pos": "subhanta", "linga": "strilinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.97
    },
    "tvam": {
        "stem": "yuṣmad", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.97
    },
    "naraḥ": {
        "stem": "nara", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.97
    },

    # Category E — Indeclinables
    "eva": {
        "stem": "eva", "pos": "nipata", "linga": "na",
        "vibhakti": "na", "vacana": "na", "confidence": 0.99
    },
    "tataḥ": {
        "stem": "tatas", "pos": "avyaya", "linga": "na",
        "vibhakti": "na", "vacana": "na", "confidence": 0.97
    },
    "yathā": {
        "stem": "yathā", "pos": "avyaya", "linga": "na",
        "vibhakti": "na", "vacana": "na", "confidence": 0.98
    },
    "hi": {
        "stem": "hi", "pos": "nipata", "linga": "na",
        "vibhakti": "na", "vacana": "na", "confidence": 0.99
    },
    "katham": {
        "stem": "katham", "pos": "nipata", "linga": "na",
        "vibhakti": "na", "vacana": "na", "confidence": 0.98
    },
    "adya": {
        "stem": "adya", "pos": "avyaya", "linga": "na",
        "vibhakti": "na", "vacana": "na", "confidence": 0.98
    },
    "upa": {
        "stem": "upa", "pos": "upasarga", "linga": "na",
        "vibhakti": "na", "vacana": "na", "confidence": 0.98
    },

    # Category D — Tinanta Verbs
    "bhavati": {
        "stem": "bhavat", "pos": "tinanta", "linga": "na",
        "vibhakti": "na", "vacana": "ekavacana",
        "dhatu": "bhū", "gana": 1, "confidence": 0.97
    },
    "paṭhati": {
        "stem": "paṭhat", "pos": "tinanta", "linga": "na",
        "vibhakti": "na", "vacana": "ekavacana",
        "dhatu": "paṭh", "gana": 1, "confidence": 0.96
    },
    "karoti": {
        "stem": "karot", "pos": "tinanta", "linga": "na",
        "vibhakti": "na", "vacana": "ekavacana",
        "dhatu": "kṛ", "gana": 8, "confidence": 0.97
    },
    "pibati": {
        "stem": "pibat", "pos": "tinanta", "linga": "na",
        "vibhakti": "na", "vacana": "ekavacana",
        "dhatu": "pā", "gana": 1, "confidence": 0.96
    },
    "labhate": {
        "stem": "labhat", "pos": "tinanta", "linga": "na",
        "vibhakti": "na", "vacana": "ekavacana",
        "dhatu": "labh", "gana": 1, "confidence": 0.95
    },
    "dadāti": {
        "stem": "dadāt", "pos": "tinanta", "linga": "na",
        "vibhakti": "na", "vacana": "ekavacana",
        "dhatu": "dā", "gana": 3, "confidence": 0.96
    },
    "viśati": {
        "stem": "viśat", "pos": "tinanta", "linga": "na",
        "vibhakti": "na", "vacana": "ekavacana",
        "dhatu": "viś", "gana": 6, "confidence": 0.95
    },
    "vahati": {
        "stem": "vahat", "pos": "tinanta", "linga": "na",
        "vibhakti": "na", "vacana": "ekavacana",
        "dhatu": "vah", "gana": 1, "confidence": 0.96
    },
    "likhati": {
        "stem": "likhat", "pos": "tinanta", "linga": "na",
        "vibhakti": "na", "vacana": "ekavacana",
        "dhatu": "likh", "gana": 6, "confidence": 0.95
    },

    # Category B — Ambiguity Components
    "nara": {
        "stem": "nara", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95
    },
    "reśaḥ": {
        "stem": "reśa", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.80
    },
    "sarva": {
        "stem": "sarva", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95
    },
    "īśvaraḥ": {
        "stem": "īśvara", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95
    },
    "sarve": {
        "stem": "sarva", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "bahuvacana", "confidence": 0.85
    },
    "śvaraḥ": {
        "stem": "śvara", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.70
    },
    "maha": {
        "stem": "maha", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.90
    },
    "mahā": {
        "stem": "mahat", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95
    },
    "ṛṣiḥ": {
        "stem": "ṛṣi", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95
    },
    "sā": {
        "stem": "tad", "pos": "subhanta", "linga": "strilinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.98
    },
    "sa": {
        "stem": "tad", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95
    },
    "saḥ": {
        "stem": "tad", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.98
    },
    "ayaṃ": {
        "stem": "idam", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.98
    },
    "se": {
        "stem": "sa", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.70
    },
    "te": {
        "stem": "tad", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "bahuvacana", "confidence": 0.98
    },
    "taḥ": {
        "stem": "tad", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.75
    },
    "tada": {
        "stem": "tad", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.70
    },
    "pi": {
        "stem": "pi", "pos": "nipata", "linga": "na",
        "vibhakti": "na", "vacana": "na", "confidence": 0.70
    },
    "atra": {
        "stem": "atra", "pos": "avyaya", "linga": "na",
        "vibhakti": "na", "vacana": "na", "confidence": 0.98
    },
    "itya": {
        "stem": "itya", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.70
    },
    "tra": {
        "stem": "tra", "pos": "avyaya", "linga": "na",
        "vibhakti": "na", "vacana": "na", "confidence": 0.70
    },
    "hariḥ": {
        "stem": "hari", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95
    },
    "guruḥ": {
        "stem": "guru", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95
    },
    "somaḥ": {
        "stem": "soma", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95
    },
    "agniḥ": {
        "stem": "agni", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95
    },
    "kṛṣṇaḥ": {
        "stem": "kṛṣṇa", "pos": "subhanta", "linga": "pullinga",
        "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95
    },
}

def lookup(word: str):
    return WORDS.get(word)
