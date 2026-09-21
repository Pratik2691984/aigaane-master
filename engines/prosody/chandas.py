"""
engine/prosody/chandas.py
Piṅgala Chhandaḥśāstra Prosody Scansion Engine

Architecture:
- Layer A: Akṣara Tokenizer (nucleus-driven segmentation, cross-boundary saṁyoga onset detection)
- Layer B: Mātrā Classifier (Laghu 1 / Guru 2 with dīrgha, anusvāra/visarga, and saṁyoga-para rules)
- Layer C: Meter Validator & Diagnostic Generator (Anuṣṭubh Pathyā & Vipulā classification)
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import unicodedata
import re

VOWELS_SHORT = set(['\u0905', '\u0907', '\u0909', '\u090b', '\u090c']) # अ, इ, उ, ऋ, ऌ
VOWEL_SIGNS_SHORT = set(['\u093f', '\u0941', '\u0943', '\u0962']) # ि, ु, ृ, ॢ

VOWELS_LONG = set(['\u0906', '\u0908', '\u090a', '\u0960', '\u090f', '\u0910', '\u0913', '\u0914']) # आ, ई, ऊ, ॠ, ए, ऐ, ओ, औ
VOWEL_SIGNS_LONG = set(['\u093e', '\u0940', '\u0942', '\u0944', '\u0947', '\u0948', '\u094b', '\u094c']) # ा, ी, ू, ॄ, े, ै, ो, ौ

VIRAMA = '\u094d'
ANUSVARA = '\u0902'
VISARGA = '\u0903'
CONSONANTS = set(chr(c) for c in range(0x0915, 0x093A)) | set(['\u0929', '\u0931', '\u0934', '\u0958', '\u0959', '\u095A', '\u095B', '\u095C', '\u095D', '\u095E', '\u095F'])

@dataclass
class SyllableToken:
    text: str
    vowel_type: str
    has_coda_modifier: bool
    starts_with_cluster: bool

# Layer A: Akṣara Tokenizer
def tokenize_aksaras(text: str) -> List[SyllableToken]:
    norm = unicodedata.normalize('NFC', text.strip())
    tokens: List[SyllableToken] = []
    i = 0
    n = len(norm)

    while i < n:
        char = norm[i]
        if char.isspace() or char in '।,॥!?.0123456789':
            i += 1
            continue

        start = i

        # Independent Vowel
        if char in VOWELS_SHORT or char in VOWELS_LONG:
            v_type = 'short' if char in VOWELS_SHORT else 'long'
            i += 1
            has_mod = False
            if i < n and norm[i] in (ANUSVARA, VISARGA):
                has_mod = True
                i += 1
            tokens.append(SyllableToken(norm[start:i], v_type, has_mod, starts_with_cluster=False))
            continue

        # Consonant Cluster
        if char in CONSONANTS:
            cluster_len = 0
            while i < n and norm[i] in CONSONANTS:
                if i + 1 < n and norm[i+1] == VIRAMA:
                    cluster_len += 1
                    i += 2
                else:
                    break

            if i < n and norm[i] in CONSONANTS:
                i += 1

            v_type = 'inherent_short'
            if i < n:
                if norm[i] in VOWEL_SIGNS_SHORT:
                    v_type = 'short'
                    i += 1
                elif norm[i] in VOWEL_SIGNS_LONG:
                    v_type = 'long'
                    i += 1

            has_mod = False
            if i < n and norm[i] in (ANUSVARA, VISARGA):
                has_mod = True
                i += 1

            tokens.append(SyllableToken(norm[start:i], v_type, has_mod, starts_with_cluster=(cluster_len > 0)))
            continue

        i += 1

    return tokens

# Layer B: Mātrā Classifier
def classify_syllables(tokens: List[SyllableToken], padanta_guru: bool = True) -> List[Dict[str, Any]]:
    classified = []
    total = len(tokens)

    for idx, tok in enumerate(tokens):
        is_last = (idx == total - 1)
        next_tok = tokens[idx + 1] if not is_last else None

        has_samyoga = bool(next_tok and next_tok.starts_with_cluster)

        if is_last and padanta_guru:
            classified.append({
                'index': idx + 1,
                'text': tok.text,
                'weight': 'G',
                'matra': 2,
                'rule': 'pādānte-vā'
            })
        elif tok.vowel_type == 'long':
            classified.append({
                'index': idx + 1,
                'text': tok.text,
                'weight': 'G',
                'matra': 2,
                'rule': 'dīrgha-svara'
            })
        elif tok.has_coda_modifier:
            classified.append({
                'index': idx + 1,
                'text': tok.text,
                'weight': 'G',
                'matra': 2,
                'rule': 'anusvāra-visarga'
            })
        elif has_samyoga:
            classified.append({
                'index': idx + 1,
                'text': tok.text,
                'weight': 'G',
                'matra': 2,
                'rule': 'saṁyoga-para'
            })
        else:
            classified.append({
                'index': idx + 1,
                'text': tok.text,
                'weight': 'L',
                'matra': 1,
                'rule': 'hrasva'
            })

    return classified

# Layer C: Meter Validation & Diagnostics
def scan_pada(text: str, pada_num: int = 1, padanta_guru: bool = True) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    tokens = tokenize_aksaras(text)
    syls = classify_syllables(tokens, padanta_guru=padanta_guru)
    weights = [s['weight'] for s in syls]
    weight_pattern = ''.join(weights)
    count = len(syls)

    diagnostics = []
    trace = []
    is_valid = True

    # 1. Check 8 Syllables
    if count != 8:
        is_valid = False
        diagnostics.append({
            'pada': pada_num,
            'syllable': count,
            'found': 'L' if count < 8 else 'G',
            'expected': 'G',
            'rule': 'anustubh-8-aksharas',
            'sutra': 'Piṅgala Chhandaḥśāstra',
            'message': f'Pāda {pada_num} has {count} syllables (strictly requires 8).'
        })

    # 2. Check 5th Syllable -> Laghu (L)
    if count >= 5:
        w5 = weights[4]
        ok5 = (w5 == 'L')
        trace.append({'rule': 'pathyā-5-L', 'pada': pada_num, 'syllable': 5, 'found': w5, 'ok': ok5})
        if not ok5:
            is_valid = False
            diagnostics.append({
                'pada': pada_num,
                'syllable': 5,
                'found': w5,
                'expected': 'L',
                'rule': 'pathyā-5-L',
                'sutra': 'Piṅgala 5th Laghu Rule',
                'message': f'Pāda {pada_num} syllable 5 ({syls[4]["text"]}) is {w5}; must be Laghu (L).'
            })

    # 3. Check 6th Syllable -> Guru (G)
    if count >= 6:
        w6 = weights[5]
        ok6 = (w6 == 'G')
        trace.append({'rule': 'pathyā-6-G', 'pada': pada_num, 'syllable': 6, 'found': w6, 'ok': ok6})
        if not ok6:
            is_valid = False
            diagnostics.append({
                'pada': pada_num,
                'syllable': 6,
                'found': w6,
                'expected': 'G',
                'rule': 'pathyā-6-G',
                'sutra': 'Piṅgala 6th Guru Rule',
                'message': f'Pāda {pada_num} syllable 6 ({syls[5]["text"]}) is {w6}; must be Guru (G).'
            })

    # 4. Check 7th Syllable Alternation (Odd -> G, Even -> L)
    if count >= 7:
        w7 = weights[6]
        expected_7 = 'G' if (pada_num % 2 != 0) else 'L'
        ok7 = (w7 == expected_7)
        rule_name = 'pathyā-7-G' if (pada_num % 2 != 0) else 'pathyā-7-L'
        trace.append({'rule': rule_name, 'pada': pada_num, 'syllable': 7, 'found': w7, 'ok': ok7})
        if not ok7:
            is_valid = False
            diagnostics.append({
                'pada': pada_num,
                'syllable': 7,
                'found': w7,
                'expected': expected_7,
                'rule': rule_name,
                'sutra': 'Piṅgala 7th Alternation Rule',
                'message': f'Pāda {pada_num} syllable 7 ({syls[6]["text"]}) is {w7}; expected {expected_7} for Pathyā.'
            })

    pada_result = {
        'pada_number': pada_num,
        'text': text,
        'syllables': [s['text'] for s in syls],
        'weights': weights,
        'weight_pattern': weight_pattern,
        'total_syllables': count,
        'total_matras': sum(s['matra'] for s in syls),
        'valid': is_valid
    }

    return pada_result, diagnostics, trace

def scan_anustubh(sloka: str, padanta_guru: bool = True) -> Dict[str, Any]:
    split_pat = chr(13) + chr(10) + "/|।॥"
    lines = [ln.strip() for ln in re.split(f"[{split_pat}]+", sloka) if ln.strip()]

    padas = []
    for line in lines:
        toks = tokenize_aksaras(line)
        if len(toks) > 10:
            words = line.split()
            h1, h2 = [], []
            c = 0
            for w in words:
                w_c = len(tokenize_aksaras(w))
                if c + w_c <= 8 or not h1:
                    h1.append(w)
                    c += w_c
                else:
                    h2.append(w)
            padas.append(' '.join(h1))
            if h2:
                padas.append(' '.join(h2))
        else:
            padas.append(line)

    all_padas = []
    all_diagnostics = []
    all_traces = []
    all_valid = True

    for idx, p_text in enumerate(padas[:4], 1):
        res, diags, tr = scan_pada(p_text, idx, padanta_guru=padanta_guru)
        all_padas.append(res)
        all_diagnostics.extend(diags)
        all_traces.extend(tr)
        if not res['valid']:
            all_valid = False

    if len(all_padas) < 4:
        all_valid = False
        all_diagnostics.append({
            'pada': len(all_padas) + 1,
            'syllable': 0,
            'found': 'L',
            'expected': 'G',
            'rule': 'complete-catushpadi',
            'sutra': 'Anuṣṭubh 4-Pāda Requirement',
            'message': f'Verse has only {len(all_padas)} pādas; complete Anuṣṭubh requires 4.'
        })

    return {
        'valid': all_valid,
        'chandas': 'anuṣṭubh',
        'variant': 'pathyā' if all_valid else None,
        'padas': all_padas,
        'diagnostics': all_diagnostics,
        'trace': all_traces,
        'governance': {
            'engine': 'engine.prosody.chandas',
            'authority': 'Piṅgala Chhandaḥśāstra',
            'normalization': 'NFC'
        }
    }

scan_line = scan_pada
verify_anustubh = scan_anustubh


# Gaṇa Patterns
METER_SCHEMAS = {
    "indravajra": {
        "syllables": 11,
        "pattern": "GGLGGLLGLGG",
        "name": "इन्द्रवज्रा"
    },
    "upendravajra": {
        "syllables": 11,
        "pattern": "LGLGLLGLGG",
        "name": "उपेन्द्रवज्रा"
    },
    "shardulavikridita": {
        "syllables": 19,
        "pattern": "GGGLLLGLLGLLLLGGLLG",
        "name": "शार्दूलविक्रीडितम्"
    }
}

def scan_varnavrtta_pada(text: str, pada_num: int, target_meter: str, padanta_guru: bool = True):
    tokens = tokenize_aksaras(text)
    syls = classify_syllables(tokens, padanta_guru=padanta_guru)
    weights = "".join(s["weight"] for s in syls)
    count = len(syls)
    
    spec = METER_SCHEMAS.get(target_meter, {})
    diagnostics = []
    
    expected_len = spec.get("syllables", 11)
    expected_pattern = spec.get("pattern", "GGLGGLLGLGG")
    
    is_valid = True
    if count != expected_len:
        is_valid = False
        diagnostics.append({
            "pada": pada_num,
            "syllable": count,
            "found": str(count),
            "expected": str(expected_len),
            "rule": f"{target_meter}-syllables",
            "sutra": "Piṅgala Vṛttasaṅkhyā",
            "message": f"Pāda {pada_num} has {count} akṣaras, expected {expected_len}."
        })
    else:
        for idx, (f, e) in enumerate(zip(weights, expected_pattern)):
            if idx == expected_len - 1 and padanta_guru:
                continue
            if f != e:
                is_valid = False
                diagnostics.append({
                    "pada": pada_num,
                    "syllable": idx + 1,
                    "found": f,
                    "expected": e,
                    "rule": f"{target_meter}-weight-mismatch",
                    "sutra": "Piṅgala Gaṇabheda",
                    "message": f"Pāda {pada_num} syllable {idx+1} ({syls[idx]['text']}) is {f}; expected {e}."
                })

    res = {
        "pada_number": pada_num,
        "text": text,
        "syllables": [s["text"] for s in syls],
        "weights": [s["weight"] for s in syls],
        "weight_pattern": weights,
        "total_syllables": count,
        "total_matras": sum(s["matra"] for s in syls),
        "valid": is_valid
    }
    return res, diagnostics

def scan_upajati(sloka: str, padanta_guru: bool = True):
    split_pat = chr(13) + chr(10) + "/|।॥"
    lines = [ln.strip() for ln in re.split(f"[{split_pat}]+", sloka) if ln.strip()]
    
    padas = []
    diagnostics = []
    has_indra = False
    has_upendra = False
    all_valid = True
    
    if len(lines) != 4:
        all_valid = False
        diagnostics.append({
            "pada": len(lines),
            "syllable": 0,
            "found": str(len(lines)),
            "expected": "4",
            "rule": "verse-pada-count",
            "sutra": "Piṅgala Catuṣpadī",
            "message": f"Verse has {len(lines)} pādas, expected exactly 4."
        })

    for idx, line in enumerate(lines[:4], 1):
        res_i, diag_i = scan_varnavrtta_pada(line, idx, "indravajra", padanta_guru)
        res_u, diag_u = scan_varnavrtta_pada(line, idx, "upendravajra", padanta_guru)
        
        if res_i["valid"]:
            has_indra = True
            res_i["meter"] = "indravajra"
            padas.append(res_i)
        elif res_u["valid"]:
            has_upendra = True
            res_u["meter"] = "upendravajra"
            padas.append(res_u)
        else:
            all_valid = False
            # Choose whichever has fewer diagnostics
            chosen = res_i if len(diag_i) <= len(diag_u) else res_u
            chosen_diag = diag_i if len(diag_i) <= len(diag_u) else diag_u
            chosen["meter"] = "unknown"
            padas.append(chosen)
            diagnostics.extend(chosen_diag)
            
    is_upajati = all_valid and len(padas) == 4
    chandas_name = "upajāti" if (has_indra and has_upendra) else ("indravajrā" if has_indra else ("upendravajrā" if has_upendra else "upajāti"))
    variant_name = "miśra" if (has_indra and has_upendra) else ("śuddha" if (has_indra or has_upendra) else "avedyā")

    return {
        "valid": is_upajati,
        "chandas": chandas_name,
        "variant": variant_name,
        "padas": padas,
        "diagnostics": diagnostics,
        "governance": {
            "engine": "engine.prosody.chandas",
            "authority": "Piṅgala Chhandaḥśāstra"
        }
    }
