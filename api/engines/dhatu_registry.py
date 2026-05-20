from pathlib import Path
from typing import Any, Dict, List, Optional
import copy
import json
import re


DHATU_ID_RE = re.compile(r"^[0-9]{2}\.[0-9]{4}$")
SUTRA_ID_RE = re.compile(r"^[1-8]\.[1-4]\.[0-9]+$")
OBVIOUS_TIN_ENDINGS = ("ति", "ते", "सि", "से")
REQUIRED_RECORD_FIELDS = {
    "schema",
    "version",
    "id",
    "identity",
    "grammar",
    "semantics",
    "padaProfile",
    "forms",
    "derivations",
    "upasargaVariants",
    "prakriyaRefs",
    "sources",
    "tags",
}


def load_dhatu_file(path: Any) -> List[Dict[str, Any]]:
    dhatu_path = Path(path)
    with dhatu_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict) and isinstance(payload.get("records"), list):
        records = payload["records"]
    else:
        raise ValueError("Dhatu file must contain a records array.")

    expected_gana_id = dhatu_path.name.split("_", 1)[0]
    validated = []
    for record in records:
        validate_dhatu_record(record, expected_gana_id=expected_gana_id)
        validated.append(copy.deepcopy(record))
    return validated


def load_all_dhatus(root_dir: Any) -> List[Dict[str, Any]]:
    root_path = Path(root_dir)
    records: List[Dict[str, Any]] = []
    for path in sorted(root_path.glob("*.json")):
        if path.name == "index.json":
            continue
        records.extend(load_dhatu_file(path))
    return records


def build_dhatu_index(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    if not isinstance(records, list):
        raise ValueError("records must be a list.")
    index: Dict[str, Dict[str, Any]] = {}
    for record in records:
        validate_dhatu_record(record)
        dhatu_id = record["id"]
        identity = record["identity"]
        gana = record["grammar"]["gana"]
        index[dhatu_id] = {
            "root": identity["root"],
            "canonicalForm": identity["canonicalForm"],
            "gana": {
                "slug": gana["slug"],
            },
        }
    return index


def validate_dhatu_record(record: Dict[str, Any], expected_gana_id: Optional[str] = None) -> Dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError("Dhatu record must be a dict.")

    missing = sorted(REQUIRED_RECORD_FIELDS - set(record.keys()))
    if missing:
        raise ValueError(f"Dhatu record missing required fields: {', '.join(missing)}.")

    dhatu_id = record.get("id")
    if not isinstance(dhatu_id, str) or not DHATU_ID_RE.match(dhatu_id):
        raise ValueError("Dhatu id must match GG.NNNN.")

    identity = record.get("identity")
    if not isinstance(identity, dict) or not identity.get("root") or not identity.get("canonicalForm"):
        raise ValueError("Dhatu identity must include root and canonicalForm.")

    grammar = record.get("grammar")
    gana = grammar.get("gana") if isinstance(grammar, dict) else None
    if not isinstance(gana, dict) or not isinstance(gana.get("id"), str):
        raise ValueError("Dhatu grammar.gana.id is required.")
    if expected_gana_id is not None and gana["id"] != expected_gana_id:
        raise ValueError(f"Dhatu grammar.gana.id must match file prefix {expected_gana_id}.")

    pada_profile = record.get("padaProfile")
    if not isinstance(pada_profile, dict):
        raise ValueError("padaProfile must be a dict.")
    for sutra_id in pada_profile.get("ruleTriggers", []):
        if not isinstance(sutra_id, str) or not SUTRA_ID_RE.match(sutra_id):
            raise ValueError(f"Invalid padaProfile rule trigger: {sutra_id}.")

    forms = record.get("forms")
    if not isinstance(forms, dict):
        raise ValueError("forms must be a dict.")
    for matrix in _iter_form_matrices(forms):
        validate_lakara_matrix(matrix)

    derivations = record.get("derivations")
    if not isinstance(derivations, list):
        raise ValueError("derivations must be a list.")
    for derivation in derivations:
        if not isinstance(derivation, dict) or not derivation.get("type") or not derivation.get("base"):
            raise ValueError("Each derivation must include type and base.")
        base = derivation["base"]
        if not isinstance(base, str):
            raise ValueError("Derivation base must be a string.")
        if base.endswith(OBVIOUS_TIN_ENDINGS):
            raise ValueError(f"Derivation base must be stem-only, not a finite form: {base}.")

    for field_name in ("upasargaVariants", "prakriyaRefs", "sources", "tags"):
        if not isinstance(record.get(field_name), list):
            raise ValueError(f"{field_name} must be a list.")

    return copy.deepcopy(record)


def validate_lakara_matrix(matrix: Any) -> List[List[str]]:
    if not isinstance(matrix, list) or len(matrix) != 3:
        raise ValueError("Lakara matrix must have exactly 3 rows.")
    for row in matrix:
        if not isinstance(row, list) or len(row) != 3:
            raise ValueError("Lakara matrix rows must have exactly 3 columns.")
        for form in row:
            if not isinstance(form, str) or not form:
                raise ValueError("Lakara matrix cells must be non-empty strings.")
    return copy.deepcopy(matrix)


def find_dhatu_by_id(records: List[Dict[str, Any]], dhatu_id: str) -> Optional[Dict[str, Any]]:
    for record in records:
        if isinstance(record, dict) and record.get("id") == dhatu_id:
            return copy.deepcopy(record)
    return None


def find_dhatus_by_root(records: List[Dict[str, Any]], root: str) -> List[Dict[str, Any]]:
    return [
        copy.deepcopy(record)
        for record in records
        if isinstance(record, dict) and isinstance(record.get("identity"), dict) and record["identity"].get("root") == root
    ]


def _iter_form_matrices(value: Any) -> List[Any]:
    matrices = []
    if isinstance(value, dict):
        for child in value.values():
            matrices.extend(_iter_form_matrices(child))
    elif isinstance(value, list):
        if len(value) == 3 and all(isinstance(row, list) for row in value):
            matrices.append(value)
        else:
            for child in value:
                matrices.extend(_iter_form_matrices(child))
    return matrices
