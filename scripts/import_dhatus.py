#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from engines.dhatu_registry import build_dhatu_index, validate_dhatu_record, validate_lakara_matrix


DHATU_ID_PATTERN = r"^[0-9]{2}\.[0-9]{4}$"
SUTRA_ID_PATTERN = r"^\d+\.\d+\.\d+$"
TING_ENDINGS = [
    "ति",
    "ते",
    "सि",
    "से",
    "तु",
    "ताम्",
    "न्तु",
    "त",
    "तम्",
    "मि",
    "वः",
    "मः",
    "यते",
    "येते",
    "न्ते",
]

MATRIX_FIELDS = {
    "lat_kartari_parasmaipada": ("kartari", "lat", "parasmaipada"),
    "lot_kartari_parasmaipada": ("kartari", "lot", "parasmaipada"),
    "lat_kartari_atmanepada": ("kartari", "lat", "atmanepada"),
    "lot_kartari_atmanepada": ("kartari", "lot", "atmanepada"),
    "lat_bhavaKarmani_atmanepada": ("bhavaKarmani", "lat", "atmanepada"),
}

DERIVATION_FIELDS = {
    "sananta_base": "sananta",
    "nijanta_base": "nijanta",
    "yanganta_base": "yanganta",
}

GANA_MAP = {
    "01": ("bhvadi", "01_bhvadi.json", "भ्वादिगणः"),
    "02": ("adadi", "02_adadi.json", "अदादिगणः"),
    "03": ("juhotyadi", "03_juhotyadi.json", "जुहोत्यादिगणः"),
    "04": ("divadi", "04_divadi.json", "दिवादिगणः"),
    "05": ("svadi", "05_svadi.json", "स्वादिगणः"),
    "06": ("tudadi", "06_tudadi.json", "तुदादिगणः"),
    "07": ("rudhadi", "07_rudhadi.json", "रुधादिगणः"),
    "08": ("tanadi", "08_tanadi.json", "तनादिगणः"),
    "09": ("kryadi", "09_kryadi.json", "क्र्यादिगणः"),
    "10": ("curadi", "10_curadi.json", "चुरादिगणः"),
}


@dataclass
class ImportErrorItem:
    line: int
    message: str
    row: Dict[str, Any]


@dataclass
class ImportResult:
    parsed: int = 0
    valid: int = 0
    errors: List[ImportErrorItem] = field(default_factory=list)
    skipped_duplicates: int = 0
    replaced_duplicates: int = 0
    written_files: List[str] = field(default_factory=list)
    index_rebuilt: bool = False
    dry_run: bool = True


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import raw dhatu rows into canonical Aigaane dhatu JSON.")
    parser.add_argument("--input", required=True, help="CSV or JSONL input path.")
    parser.add_argument("--limit", type=int, default=None, help="Maximum source rows to read.")
    parser.add_argument("--write", action="store_true", help="Write canonical dhatu files. Default is dry-run.")
    parser.add_argument("--strict", action="store_true", help="Stop on first row error.")
    parser.add_argument("--force", action="store_true", help="Replace existing curated records with matching ids.")
    parser.add_argument("--output-dir", default=str(ROOT / "data" / "sanskrit" / "dhatus"))
    parser.add_argument("--schema", default=str(ROOT / "data" / "sanskrit" / "schemas" / "dhatu.schema.v2.json"))
    return parser.parse_args(argv)


def iter_source_rows(input_path: Any, limit: Optional[int] = None) -> Iterable[Tuple[int, Dict[str, Any]]]:
    path = Path(input_path)
    suffix = path.suffix.lower()
    count = 0
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for line_number, row in enumerate(reader, start=2):
                if limit is not None and count >= limit:
                    break
                count += 1
                yield line_number, {key: _clean(value) for key, value in row.items()}
        return

    if suffix in {".jsonl", ".ndjson"}:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if limit is not None and count >= limit:
                    break
                if not line.strip():
                    continue
                count += 1
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"JSONL line {line_number} must be an object.")
                yield line_number, {key: _clean(raw_value) for key, raw_value in value.items()}
        return

    raise ValueError("Input must be a CSV or JSONL file.")


def normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    dhatu_id = _required(row, "id")
    gana_id = _required(row, "gana_id")
    if gana_id not in GANA_MAP:
        raise ValueError(f"Unsupported gana_id: {gana_id}.")
    slug, _filename, gana_name = GANA_MAP[gana_id]

    forms: Dict[str, Any] = {}
    for raw_field, path in MATRIX_FIELDS.items():
        raw_value = row.get(raw_field)
        if raw_value:
            matrix = parse_matrix(raw_value)
            validate_lakara_matrix(matrix)
            _set_nested(forms, path, matrix)

    derivations = []
    for raw_field, derivation_type in DERIVATION_FIELDS.items():
        base = row.get(raw_field)
        if base:
            ensure_stem_only(base)
            derivations.append({"type": derivation_type, "base": base})

    default_pada = row.get("defaultPada") or ""
    allowed_padas = _split_list(row.get("allowedPadas") or default_pada)
    has_parasmaipada = "parasmaipada" in allowed_padas or _has_form(forms, "parasmaipada")
    has_atmanepada = "atmanepada" in allowed_padas or _has_form(forms, "atmanepada")
    is_ubhayapada = default_pada == "ubhayapada" or (has_parasmaipada and has_atmanepada)

    rule_triggers = _split_list(row.get("ruleTriggers") or row.get("pada_ruleTriggers"))
    for sutra_id in rule_triggers:
        if not _matches(SUTRA_ID_PATTERN, sutra_id):
            raise ValueError(f"Invalid rule trigger sutra id: {sutra_id}.")

    record = {
        "schema": "aigaane.dhatu.v2",
        "version": "20B.import.1",
        "id": dhatu_id,
        "identity": {
            "upadesha": row.get("upadesha") or row.get("root") or "",
            "root": _required(row, "root"),
            "rootIast": row.get("romanized") or "",
            "canonicalForm": _required(row, "canonicalForm"),
        },
        "grammar": {
            "gana": {"id": gana_id, "slug": slug, "name": gana_name},
            "itStatus": row.get("itStatus") or "",
            "karmatva": row.get("karmatva") or "",
            "primaryPada": default_pada,
        },
        "semantics": {
            "sanskrit": row.get("semantics_sanskrit") or "",
            "english": row.get("semantics_english") or "",
        },
        "padaProfile": {
            "primary": default_pada,
            "isUbhayapada": is_ubhayapada,
            "ruleTriggers": rule_triggers,
        },
        "forms": forms,
        "derivations": derivations,
        "upasargaVariants": [{"upasarga": item} for item in _split_list(row.get("upasarga_list"))],
        "prakriyaRefs": [],
        "sources": [
            {
                "name": "Ashtadhyayi dhatu reference",
                "type": "scholarly",
                "citation": f"https://ashtadhyayi.com/dhatu/{dhatu_id}",
                "ashtadhyayi": f"https://ashtadhyayi.com/dhatu/{dhatu_id}",
                "license": "external-reference",
            }
        ],
        "tags": _tags("dhatu", slug, row.get("itStatus"), row.get("karmatva"), default_pada),
    }

    validate_import_record(record)
    return record


def parse_matrix(raw_value: Any) -> List[List[str]]:
    if isinstance(raw_value, list):
        cells = raw_value
    else:
        cells = [item.strip() for item in str(raw_value).split(",")]
    if len(cells) != 9:
        raise ValueError("Lakara matrix fields must contain exactly 9 comma-separated forms.")
    if any(not isinstance(cell, str) or not cell for cell in cells):
        raise ValueError("Lakara matrix cells must be non-empty strings.")
    return [cells[0:3], cells[3:6], cells[6:9]]


def ensure_stem_only(base: str) -> None:
    if any(base.endswith(ending) for ending in TING_ENDINGS):
        raise ValueError(f"Derivation base must be stem-only, not a finite tiṅ form: {base}.")


def validate_import_record(record: Dict[str, Any]) -> Dict[str, Any]:
    if not _matches(DHATU_ID_PATTERN, record.get("id", "")):
        raise ValueError("Dhatu id must match GG.NNNN.")
    expected_gana_id = record["id"].split(".", 1)[0]
    if record["grammar"]["gana"]["id"] != expected_gana_id:
        raise ValueError(f"grammar.gana.id must match target file prefix {expected_gana_id}.")
    for matrix in _iter_matrices(record.get("forms", {})):
        validate_lakara_matrix(matrix)
        for row in matrix:
            for cell in row:
                if not isinstance(cell, str):
                    raise ValueError("Every matrix cell must be a string.")
    for sutra_id in record.get("padaProfile", {}).get("ruleTriggers", []):
        if not _matches(SUTRA_ID_PATTERN, sutra_id):
            raise ValueError(f"Invalid rule trigger sutra id: {sutra_id}.")
    for derivation in record.get("derivations", []):
        ensure_stem_only(derivation.get("base", ""))
    return validate_dhatu_record(record, expected_gana_id=expected_gana_id)


def import_dhatus(
    input_path: Any,
    output_dir: Any,
    schema_path: Any,
    limit: Optional[int] = None,
    write: bool = False,
    strict: bool = False,
    force: bool = False,
) -> ImportResult:
    schema_file = Path(schema_path)
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema not found: {schema_file}")

    result = ImportResult(dry_run=not write)
    records_by_gana: Dict[str, List[Dict[str, Any]]] = {}
    for line_number, row in iter_source_rows(input_path, limit=limit):
        result.parsed += 1
        try:
            record = normalize_row(row)
            result.valid += 1
            gana_id = record["grammar"]["gana"]["id"]
            records_by_gana.setdefault(gana_id, []).append(record)
        except Exception as exc:
            result.errors.append(ImportErrorItem(line=line_number, message=str(exc), row=row))
            if strict:
                raise

    if write and records_by_gana:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        for gana_id, new_records in sorted(records_by_gana.items()):
            written, skipped, replaced = merge_and_write_gana_file(output_path, gana_id, new_records, force=force)
            result.skipped_duplicates += skipped
            result.replaced_duplicates += replaced
            if written:
                result.written_files.append(str(written))
        rebuild_index(output_path)
        result.index_rebuilt = True
        write_logs(output_path, result)

    return result


def merge_and_write_gana_file(output_dir: Path, gana_id: str, new_records: List[Dict[str, Any]], force: bool = False) -> Tuple[Optional[Path], int, int]:
    slug, filename, gana_name = GANA_MAP[gana_id]
    path = output_dir / filename
    existing_payload = _load_gana_payload(path, gana_id, slug, gana_name)
    existing_records = existing_payload.get("records", [])
    merged = {record["id"]: record for record in existing_records}
    skipped = 0
    replaced = 0
    changed = False

    for record in new_records:
        validate_import_record(record)
        if record["id"] in merged and not force:
            skipped += 1
            continue
        if record["id"] in merged and force:
            replaced += 1
        merged[record["id"]] = record
        changed = True

    if not changed:
        return None, skipped, replaced

    final_records = [merged[key] for key in sorted(merged)]
    for record in final_records:
        validate_dhatu_record(record, expected_gana_id=gana_id)
    payload = {
        "schema": "aigaane.dhatu_file.v1",
        "version": "20B.import.1",
        "gana": {"id": gana_id, "slug": slug, "name": gana_name},
        "records": final_records,
    }
    _atomic_write_json(path, payload)
    return path, skipped, replaced


def rebuild_index(output_dir: Any) -> Path:
    output_path = Path(output_dir)
    all_records: List[Dict[str, Any]] = []
    for path in sorted(output_path.glob("*.json")):
        if path.name == "index.json":
            continue
        payload = _read_json(path)
        records = payload.get("records", []) if isinstance(payload, dict) else []
        for record in records:
            validate_dhatu_record(record, expected_gana_id=path.name.split("_", 1)[0])
            all_records.append(record)
    index = {
        "schema": "aigaane.dhatu_index.v1",
        "version": "20B.import.1",
        "records": build_dhatu_index(all_records),
    }
    index_path = output_path / "index.json"
    _atomic_write_json(index_path, index)
    return index_path


def write_logs(output_dir: Any, result: ImportResult) -> None:
    output_path = Path(output_dir)
    timestamp = datetime.now(timezone.utc).isoformat()
    log_path = output_path / "import.log"
    error_path = output_path / "import_errors.jsonl"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(
            f"{timestamp} parsed={result.parsed} valid={result.valid} errors={len(result.errors)} "
            f"skipped_duplicates={result.skipped_duplicates} replaced_duplicates={result.replaced_duplicates} "
            f"written_files={len(result.written_files)}\n"
        )
    if result.errors:
        with error_path.open("a", encoding="utf-8") as handle:
            for error in result.errors:
                handle.write(json.dumps(error.__dict__, ensure_ascii=False, sort_keys=True) + "\n")


def print_summary(result: ImportResult) -> None:
    mode = "dry-run" if result.dry_run else "write"
    print(
        f"Dhatu import {mode}: parsed={result.parsed} valid={result.valid} errors={len(result.errors)} "
        f"skipped_duplicates={result.skipped_duplicates} replaced_duplicates={result.replaced_duplicates} "
        f"written_files={len(result.written_files)} index_rebuilt={result.index_rebuilt}"
    )
    for error in result.errors:
        print(f"line {error.line}: {error.message}", file=sys.stderr)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        result = import_dhatus(
            input_path=args.input,
            output_dir=args.output_dir,
            schema_path=args.schema,
            limit=args.limit,
            write=args.write,
            strict=args.strict,
            force=args.force,
        )
        print_summary(result)
        return 1 if result.errors and args.strict else 0
    except Exception as exc:
        print(f"Dhatu import failed: {exc}", file=sys.stderr)
        return 1


def _load_gana_payload(path: Path, gana_id: str, slug: str, gana_name: str) -> Dict[str, Any]:
    if path.exists():
        payload = _read_json(path)
        if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
            raise ValueError(f"Malformed dhatu gana file: {path}")
        return payload
    return {
        "schema": "aigaane.dhatu_file.v1",
        "version": "20B.import.1",
        "gana": {"id": gana_id, "slug": slug, "name": gana_name},
        "records": [],
    }


def _atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    if path.exists():
        shutil.copystat(path, tmp_path, follow_symlinks=False)
    tmp_path.replace(path)


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _clean(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return value


def _required(row: Dict[str, Any], key: str) -> str:
    value = row.get(key)
    if not value:
        raise ValueError(f"Missing required raw field: {key}.")
    return str(value)


def _set_nested(target: Dict[str, Any], path: Tuple[str, str, str], value: Any) -> None:
    current = target
    for key in path[:-1]:
        current = current.setdefault(key, {})
    current[path[-1]] = value


def _split_list(value: Any) -> List[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value)
    separator = ";" if ";" in text else "|"
    if separator not in text and "," in text:
        separator = ","
    return [item.strip() for item in text.split(separator) if item.strip()]


def _tags(*values: Any) -> List[str]:
    tags = []
    for value in values:
        if value:
            tags.append(str(value))
    return sorted(set(tags))


def _has_form(forms: Dict[str, Any], pada: str) -> bool:
    if isinstance(forms, dict):
        return any(key == pada or _has_form(value, pada) for key, value in forms.items())
    return False


def _iter_matrices(value: Any) -> List[Any]:
    matrices = []
    if isinstance(value, dict):
        for child in value.values():
            matrices.extend(_iter_matrices(child))
    elif isinstance(value, list):
        if len(value) == 3 and all(isinstance(row, list) for row in value):
            matrices.append(value)
        else:
            for child in value:
                matrices.extend(_iter_matrices(child))
    return matrices


def _matches(pattern: str, value: str) -> bool:
    import re

    return bool(re.match(pattern, value))


if __name__ == "__main__":
    raise SystemExit(main())
