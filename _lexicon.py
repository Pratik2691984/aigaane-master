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
    "as":   {"gana": 2,  "pada": "parasmaipada", "stem_pres": "as",      "stem_fut": None,         "stem_perf": None,          "meaning": "to be"},
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
    ("ta",    "ekavacana",   "prathama_purusha"),
    ("etām",  "dvivacana",   "prathama_purusha"),
    ("anta",  "bahuvacana",  "prathama_purusha"),
    ("thāḥ",  "ekavacana",   "madhyama_purusha"),
    ("ethām", "dvivacana",   "madhyama_purusha"),
    ("dhvam", "bahuvacana",  "madhyama_purusha"),
    ("i",     "ekavacana",   "uttama_purusha"),
    ("vahi",  "dvivacana",   "uttama_purusha"),
    ("mahi",  "bahuvacana",  "uttama_purusha"),
]

_LAT_PARASMAI = [
    ("ti",    "ekavacana",   "prathama_purusha"),
    ("taḥ",   "dvivacana",   "prathama_purusha"),
    ("anti",  "bahuvacana",  "prathama_purusha"),
    ("si",    "ekavacana",   "madhyama_purusha"),
    ("thaḥ",  "dvivacana",   "madhyama_purusha"),
    ("tha",   "bahuvacana",  "madhyama_purusha"),
    ("mi",    "ekavacana",   "uttama_purusha"),
    ("vaḥ",   "dvivacana",   "uttama_purusha"),
    ("maḥ",   "bahuvacana",  "uttama_purusha"),
]

_LAT_ATMANE = [
    ("te",    "ekavacana",   "prathama_purusha"),
    ("ete",   "dvivacana",   "prathama_purusha"),
    ("ante",  "bahuvacana",  "prathama_purusha"),
    ("se",    "ekavacana",   "madhyama_purusha"),
    ("ethe",  "dvivacana",   "madhyama_purusha"),
    ("dhve",  "bahuvacana",  "madhyama_purusha"),
    ("e",     "ekavacana",   "uttama_purusha"),
    ("vahe",  "dvivacana",   "uttama_purusha"),
    ("mahe",  "bahuvacana",  "uttama_purusha"),
]

_LIT_PARASMAI = [
    ("a",     "ekavacana",   "prathama_purusha"),
    ("atuḥ",  "dvivacana",   "prathama_purusha"),
    ("uḥ",    "bahuvacana",  "prathama_purusha"),
    ("tha",   "ekavacana",   "madhyama_purusha"),
    ("athuḥ", "dvivacana",   "madhyama_purusha"),
    ("a",     "bahuvacana",  "madhyama_purusha"),
    ("a",     "ekavacana",   "uttama_purusha"),
    ("va",    "dvivacana",   "uttama_purusha"),
    ("ma",    "bahuvacana",  "uttama_purusha"),
]

_LIT_ATMANE = [
    ("e",     "ekavacana",   "prathama_purusha"),
    ("āte",   "dvivacana",   "prathama_purusha"),
    ("ire",   "bahuvacana",  "prathama_purusha"),
    ("se",    "ekavacana",   "madhyama_purusha"),
    ("āthe",  "dvivacana",   "madhyama_purusha"),
    ("dhve",  "bahuvacana",  "madhyama_purusha"),
    ("e",     "ekavacana",   "uttama_purusha"),
    ("vahe",  "dvivacana",   "uttama_purusha"),
    ("mahe",  "bahuvacana",  "uttama_purusha"),
]

_LAT_ENDINGS = _LAT_PARASMAI + [
    ("te",  "ekavacana",  "prathama_purusha"),
    ("ite", "dvivacana",  "prathama_purusha"),
    ("ete", "dvivacana",  "prathama_purusha"),
    ("nte", "bahuvacana", "prathama_purusha"),
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
        pada_lat = info.get("pada", "parasmaipada")
        lat_candidates = []
        if pada_lat in ("parasmaipada", "ubhayapada"):
            lat_candidates.extend(_LAT_PARASMAI)
        if pada_lat in ("ātmanepada", "ubhayapada"):
            lat_candidates.extend(_LAT_ATMANE)
            lat_candidates.append(("ite", "dvivacana", "prathama_purusha"))

        for ending, vacana, purusha in lat_candidates:
            expected_form = None
            if ending.startswith("a") or ending.startswith("e"):
                if base_pres.endswith("a"):
                    expected_form = base_pres[:-1] + ending
                else:
                    expected_form = base_pres + ending
            elif ending.startswith("i"):
                if base_pres.endswith("a"):
                    expected_form = base_pres[:-1] + "e" + ending[1:]
                else:
                    expected_form = base_pres + ending
            elif ending in ("vaḥ", "maḥ", "vahe", "mahe"):
                # Ato dīrgho yañi (7.3.101): lengthening before v/m
                if base_pres.endswith("a"):
                    expected_form = base_pres[:-1] + "ā" + ending
                else:
                    expected_form = base_pres + ending
            elif ending == "mi":
                # Ato dīrgho yañi (7.3.101): lengthening before mi
                if base_pres.endswith("a"):
                    expected_form = base_pres[:-1] + "āmi"
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
            elif ending in ("va", "ma", "vahi", "mahi"):
                # Ato dīrgho yañi (7.3.101): lengthening before v/m
                expected_lan = aug_base[:-1] + "ā" + ending if aug_base.endswith("a") else aug_base + ending
            elif ending.startswith("e"):
                expected_lan = aug_base[:-1] + ending if aug_base.endswith("a") else aug_base + ending
            elif ending == "anta":
                expected_lan = aug_base[:-1] + "anta" if aug_base.endswith("a") else aug_base + ending
            elif ending == "i":
                # 1st person singular Ātmanepada: a + i -> e
                expected_lan = aug_base[:-1] + "e" if aug_base.endswith("a") else aug_base + "i"
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

        # Lṛṭ (Simple Future) evaluation with stem_fut (3.1.33)
        base_fut = info.get("stem_fut")
        if base_fut:
            pada_fut = info.get("pada", "parasmaipada")
            lrt_candidates = []
            if pada_fut in ("parasmaipada", "ubhayapada"):
                lrt_candidates.extend(_LAT_PARASMAI)
            if pada_fut in ("ātmanepada", "ubhayapada"):
                lrt_candidates.extend(_LAT_ATMANE)

            for ending, vacana, purusha in lrt_candidates:
                expected_lrt = None
                if ending.startswith("a") or ending.startswith("e"):
                    expected_lrt = base_fut[:-1] + ending if base_fut.endswith("a") else base_fut + ending
                elif ending == "nte":
                    expected_lrt = base_fut + "nte" if not base_fut.endswith("a") else base_fut[:-1] + "ante"
                elif ending.startswith("i"):
                    expected_lrt = base_fut[:-1] + "e" + ending[1:] if base_fut.endswith("a") else base_fut + ending
                elif ending in ("vaḥ", "maḥ", "vahe", "mahe"):
                    # Ato dīrgho yañi (7.3.101): lengthening before v/m
                    expected_lrt = base_fut[:-1] + "ā" + ending if base_fut.endswith("a") else base_fut + ending
                elif ending == "mi":
                    # Ato dīrgho yañi (7.3.101): lengthening before mi
                    expected_lrt = base_fut[:-1] + "āmi" if base_fut.endswith("a") else base_fut + ending
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
        pada_lit = info.get("pada", "parasmaipada")
        stem_sg = info.get("stem_perf_sg") or info.get("stem_perf")
        stem_pl = info.get("stem_perf_pl") or info.get("stem_perf")

        if stem_sg or stem_pl:
            # Āto ṇala auḥ (3.4.82) for ākārānta roots (dadau, papau)
            if stem_sg and stem_sg.endswith("au") and word == stem_sg:
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

            if pada_lit in ("parasmaipada", "ubhayapada"):
                for ending, vacana, purusha in _LIT_PARASMAI:
                    # Select strong grade for 3sg/1sg ṇal, weak for dual/plural
                    curr_stem = stem_sg if purusha == "prathama_purusha" and vacana == "ekavacana" else (stem_pl or stem_sg)
                    if not curr_stem:
                        continue
                    
                    expected = curr_stem + ending
                    # iḍ-āgama (7.2.35) for valādi ardhadhātuka endings (-tha, -va, -ma) on set roots like bhū
                    if dhatu == "bhū":
                        if ending == "tha":
                            expected = curr_stem + "itha"
                        elif ending in ("va", "ma"):
                            expected = curr_stem + "i" + ending
                    
                    if word == expected:
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

            if pada_lit in ("ātmanepada", "ubhayapada"):
                base_stem = stem_pl or stem_sg
                if base_stem:
                    for ending, vacana, purusha in _LIT_ATMANE:
                        expected = base_stem + ending
                        # iṭ-āgama & ṣatva for labh: se -> iṣe, dhve -> idhve, vahe -> ivahe, mahe -> imahe
                        if dhatu == "labh":
                            if ending == "se":
                                expected = base_stem + "iṣe"
                            elif ending == "dhve":
                                expected = base_stem + "idhve"
                            elif ending in ("vahe", "mahe"):
                                expected = base_stem + "i" + ending
                        
                        if word == expected:
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

    return None


# --- Subanta Paradigm Tables (v0.8.0) ---
_PRONOUNS_EXACT = {
    # tad (pulliṅga)
    "saḥ":     {"stem": "tad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.98},
    "tau":     {"stem": "tad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "dvivacana", "confidence": 0.98},
    "te":      {"stem": "tad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "bahuvacana", "confidence": 0.98},
    "tam":     {"stem": "tad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "dvitiya", "vacana": "ekavacana", "confidence": 0.98},
    "tān":     {"stem": "tad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "dvitiya", "vacana": "bahuvacana", "confidence": 0.98},
    "tena": {"stem": "tad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "trtiya", "vacana": "ekavacana", "confidence": 0.98},
    "tābhyām": {"stem": "tad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "trtiya", "vacana": "dvivacana", "confidence": 0.98},
    "taiḥ":    {"stem": "tad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "trtiya", "vacana": "bahuvacana", "confidence": 0.98},
    "tasmai":  {"stem": "tad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "caturthi", "vacana": "ekavacana", "confidence": 0.98},
    "tasmāt":  {"stem": "tad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "pancami", "vacana": "ekavacana", "confidence": 0.98},
    "tasya":   {"stem": "tad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "shasthi", "vacana": "ekavacana", "confidence": 0.98},
    "tayoḥ":   {"stem": "tad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "shasthi", "vacana": "dvivacana", "confidence": 0.98},
    "teṣām":   {"stem": "tad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "shasthi", "vacana": "bahuvacana", "confidence": 0.98},
    "tasmin":  {"stem": "tad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "saptami", "vacana": "ekavacana", "confidence": 0.98},
    "teṣu":    {"stem": "tad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "saptami", "vacana": "bahuvacana", "confidence": 0.98},

    # tad (strīliṅga)
    "sā":      {"stem": "tad", "pos": "subhanta", "linga": "strilinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.98},
    "tāḥ":     {"stem": "tad", "pos": "subhanta", "linga": "strilinga", "vibhakti": "prathama", "vacana": "bahuvacana", "confidence": 0.98},
    "tām":     {"stem": "tad", "pos": "subhanta", "linga": "strilinga", "vibhakti": "dvitiya", "vacana": "ekavacana", "confidence": 0.98},
    "tayā":    {"stem": "tad", "pos": "subhanta", "linga": "strilinga", "vibhakti": "trtiya", "vacana": "ekavacana", "confidence": 0.98},
    "tasyai":  {"stem": "tad", "pos": "subhanta", "linga": "strilinga", "vibhakti": "caturthi", "vacana": "ekavacana", "confidence": 0.98},
    "tasyāḥ":  {"stem": "tad", "pos": "subhanta", "linga": "strilinga", "vibhakti": "pancami", "vacana": "ekavacana", "confidence": 0.98},
    "tāsām":   {"stem": "tad", "pos": "subhanta", "linga": "strilinga", "vibhakti": "shasthi", "vacana": "bahuvacana", "confidence": 0.98},
    "tasyām":  {"stem": "tad", "pos": "subhanta", "linga": "strilinga", "vibhakti": "saptami", "vacana": "ekavacana", "confidence": 0.98},
    "tāsu":    {"stem": "tad", "pos": "subhanta", "linga": "strilinga", "vibhakti": "saptami", "vacana": "bahuvacana", "confidence": 0.98},

    # tad (napuṃsakaliṅga)
    "tat":     {"stem": "tad", "pos": "subhanta", "linga": "napumsakalinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.98},
    "tāni":    {"stem": "tad", "pos": "subhanta", "linga": "napumsakalinga", "vibhakti": "prathama", "vacana": "bahuvacana", "confidence": 0.98},

    # asmad (1st person)
    "aham":    {"stem": "asmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.98},
    "āvām":    {"stem": "asmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "dvivacana", "confidence": 0.98},
    "vayam":   {"stem": "asmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "bahuvacana", "confidence": 0.98},
    "mām":     {"stem": "asmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "dvitiya", "vacana": "ekavacana", "confidence": 0.98},
    "mayā":    {"stem": "asmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "trtiya", "vacana": "ekavacana", "confidence": 0.98},
    "mahyam":  {"stem": "asmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "caturthi", "vacana": "ekavacana", "confidence": 0.98},
    "mat":     {"stem": "asmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "pancami", "vacana": "ekavacana", "confidence": 0.98},
    "mama":    {"stem": "asmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "shasthi", "vacana": "ekavacana", "confidence": 0.98},
    "mayi":    {"stem": "asmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "saptami", "vacana": "ekavacana", "confidence": 0.98},

    # yuṣmad (2nd person)
    "tvam":    {"stem": "yuṣmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.98},
    "yuvām":   {"stem": "yuṣmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "dvivacana", "confidence": 0.98},
    "yūyam":   {"stem": "yuṣmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "bahuvacana", "confidence": 0.98},
    "tvām":    {"stem": "yuṣmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "dvitiya", "vacana": "ekavacana", "confidence": 0.98},
    "tvayā":   {"stem": "yuṣmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "trtiya", "vacana": "ekavacana", "confidence": 0.98},
    "tubhyam": {"stem": "yuṣmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "caturthi", "vacana": "ekavacana", "confidence": 0.98},
    "tvat":    {"stem": "yuṣmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "pancami", "vacana": "ekavacana", "confidence": 0.98},
    "tava":    {"stem": "yuṣmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "shasthi", "vacana": "ekavacana", "confidence": 0.98},
    "tvayi":   {"stem": "yuṣmad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "saptami", "vacana": "ekavacana", "confidence": 0.98},
}

_KNOWN_FEMININE_AA = {"latā": "lat", "bālā": "bāl", "kanyā": "kany"}
_KNOWN_NEUTER_A    = {"phala": "phal", "vana": "van", "kamala": "kamal"}

def _analyze_subanta(word: str):
    # 1. Exact Pronouns
    if word in _PRONOUNS_EXACT:
        return dict(_PRONOUNS_EXACT[word])

    # 2. Feminine ākārānta (latā)
    for stem_full, base in _KNOWN_FEMININE_AA.items():
        if word == stem_full:
            return {"stem": stem_full, "pos": "subhanta", "linga": "strilinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.96}
        if word == base + "e":
            return {"stem": stem_full, "pos": "subhanta", "linga": "strilinga", "vibhakti": "prathama", "vacana": "dvivacana", "confidence": 0.96}
        if word == base + "āḥ":
            return {"stem": stem_full, "pos": "subhanta", "linga": "strilinga", "vibhakti": "prathama", "vacana": "bahuvacana", "confidence": 0.96}
        if word == base + "ām":
            return {"stem": stem_full, "pos": "subhanta", "linga": "strilinga", "vibhakti": "dvitiya", "vacana": "ekavacana", "confidence": 0.96}
        if word == base + "ayā":
            return {"stem": stem_full, "pos": "subhanta", "linga": "strilinga", "vibhakti": "trtiya", "vacana": "ekavacana", "confidence": 0.96}
        if word == base + "āyai":
            return {"stem": stem_full, "pos": "subhanta", "linga": "strilinga", "vibhakti": "caturthi", "vacana": "ekavacana", "confidence": 0.96}
        if word == base + "āyāḥ":
            return {"stem": stem_full, "pos": "subhanta", "linga": "strilinga", "vibhakti": "pancami", "vacana": "ekavacana", "confidence": 0.96}
        if word == base + "āyām":
            return {"stem": stem_full, "pos": "subhanta", "linga": "strilinga", "vibhakti": "saptami", "vacana": "ekavacana", "confidence": 0.96}

    # 3. Neuter akārānta (phala)
    for stem_full, base in _KNOWN_NEUTER_A.items():
        if word == base + "am":
            return {"stem": stem_full, "pos": "subhanta", "linga": "napumsakalinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.96}
        if word == base + "e":
            return {"stem": stem_full, "pos": "subhanta", "linga": "napumsakalinga", "vibhakti": "prathama", "vacana": "dvivacana", "confidence": 0.96}
        if word in (base + "āni", base + "ani"):
            return {"stem": stem_full, "pos": "subhanta", "linga": "napumsakalinga", "vibhakti": "prathama", "vacana": "bahuvacana", "confidence": 0.96}

    # 4. Masculine akārānta (legacy)
    if word.endswith("asya") and len(word) > 4:
        stem = word[:-4] + "a"
        if stem in _STATIC_LEXICON or (stem + "ḥ") in _STATIC_LEXICON:
            return {"stem": stem, "pos": "subhanta", "linga": "pullinga", "vibhakti": "shasthi", "vacana": "ekavacana", "confidence": 0.95}
    if word.endswith("āt") and len(word) > 2:
        stem = word[:-2] + "a"
        if stem in _STATIC_LEXICON or (stem + "ḥ") in _STATIC_LEXICON:
            return {"stem": stem, "pos": "subhanta", "linga": "pullinga", "vibhakti": "pancami", "vacana": "ekavacana", "confidence": 0.95}
    if word.endswith("am") and len(word) > 2:
        stem = word[:-2] + "a"
        if stem in _STATIC_LEXICON or (stem + "ḥ") in _STATIC_LEXICON:
            return {"stem": stem, "pos": "subhanta", "linga": "napumsakalinga", "vibhakti": "dvitiya", "vacana": "ekavacana", "confidence": 0.92}
    return None


# Halanta (Consonant-ending) Nominal Paradigms (v0.8.2)
_HALANTA_LOOKUP = {
    # marut (m., t-stem)
    "marut": {"stem": "marut", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.98},
    "marutau": {"stem": "marut", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "dvivacana", "confidence": 0.98},
    "marutaḥ": {"stem": "marut", "pos": "subhanta", "linga": "pullinga", "vibhakti": "prathama", "vacana": "bahuvacana", "confidence": 0.98},
    "marutam": {"stem": "marut", "pos": "subhanta", "linga": "pullinga", "vibhakti": "dvitiya", "vacana": "ekavacana", "confidence": 0.98},
    "marutā": {"stem": "marut", "pos": "subhanta", "linga": "pullinga", "vibhakti": "trtiya", "vacana": "ekavacana", "confidence": 0.98},
    "marudbhyām": {"stem": "marut", "pos": "subhanta", "linga": "pullinga", "vibhakti": "trtiya", "vacana": "dvivacana", "confidence": 0.98},
    "marudbhiḥ": {"stem": "marut", "pos": "subhanta", "linga": "pullinga", "vibhakti": "trtiya", "vacana": "bahuvacana", "confidence": 0.98},
    "marute": {"stem": "marut", "pos": "subhanta", "linga": "pullinga", "vibhakti": "caturthi", "vacana": "ekavacana", "confidence": 0.98},
    "marudbhyaḥ": {"stem": "marut", "pos": "subhanta", "linga": "pullinga", "vibhakti": "caturthi", "vacana": "bahuvacana", "confidence": 0.98},
    "marutoḥ": {"stem": "marut", "pos": "subhanta", "linga": "pullinga", "vibhakti": "sasthi", "vacana": "dvivacana", "confidence": 0.98},
    "marutām": {"stem": "marut", "pos": "subhanta", "linga": "pullinga", "vibhakti": "sasthi", "vacana": "bahuvacana", "confidence": 0.98},
    "maruti": {"stem": "marut", "pos": "subhanta", "linga": "pullinga", "vibhakti": "saptami", "vacana": "ekavacana", "confidence": 0.98},
    "marutsu": {"stem": "marut", "pos": "subhanta", "linga": "pullinga", "vibhakti": "saptami", "vacana": "bahuvacana", "confidence": 0.98},

    # vāc (f., c-stem, coḥ kuḥ 8.2.30)
    "vāk": {"stem": "vāc", "pos": "subhanta", "linga": "strilinga", "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.98},
    "vācau": {"stem": "vāc", "pos": "subhanta", "linga": "strilinga", "vibhakti": "prathama", "vacana": "dvivacana", "confidence": 0.98},
    "vācaḥ": {"stem": "vāc", "pos": "subhanta", "linga": "strilinga", "vibhakti": "prathama", "vacana": "bahuvacana", "confidence": 0.98},
    "vācam": {"stem": "vāc", "pos": "subhanta", "linga": "strilinga", "vibhakti": "dvitiya", "vacana": "ekavacana", "confidence": 0.98},
    "vācā": {"stem": "vāc", "pos": "subhanta", "linga": "strilinga", "vibhakti": "trtiya", "vacana": "ekavacana", "confidence": 0.98},
    "vāgbhyām": {"stem": "vāc", "pos": "subhanta", "linga": "strilinga", "vibhakti": "trtiya", "vacana": "dvivacana", "confidence": 0.98},
    "vāgbhiḥ": {"stem": "vāc", "pos": "subhanta", "linga": "strilinga", "vibhakti": "trtiya", "vacana": "bahuvacana", "confidence": 0.98},
    "vāce": {"stem": "vāc", "pos": "subhanta", "linga": "strilinga", "vibhakti": "caturthi", "vacana": "ekavacana", "confidence": 0.98},
    "vāgbhyaḥ": {"stem": "vāc", "pos": "subhanta", "linga": "strilinga", "vibhakti": "caturthi", "vacana": "bahuvacana", "confidence": 0.98},
    "vācoḥ": {"stem": "vāc", "pos": "subhanta", "linga": "strilinga", "vibhakti": "sasthi", "vacana": "dvivacana", "confidence": 0.98},
    "vācām": {"stem": "vāc", "pos": "subhanta", "linga": "strilinga", "vibhakti": "sasthi", "vacana": "bahuvacana", "confidence": 0.98},
    "vāci": {"stem": "vāc", "pos": "subhanta", "linga": "strilinga", "vibhakti": "saptami", "vacana": "ekavacana", "confidence": 0.98},
    "vākṣu": {"stem": "vāc", "pos": "subhanta", "linga": "strilinga", "vibhakti": "saptami", "vacana": "bahuvacana", "confidence": 0.98},
}

def lookup(word: str) -> Optional[dict]:
    w = word.strip()
    if "_HALANTA_LOOKUP" in globals() and w in _HALANTA_LOOKUP:
        return _HALANTA_LOOKUP[w]
    if w == "tena":
        return {"stem": "tad", "pos": "subhanta", "linga": "pullinga", "vibhakti": "trtiya", "vacana": "ekavacana", "confidence": 0.98}
    if "_PRONOUNS_EXACT" in globals() and w in _PRONOUNS_EXACT:
        return dict(_PRONOUNS_EXACT[w])
    if w in _STATIC_LEXICON:
        return _STATIC_LEXICON[w]
    tin_hit = _analyze_tinanta(w)
    if tin_hit is not None:
        return tin_hit
    sub_hit = _analyze_subanta(w)
    if sub_hit is not None:
        return sub_hit
    return None

