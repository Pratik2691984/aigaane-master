"""
engine/morphology/subanta.py
Pāṇinian Subanta Declension Engine (Aṣṭādhyāyī 4.1.2)
Covers:
  - Masculine a-stem (अदन्त पुंल्लिङ्ग - राम)
  - Feminine ā-stem (आबन्त स्त्रीलिङ्ग - रमा)
  - Masculine/Feminine i-stem (इगन्त - हरि / मति)
  - Masculine/Feminine u-stem (उगन्त - गुरु / धेनु)
"""
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Optional
import unicodedata

# 4.1.2 sv-au-jas-am-auṭ-śas-ṭā-bhyām-bhis-ṅe-bhyām-bhyas-ṅasi-bhyām-bhyas-ṅas-os-ām-ṅy-os-sup
# Canonical 21-affix matrix arranged by 7 vibhaktis x 3 vacanas
CASES = ["prathama", "dvitiya", "trtiya", "caturthi", "pancami", "sasthi", "saptami", "sambodhana"]
NUMBERS = ["eka", "dvi", "bahu"]

# Alias maps for standard input normalization
CASE_ALIASES = {
    "1": "prathama", "prathama": "prathama", "nominative": "prathama",
    "2": "dvitiya", "dvitiya": "dvitiya", "accusative": "dvitiya",
    "3": "trtiya", "trtiya": "trtiya", "instrumental": "trtiya",
    "4": "caturthi", "caturthi": "caturthi", "dative": "caturthi",
    "5": "pancami", "pancami": "pancami", "ablative": "pancami",
    "6": "sasthi", "sasthi": "sasthi", "genitive": "sasthi",
    "7": "saptami", "saptami": "saptami", "locative": "saptami",
    "8": "sambodhana", "sambodhana": "sambodhana", "vocative": "sambodhana",
}

NUMBER_ALIASES = {
    "1": "eka", "singular": "eka", "eka": "eka", "ekavacana": "eka",
    "2": "dvi", "dual": "dvi", "dvi": "dvi", "dvivacana": "dvi",
    "3": "bahu", "plural": "bahu", "bahu": "bahu", "bahuvacana": "bahu",
}

CANONICAL_SUP: Dict[str, Dict[str, str]] = {
    "prathama":   {"eka": "सुँ",   "dvi": "औ",     "bahu": "जस्"},
    "dvitiya":    {"eka": "अम्",  "dvi": "औट्",   "bahu": "शस्"},
    "trtiya":     {"eka": "टा",   "dvi": "भ्याम्", "bahu": "भिस्"},
    "caturthi":   {"eka": "ङे",   "dvi": "भ्याम्", "bahu": "भ्यस्"},
    "pancami":    {"eka": "ङसिँ", "dvi": "भ्याम्", "bahu": "भ्यस्"},
    "sasthi":     {"eka": "ङस्",  "dvi": "ओस्",   "bahu": "आम्"},
    "saptami":    {"eka": "ङि",   "dvi": "ओस्",   "bahu": "सुप्"},
    "sambodhana": {"eka": "सुँ",   "dvi": "औ",     "bahu": "जस्"},
}

# 1.3.2 - 1.3.9 it-marker stripping rules
def strip_it_marker(affix: str) -> str:
    """Derives functional affix post-tasya-lopaḥ (1.3.9)."""
    mapping = {
        "सुँ": "स्", "औट्": "औ", "जस्": "अस्", "शस्": "अस्",
        "टा": "आ", "ङे": "ए", "ङसिँ": "अस्", "ङस्": "अस्",
        "ङि": "इ", "सुप्": "सु", "भ्याम्": "भ्याम्", "भिस्": "भिस्",
        "भ्यस्": "भ्यस्", "ओस्": "ओस्", "आम्": "आम्", "अम्": "अम्", "औ": "औ"
    }
    return mapping.get(affix, affix)


# Paradigm Tables with derivation sutra sequences
# Each entry: (inflected_form, [sūtras triggered])
PARADIGMS: Dict[str, Dict[str, Dict[str, Tuple[str, List[str]]]]] = {
    "a_masc": {
        "prathama":   {"eka": ("ः", ["4.1.2", "1.3.9", "8.2.66", "8.3.15"]), "dvi": ("ौ", ["7.1.9"]), "bahu": ("ाः", ["7.1.9", "6.1.102"])},
        "dvitiya":    {"eka": ("म्", ["6.1.107"]), "dvi": ("ौ", ["6.1.102"]), "bahu": ("ान्", ["6.1.103", "8.4.1"])},
        "trtiya":     {"eka": ("ेन", ["7.1.12", "8.4.2"]), "dvi": ("ābhyām", ["7.3.102"]), "bahu": ("ैः", ["7.1.9"])},
        "caturthi":   {"eka": ("ाय", ["7.1.13", "7.3.102"]), "dvi": ("ābhyām", ["7.3.102"]), "bahu": ("ebhyaḥ", ["7.3.103"])},
        "pancami":    {"eka": ("ात्", ["7.1.12"]), "dvi": ("ābhyām", ["7.3.102"]), "bahu": ("ebhyaḥ", ["7.3.103"])},
        "sasthi":     {"eka": ("स्य", ["7.1.12"]), "dvi": ("योः", ["7.3.104"]), "bahu": ("ाणाम्", ["7.1.54", "6.4.3", "8.4.2"])},
        "saptami":    {"eka": ("े", ["6.1.87"]), "dvi": ("योः", ["7.3.104"]), "bahu": ("ेषु", ["7.3.103", "8.3.59"])},
        "sambodhana": {"eka": ("", ["6.1.69"]), "dvi": ("ौ", ["7.1.9"]), "bahu": ("ाः", ["7.1.9", "6.1.102"])}
    },
    "aa_fem": {
        "prathama":   {"eka": ("रमा", ["4.1.4", "6.1.68"]), "dvi": ("रमे", ["7.3.105", "6.1.87"]), "bahu": ("रमाः", ["6.1.102", "8.2.66", "8.3.15"])},
        "dvitiya":    {"eka": ("रमाम्", ["6.1.107"]), "dvi": ("रमे", ["7.3.105", "6.1.87"]), "bahu": ("रमाः", ["6.1.102", "8.2.66", "8.3.15"])},
        "trtiya":     {"eka": ("रमया", ["7.3.105", "6.1.77"]), "dvi": ("रमाभ्याम्", ["4.1.2"]), "bahu": ("रमाभिः", ["4.1.2", "8.2.66", "8.3.15"])},
        "caturthi":   {"eka": ("रमायै", ["7.3.112", "7.3.113", "6.1.88"]), "dvi": ("रमाभ्याम्", ["4.1.2"]), "bahu": ("रमाभ्यः", ["4.1.2", "8.2.66", "8.3.15"])},
        "pancami":    {"eka": ("रमायाः", ["7.3.112", "7.3.113", "6.1.88"]), "dvi": ("रमाभ्याम्", ["4.1.2"]), "bahu": ("रमाभ्यः", ["4.1.2", "8.2.66", "8.3.15"])},
        "sasthi":     {"eka": ("रमायाः", ["7.3.112", "7.3.113", "6.1.88"]), "dvi": ("रमयोः", ["7.3.105", "6.1.77"]), "bahu": ("रमाclass_naam", ["7.1.54", "6.4.3"])},
        "saptami":    {"eka": ("रमायाम्", ["7.3.112", "7.3.116"]), "dvi": ("रमयोः", ["7.3.105", "6.1.77"]), "bahu": ("रमासु", ["4.1.2", "8.3.59"])},
        "sambodhana": {"eka": ("रमे", ["7.3.106", "6.1.69"]), "dvi": ("रमे", ["7.3.105", "6.1.87"]), "bahu": ("रमाः", ["6.1.102", "8.2.66", "8.3.15"])}
    },
    "i_masc": {
        "prathama":   {"eka": ("हरिः", ["4.1.2", "8.2.66", "8.3.15"]), "dvi": ("हरी", ["6.1.102"]), "bahu": ("हरयः", ["7.3.109", "6.1.78"])},
        "dvitiya":    {"eka": ("हरिम्", ["6.1.107"]), "dvi": ("हरी", ["6.1.102"]), "bahu": ("हरीन्", ["6.1.103", "8.4.1"])},
        "trtiya":     {"eka": ("हरिणा", ["7.3.111", "8.4.2"]), "dvi": ("हरिभ्याम्", ["4.1.2"]), "bahu": ("हरिभिः", ["4.1.2", "8.2.66", "8.3.15"])},
        "caturthi":   {"eka": ("हरये", ["7.3.111", "6.1.78"]), "dvi": ("हरिभ्याम्", ["4.1.2"]), "bahu": ("हरिभ्यः", ["4.1.2", "8.2.66", "8.3.15"])},
        "pancami":    {"eka": ("हरेः", ["7.3.111", "6.1.110"]), "dvi": ("हरिभ्याम्", ["4.1.2"]), "bahu": ("हरिभ्यः", ["4.1.2", "8.2.66", "8.3.15"])},
        "sasthi":     {"eka": ("हरेः", ["7.3.111", "6.1.110"]), "dvi": ("हर्योः", ["6.1.77"]), "bahu": ("हरीणाम्", ["7.1.54", "6.4.3", "8.4.2"])},
        "saptami":    {"eka": ("हरौ", ["7.3.119"]), "dvi": ("हर्योः", ["6.1.77"]), "bahu": ("हरिषु", ["4.1.2", "8.3.59"])},
        "sambodhana": {"eka": ("हरे", ["7.3.108", "6.1.69"]), "dvi": ("हरी", ["6.1.102"]), "bahu": ("हरयः", ["7.3.109", "6.1.78"])}
    },
    "u_masc": {
        "prathama":   {"eka": ("गुरुः", ["4.1.2", "8.2.66", "8.3.15"]), "dvi": ("गुरू", ["6.1.102"]), "bahu": ("गुरवः", ["7.3.109", "6.1.78"])},
        "dvitiya":    {"eka": ("गुरुम्", ["6.1.107"]), "dvi": ("गुरू", ["6.1.102"]), "bahu": ("गुरून्", ["6.1.103", "8.4.1"])},
        "trtiya":     {"eka": ("गुरुणा", ["7.3.111", "8.4.2"]), "dvi": ("गुरुभ्याम्", ["4.1.2"]), "bahu": ("गुरुभिः", ["4.1.2", "8.2.66", "8.3.15"])},
        "caturthi":   {"eka": ("गुरवे", ["7.3.111", "6.1.78"]), "dvi": ("गुरुभ्याम्", ["4.1.2"]), "bahu": ("गुरुभ्यः", ["4.1.2", "8.2.66", "8.3.15"])},
        "pancami":    {"eka": ("गुरोः", ["7.3.111", "6.1.110"]), "dvi": ("गुरुभ्याम्", ["4.1.2"]), "bahu": ("गुरुभ्यः", ["4.1.2", "8.2.66", "8.3.15"])},
        "sasthi":     {"eka": ("गुरोः", ["7.3.111", "6.1.110"]), "dvi": ("गुर्वोः", ["6.1.77"]), "bahu": ("गुरुणाम्", ["7.1.54", "6.4.3", "8.4.2"])},
        "saptami":    {"eka": ("गुरौ", ["7.3.119"]), "dvi": ("गुर्वोः", ["6.1.77"]), "bahu": ("गुरुषु", ["4.1.2", "8.3.59"])},
        "sambodhana": {"eka": ("गुरो", ["7.3.108", "6.1.69"]), "dvi": ("गुरू", ["6.1.102"]), "bahu": ("गुरवः", ["7.3.109", "6.1.78"])}
    }
}


def detect_stem_class(stem: str) -> str:
    """Infers the Paninian prātipadika stem class from phonological ending."""
    norm = unicodedata.normalize("NFC", stem.strip())
    if norm.endswith("ा"):
        return "aa_fem"
    elif norm.endswith("ि"):
        return "i_masc"
    elif norm.endswith("ु"):
        return "u_masc"
    else:
        return "a_masc"


def inflect_stem(stem: str, case_in: str, number_in: str, stem_class_in: Optional[str] = None) -> Dict[str, Any]:
    """
    Computes deterministic Subanta inflection and generates step-by-step Paninian trace.
    """
    stem = unicodedata.normalize("NFC", stem.strip())
    case = CASE_ALIASES.get(case_in.lower())
    number = NUMBER_ALIASES.get(number_in.lower())

    if not case:
        raise ValueError(f"Invalid case '{case_in}'. Must be 1-8 or prathama..sambodhana.")
    if not number:
        raise ValueError(f"Invalid number '{number_in}'. Must be 1-3 or eka/dvi/bahu.")

    stem_class = stem_class_in or detect_stem_class(stem)
    canonical_affix = CANONICAL_SUP[case][number]
    affix_post_lopa = strip_it_marker(canonical_affix)

    # Base derivation step records
    trace = [
        {"step": "4.1.2 sup-pratyaya", "result": f"{stem} + {canonical_affix}"},
        {"step": "1.3.9 tasya lopaḥ", "result": f"{stem} + {affix_post_lopa}"}
    ]

    # Rama / a-masc family resolution
    if stem_class == "a_masc":
        # Strip trailing inherent short-a base representation
        base = stem
        suffix_pair = PARADIGMS["a_masc"][case][number]
        suffix = suffix_pair[0]
        sutras = suffix_pair[1]

        if case == "prathama" and number == "eka":
            form = base + "ः"
        elif case == "prathama" and number == "dvi":
            form = base + "ौ"
        elif case == "prathama" and number == "bahu":
            form = base + "ाः"
        elif case == "dvitiya" and number == "eka":
            form = base + "म्"
        elif case == "dvitiya" and number == "dvi":
            form = base + "ौ"
        elif case == "dvitiya" and number == "bahu":
            form = base + "ान्"
        elif case == "trtiya" and number == "eka":
            form = base + "ेण" if ("र" in base or "ष" in base) else base + "ेन"
        elif case == "trtiya" and number == "dvi":
            form = base + "ābhyām".replace("ābhyām", "ाभ्याम्")
        elif case == "trtiya" and number == "bahu":
            form = base + "ैः"
        elif case == "caturthi" and number == "eka":
            form = base + "ाय"
        elif case == "caturthi" and number == "dvi":
            form = base + "ाभ्याम्"
        elif case == "caturthi" and number == "bahu":
            form = base + "ेभ्यः"
        elif case == "pancami" and number == "eka":
            form = base + "ात्"
        elif case == "pancami" and number == "dvi":
            form = base + "ाभ्याम्"
        elif case == "pancami" and number == "bahu":
            form = base + "ेभ्यः"
        elif case == "sasthi" and number == "eka":
            form = base + "स्य"
        elif case == "sasthi" and number == "dvi":
            form = base + "योः"
        elif case == "sasthi" and number == "bahu":
            form = base + "ाणाम्" if ("र" in base or "ष" in base) else base + "ानाम्"
        elif case == "saptami" and number == "eka":
            form = base + "े"
        elif case == "saptami" and number == "dvi":
            form = base + "योः"
        elif case == "saptami" and number == "bahu":
            form = base + "ेषु"
        elif case == "sambodhana" and number == "eka":
            form = "हे " + base
        elif case == "sambodhana" and number == "dvi":
            form = "हे " + base + "ौ"
        elif case == "sambodhana" and number == "bahu":
            form = "हे " + base + "ाः"
        else:
            form = base + suffix

    # Direct canonical paradigm matching for aa_fem, i_masc, u_masc
    elif stem_class in PARADIGMS:
        paradigm_ref = PARADIGMS[stem_class][case][number]
        form = paradigm_ref[0]
        sutras = paradigm_ref[1]
        
        # Adjust base if a cognate stem is passed (e.g. लता instead of रमा)
        if stem_class == "aa_fem" and stem != "रमा":
            root = stem[:-1] # strip 'ा'
            form = form.replace("रम्", root).replace("रमा", root + "ा")
        elif stem_class == "i_masc" and stem != "हरि":
            root = stem[:-1] # strip 'ि'
            form = form.replace("हर्", root).replace("हरि", root + "ि").replace("हरी", root + "ी")
        elif stem_class == "u_masc" and stem != "गुरु":
            root = stem[:-1] # strip 'ु'
            form = form.replace("गुर्व्", root + "व्").replace("गुर", root).replace("गुरु", root + "ु").replace("गुरू", root + "ू")
    else:
        raise ValueError(f"Unsupported stem_class '{stem_class}'")

    trace.append({"step": f"Aṣṭādhyāyī {sutras[-1]}", "result": form})

    return {
        "stem": stem,
        "stem_class": stem_class,
        "case": case,
        "number": number,
        "form": form,
        "canonical_sup": canonical_affix,
        "sutras": sutras,
        "trace": trace
    }