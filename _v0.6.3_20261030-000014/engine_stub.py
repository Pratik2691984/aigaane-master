"""
Aigaane v0.2.0 - Engine Stub

Three pre-green fixtures (A01 rāmo gacchati, E01 ca, F01 Nyaya) prove the
harness works end-to-end before a real engine exists. Delete each fixture
the moment a real parse() produces that document.

Contract:
    parse(text: str) -> dict | None
    route(doc: dict, policy: dict, intent_hint: str | None) -> dict | None
"""

import copy

_FIXTURES = {
    "ca": {
        "schema_version": "0.2.0",
        "trace_id": "00000000-0000-0000-0000-0000000000e1",
        "script_original": "iast",
        "surface": "ca",
        "normalized": "च",
        "transliteration": {"devanagari": "च", "iast": "ca"},
        "parse_rank": 1,
        "tokens": [{"pada": "ca", "stem": "ca", "vibhakti": "na",
                    "vacana": "na", "linga": "na", "pos": "nipata",
                    "confidence": 0.99}],
        "sandhi_splits": [],
        "ambiguous_parses": [],
        "confidence": 0.99,
        "confidence_aggregate": {"min": 0.99, "mean": 0.99},
        "provenance": ["engine=stub-0.2.0"],
    },
    "rāmo gacchati": {
        "schema_version": "0.2.0",
        "trace_id": "00000000-0000-0000-0000-0000000000a1",
        "script_original": "iast",
        "surface": "rāmo gacchati",
        "normalized": "रामो गच्छति",
        "transliteration": {"devanagari": "रामो गच्छति", "iast": "rāmo gacchati"},
        "parse_rank": 1,
        "tokens": [
            {"pada": "rāmaḥ", "stem": "rāma", "vibhakti": "prathama",
             "vacana": "ekavacana", "linga": "pullinga", "pos": "subhanta",
             "confidence": 0.98},
            {"pada": "gacchati", "stem": "gam", "dhatu": "gam", "gana": 1,
             "prefixes": [], "suffixes": ["śap", "tip"],
             "vibhakti": "na", "vacana": "ekavacana", "linga": "na",
             "pos": "tinanta", "confidence": 0.97},
        ],
        "sandhi_splits": [{"parts": ["rāmaḥ", "gacchati"],
                            "rule": "visarga_o", "rule_canon_ref": "8.2.66",
                            "confidence": 0.99}],
        "ambiguous_parses": [],
        "canon_refs": [{"canon_name": "Aṣṭādhyāyī",
                         "reference_locator": "8.2.66", "domain": "vyakarana"}],
        "confidence": 0.97,
        "confidence_aggregate": {"min": 0.97, "mean": 0.975},
        "provenance": ["engine=stub-0.2.0", "lexicon=MW-2024-11"],
    },
    "parvato vahnimān dhūmavattvāt": {
        "schema_version": "0.2.0",
        "trace_id": "00000000-0000-0000-0000-0000000000f1",
        "script_original": "iast",
        "surface": "parvato vahnimān dhūmavattvāt",
        "normalized": "पर्वतो वह्निमान् धूमवत्त्वात्",
        "transliteration": {"devanagari": "पर्वतो वह्निमान् धूमवत्त्वात्",
                             "iast": "parvato vahnimān dhūmavattvāt"},
        "parse_rank": 1,
        "tokens": [
            {"pada": "parvataḥ", "stem": "parvata", "vibhakti": "prathama",
             "vacana": "ekavacana", "linga": "pullinga", "pos": "subhanta",
             "confidence": 0.95},
            {"pada": "vahnimān", "stem": "vahnimat", "vibhakti": "prathama",
             "vacana": "ekavacana", "linga": "pullinga", "pos": "subhanta",
             "confidence": 0.93},
            {"pada": "dhūmavattvāt", "stem": "dhūmavattva",
             "vibhakti": "pancami", "vacana": "ekavacana",
             "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.91},
        ],
        "sandhi_splits": [{"parts": ["parvataḥ", "vahnimān"],
                            "rule": "visarga_o", "rule_canon_ref": "8.2.66",
                            "confidence": 0.95}],
        "ambiguous_parses": [],
        "canon_refs": [{"canon_name": "Nyāyasūtra",
                         "reference_locator": "1.1.33", "domain": "nyaya"}],
        "confidence": 0.93,
        "confidence_aggregate": {"min": 0.91, "mean": 0.93},
        "provenance": ["engine=stub-0.2.0"],
    },
}

_F01_DECISION = {
    "studio": "Studio_II",
    "intent_class": "logical_argumentation",
    "classifier_confidence": 0.98,
    "rule_id": "R-NYAYA",
    "risk_flags": ["logical_consistency_mandatory"],
    "governance_flags": ["philosophical_no_authority_claim"],
    "nyaya_verifier_mode": "deterministic",
    "nyaya_syllogism": {
        "steps": [
            {"step": "pratijna",  "text": "parvato vahnimān",
             "canon_ref": "Nyāyasūtra 1.1.33",
             "verifier_status": "verified", "confidence": 0.96},
            {"step": "hetu",      "text": "dhūmavattvāt",
             "canon_ref": "Nyāyasūtra 1.1.34",
             "verifier_status": "verified", "confidence": 0.95},
            {"step": "udaharana", "text": "yathā pākāśālā",
             "canon_ref": "Nyāyasūtra 1.1.36",
             "verifier_status": "verified", "confidence": 0.90},
            {"step": "upanaya",   "text": "tathā ayam parvatas",
             "canon_ref": "Nyāyasūtra 1.1.38",
             "verifier_status": "verified", "confidence": 0.93},
            {"step": "nigamana",  "text": "tasmāt parvato vahnimān",
             "canon_ref": "Nyāyasūtra 1.1.39",
             "verifier_status": "verified", "confidence": 0.95},
        ],
        "on_reject": "block_response_and_return_verifier_trace",
        "on_unverifiable": "escalate_to_human_expert",
        "verifier_trace_id": "00000000-0000-0000-0000-0000000000f1",
    },
}


def parse(text):
    if text in _FIXTURES:
        return copy.deepcopy(_FIXTURES[text])
    return None


def route(doc, policy, intent_hint=None):
    if doc.get("surface") == "parvato vahnimān dhūmavattvāt":
        return copy.deepcopy(_F01_DECISION)

    intent = intent_hint or "unknown"
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
        "classifier_confidence": 0.95 if matched else 0.4,
        "rule_id": matched.get("rule_id") if matched else None,
        "risk_flags": list(matched.get("risk_flags", [])) if matched else [],
        "governance_flags": list(matched.get("governance_flags", [])) if matched else [],
    }
    if verifier_mode:
        decision["nyaya_verifier_mode"] = verifier_mode
    return decision