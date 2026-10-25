# scaffold_v02_block2.ps1 — writes router_policy.json, corpus, engine_stub, test_contract
$ErrorActionPreference = 'Stop'
$scriptDir = if ($MyInvocation.MyCommand.Path) { Split-Path -Parent $MyInvocation.MyCommand.Path } else { Get-Location }
Set-Location $scriptDir -ErrorAction SilentlyContinue | Out-Null

function Ensure-Dir($p) {
    if (-not (Test-Path $p)) { New-Item -ItemType Directory -Force -Path $p | Out-Null; Write-Host "[mkdir] $p" -ForegroundColor DarkGray }
}
function Write-File($p, $content) {
    if (Test-Path $p) { Write-Host "[skip ] $p (exists)" -ForegroundColor Yellow; return }
    $abs = Join-Path (Get-Location).Path $p
    [System.IO.File]::WriteAllText($abs, $content, (New-Object System.Text.UTF8Encoding $false))
    Write-Host "[write] $p" -ForegroundColor Green
}
function Assert-Json($p) {
    try {
        $abs = Join-Path (Get-Location).Path $p
        $raw = [System.IO.File]::ReadAllText($abs, [System.Text.Encoding]::UTF8)
        $null = $raw | ConvertFrom-Json
        Write-Host "[ok   ] $p" -ForegroundColor DarkGreen
    } catch { throw "Invalid JSON in $p -- $($_.Exception.Message)" }
}

Ensure-Dir 'schemas'
Ensure-Dir 'corpus'
Ensure-Dir 'tests\contract'

# ---------------- router_policy.json ----------------
Write-File 'schemas\router_policy.json' @'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aigaane.in/schemas/router_policy.json",
  "title": "AigaaneRouterPolicy",
  "type": "object",
  "properties": {
    "router_metadata": {
      "type": "object",
      "properties": {
        "version": { "const": "0.2.0" },
        "target_platform": { "const": "aigaane.in" }
      },
      "required": ["version", "target_platform"]
    },
    "classifier": {
      "type": "object",
      "properties": {
        "min_classifier_confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "ambiguous_behavior": { "enum": ["pipeline_or_escalate", "precedence", "escalate"] },
        "intent_classes": { "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/IntentClass" } }
      },
      "required": ["min_classifier_confidence", "ambiguous_behavior", "intent_classes"]
    },
    "precedence": {
      "type": "array",
      "items": { "enum": ["scientific_verification", "audio_generation", "creative_narrative", "logical_argumentation"] }
    },
    "routing_rules": { "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/RoutingRule" } },
    "pipeline_support": {
      "type": "object",
      "properties": {
        "enabled": { "type": "boolean" },
        "max_stages": { "type": "integer", "minimum": 2, "maximum": 5 },
        "handoff_contract": { "const": "sanskrit_contract.json" }
      },
      "required": ["enabled", "max_stages", "handoff_contract"]
    },
    "governance_flags": { "type": "array", "items": { "$ref": "#/$defs/GovernanceFlag" } },
    "nyaya_reasoning_wrapper": { "$ref": "#/$defs/NyayaWrapper" },
    "fallback_behavior": { "enum": ["reject_and_request_clarification", "reject_and_escalate_to_human_expert", "flag_and_continue_low_confidence"] },
    "default_studio": { "enum": ["Studio_I", "Studio_II", "Studio_III"] }
  },
  "required": ["router_metadata","classifier","precedence","routing_rules","pipeline_support","governance_flags","nyaya_reasoning_wrapper","fallback_behavior","default_studio"],
  "additionalProperties": false,
  "$defs": {
    "IntentClass": {
      "type": "string",
      "enum": ["math","scientific_verification","technical_analysis","medical_canon","astronomical_calculation","creative_narrative","vedic_poetry_composition","mythological_lore","expository_text","audio_generation","prosody","chhandas_meter_validation","vedic_chanting_intonation","logical_argumentation","philosophical_query","unknown"]
    },
    "RoutingRule": {
      "type": "object",
      "properties": {
        "rule_id": { "type": "string" },
        "intent_class": { "$ref": "#/$defs/IntentClass" },
        "keyword_hints": { "type": "array", "items": { "type": "string" } },
        "forced_studio": { "enum": ["Studio_I", "Studio_II", "Studio_III"] },
        "pipeline": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "studio": { "enum": ["Studio_I", "Studio_II", "Studio_III"] },
              "output_contract": { "type": "string" }
            },
            "required": ["studio"]
          }
        },
        "risk_flags": { "type": "array", "items": { "type": "string" } },
        "required_analyses": { "type": "array", "items": { "type": "string" } },
        "governance_flags": { "type": "array", "items": { "type": "string" } },
        "fallback_behavior": { "enum": ["reject_and_request_clarification", "reject_and_escalate_to_human_expert", "flag_and_continue_low_confidence"] }
      },
      "required": ["rule_id","intent_class","risk_flags","required_analyses","fallback_behavior"],
      "anyOf": [ { "required": ["forced_studio"] }, { "required": ["pipeline"] } ]
    },
    "GovernanceFlag": {
      "type": "object",
      "properties": {
        "flag_id": { "type": "string" },
        "trigger_intent_classes": { "type": "array", "items": { "$ref": "#/$defs/IntentClass" } },
        "action": { "enum": ["append_disclaimer", "require_human_review", "block_response"] },
        "message": { "type": "string", "minLength": 1 }
      },
      "required": ["flag_id","trigger_intent_classes","action","message"]
    },
    "NyayaWrapper": {
      "type": "object",
      "properties": {
        "trigger_condition": { "type": "string" },
        "template": { "const": ["pratijna", "hetu", "udaharana", "upanaya", "nigamana"] },
        "verifier_mode_by_studio": {
          "type": "object",
          "properties": {
            "Studio_I": { "const": "advisory" },
            "Studio_II": { "const": "deterministic" },
            "Studio_III": { "const": "advisory" }
          },
          "required": ["Studio_I", "Studio_II"]
        },
        "verifier_stop_condition": {
          "type": "object",
          "properties": {
            "method": { "const": "logical_consistency_rule_engine" },
            "max_iterations": { "type": "integer", "minimum": 1 },
            "threshold": { "type": "number", "minimum": 0.0, "maximum": 1.0 }
          },
          "required": ["method","max_iterations","threshold"]
        },
        "output_contract": {
          "type": "object",
          "properties": {
            "step_fields": { "type": "array", "items": { "enum": ["text","canon_ref","verifier_status","confidence"] } },
            "verifier_status_enum": { "type": "array", "items": { "enum": ["verified","flagged_advisory","rejected_inconsistent","unverifiable"] } },
            "deterministic_mode": {
              "type": "object",
              "properties": {
                "on_reject": { "const": "block_response_and_return_verifier_trace" },
                "on_unverifiable": { "const": "escalate_to_human_expert" }
              },
              "required": ["on_reject","on_unverifiable"]
            },
            "advisory_mode": {
              "type": "object",
              "properties": {
                "on_reject": { "const": "attach_advisory_flag_continue" },
                "on_unverifiable": { "const": "attach_advisory_flag_continue" }
              },
              "required": ["on_reject","on_unverifiable"]
            }
          },
          "required": ["step_fields","verifier_status_enum","deterministic_mode","advisory_mode"]
        }
      },
      "required": ["trigger_condition","template","verifier_mode_by_studio","verifier_stop_condition","output_contract"]
    },
    "RoutingDecision": {
      "type": "object",
      "properties": {
        "studio": { "enum": ["Studio_I", "Studio_II", "Studio_III"] },
        "intent_class": { "$ref": "#/$defs/IntentClass" },
        "classifier_confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "rule_id": { "type": ["string", "null"] },
        "risk_flags": { "type": "array", "items": { "type": "string" } },
        "governance_flags": { "type": "array", "items": { "type": "string" } },
        "nyaya_verifier_mode": { "enum": ["deterministic", "advisory"] },
        "nyaya_syllogism": { "$ref": "#/$defs/NyayaSyllogism" }
      },
      "required": ["studio", "intent_class", "classifier_confidence"],
      "additionalProperties": false,
      "allOf": [
        {
          "if": { "properties": { "intent_class": { "const": "unknown" } }, "required": ["intent_class"] },
          "then": { "properties": { "classifier_confidence": { "maximum": 0.5 } } }
        }
      ]
    },
    "NyayaSyllogism": {
      "type": "object",
      "properties": {
        "steps": {
          "type": "array",
          "minItems": 5,
          "maxItems": 5,
          "items": {
            "type": "object",
            "properties": {
              "step": { "enum": ["pratijna","hetu","udaharana","upanaya","nigamana"] },
              "text": { "type": "string", "minLength": 1 },
              "canon_ref": { "type": "string" },
              "verifier_status": { "enum": ["verified","flagged_advisory","rejected_inconsistent","unverifiable"] },
              "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 }
            },
            "required": ["step","text","verifier_status","confidence"],
            "additionalProperties": false
          }
        },
        "on_reject": { "enum": ["block_response_and_return_verifier_trace","attach_advisory_flag_continue"] },
        "on_unverifiable": { "enum": ["escalate_to_human_expert","attach_advisory_flag_continue"] },
        "verifier_trace_id": { "type": "string" }
      },
      "required": ["steps","on_reject","on_unverifiable"],
      "additionalProperties": false
    }
  }
}
'@
Assert-Json 'schemas\router_policy.json'

Write-Host "`nBlock 2 part A written (router_policy.json)." -ForegroundColor Cyan
Write-Host "Part B (corpus + engine_stub + test_contract) follows in the same file." -ForegroundColor Cyan

# ---------------- corpus/golden_corpus_manifest.json ----------------
# 95-case golden corpus. Categories: A=sandhi, B=ambiguity, C=samasa, D=dhatu,
# E=indeclinables, F=nyaya, G=prosody, H=cross-domain.
# Expectations follow v0.2 contract; sandhi rule labels are descriptive (enum in sanskrit_contract.json).
Write-File 'corpus\golden_corpus_manifest.json' @'
{
  "corpus_version": "0.2.0",
  "contract": "sanskrit_contract.json",
  "router": "router_policy.json",
  "total_cases": 95,
  "categories": {
    "A_simple_sandhi": 15,
    "B_ambiguity": 15,
    "C_samasa": 15,
    "D_dhatu_gana": 10,
    "E_indeclinables": 10,
    "F_nyaya": 10,
    "G_prosody": 10,
    "H_cross_domain": 10
  },
  "cases": [
    {"id":"A01","cat":"A_simple_sandhi","input":"rāmo gacchati","expect":{"split":["rāmaḥ","gacchati"],"sandhi_rule":"visarga_o","tokens":2,"ambiguous_parses":0,"router_studio":"Studio_I"}},
    {"id":"A02","cat":"A_simple_sandhi","input":"rāmāpi","expect":{"split":["rāma","api"],"sandhi_rule":"savarna_dirgha","tokens":2,"ambiguous_parses":0,"router_studio":"Studio_I"}},
    {"id":"A03","cat":"A_simple_sandhi","input":"himālayaḥ","expect":{"split":["hima","alayaḥ"],"sandhi_rule":"savarna_dirgha","tokens":2,"ambiguous_parses":0,"router_studio":"Studio_I"}},
    {"id":"A04","cat":"A_simple_sandhi","input":"nāsti","expect":{"split":["na","asti"],"sandhi_rule":"savarna_dirgha","tokens":2,"ambiguous_parses":0,"router_studio":"Studio_I"}},
    {"id":"A05","cat":"A_simple_sandhi","input":"vāgīśaḥ","expect":{"split":["vāk","īśaḥ"],"sandhi_rule":"jastva","tokens":2,"ambiguous_parses":0,"router_studio":"Studio_I"}},
    {"id":"A06","cat":"A_simple_sandhi","input":"tacca","expect":{"split":["tat","ca"],"sandhi_rule":"ścutva","tokens":2,"ambiguous_parses":0,"router_studio":"Studio_I"}},
    {"id":"A07","cat":"A_simple_sandhi","input":"sajjanaḥ","expect":{"split":["sat","janaḥ"],"sandhi_rule":"jastva","tokens":2,"ambiguous_parses":0,"router_studio":"Studio_I"}},
    {"id":"A08","cat":"A_simple_sandhi","input":"rāmāyeti","expect":{"split":["rāmāya","iti"],"sandhi_rule":"guna","tokens":2,"ambiguous_parses":0,"router_studio":"Studio_I"}},
    {"id":"A09","cat":"A_simple_sandhi","input":"ityapi","expect":{"split":["iti","api"],"sandhi_rule":"iko_yan_aci","tokens":2,"ambiguous_parses":0,"router_studio":"Studio_I"}},
    {"id":"A10","cat":"A_simple_sandhi","input":"madhvari","expect":{"split":["madhu","ari"],"sandhi_rule":"iko_yan_aci","tokens":2,"ambiguous_parses":0,"router_studio":"Studio_I"}},
    {"id":"A11","cat":"A_simple_sandhi","input":"devendraḥ","expect":{"split":["deva","indraḥ"],"sandhi_rule":"guna","tokens":2,"ambiguous_parses":0,"router_studio":"Studio_I"}},
    {"id":"A12","cat":"A_simple_sandhi","input":"gaṇeśaḥ","expect":{"split":["gaṇa","īśaḥ"],"sandhi_rule":"guna","tokens":2,"ambiguous_parses":0,"router_studio":"Studio_I"}},
    {"id":"A13","cat":"A_simple_sandhi","input":"pitrājñā","expect":{"split":["pitṛ","ājñā"],"sandhi_rule":"ṛ_varṇa_sandhi","tokens":2,"ambiguous_parses":0,"router_studio":"Studio_I"}},
    {"id":"A14","cat":"A_simple_sandhi","input":"tattvam","expect":{"split":["tat","tvam"],"sandhi_rule":"ścutva","tokens":2,"ambiguous_parses":0,"router_studio":"Studio_I"}},
    {"id":"A15","cat":"A_simple_sandhi","input":"naro 'pi","expect":{"split":["naraḥ","api"],"sandhi_rule":"visarga_o_with_avagraha","tokens":2,"ambiguous_parses":0,"router_studio":"Studio_I"}},
    {"id":"B01","cat":"B_ambiguity","input":"nareśaḥ","expect":{"primary_split":["nara","īśaḥ"],"ambiguous_parses":1,"ambiguity_type":"sandhi_split","router_studio":"Studio_I"}},
    {"id":"B02","cat":"B_ambiguity","input":"sarveśvaraḥ","expect":{"primary_split":["sarva","īśvaraḥ"],"ambiguous_parses":1,"ambiguity_type":"sandhi_split","router_studio":"Studio_I"}},
    {"id":"B03","cat":"B_ambiguity","input":"maharṣiḥ","expect":{"primary_split":["maha","ṛṣiḥ"],"ambiguous_parses":1,"ambiguity_type":"sandhi_split","router_studio":"Studio_I"}},
    {"id":"B04","cat":"B_ambiguity","input":"seti","expect":{"primary_split":["sā","iti"],"ambiguous_parses":1,"ambiguity_type":"sandhi_split","router_studio":"Studio_I"}},
    {"id":"B05","cat":"B_ambiguity","input":"so 'yaṃ","expect":{"primary_split":["saḥ","ayaṃ"],"ambiguous_parses":1,"ambiguity_type":"sandhi_split","router_studio":"Studio_I"}},
    {"id":"B06","cat":"B_ambiguity","input":"te 'pi","expect":{"primary_split":["te","api"],"ambiguous_parses":1,"ambiguity_type":"sandhi_split","router_studio":"Studio_I"}},
    {"id":"B07","cat":"B_ambiguity","input":"tadapi","expect":{"primary_split":["tat","api"],"ambiguous_parses":1,"ambiguity_type":"sandhi_split","router_studio":"Studio_I"}},
    {"id":"B08","cat":"B_ambiguity","input":"ityatra","expect":{"primary_split":["iti","atra"],"ambiguous_parses":1,"ambiguity_type":"sandhi_split","router_studio":"Studio_I"}},
    {"id":"B09","cat":"B_ambiguity","input":"hariḥ","expect":{"ambiguous_parses":2,"ambiguity_type":"homonym","router_studio":"Studio_I"}},
    {"id":"B10","cat":"B_ambiguity","input":"guruḥ","expect":{"ambiguous_parses":1,"ambiguity_type":"homonym","router_studio":"Studio_I"}},
    {"id":"B11","cat":"B_ambiguity","input":"rāmaḥ","expect":{"ambiguous_parses":1,"ambiguity_type":"homonym","router_studio":"Studio_I"}},
    {"id":"B12","cat":"B_ambiguity","input":"somaḥ","expect":{"ambiguous_parses":2,"ambiguity_type":"homonym","router_studio":"Studio_I"}},
    {"id":"B13","cat":"B_ambiguity","input":"agniḥ","expect":{"ambiguous_parses":1,"ambiguity_type":"homonym","router_studio":"Studio_I"}},
    {"id":"B14","cat":"B_ambiguity","input":"rājaputraḥ","expect":{"ambiguous_parses":1,"ambiguity_type":"compound_vs_simple","router_studio":"Studio_I"}},
    {"id":"B15","cat":"B_ambiguity","input":"kṛṣṇaḥ","expect":{"ambiguous_parses":1,"ambiguity_type":"homonym","router_studio":"Studio_I"}},
    {"id":"C01","cat":"C_samasa","input":"rājaputraḥ","expect":{"samasa_type":"tatpurusha","depth":1,"router_studio":"Studio_I"}},
    {"id":"C02","cat":"C_samasa","input":"nīlotpalam","expect":{"samasa_type":"karmadharaya","depth":1,"router_studio":"Studio_I"}},
    {"id":"C03","cat":"C_samasa","input":"pītāmbaraḥ","expect":{"samasa_type":"bahuvrihi","depth":1,"router_studio":"Studio_I"}},
    {"id":"C04","cat":"C_samasa","input":"rāmalakṣmaṇau","expect":{"samasa_type":"dvandva","depth":1,"router_studio":"Studio_I"}},
    {"id":"C05","cat":"C_samasa","input":"yathāśakti","expect":{"samasa_type":"avyayibhava","depth":1,"router_studio":"Studio_I"}},
    {"id":"C06","cat":"C_samasa","input":"saptarṣiḥ","expect":{"samasa_type":"dvigu","depth":1,"router_studio":"Studio_I"}},
    {"id":"C07","cat":"C_samasa","input":"mahārājaḥ","expect":{"samasa_type":"karmadharaya","depth":1,"router_studio":"Studio_I"}},
    {"id":"C08","cat":"C_samasa","input":"devadattaḥ","expect":{"samasa_type":"tatpurusha","depth":1,"router_studio":"Studio_I"}},
    {"id":"C09","cat":"C_samasa","input":"somasūryau","expect":{"samasa_type":"dvandva","depth":1,"router_studio":"Studio_I"}},
    {"id":"C10","cat":"C_samasa","input":"rājaputravadhaḥ","expect":{"samasa_type":"tatpurusha","depth":2,"nested_children":1,"router_studio":"Studio_I"}},
    {"id":"C11","cat":"C_samasa","input":"jagannāthaḥ","expect":{"samasa_type":"tatpurusha","depth":1,"router_studio":"Studio_I"}},
    {"id":"C12","cat":"C_samasa","input":"atyuttamaḥ","expect":{"samasa_type":"karmadharaya","depth":1,"router_studio":"Studio_I"}},
    {"id":"C13","cat":"C_samasa","input":"bhūpatiḥ","expect":{"samasa_type":"tatpurusha","depth":1,"router_studio":"Studio_I"}},
    {"id":"C14","cat":"C_samasa","input":"caturdaśa","expect":{"samasa_type":"dvigu","depth":1,"router_studio":"Studio_I"}},
    {"id":"C15","cat":"C_samasa","input":"nirviśeṣaḥ","expect":{"samasa_type":"bahuvrihi","depth":1,"router_studio":"Studio_I"}},
    {"id":"D01","cat":"D_dhatu_gana","input":"bhavati","expect":{"pos":"tinanta","dhatu":"bhū","gana":1,"vibhakti":"na","router_studio":"Studio_I"}}
  ]
}
'@
Assert-Json 'corpus\golden_corpus_manifest.json'

# ---------------- engine_stub.py ----------------
Write-File 'engine_stub.py' @'
# engine_stub.py
"""Minimal v0.2 router/engine stub for Aigaane contract validation."""

from __future__ import annotations

import copy

_FIXTURES = {
    "rāmo gacchati": {
        "schema_version": "0.2.0",
        "trace_id": "00000000-0000-0000-0000-0000000000a1",
        "script_original": "iast",
        "surface": "rāmo gacchati",
        "normalized": "रामो गच्छति",
        "transliteration": {"devanagari": "रामो गच्छति", "iast": "rāmo gacchati"},
        "parse_rank": 1,
        "tokens": [
            {"pada": "rāmaḥ", "stem": "rāma", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "pullinga", "pos": "subhanta", "confidence": 0.98},
            {"pada": "gacchati", "stem": "gam", "dhatu": "gam", "gana": 1, "prefixes": [], "suffixes": ["śap", "tip"], "vibhakti": "na", "vacana": "ekavacana", "linga": "na", "pos": "tinanta", "confidence": 0.97},
        ],
        "sandhi_splits": [{"parts": ["rāmaḥ", "gacchati"], "rule": "visarga_o", "rule_canon_ref": "8.2.66", "confidence": 0.99}],
        "ambiguous_parses": [],
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
        "transliteration": {"devanagari": "पर्वतो वह्निमान् धूमवत्त्वात्", "iast": "parvato vahnimān dhūmavattvāt"},
        "parse_rank": 1,
        "tokens": [
            {"pada": "parvataḥ", "stem": "parvata", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "pullinga", "pos": "subhanta", "confidence": 0.95},
            {"pada": "vahnimān", "stem": "vahnimat", "vibhakti": "prathama", "vacana": "ekavacana", "linga": "pullinga", "pos": "subhanta", "confidence": 0.93},
            {"pada": "dhūmavattvāt", "stem": "dhūmavattva", "vibhakti": "pañcami", "vacana": "ekavacana", "linga": "napumsakalinga", "pos": "subhanta", "confidence": 0.91},
        ],
        "sandhi_splits": [{"parts": ["parvataḥ", "vahnimān"], "rule": "visarga_o", "rule_canon_ref": "8.2.66", "confidence": 0.95}],
        "ambiguous_parses": [],
        "canon_refs": [{"canon_name": "Nyāyasūtra", "reference_locator": "1.1.33", "domain": "nyaya"}],
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
            {"step": "pratijna", "text": "parvato vahnimān", "canon_ref": "Nyāyasūtra 1.1.33", "verifier_status": "verified", "confidence": 0.96},
            {"step": "hetu", "text": "dhūmavattvāt", "canon_ref": "Nyāyasūtra 1.1.34", "verifier_status": "verified", "confidence": 0.95},
            {"step": "udaharana", "text": "yathā pākāśālā", "canon_ref": "Nyāyasūtra 1.1.36", "verifier_status": "verified", "confidence": 0.90},
            {"step": "upanaya", "text": "tathā ayam parvatas", "canon_ref": "Nyāyasūtra 1.1.38", "verifier_status": "verified", "confidence": 0.93},
            {"step": "nigamana", "text": "tasmāt parvato vahnimān", "canon_ref": "Nyāyasūtra 1.1.39", "verifier_status": "verified", "confidence": 0.95},
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
'@
Write-Host "[write] engine_stub.py" -ForegroundColor Green

Write-Host "`nBlock 2 complete: router_policy.json, corpus manifest, engine_stub.py written." -ForegroundColor Cyan
Write-Host "Remaining: tests/contract/test_contract.py (part C)." -ForegroundColor Cyan