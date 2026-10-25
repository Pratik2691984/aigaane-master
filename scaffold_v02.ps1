# scaffold_v02.ps1 — creates v0.2 contract layer. Does NOT touch existing files.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

function Ensure-Dir($p) {
    if (-not (Test-Path $p)) {
        New-Item -ItemType Directory -Force -Path $p | Out-Null
        Write-Host "[mkdir] $p" -ForegroundColor DarkGray
    }
}
function Write-File($p, $content) {
    if (Test-Path $p) {
        Write-Host "[skip ] $p (exists)" -ForegroundColor Yellow
        return
    }
    Set-Content -Path $p -Value $content -Encoding UTF8 -NoNewline
    Write-Host "[write] $p" -ForegroundColor Green
}
function Assert-Json($p) {
    try { Get-Content $p -Raw | ConvertFrom-Json | Out-Null; Write-Host "[ok   ] $p" -ForegroundColor DarkGreen }
    catch { throw "Invalid JSON written to $p -- $($_.Exception.Message)" }
}

Ensure-Dir 'schemas'
Ensure-Dir 'tests\contract'
Ensure-Dir 'corpus'

# ---------- schemas/samasa_node.json ----------
Write-File 'schemas\samasa_node.json' @'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aigaane.in/schemas/samasa_node.json",
  "title": "SamasaNode",
  "type": "object",
  "properties": {
    "samasa_id": { "type": "string" },
    "component_surface": { "type": "string", "minLength": 1 },
    "role": { "enum": ["purva_pada", "uttara_pada", "madhyama_pada", "single"] },
    "type": { "enum": ["tatpurusha", "bahuvrihi", "dvandva", "avyayibhava", "karmadharaya", "dvigu"] },
    "vigraha": { "type": "string" },
    "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "children": { "type": "array", "items": { "$ref": "#" } }
  },
  "required": ["component_surface", "role", "confidence"],
  "additionalProperties": false
}
'@
Assert-Json 'schemas\samasa_node.json'

# ---------- schemas/sanskrit_contract.json ----------
Write-File 'schemas\sanskrit_contract.json' @'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aigaane.in/schemas/sanskrit_contract.json",
  "title": "AigaaneSanskritTokenContract",
  "type": "object",
  "properties": {
    "schema_version": { "const": "0.2.0" },
    "trace_id": { "type": "string", "format": "uuid" },
    "script_original": { "enum": ["devanagari", "iast", "itrans"] },
    "surface": { "type": "string", "minLength": 1 },
    "normalized": { "type": "string", "minLength": 1 },
    "transliteration": {
      "type": "object",
      "properties": {
        "devanagari": { "type": "string", "minLength": 1 },
        "iast": { "type": "string", "minLength": 1 },
        "itrans": { "type": "string" }
      },
      "required": ["devanagari", "iast"],
      "additionalProperties": false
    },
    "parse_rank": { "type": "integer", "const": 1 },
    "tokens": { "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/Token" } },
    "sandhi_splits": { "type": "array", "items": { "$ref": "#/$defs/SandhiSplit" } },
    "samasa_tree": { "$ref": "samasa_node.json" },
    "ambiguous_parses": { "type": "array", "items": { "$ref": "#/$defs/AlternativeParse" } },
    "canon_refs": { "type": "array", "items": { "$ref": "#/$defs/CanonRef" } },
    "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "confidence_aggregate": {
      "type": "object",
      "properties": {
        "min": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "mean": { "type": "number", "minimum": 0.0, "maximum": 1.0 }
      },
      "required": ["min", "mean"]
    },
    "provenance": { "type": "array", "items": { "type": "string" } }
  },
  "required": ["schema_version","trace_id","script_original","surface","normalized","transliteration","parse_rank","tokens","sandhi_splits","ambiguous_parses","confidence","confidence_aggregate"],
  "additionalProperties": false,
  "$defs": {
    "SandhiRule": {
      "type": "string",
      "enum": ["savarna_dirgha","guna","vṛddhi","visarga_o","visarga_o_with_avagraha","visarga_r","jastva","ścutva","iko_yan_aci","ṛ_varṇa_sandhi","pūrvarūpa","para_rūpa","anunāsika","other"]
    },
    "Token": {
      "type": "object",
      "properties": {
        "token_id": { "type": "string" },
        "pada": { "type": "string", "minLength": 1 },
        "stem": { "type": "string" },
        "dhatu": { "type": "string" },
        "gana": { "type": "integer", "minimum": 1, "maximum": 10 },
        "prefixes": { "type": "array", "items": { "type": "string" } },
        "suffixes": { "type": "array", "items": { "type": "string" } },
        "vibhakti": { "enum": ["prathama","dvitiya","trtiya","caturthi","pancami","shasthi","saptami","sambodhana","na"] },
        "vacana": { "enum": ["ekavacana","dvivacana","bahuvacana","na"] },
        "linga": { "enum": ["pullinga","strilinga","napumsakalinga","na"] },
        "pos": { "enum": ["subhanta","tinanta","avyaya","upasarga","nipata"] },
        "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 }
      },
      "required": ["pada","stem","vibhakti","vacana","linga","pos","confidence"],
      "allOf": [
        { "if": { "properties": { "pos": { "const": "tinanta" } }, "required": ["pos"] }, "then": { "required": ["dhatu","gana"], "properties": { "vibhakti": { "const": "na" }, "vacana": { "enum": ["ekavacana","dvivacana","bahuvacana"] } } } },
        { "if": { "properties": { "pos": { "const": "subhanta" } }, "required": ["pos"] }, "then": { "properties": { "vibhakti": { "not": { "const": "na" } } } } },
        { "if": { "properties": { "pos": { "const": "avyaya" } }, "required": ["pos"] }, "then": { "properties": { "vibhakti": { "const": "na" }, "vacana": { "const": "na" }, "linga": { "const": "na" } } } },
        { "if": { "properties": { "pos": { "const": "nipata" } }, "required": ["pos"] }, "then": { "properties": { "vibhakti": { "const": "na" }, "vacana": { "const": "na" }, "linga": { "const": "na" } } } },
        { "if": { "properties": { "pos": { "const": "upasarga" } }, "required": ["pos"] }, "then": { "properties": { "vibhakti": { "const": "na" }, "vacana": { "const": "na" }, "linga": { "const": "na" } } } }
      ]
    },
    "SandhiSplit": {
      "type": "object",
      "properties": {
        "parts": { "type": "array", "items": { "type": "string", "minLength": 1 }, "minItems": 2 },
        "rule": { "$ref": "#/$defs/SandhiRule" },
        "rule_canon_ref": { "type": "string" },
        "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 }
      },
      "required": ["parts","rule","confidence"],
      "allOf": [
        { "if": { "properties": { "rule": { "const": "other" } }, "required": ["rule"] }, "then": { "required": ["rule_canon_ref"] } }
      ]
    },
    "AlternativeParse": {
      "type": "object",
      "properties": {
        "parse_rank": { "type": "integer", "minimum": 2 },
        "tokens": { "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/Token" } },
        "sandhi_splits": { "type": "array", "items": { "$ref": "#/$defs/SandhiSplit" } },
        "samasa_tree": { "$ref": "samasa_node.json" },
        "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "ambiguity_type": { "enum": ["sandhi_split","vibhakti","dhatu","homonym","compound_vs_simple","accent","other"] }
      },
      "required": ["parse_rank","tokens","confidence","ambiguity_type"]
    },
    "CanonRef": {
      "type": "object",
      "properties": {
        "canon_name": { "type": "string", "minLength": 1 },
        "reference_locator": { "type": "string", "minLength": 1 },
        "domain": { "enum": ["vyakarana","nyaya","shastra","ayurveda","jyotisha","chhandas","artha","other"] }
      },
      "required": ["canon_name","reference_locator"]
    }
  }
}
'@
Assert-Json 'schemas\sanskrit_contract.json'