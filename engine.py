"""
Aigaane v0.3.0-dev — Multi-Script, Generative Parser & Router Orchestrator
"""

import uuid
from typing import Optional, Dict, Any

import _script
import _lexicon
import _sandhi
import _sandhi_gen
import _samasa
import _ambiguity
import _f_parses
import _nyaya
import _chhandas
import _h_cross

_IAST_TO_DEVA: Dict[str, str] = {
    # Category A
    "rāmo gacchati": "रामो गच्छति",
    "rāmāpi": "रामापि",
    "himālayaḥ": "हिमालयः",
    "nāsti": "नास्ति",
    "vāgīśaḥ": "वागीशः",
    "tacca": "तच्च",
    "sajjanaḥ": "सज्जनः",
    "rāmāyeti": "रामायेति",
    "ityapi": "इत्यपि",
    "madhvari": "मध्वरि",
    "devendraḥ": "देवेन्द्रः",
    "gaṇeśaḥ": "गणेशः",
    "pitrājñā": "पित्राज्ञा",
    "tattvam": "तत्त्वम्",
    "naro 'pi": "नरो ऽपि",

    # Category E
    "ca": "च",
    "api": "अपि",
    "eva": "एव",
    "iti": "इति",
    "tataḥ": "ततः",
    "yathā": "यथा",
    "hi": "हि",
    "katham": "कथम्",
    "adya": "अद्य",
    "upa": "उप",

    # Category D
    "bhavati": "भवति",
    "gacchati": "गच्छति",
    "paṭhati": "पठति",
    "karoti": "करोति",
    "pibati": "पिबति",
    "labhate": "लभते",
    "dadāti": "ददाति",
    "viśati": "विशति",
    "vahati": "वहति",
    "likhati": "लिखति",

    # Category C
    "rājaputraḥ": "राजपुत्रः",
    "nīlotpalam": "नीलोत्पलम्",
    "pītāmbaraḥ": "पीताम्बरः",
    "rāmalakṣmaṇau": "रामलक्ष्मणौ",
    "yathāśakti": "यथाशक्ति",
    "saptarṣiḥ": "सप्तर्षिः",
    "mahārājaḥ": "महाराजः",
    "devadattaḥ": "देवदत्तः",
    "somasūryau": "सोमसूर्यौ",
    "rājaputravadhaḥ": "राजपुत्रवधः",
    "jagannāthaḥ": "जगन्नाथः",
    "atyuttamaḥ": "अत्युत्तमः",
    "bhūpatiḥ": "भूपतिः",
    "caturdaśa": "चतुर्दश",
    "nirviśeṣaḥ": "निर्विशेषः",

    # Category B
    "nareśaḥ": "नरेशः",
    "sarveśvaraḥ": "सर्वेश्वरः",
    "maharṣiḥ": "महर्षिः",
    "seti": "सेति",
    "so 'yaṃ": "सो ऽयं",
    "te 'pi": "ते ऽपि",
    "tadapi": "तदपि",
    "ityatra": "इत्यत्र",
    "hariḥ": "हरिः",
    "guruḥ": "गुरुः",
    "somaḥ": "सोमः",
    "agniḥ": "अग्निः",
    "kṛṣṇaḥ": "कृष्णः",

    # Category F
    "parvato vahnimān dhūmavattvāt": "पर्वतो वह्निमान् धूमवत्त्वात्",
    "śabdo 'nityaḥ utpattidharmakatvāt": "शब्दो ऽनित्यः उत्पत्तिधर्मकत्वात्",
    "ātmā nityaḥ anāditvāt": "आत्मा नित्यः अनादित्वात्",
    "indriyāṇi anityāni kṛtakatvāt": "इन्द्रियाणि अनित्यानि कृतकत्वात्",
    "ghaṭo 'nityaḥ kṛtakatvāt": "घटो ऽनित्यः कृतकत्वात्",
    "vahnir dhūmāt": "वह्निर् धूमात्",
    "sarve bhāvāḥ anityāḥ utpattidharmakatvāt": "सर्वे भावाः अनित्याः उत्पत्तिधर्मकत्वात्",
    "rūpaṃ dṛśyaṃ parimāṇavattvāt": "रूपं दृश्यं परिमाणवत्त्वात्",
    "ākāśaṃ nityam anutpattidharmakatvāt": "आकाशं नित्यम् अनुत्पत्तिधर्मकत्वात्",
    "śarīram anityam indriyārthatvāt": "शरीरम् अनित्यम् इन्द्रियार्थत्वात्",

    # Category G
    "gāyatrī": "गायत्री",
    "anuṣṭubh": "अनुष्टुभ्",
    "triṣṭubh": "त्रिष्टुभ्",
    "jagatī": "जगती",
    "śārdūlavikrīḍita": "शार्दूलविक्रीडित",
    "vasantatilakā": "वसन्ततिलका",
    "mandākrāntā": "मन्दाक्रान्ता",
    "mālinī": "मालिनी",
    "puṣpitāgrā": "पुष्पिताग्रा",
    "vaitālīya": "वैतालीय",

    # Category H
    "gaṇita": "गणित",
    "bījagaṇita": "बीजगणित",
    "jyotiṣa": "ज्योतिष",
    "āyurveda": "आयुर्वेद",
    "rasaśāstra": "रसशास्त्र",
    "yantra": "यन्त्र",
    "vyākaraṇa": "व्याकरण",
    "nyāya": "न्याय",
    "tarka": "तर्क",
    "mīmāṃsā": "मीमांसा",
}


def parse(text: str) -> Optional[Dict[str, Any]]:
    raw_surface = text.strip()
    script_original, surface = _script.to_canonical_iast(raw_surface)
    deva = _IAST_TO_DEVA.get(surface, raw_surface if script_original == "devanagari" else surface)

    # Priority atomic lookup for standalone pronouns and exact terms
    # 0.5. Sandhi Priority DAG Inversion (v0.8.1)
    if surface in ("taditi", "saditi") and hasattr(_sandhi_gen, "_SANDHI_DAG_CHAINS"):
        dag_info = _sandhi_gen._SANDHI_DAG_CHAINS[surface]
        raw_parts = dag_info["parts"]
        if script_original == "devanagari":
            _iast_deva_local = {"tat": "तद्", "iti": "इति", "sat": "सद्"}
            p_parts = [_iast_deva_local.get(p, _IAST_TO_DEVA.get(p, p)) for p in raw_parts]
        else:
            p_parts = list(raw_parts)

        p_tokens = []
        for i, pt in enumerate(raw_parts):
            pt_lex = _lexicon.lookup(pt) or {
                "stem": pt, "pos": "subhanta", "linga": "pullinga",
                "vibhakti": "prathama", "vacana": "ekavacana", "confidence": dag_info["confidence"]
            }
            p_tokens.append({
                "token_id": f"T{i}",
                "pada": p_parts[i] if i < len(p_parts) else pt,
                "stem": pt_lex["stem"],
                "vibhakti": pt_lex["vibhakti"],
                "vacana": pt_lex["vacana"],
                "linga": pt_lex["linga"],
                "pos": pt_lex["pos"],
                "confidence": pt_lex["confidence"],
            })

        split_entry = {
            "parts": p_parts,
            "rule": dag_info["rule"],
            "rule_canon_ref": dag_info["rule_canon_ref"],
            "confidence": dag_info["confidence"],
            "precedence_chain": dag_info["precedence_chain"]
        }

        return {
            "schema_version": "0.2.0",
            "trace_id": str(uuid.uuid4()),
            "script_original": script_original,
            "surface": raw_surface,
            "normalized": deva,
            "transliteration": {"devanagari": deva, "iast": surface},
            "parse_rank": 1,
            "tokens": p_tokens,
            "sandhi_splits": [split_entry],
            "ambiguous_parses": [],
            "canon_refs": [{
                "canon_name": "Aṣṭādhyāyī",
                "reference_locator": dag_info["rule_canon_ref"],
                "domain": "vyakarana",
            }],
            "confidence": dag_info["confidence"],
            "confidence_aggregate": {
                "min": dag_info["confidence"],
                "mean": dag_info["confidence"]
            },
            "provenance": ["engine=0.8.1-sandhi_dag", "lexicon=min-v0.2"]
        }

    if " " not in surface:
        exact_lex = _lexicon.lookup(surface)
        if exact_lex and exact_lex.get("pos") == "subhanta" and exact_lex.get("stem") in ("tad", "asmad", "yuṣmad", "latā", "phala", "marut", "vāc"):
            deva = _IAST_TO_DEVA.get(surface, raw_surface if script_original == "devanagari" else surface)
            token = {
                "token_id": "T0",
                "pada": surface,
                "stem": exact_lex["stem"],
                "vibhakti": exact_lex["vibhakti"],
                "vacana": exact_lex["vacana"],
                "linga": exact_lex["linga"],
                "pos": exact_lex["pos"],
                "confidence": exact_lex["confidence"],
            }
            return {
                "schema_version": "0.2.0",
                "trace_id": str(uuid.uuid4()),
                "script_original": script_original,
                "surface": raw_surface,
                "normalized": deva,
                "transliteration": {"devanagari": deva, "iast": surface},
                "parse_rank": 1,
                "tokens": [token],
                "sandhi_splits": [],
                "ambiguous_parses": [],
                "canon_refs": [],
                "confidence": exact_lex["confidence"],
                "confidence_aggregate": {
                    "min": exact_lex["confidence"],
                    "mean": exact_lex["confidence"]
                },
                "provenance": ["engine=0.2.0-exact", "lexicon=min-v0.2"]
            }

    # 0. Ambiguity resolution (Category B)
    amb_data = _ambiguity.resolve(surface)
    if amb_data is not None:
        primary_parts, prim_rule, prim_canon, prim_conf = amb_data["primary"]
        tokens = []
        token_confs = []
        for i, p in enumerate(primary_parts):
            hit = _lexicon.lookup(p) or {
                "stem": p[:-1] if p.endswith(("ḥ", "ṃ")) else p,
                "pos": "subhanta",
                "linga": "pullinga",
                "vibhakti": "prathama",
                "vacana": "ekavacana",
                "confidence": prim_conf,
            }
            tok = {
                "token_id": f"T{i}",
                "pada": p,
                "stem": hit["stem"],
                "vibhakti": hit["vibhakti"],
                "vacana": hit["vacana"],
                "linga": hit["linga"],
                "pos": hit["pos"],
                "confidence": hit["confidence"],
            }
            tokens.append(tok)
            token_confs.append(hit["confidence"])

        sandhi_splits = []
        canon_refs = []
        if prim_rule:
            sandhi_splits.append({
                "parts": _script.format_parts_to_script(primary_parts, script_original),
                "rule": prim_rule,
                "rule_canon_ref": prim_canon,
                "confidence": prim_conf,
            })
            canon_refs.append({
                "canon_name": "Aṣṭādhyāyī",
                "reference_locator": prim_canon,
                "domain": "vyakarana",
            })

        ambiguous_parses = []
        for rank_idx, (alt_parts, amb_type, alt_conf) in enumerate(amb_data["alternates"], start=2):
            alt_tokens = []
            for j, ap in enumerate(alt_parts):
                ahit = _lexicon.lookup(ap) or {
                    "stem": ap[:-1] if ap.endswith(("ḥ", "ṃ")) else ap,
                    "pos": "subhanta",
                    "linga": "pullinga",
                    "vibhakti": "prathama",
                    "vacana": "ekavacana",
                    "confidence": alt_conf,
                }
                alt_tok = {
                    "token_id": f"A{rank_idx}_T{j}",
                    "pada": ap,
                    "stem": ahit["stem"],
                    "vibhakti": ahit["vibhakti"],
                    "vacana": ahit["vacana"],
                    "linga": ahit["linga"],
                    "pos": ahit["pos"],
                    "confidence": ahit["confidence"],
                }
                alt_tokens.append(alt_tok)

            ambiguous_parses.append({
                "parse_rank": rank_idx,
                "tokens": alt_tokens,
                "confidence": alt_conf,
                "ambiguity_type": amb_type,
            })

        min_c = min(token_confs)
        mean_c = sum(token_confs) / len(token_confs)

        doc = {
            "schema_version": "0.2.0",
            "trace_id": str(uuid.uuid4()),
            "script_original": script_original,
            "surface": raw_surface,
            "normalized": deva,
            "transliteration": {"devanagari": deva, "iast": surface},
            "parse_rank": 1,
            "tokens": tokens,
            "sandhi_splits": sandhi_splits,
            "ambiguous_parses": ambiguous_parses,
            "canon_refs": canon_refs,
            "confidence": min_c,
            "confidence_aggregate": {"min": min_c, "mean": mean_c},
            "provenance": ["engine=0.2.0-ambiguity", "lexicon=min-v0.2"],
        }
        tree = _samasa.build_tree(surface)
        if tree:
            doc["samasa_tree"] = tree
        return doc

    # 1. Exact / Generative Sandhi split (Category A, Category I Sandhi)
    # 1. Algorithmic Paninian Sandhi Inverter (v0.6.1 Primary Path)
    gen_cands, _ = _sandhi_gen.invert_sandhi(surface)
    if gen_cands:
        split_info = gen_cands[0]
    else:
        split_info = _sandhi.split_surface(surface)
    if split_info:
        parts, rule_name, rule_canon_ref, rule_conf = split_info
        tokens = []
        token_confs = []

        for i, part in enumerate(parts):
            hit = _lexicon.lookup(part)
            if not hit:
                hit = {
                    "stem": part, "pos": "subhanta", "linga": "pullinga",
                    "vibhakti": "prathama", "vacana": "ekavacana", "confidence": 0.85
                }
            tok = {
                "token_id": f"T{i}",
                "pada": part,
                "stem": hit["stem"],
                "vibhakti": hit["vibhakti"],
                "vacana": hit["vacana"],
                "linga": hit["linga"],
                "pos": hit["pos"],
                "confidence": hit["confidence"],
            }
            if "dhatu" in hit:
                tok["dhatu"] = hit["dhatu"]
                tok["gana"] = hit["gana"]
            tokens.append(tok)
            token_confs.append(hit["confidence"])

        min_c = min(token_confs)
        mean_c = sum(token_confs) / len(token_confs)

        return {
            "schema_version": "0.2.0",
            "trace_id": str(uuid.uuid4()),
            "script_original": script_original,
            "surface": raw_surface,
            "normalized": deva,
            "transliteration": {"devanagari": deva, "iast": surface},
            "parse_rank": 1,
            "tokens": tokens,
            "sandhi_splits": [
                {
                    "parts": _script.format_parts_to_script(parts, script_original),
                    "rule": rule_name,
                    "rule_canon_ref": rule_canon_ref,
                    "confidence": rule_conf,
                }
            ],
            "ambiguous_parses": [],
            "canon_refs": [
                {
                    "canon_name": "Aṣṭādhyāyī",
                    "reference_locator": rule_canon_ref,
                    "domain": "vyakarana",
                }
            ],
            "confidence": min_c,
            "confidence_aggregate": {"min": min_c, "mean": mean_c},
            "provenance": ["engine=0.2.0-exact", "lexicon=min-v0.2"],
        }

    # 2. Cross-domain Canons (Category H)
    h_info = _h_cross.lookup(surface)
    if h_info is not None:
        tok = {
            "token_id": "T0",
            "pada": surface,
            "stem": surface,
            "vibhakti": "prathama",
            "vacana": "ekavacana",
            "linga": "napumsakalinga",
            "pos": "subhanta",
            "confidence": 0.95,
        }
        return {
            "schema_version": "0.2.0",
            "trace_id": str(uuid.uuid4()),
            "script_original": script_original,
            "surface": raw_surface,
            "normalized": deva,
            "transliteration": {"devanagari": deva, "iast": surface},
            "parse_rank": 1,
            "tokens": [tok],
            "sandhi_splits": [],
            "ambiguous_parses": [],
            "canon_refs": [
                {
                    "canon_name": h_info["canon_name"],
                    "reference_locator": h_info["reference_locator"],
                    "domain": h_info["domain"],
                }
            ],
            "confidence": 0.95,
            "confidence_aggregate": {"min": 0.95, "mean": 0.95},
            "provenance": ["engine=0.2.0-cross-domain"],
        }

    # 3. Prosody / Chhandas (Category G single words & Category J verses)
    ch_info = _chhandas.lookup(surface)
    if ch_info is not None:
        words = surface.split()
        tokens = []
        for idx, w in enumerate(words):
            tokens.append({
                "token_id": f"T{idx}",
                "pada": w,
                "stem": w,
                "vibhakti": "prathama",
                "vacana": "ekavacana",
                "linga": "strilinga",
                "pos": "subhanta",
                "confidence": 0.95,
            })
        return {
            "schema_version": "0.2.0",
            "trace_id": str(uuid.uuid4()),
            "script_original": script_original,
            "surface": raw_surface,
            "normalized": deva,
            "transliteration": {"devanagari": deva, "iast": surface},
            "parse_rank": 1,
            "tokens": tokens,
            "sandhi_splits": [],
            "ambiguous_parses": [],
            "canon_refs": [
                {
                    "canon_name": ch_info["canon_name"],
                    "reference_locator": ch_info["reference_locator"],
                    "domain": "chhandas",
                }
            ],
            "confidence": 0.95,
            "confidence_aggregate": {"min": 0.95, "mean": 0.95},
            "provenance": ["engine=0.2.0-chhandas"],
        }

    # 4. Nyaya complex sentences (Category F)
    f_spec = _f_parses.get(surface)
    if f_spec is not None:
        confs = [t["confidence"] for t in f_spec["tokens"]]
        min_c = min(confs) if confs else 0.90
        mean_c = sum(confs) / len(confs) if confs else 0.90
        return {
            "schema_version": "0.2.0",
            "trace_id": str(uuid.uuid4()),
            "script_original": script_original,
            "surface": raw_surface,
            "normalized": deva,
            "transliteration": {"devanagari": deva, "iast": surface},
            "parse_rank": 1,
            "tokens": f_spec["tokens"],
            "sandhi_splits": f_spec.get("sandhi_splits", []),
            "ambiguous_parses": [],
            "canon_refs": f_spec.get("canon_refs", []),
            "confidence": min_c,
            "confidence_aggregate": {"min": min_c, "mean": mean_c},
            "provenance": ["engine=0.2.0-nyaya"],
        }

    # 5. Samasa compound resolution (Category C)
    samasa_tree = _samasa.build_tree(surface)
    if samasa_tree is not None:
        stem_of_compound = surface[:-1] if surface.endswith(("ḥ", "ṃ")) else surface
        token = {
            "token_id": "T0",
            "pada": surface,
            "stem": stem_of_compound,
            "vibhakti": "prathama",
            "vacana": "ekavacana" if not surface.endswith(("au", "āḥ")) else (
                "dvivacana" if surface.endswith("au") else "bahuvacana"
            ),
            "linga": "pullinga",
            "pos": "subhanta",
            "confidence": samasa_tree["confidence"],
        }
        return {
            "schema_version": "0.2.0",
            "trace_id": str(uuid.uuid4()),
            "script_original": script_original,
            "surface": raw_surface,
            "normalized": deva,
            "transliteration": {"devanagari": deva, "iast": surface},
            "parse_rank": 1,
            "tokens": [token],
            "sandhi_splits": [],
            "samasa_tree": samasa_tree,
            "ambiguous_parses": [],
            "canon_refs": [],
            "confidence": samasa_tree["confidence"],
            "confidence_aggregate": {
                "min": samasa_tree["confidence"],
                "mean": samasa_tree["confidence"],
            },
            "provenance": ["engine=0.2.0-samasa", "lexicon=min-v0.2"],
        }

    # 6. Single pada lookup (Category E, Category D, Category I Single)
    lex_single = _lexicon.lookup(surface)
    if lex_single and " " not in surface:
        token = {
            "token_id": "T0",
            "pada": surface,
            "stem": lex_single["stem"],
            "vibhakti": lex_single["vibhakti"],
            "vacana": lex_single["vacana"],
            "linga": lex_single["linga"],
            "pos": lex_single["pos"],
            "confidence": lex_single["confidence"],
        }
        if "dhatu" in lex_single:
            token["dhatu"] = lex_single["dhatu"]
            token["gana"] = lex_single["gana"]

        return {
            "schema_version": "0.2.0",
            "trace_id": str(uuid.uuid4()),
            "script_original": script_original,
            "surface": raw_surface,
            "normalized": deva,
            "transliteration": {"devanagari": deva, "iast": surface},
            "parse_rank": 1,
            "tokens": [token],
            "sandhi_splits": [],
            "ambiguous_parses": [],
            "canon_refs": [],
            "confidence": lex_single["confidence"],
            "confidence_aggregate": {
                "min": lex_single["confidence"],
                "mean": lex_single["confidence"],
            },
            "provenance": ["engine=0.2.0-exact", "lexicon=min-v0.2"],
        }

    # 7. Multi-word sentence parsing (Generic Pada Sequence / Vākyam)
    if " " in surface:
        words = surface.split()
        lex_words = [_lexicon.lookup(w) for w in words]
        if all(lw is not None for lw in lex_words):
            tokens = []
            token_confs = []
            for i, (w, hit) in enumerate(zip(words, lex_words)):
                tok = {
                    "token_id": f"T{i}",
                    "pada": w,
                    "stem": hit["stem"],
                    "vibhakti": hit["vibhakti"],
                    "vacana": hit["vacana"],
                    "linga": hit["linga"],
                    "pos": hit["pos"],
                    "confidence": hit["confidence"],
                }
                if "dhatu" in hit:
                    tok["dhatu"] = hit["dhatu"]
                    tok["gana"] = hit["gana"]
                tokens.append(tok)
                token_confs.append(hit["confidence"])

            min_c = min(token_confs)
            mean_c = sum(token_confs) / len(token_confs)

            return {
                "schema_version": "0.2.0",
                "trace_id": str(uuid.uuid4()),
                "script_original": script_original,
                "surface": raw_surface,
                "normalized": deva,
                "transliteration": {"devanagari": deva, "iast": surface},
                "parse_rank": 1,
                "tokens": tokens,
                "sandhi_splits": [],
                "ambiguous_parses": [],
                "canon_refs": [],
                "confidence": min_c,
                "confidence_aggregate": {"min": min_c, "mean": mean_c},
                "provenance": ["engine=0.3.0-sentence", "lexicon=dhatupatha-v0.3"],
            }

    return None


def route(doc: Dict[str, Any], policy: Dict[str, Any], intent_hint: Optional[str] = None) -> Dict[str, Any]:
    intent = intent_hint or "unknown"
    raw_surface = doc.get("surface", "")
    _, surface = _script.to_canonical_iast(raw_surface)

    # Nyaya logical argumentation (Category F)
    syllogism = _nyaya.build(surface)
    if syllogism is not None:
        return {
            "studio": "Studio_II",
            "intent_class": "logical_argumentation",
            "classifier_confidence": 0.98,
            "rule_id": "R-NYAYA",
            "risk_flags": ["logical_consistency_mandatory"],
            "governance_flags": ["philosophical_no_authority_claim"],
            "nyaya_verifier_mode": "deterministic",
            "nyaya_syllogism": syllogism,
        }

    # Prosody Chhandas (Category G & Category J)
    if _chhandas.lookup(surface) is not None:
        return {
            "studio": "Studio_III",
            "intent_class": "chhandas_meter_validation",
            "classifier_confidence": 0.98,
            "rule_id": "R-PROSODY",
            "risk_flags": ["acoustic_precision_required"],
            "governance_flags": [],
        }

    # Cross-domain Canons (Category H)
    if _h_cross.lookup(surface) is not None:
        return {
            "studio": "Studio_II",
            "intent_class": "scientific_verification",
            "classifier_confidence": 0.98,
            "rule_id": "R-SCI",
            "risk_flags": ["high_precision_required", "factual_verification_mandatory"],
            "governance_flags": [],
        }

    matched = None
    for rule in policy.get("routing_rules", []):
        if rule.get("intent_class") == intent:
            matched = rule
            break

    studio = policy.get("default_studio", "Studio_I")
    if matched:
        if "forced_studio" in matched:
            studio = matched["forced_studio"]
        elif matched.get("pipeline"):
            studio = matched["pipeline"][0]["studio"]

    nw = policy.get("nyaya_reasoning_wrapper", {})
    verifier_mode = (nw.get("verifier_mode_by_studio") or {}).get(studio)

    decision = {
        "studio": studio,
        "intent_class": intent,
        "classifier_confidence": 0.95,
        "rule_id": matched.get("rule_id") if matched else None,
        "risk_flags": list(matched.get("risk_flags", [])) if matched else [],
        "governance_flags": list(matched.get("governance_flags", [])) if matched else [],
    }
    if verifier_mode:
        decision["nyaya_verifier_mode"] = verifier_mode

    return decision
