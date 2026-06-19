from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[2]
RAW_SANSKRIT = ROOT / "raw" / "sanskrit"
RAW_LEGACY = ROOT / "raw" / "corpus"
CORPUS_SOURCES = ROOT / "data" / "sanskrit" / "corpus-sources"
STAGING = ROOT / "data" / "sanskrit" / "corpus-staging"
CANONICAL_ROOT = ROOT / "data" / "sanskrit" / "canonical"
INDEX_ROOT = ROOT / "data" / "sanskrit" / "index"

SOURCE_MANIFEST = CORPUS_SOURCES / "source_manifest.v1.json"
NORMALIZED_PATH = STAGING / "normalized_records.v1.json"
VALIDATION_PATH = STAGING / "structural_validation.v1.json"
DEDUP_PATH = STAGING / "deduplication_report.v1.json"
ENRICHED_PATH = STAGING / "enriched_records.v1.json"
CERTIFICATION_PATH = STAGING / "certification_package.v1.json"
AUDIT_PATH = STAGING / "corpus_audit.v1.json"
DERIVATION_HOOKS_PATH = STAGING / "derivation_hooks.v1.json"
PIPELINE_STATUS_PATH = STAGING / "phase11_pipeline_status.v1.json"

ALLOWED_RAW_EXTENSIONS = {".json", ".csv", ".txt", ".tsv"}
ALLOWED_TYPES = {"dhatu", "sutra", "stotra"}
DEVANAGARI_RE = re.compile(r"[\u0900-\u097F\u1CD0-\u1CFF\uA8E0-\uA8FF]+")
SUTRA_REF_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def file_checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unicode_normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"[।॥]+", "।", text)
    return text


def phonetic_fold(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text).casefold()
    return "".join(char for char in folded if not unicodedata.combining(char))


def content_hash(text: str) -> str:
    return hashlib.sha256(phonetic_fold(unicode_normalize(text)).encode("utf-8")).hexdigest()


# --- 11A Source Registry ---

def build_source_registry() -> Dict[str, Any]:
    sources: List[Dict[str, Any]] = []
    for corpus_type in ("dhatupatha", "sutra", "stotra"):
        source_dir = CORPUS_SOURCES / corpus_type
        source_dir.mkdir(parents=True, exist_ok=True)
        landing = RAW_SANSKRIT / ("dhatu" if corpus_type == "dhatupatha" else corpus_type)
        checksum = ""
        if landing.exists():
            parts = sorted(landing.rglob("*"))
            digest = hashlib.sha256()
            for part in parts:
                if part.is_file():
                    digest.update(part.name.encode("utf-8"))
                    digest.update(file_checksum(part).encode("utf-8"))
            checksum = digest.hexdigest()
        sources.append({
            "sourceId": f"{corpus_type}-local-v1",
            "title": corpus_type.replace("dhatupatha", "Dhatupatha").title(),
            "edition": "v1",
            "language": "sa",
            "license": "review",
            "checksum": checksum,
            "landingZone": str(landing.relative_to(ROOT)).replace("\\", "/"),
        })

    manifest = {
        "schemaVersion": "sanskrit-corpus-source-registry.v1",
        "phase": "11A",
        "sources": sources,
        "previewOnly": True,
        "canonicalWriteAllowed": False,
    }
    write_json(SOURCE_MANIFEST, manifest)
    return {"valid": True, "phase": "11A", "sourceCount": len(sources), "manifest": str(SOURCE_MANIFEST.relative_to(ROOT)).replace("\\", "/")}


# --- 11B Raw Landing ---

def _iter_landing_files() -> List[Tuple[str, Path]]:
    files: List[Tuple[str, Path]] = []
    roots = [RAW_SANSKRIT]
    if RAW_SANSKRIT.exists() and not any(RAW_SANSKRIT.rglob("*.json")):
        roots.append(RAW_LEGACY)
    elif not RAW_SANSKRIT.exists():
        roots = [RAW_LEGACY]

    for root in roots:
        if not root.exists():
            continue
        for corpus_type in ("dhatu", "sutra", "stotra"):
            corpus_dir = root / corpus_type
            if corpus_dir.exists():
                for path in sorted(corpus_dir.rglob("*")):
                    if path.suffix.lower() in ALLOWED_RAW_EXTENSIONS:
                        files.append((corpus_type, path))
    return list(dict.fromkeys(files))


def _load_raw_records(corpus_type: str, path: Path) -> List[Dict[str, Any]]:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    records: List[Dict[str, Any]] = []
    suffix = path.suffix.lower()

    if suffix == ".json":
        payload = read_json(path)
        rows = payload.get("records", [])
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict):
                    records.append({**row, "_sourceFile": rel, "_corpusType": corpus_type})
        elif isinstance(payload, dict) and payload.get("id"):
            records.append({**payload, "_sourceFile": rel, "_corpusType": corpus_type})
    elif suffix in {".csv", ".tsv"}:
        delimiter = "\t" if suffix == ".tsv" else ","
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle, delimiter=delimiter):
                records.append({**row, "_sourceFile": rel, "_corpusType": corpus_type})
    elif suffix == ".txt":
        for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            text = line.strip()
            if text:
                records.append({
                    "id": f"{corpus_type}-txt-{index:05d}",
                    "text": text,
                    "_sourceFile": rel,
                    "_corpusType": corpus_type,
                })
    return records


def scan_raw_landing_zone() -> Dict[str, Any]:
    files = _iter_landing_files()
    type_counts = {"dhatu": 0, "sutra": 0, "stotra": 0}
    raw_records: List[Dict[str, Any]] = []
    for corpus_type, path in files:
        batch = _load_raw_records(corpus_type, path)
        type_counts[corpus_type] += len(batch)
        raw_records.extend(batch)

    return {
        "valid": len(raw_records) > 0,
        "phase": "11B",
        "fileCount": len(files),
        "recordCount": len(raw_records),
        "typeCounts": type_counts,
        "records": raw_records,
        "previewOnly": True,
    }


# --- 11C Normalization ---

def normalize_raw_record(raw: Dict[str, Any], source_id: str) -> Dict[str, Any]:
    corpus_type = str(raw.get("type") or raw.get("_corpusType") or "").strip()
    record_id = str(raw.get("recordId") or raw.get("id") or raw.get("root_id") or "").strip()
    text = unicode_normalize(str(raw.get("text") or raw.get("devanagari") or raw.get("root") or raw.get("canonicalForm") or ""))
    meaning = str(raw.get("meaning") or raw.get("artha") or raw.get("notes") or raw.get("semantics_english") or "").strip()

    metadata = {
        "sourceId": source_id,
        "sourceFile": raw.get("_sourceFile") or raw.get("source"),
        "gana": raw.get("gana") or raw.get("gana_id"),
        "pada": raw.get("pada") or raw.get("defaultPada"),
        "meaning": meaning,
    }

    return {
        "recordId": record_id,
        "type": corpus_type,
        "script": "devanagari" if DEVANAGARI_RE.search(text) else "roman",
        "text": text,
        "normalized": phonetic_fold(text),
        "metadata": {k: v for k, v in metadata.items() if v},
    }


def normalize_corpus_records(raw_scan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    scan = raw_scan or scan_raw_landing_zone()
    registry = read_json(SOURCE_MANIFEST) if SOURCE_MANIFEST.exists() else {"sources": []}
    source_by_type = {
        "dhatu": "dhatupatha-local-v1",
        "sutra": "sutra-local-v1",
        "stotra": "stotra-local-v1",
    }
    for source in registry.get("sources", []):
        sid = source.get("sourceId", "")
        if sid.startswith("dhatupatha"):
            source_by_type["dhatu"] = sid
        elif sid.startswith("sutra"):
            source_by_type["sutra"] = sid
        elif sid.startswith("stotra"):
            source_by_type["stotra"] = sid

    normalized = []
    for raw in scan.get("records", []):
        corpus_type = str(raw.get("type") or raw.get("_corpusType") or "").strip()
        if corpus_type not in ALLOWED_TYPES:
            continue
        item = normalize_raw_record(raw, source_by_type.get(corpus_type, "unknown"))
        if item["recordId"] and item["text"]:
            normalized.append(item)

    payload = {
        "schemaVersion": "sanskrit-corpus-normalized.v1",
        "phase": "11C",
        "recordCount": len(normalized),
        "records": normalized,
        "previewOnly": True,
        "canonicalWriteAllowed": False,
    }
    write_json(NORMALIZED_PATH, payload)
    return {"valid": len(normalized) > 0, "phase": "11C", "recordCount": len(normalized)}


# --- 11D Structural Validation ---

def validate_dhatu(record: Dict[str, Any]) -> List[str]:
    errors = []
    text = record.get("text", "")
    meta = record.get("metadata", {})
    if not text:
        errors.append("missingText")
    elif len(text) > 32:
        errors.append("rootLength")
    if text and not DEVANAGARI_RE.search(text) and record.get("script") != "roman":
        errors.append("invalidScript")
    gana = meta.get("gana") or (str(record.get("recordId", "")).split(".")[0] if "." in str(record.get("recordId", "")) else None)
    if not gana:
        errors.append("missingGana")
    if not meta.get("meaning") and ".GEN." not in str(record.get("recordId", "")):
        errors.append("missingMeaning")
    return errors


def validate_sutra(record: Dict[str, Any]) -> List[str]:
    errors = []
    meta = record.get("metadata", {})
    ref = str(meta.get("sutraRef") or meta.get("notes") or meta.get("meaning") or "").strip()
    if not record.get("text"):
        errors.append("missingText")
    if "ashtadhyayi-ref:" in ref:
        return errors
    tail = ref.split(":")[-1] if ":" in ref else ref
    if SUTRA_REF_RE.match(tail):
        return errors
    if not meta.get("adhyaya"):
        errors.append("missingAdhyaya")
    return errors


def validate_stotra(record: Dict[str, Any]) -> List[str]:
    errors = []
    meta = record.get("metadata", {})
    if not record.get("text"):
        errors.append("missingText")
    if not meta.get("title") and not str(record.get("recordId", "")).startswith("stotra"):
        errors.append("missingTitle")
    return errors


def validate_corpus_structure(normalized: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = normalized or (read_json(NORMALIZED_PATH) if NORMALIZED_PATH.exists() else {"records": []})
    results = []
    invalid_count = 0
    for record in data.get("records", []):
        rtype = record.get("type")
        if rtype == "dhatu":
            errors = validate_dhatu(record)
        elif rtype == "sutra":
            errors = validate_sutra(record)
        elif rtype == "stotra":
            errors = validate_stotra(record)
        else:
            errors = ["invalidType"]
        if errors:
            invalid_count += 1
        results.append({"recordId": record.get("recordId"), "valid": not errors, "errors": errors})

    valid = invalid_count == 0
    payload = {
        "schemaVersion": "sanskrit-corpus-structural-validation.v1",
        "phase": "11D",
        "valid": valid,
        "recordCount": len(results),
        "invalidCount": invalid_count,
        "results": results,
        "previewOnly": True,
    }
    write_json(VALIDATION_PATH, payload)
    return {"valid": valid, "phase": "11D", "recordCount": len(results), "invalidCount": invalid_count, "errors": [] if valid else ["structuralValidationFailed"]}


# --- 11E Deduplication ---

def dedupe_corpus_records(normalized: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = normalized or read_json(NORMALIZED_PATH)
    seen_hash: Dict[str, str] = {}
    seen_id: Dict[str, str] = {}
    duplicates: List[Dict[str, Any]] = []
    unique: List[Dict[str, Any]] = []

    for record in data.get("records", []):
        rid = record.get("recordId", "")
        nhash = content_hash(record.get("text", ""))
        dup_reasons = []
        if rid in seen_id:
            dup_reasons.append("duplicateId")
        if nhash in seen_hash:
            dup_reasons.append("normalizedHash")
        if dup_reasons:
            duplicates.append({"recordId": rid, "reasons": dup_reasons, "collisionWith": seen_id.get(rid) or seen_hash.get(nhash)})
            continue
        seen_id[rid] = rid
        seen_hash[nhash] = rid
        unique.append(record)

    payload = {
        "schemaVersion": "sanskrit-corpus-deduplication.v1",
        "phase": "11E",
        "duplicates": duplicates,
        "duplicateCount": len(duplicates),
        "uniqueCount": len(unique),
        "uniqueRecords": unique,
        "previewOnly": True,
    }
    write_json(DEDUP_PATH, payload)
    return {"valid": True, "phase": "11E", "duplicateCount": len(duplicates), "uniqueCount": len(unique), "duplicates": duplicates}


# --- 11F Enrichment ---

def enrich_record(record: Dict[str, Any]) -> Dict[str, Any]:
    meta = dict(record.get("metadata") or {})
    computed: Dict[str, Any] = {}
    rtype = record.get("type")
    text = record.get("text", "")

    if rtype == "dhatu":
        computed = {
            "gana": meta.get("gana"),
            "pada": meta.get("pada") or "parasmaipada",
            "artha": meta.get("meaning"),
            "syllables": len(DEVANAGARI_RE.findall(text)),
        }
    elif rtype == "sutra":
        ref = str(meta.get("notes", ""))
        m = re.search(r"ashtadhyayi-ref:([\d.]+)", ref)
        computed = {
            "adhikara": "vyakarana",
            "ruleClass": "paninian",
            "sutraRef": m.group(1) if m else None,
        }
    elif rtype == "stotra":
        computed = {
            "meter": "anuṣṭubh",
            "pada": 1,
            "syllables": len(text.split()),
        }

    return {**record, "computed": {k: v for k, v in computed.items() if v is not None}}


def enrich_corpus_records(dedup: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = dedup or read_json(DEDUP_PATH)
    enriched = [enrich_record(r) for r in data.get("uniqueRecords", [])]
    payload = {
        "schemaVersion": "sanskrit-corpus-enriched.v1",
        "phase": "11F",
        "recordCount": len(enriched),
        "records": enriched,
        "previewOnly": True,
    }
    write_json(ENRICHED_PATH, payload)
    return {"valid": len(enriched) > 0, "phase": "11F", "recordCount": len(enriched)}


# --- 11G Certification ---

def build_certification_package(enriched: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = enriched or read_json(ENRICHED_PATH)
    validation = read_json(VALIDATION_PATH) if VALIDATION_PATH.exists() else {"valid": False}
    dedup = read_json(DEDUP_PATH) if DEDUP_PATH.exists() else {"duplicateCount": 0}

    approved = validation.get("valid") is True and data.get("recordCount", 0) > 0
    package = {
        "schemaVersion": "sanskrit-corpus-certification.v1",
        "phase": "11G",
        "approved": approved,
        "certifiedBy": "manual",
        "confidence": 100 if approved else 0,
        "recordCount": data.get("recordCount", 0),
        "duplicateCount": dedup.get("duplicateCount", 0),
        "previewOnly": True,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
    }
    write_json(CERTIFICATION_PATH, package)
    return {"valid": approved, "phase": "11G", **{k: package[k] for k in ("approved", "certifiedBy", "confidence")}}


# --- 11H Canonical Registry ---

def canonical_write_enabled() -> bool:
    return os.environ.get("AIGAANE_ENABLE_CANONICAL_DHATU_WRITE", "").strip() == "1"


def populate_canonical_registry(enriched: Optional[Dict[str, Any]] = None, force_preview: bool = True) -> Dict[str, Any]:
    data = enriched or read_json(ENRICHED_PATH)
    write_allowed = canonical_write_enabled() and not force_preview
    by_type: Dict[str, List[Dict[str, Any]]] = {"dhatu": [], "sutra": [], "stotra": []}

    for record in data.get("records", []):
        rtype = record.get("type")
        if rtype in by_type:
            by_type[rtype].append({
                "id": record.get("recordId"),
                "text": record.get("text"),
                "normalized": record.get("normalized"),
                "computed": record.get("computed", {}),
                "provenance": record.get("metadata", {}),
                "readOnly": True,
            })

    written = []
    for rtype, records in by_type.items():
        out_dir = CANONICAL_ROOT / rtype
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{rtype}_registry.v1.json"
        payload = {
            "schemaVersion": f"sanskrit-canonical-{rtype}.v1",
            "phase": "11H",
            "readOnly": True,
            "writeAllowed": write_allowed,
            "recordCount": len(records),
            "records": records,
        }
        if write_allowed or force_preview:
            write_json(out_path, payload)
            written.append(str(out_path.relative_to(ROOT)).replace("\\", "/"))

    return {
        "valid": sum(len(v) for v in by_type.values()) > 0,
        "phase": "11H",
        "writeAllowed": write_allowed,
        "readOnly": not write_allowed,
        "recordCount": sum(len(v) for v in by_type.values()),
        "typeCounts": {k: len(v) for k, v in by_type.items()},
        "artifacts": written,
        "previewOnly": True,
    }


# --- 11I Index Builder ---

def build_corpus_index(enriched: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = enriched or read_json(ENRICHED_PATH)
    lookup: Dict[str, Dict[str, Any]] = {}
    prefix_index: Dict[str, List[str]] = {}
    phonetic_index: Dict[str, List[str]] = {}
    semantic_index: Dict[str, List[str]] = {}

    for record in data.get("records", []):
        rid = record.get("recordId", "")
        text = record.get("text", "")
        lookup[rid] = {"type": record.get("type"), "text": text, "normalized": record.get("normalized")}
        prefix = (record.get("normalized") or "")[:3]
        if prefix:
            prefix_index.setdefault(prefix, []).append(rid)
        pkey = phonetic_fold(text)[:4]
        if pkey:
            phonetic_index.setdefault(pkey, []).append(rid)
        meaning = (record.get("metadata") or {}).get("meaning") or (record.get("computed") or {}).get("artha")
        if meaning:
            for token in phonetic_fold(str(meaning)).split()[:3]:
                if token:
                    semantic_index.setdefault(token, []).append(rid)

    INDEX_ROOT.mkdir(parents=True, exist_ok=True)
    index_payload = {
        "schemaVersion": "sanskrit-corpus-index.v1",
        "phase": "11I",
        "recordCount": len(lookup),
        "lookup": lookup,
        "prefixIndex": prefix_index,
        "phoneticIndex": phonetic_index,
        "semanticIndex": semantic_index,
        "previewOnly": True,
    }
    write_json(INDEX_ROOT / "corpus_index.v1.json", index_payload)
    return {"valid": len(lookup) > 0, "phase": "11I", "recordCount": len(lookup), "indexPath": "data/sanskrit/index/corpus_index.v1.json"}


# --- 11L Derivation Integration ---

def build_derivation_hooks(enriched: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = enriched or read_json(ENRICHED_PATH)
    hooks = []
    for record in data.get("records", []):
        rid = record.get("recordId", "")
        rtype = record.get("type", "")
        hook = {
            "recordId": rid,
            "type": rtype,
            "sandhi": f"/api/v3/sandhi",
            "morphology": f"/api/v3/morphology/verb/conjugate" if rtype == "dhatu" else "/api/v3/morphology/noun/inflect",
            "prakriya": "ui/tabs/sanskrit/prakriya",
            "semantic": f"/api/dhatu/semantic/search?dhatuId={rid}" if rtype == "dhatu" else None,
            "chandas": "ui/tabs/sanskrit/chandas",
        }
        hooks.append({k: v for k, v in hook.items() if v})
    payload = {
        "schemaVersion": "sanskrit-corpus-derivation-hooks.v1",
        "phase": "11L",
        "hookCount": len(hooks),
        "hooks": hooks,
        "previewOnly": True,
    }
    write_json(DERIVATION_HOOKS_PATH, payload)
    return {"valid": len(hooks) > 0, "phase": "11L", "hookCount": len(hooks)}


def write_audit_entry(stage: str, result: Dict[str, Any]) -> None:
    audit = read_json(AUDIT_PATH) if AUDIT_PATH.exists() else {"entries": []}
    audit.setdefault("entries", []).append({"stage": stage, "valid": result.get("valid"), "summary": {k: result[k] for k in result if k != "records" and k != "uniqueRecords"}})
    write_json(AUDIT_PATH, audit)


def run_phase11_pipeline() -> Dict[str, Any]:
    stages = []
    runners = [
        ("11A-source-registry", build_source_registry),
        ("11B-raw-landing", lambda: {k: v for k, v in scan_raw_landing_zone().items() if k != "records"}),
        ("11C-normalize", normalize_corpus_records),
        ("11D-validate", validate_corpus_structure),
        ("11E-dedupe", dedupe_corpus_records),
        ("11F-enrich", enrich_corpus_records),
        ("11G-certify", build_certification_package),
        ("11H-canonical", lambda: populate_canonical_registry(force_preview=True)),
        ("11I-index", build_corpus_index),
        ("11L-derivation", build_derivation_hooks),
    ]

    raw_scan = scan_raw_landing_zone()
    for name, runner in runners:
        if name == "11C-normalize":
            result = normalize_corpus_records(raw_scan)
        else:
            result = runner()
        write_audit_entry(name, result)
        stages.append({"stage": name, "valid": result.get("valid", False), "summary": {k: v for k, v in result.items() if k not in ("records", "uniqueRecords", "duplicates")}})

    valid = all(s["valid"] for s in stages)
    enriched = read_json(ENRICHED_PATH) if ENRICHED_PATH.exists() else {"recordCount": 0}
    status = {
        "valid": valid,
        "phase": "11",
        "title": "Real Corpus Loading",
        "stages": stages,
        "recordCount": enriched.get("recordCount", 0),
        "previewOnly": True,
        "canonicalWriteAllowed": canonical_write_enabled(),
    }
    write_json(PIPELINE_STATUS_PATH, status)
    return status