"""
Aigaane v0.3.0-dev — Generative Paninian Lexicon & Dhātupāṭha Engine
Provides morphological analysis for subanta nominals, tinanta verb forms,
and avyaya indeclinables with deterministic root derivation.
"""

from typing import Optional, Dict, Any

_DHATUPATHA = {
    "bhū":  {"gana": 1, "pada": "parasmaipada", "stem_pres": "bhava",  "stem_fut": "bhaviṣya", "stem_perf": "babhūv", "meaning": "to be"},
    "gam":  {"gana": 1, "pada": "parasmaipada", "stem_pres": "gaccha", "stem_fut": "gamiṣya",  "stem_perf_sg": "jagām", "stem_perf_pl": "jagm", "meaning": "to go"},
    "paṭh": {"gana": 1, "pada": "parasmaipada", "stem_pres": "paṭha",  "stem_fut": "paṭhiṣya", "stem_perf": "papāṭh", "meaning": "to read"},
    "kṛ":   {"gana": 8, "pada": "ubhayapada",   "stem_pres": "karo",   "stem_fut": "kariṣya",  "stem_perf_sg": "cakār", "stem_perf_pl": "cakr", "meaning": "to do"},
    "pā":   {"gana": 1, "pada": "parasmaipada", "stem_pres": "piba",   "stem_fut": "pāsya",    "stem_perf": "papau",   "meaning": "to drink"},
    "labh": {"gana": 1, "pada": "ātmanepada",   "stem_pres": "labha",  "stem_fut": "lapsya",   "stem_perf": "lebh",    "meaning": "to obtain"},
    "dā":   {"gana": 3, "pada": "ubhayapada",   "stem_pres": "dadā",   "stem_fut": "dāsya",    "stem_perf": "dadau",   "meaning": "to give"},
    "viś":  {"gana": 6, "pada": "parasmaipada", "stem_pres": "viśa",   "stem_fut": "vekṣya",   "stem_perf": "viveś",   "meaning": "to enter"},
    "vah":  {"gana": 1, "pada": "ubhayapada",   "stem_pres": "vaha",   "stem_fut": "vakṣya",   "stem_perf": "uvāh",    "meaning": "to carry"},
    "likh": {"gana": 6, "pada": "parasmaipada", "stem_pres": "likha",  "stem_fut": "lekhiṣya", "stem_perf": "lilekh",  "meaning": "to write"},
    "vad":  {"gana": 1,  "pada": "parasmaipada", "stem_pres": "vada",    "stem_fut": "vadiṣya",    "stem_perf": "uvād",        "meaning": "to speak"},
    "as":   {"gana": 2,  "pada": "parasmaipada", "stem_pres": "as",      "stem_fut": "bhaviṣya",   "stem_perf": "babhūv",      "meaning": "to be"},
    "hu":   {"gana": 3,  "pada": "parasmaipada", "stem_pres": "juho",    "stem_fut": "hoṣya",      "stem_perf": "juhāv",       "meaning": "to offer"},
    "jñā":  {"gana": 9,  "pada": "ubhayapada",   "stem_pres": "jānā",    "stem_fut": "jñāsya",     "stem_perf": "jajñau",      "meaning": "to know"},
    "cur":  {"gana": 10, "pada": "ubhayapada",   "stem_pres": "coraya",  "stem_fut": "corayiṣya",  "stem_perf": "corayāmāsa",  "meaning": "to steal"},
}

_LAN_PARASMAI = [
    ("t",    "ekavacana",   "prathama_purusha"),
    ("tām",  "dvivacana",   "prathama_purusha"),
    ("n",    "bahuvacana",  "prathama_purusha"),
    ("ḥ",    "ekavacana",   "madhyama_purusha"),
    ("tam",  "dvivacana",   "madhyama_purusha"),
    ("ta",   "bahuvacana",  "madhyama_purusha"),
    ("am",   "ekavacana",   "uttama_purusha"),
    ("va",   "dvivacana",   "uttama_purusha"),
    ("ma",   "bahuvacana",  "uttama_purusha"),
]

_LAN_ATMANE = [
    ("ta",   "ekavacana",   "prathama_purusha"),
    ("etām", "dvivacana",   "prathama_purusha"),
    ("anta", "bahuvacana",  "prathama_purusha"),
]

_LAT_ENDINGS = [
    ("ti",    "ekavacana",  "prathama_purusha"),
    ("taḥ",   "dvivacana",  "prathama_purusha"),
    ("anti",  "bahuvacana", "prathama_purusha"),
    ("si",    "ekavacana",  "madhyama_purusha"),
    ("thaḥ",  "dvivacana",  "madhyama_purusha"),
    ("tha",   "bahuvacana", "madhyama_purusha"),
    ("mi",    "ekavacana",  "uttama_purusha"),
    ("vaḥ",   "dvivacana",  "uttama_purusha"),
    ("maḥ",   "bahuvacana", "uttama_purusha"),
    ("te",    "ekavacana",  "prathama_purusha"),
    ("ite",   "dvivacana",  "prathama_purusha"),
    ("nte",   "bahuvacana", "prathama_purusha"),
]

_STATIC_LEXICON: Dict[str, dict] = {
    # Indeclinables / Avyaya / Nipata / Upasarga
    "ca":     {"stem": "ca",     "pos": "nipata",   "linga": "na", "vibhakti": "na", "vacana": "na", "confidence": 0.99},
    "api":    {"stem": "api",    "pos": "nipata",   "linga": "na", "vibhakti": "na", "vacana": "na", "confidence": 0.99},
    "eva":    {"stem": "eva",    "pos": "nipata",   "linga": "na", "vibhakti": "na", "vacana": "na", "confidence": 0.99},
    "iti":    {"stem": "iti",    "pos": "nipata",   "linga": "na", "vibhakti": "na", "vacana": "na", "confidence": 0.99},
    "tataḥ":  {"stem": "tatas",  "pos": "avyaya",   "linga": "na", "vibhakti": "na", "vacana": "na", "confidence": 0.98},
    "yathā":  {"stem": "yathā",  "pos": "avyaya",   "linga": "na", "vibhakti": "na", "vacana": "na", "confidence": 0.98},
    "hi":     {"stem": "hi",     "pos": "nipata",   "linga": "na", "vibhakti": "na", "vacana": "na", "confidence": 0.98},
    "katham": {"stem": "katham", "pos": "nipata",   "linga": "na", "vibhakti": "na", "vacana": "na", "confidence": 0.98},
    "adya":   {"stem": "adya",   "pos": "avyaya",   "linga": "na", "vibhakti": "na", "vacana": "na", "confidence": 0.98},
    "upa":    {"stem": "upa",    "pos": "upasarga", "linga": "na", "vibhakti": "na", "vacana": "na", "confidence": 0.99},
    "na":     {"stem": "na",     "pos": "avyaya",   "linga": "na", "vibhakti": "na", "vacana": "na", "confidence": 0.99},

    # Core Noun Stems / Nominals
    "rāma":      {"stem": "rāma",      "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.98},
    "rāmaḥ":     {"stem": "rāma",      "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.98},
    "rāmāya":    {"stem": "rāma",      "pos": "subhanta", "linga": "pullinga",      "vibhakti": "caturthi", "vacana": "ekavacana", "confidence": 0.95},
    "hima":      {"stem": "hima",      "pos": "subhanta", "linga": "napumsakalinga","vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "ālayaḥ":    {"stem": "ālaya",     "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "alayaḥ":    {"stem": "alaya",     "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "asti":      {"stem": "as",        "pos": "tinanta",  "dhatu": "as", "gana": 2, "linga": "na", "vibhakti": "na", "vacana": "ekavacana", "confidence": 0.98},
    "vāk":       {"stem": "vāc",       "pos": "subhanta", "linga": "strilinga",     "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "īśaḥ":      {"stem": "īśa",       "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "tat":       {"stem": "tad",       "pos": "subhanta", "linga": "napumsakalinga","vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.97},
    "sat":       {"stem": "sat",       "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.96},
    "janaḥ":     {"stem": "jana",      "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.96},
    "madhu":     {"stem": "madhu",     "pos": "subhanta", "linga": "napumsakalinga","vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "ari":       {"stem": "ari",       "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.94},
    "deva":      {"stem": "deva",      "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "devaḥ":     {"stem": "deva",      "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "indraḥ":    {"stem": "indra",     "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "gaṇa":      {"stem": "gaṇa",      "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "pitṛ":      {"stem": "pitṛ",      "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "ājñā":      {"stem": "ājñā",      "pos": "subhanta", "linga": "strilinga",     "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "tvam":      {"stem": "yuṣmad",    "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.96},
    "naraḥ":     {"stem": "nara",      "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.98},
    "nara":      {"stem": "nara",      "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.98},
    "maha":      {"stem": "maha",      "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "putra":     {"stem": "putra",     "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "putraḥ":    {"stem": "putra",     "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "vadha":     {"stem": "vadha",     "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
    "vadhaḥ":    {"stem": "vadha",     "pos": "subhanta", "linga": "pullinga",      "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.95},
}


def _analyze_tinanta(word: str) -> Optional[dict]:
    for dhatu, info in _DHATUPATHA.items():
        base_pres = info["stem_pres"]
        for ending, vacana, purusha in _LAT_ENDINGS:
            expected_form = None
            if ending.startswith("a"):
                if base_pres.endswith("a"):
                    expected_form = base_pres[:-1] + ending
                else:
                    expected_form = base_pres + ending
            elif ending.startswith("i"):
                if base_pres.endswith("a"):
                    expected_form = base_pres[:-1] + "e" + ending[1:]
                else:
                    expected_form = base_pres + ending
            else:
                expected_form = base_pres + ending

            if expected_form == word:
                return {
                    "stem": dhatu,
                    "pos": "tinanta",
                    "dhatu": dhatu,
                    "gana": info["gana"],
                    "vibhakti": "na",
                    "vacana": vacana,
                    "linga": "na",
                    "confidence": 0.96,
                }

        # Laṅ (Imperfect Past) evaluation with aṭ-āgama (6.4.71)
        aug_base = "a" + base_pres
        is_atmane = info.get("pada") == "ātmanepada"
        lan_endings = _LAN_ATMANE if is_atmane else _LAN_PARASMAI

        for ending, vacana, purusha in lan_endings:
            expected_lan = None
            if ending == "am":
                expected_lan = aug_base[:-1] + "am" if aug_base.endswith("a") else aug_base + "am"
            elif ending == "n":
                expected_lan = aug_base[:-1] + "an" if aug_base.endswith("a") else aug_base + "an"
            elif ending in ("va", "ma"):
                expected_lan = aug_base[:-1] + "ā" + ending if aug_base.endswith("a") else aug_base + ending
            elif ending.startswith("e"):
                expected_lan = aug_base[:-1] + ending if aug_base.endswith("a") else aug_base + ending
            elif ending == "anta":
                expected_lan = aug_base[:-1] + "anta" if aug_base.endswith("a") else aug_base + ending
            else:
                expected_lan = aug_base + ending

            if expected_lan == word:
                return {
                    "stem": dhatu,
                    "pos": "tinanta",
                    "dhatu": dhatu,
                    "gana": info["gana"],
                    "vibhakti": "na",
                    "vacana": vacana,
                    "linga": "na",
                    "confidence": 0.96,
                }


        # Lṛṭ (Simple Future) evaluation with stem_fut
        base_fut = info.get("stem_fut")
        if base_fut:
            pada_fut = info.get("pada", "parasmaipada")
            # Define primary endings for future tense
            lrt_endings = []
            if pada_fut in ("ātmanepada", "ubhayapada"):
                lrt_endings.extend([
                    ("te",   "ekavacana",   "prathama_purusha"),
                    ("ete",  "dvivacana",   "prathama_purusha"),
                    ("nte",  "bahuvacana",  "prathama_purusha"),
                    ("se",   "ekavacana",   "madhyama_purusha"),
                    ("ethe", "dvivacana",   "madhyama_purusha"),
                    ("dhve", "bahuvacana",  "madhyama_purusha"),
                    ("e",    "ekavacana",   "uttama_purusha"),
                    ("vahe", "dvivacana",   "uttama_purusha"),
                    ("mahe", "bahuvacana",  "uttama_purusha"),
                ])
            if pada_fut in ("parasmaipada", "ubhayapada"):
                lrt_endings.extend(_LAT_ENDINGS)

            for ending, vacana, purusha in lrt_endings:
                expected_lrt = None
                if ending.startswith("a"):
                    expected_lrt = base_fut[:-1] + ending if base_fut.endswith("a") else base_fut + ending
                elif ending == "nte":
                    expected_lrt = base_fut[:-1] + "nte" if base_fut.endswith("a") else base_fut + ending
                elif ending.startswith("e"):
                    expected_lrt = base_fut[:-1] + ending if base_fut.endswith("a") else base_fut + ending
                elif ending.startswith("i"):
                    expected_lrt = base_fut[:-1] + "e" + ending[1:] if base_fut.endswith("a") else base_fut + ending
                else:
                    expected_lrt = base_fut + ending

                if expected_lrt == word:
                    return {
                        "stem": dhatu,
                        "pos": "tinanta",
                        "dhatu": dhatu,
                        "gana": info["gana"],
                        "vibhakti": "na",
                        "vacana": vacana,
                        "linga": "na",
                        "confidence": 0.96,
                    }


        # Liṭ (Perfect Past) evaluation with reduplicated stems (3.2.115)
        # Parasmaipada: ṇal (a), atus (atuḥ), us (uḥ)
        # Ātmanepada: eś (e), āte (āte), irec (ire)
        pada_lit = info.get("pada", "parasmaipada")
        
        # Check singular (strong grade)
        stem_sg = info.get("stem_perf_sg") or info.get("stem_perf")
        stem_pl = info.get("stem_perf_pl") or info.get("stem_perf")

        if stem_sg:
            if pada_lit in ("parasmaipada", "ubhayapada"):
                # 3rd sg / 1st sg: Nal (-a)
                if word == stem_sg + "a":
                    return {
                        "stem": dhatu,
                        "pos": "tinanta",
                        "dhatu": dhatu,
                        "gana": info["gana"],
                        "vibhakti": "na",
                        "vacana": "ekavacana",
                        "linga": "na",
                        "confidence": 0.96,
                    }
            if pada_lit in ("ātmanepada", "ubhayapada"):
                # 3rd sg / 1st sg: eś (-e)
                if word == stem_sg + "e":
                    return {
                        "stem": dhatu,
                        "pos": "tinanta",
                        "dhatu": dhatu,
                        "gana": info["gana"],
                        "vibhakti": "na",
                        "vacana": "ekavacana",
                        "linga": "na",
                        "confidence": 0.96,
                    }

        if stem_pl:
            if pada_lit in ("parasmaipada", "ubhayapada"):
                # 3rd dual: atus (-atuḥ)
                if word == stem_pl + "atuḥ":
                    return {
                        "stem": dhatu,
                        "pos": "tinanta",
                        "dhatu": dhatu,
                        "gana": info["gana"],
                        "vibhakti": "na",
                        "vacana": "dvivacana",
                        "linga": "na",
                        "confidence": 0.96,
                    }
                # 3rd plural: us (-uḥ)
                if word == stem_pl + "uḥ":
                    return {
                        "stem": dhatu,
                        "pos": "tinanta",
                        "dhatu": dhatu,
                        "gana": info["gana"],
                        "vibhakti": "na",
                        "vacana": "bahuvacana",
                        "linga": "na",
                        "confidence": 0.96,
                    }
            if pada_lit in ("ātmanepada", "ubhayapada"):
                # 3rd plural: irec (-ire)
                if word == stem_pl + "ire":
                    return {
                        "stem": dhatu,
                        "pos": "tinanta",
                        "dhatu": dhatu,
                        "gana": info["gana"],
                        "vibhakti": "na",
                        "vacana": "bahuvacana",
                        "linga": "na",
                        "confidence": 0.96,
                    }

    return None


def _analyze_subanta(word: str) -> Optional[dict]:
    if word.endswith("asya") and len(word) > 4:
        stem = word[:-4] + "a"
        if stem in _STATIC_LEXICON or (stem + "ḥ") in _STATIC_LEXICON:
            return {
                "stem": stem,
                "pos": "subhanta",
                "linga": "pullinga",
                "vibhakti": "shasthi",
                "vacana": "ekavacana",
                "confidence": 0.95,
            }
    if word.endswith("āt") and len(word) > 2:
        stem = word[:-2] + "a"
        if stem in _STATIC_LEXICON or (stem + "ḥ") in _STATIC_LEXICON:
            return {
                "stem": stem,
                "pos": "subhanta",
                "linga": "pullinga",
                "vibhakti": "pancami",
                "vacana": "ekavacana",
                "confidence": 0.95,
            }
    if word.endswith("am") and len(word) > 2:
        stem = word[:-2] + "a"
        if stem in _STATIC_LEXICON or (stem + "ḥ") in _STATIC_LEXICON:
            return {
                "stem": stem,
                "pos": "subhanta",
                "linga": "napumsakalinga",
                "vibhakti": "dvitiya",
                "vacana": "ekavacana",
                "confidence": 0.92,
            }
    return None


def lookup(word: str) -> Optional[dict]:
    w = word.strip()
    if w in _STATIC_LEXICON:
        return _STATIC_LEXICON[w]
    tin_hit = _analyze_tinanta(w)
    if tin_hit is not None:
        return tin_hit
    sub_hit = _analyze_subanta(w)
    if sub_hit is not None:
        return sub_hit
    return None
