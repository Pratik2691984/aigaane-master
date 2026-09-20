from pathlib import Path
from typing import Any, Dict, Optional
import copy
import json

try:
    from api.engines.dhatu_registry import load_all_dhatus
    from api.engines.dhatu_semantic_overlay import get_semantics_for_dhatu, load_semantic_overlay
    from api.engines.sutra_trace_canonicalizer import canonicalize_trace
except ModuleNotFoundError:
    from engines.dhatu_registry import load_all_dhatus
    from engines.dhatu_semantic_overlay import get_semantics_for_dhatu, load_semantic_overlay
    from engines.sutra_trace_canonicalizer import canonicalize_trace


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DHATU_ROOT = ROOT / "data" / "sanskrit" / "dhatus"
DEFAULT_GOLDSET_METADATA = ROOT / "data" / "sanskrit" / "goldset" / "goldset_metadata.v1.json"
DEFAULT_SEMANTIC_OVERLAY = ROOT / "data" / "sanskrit" / "goldset" / "semantic_enrichment.v1.json"
DEFAULT_PRAKRIYA_REFS = ROOT / "data" / "sanskrit" / "goldset" / "expected_prakriya_refs.v1.json"

PERSON_ROW_LABELS = {0: "3", 1: "2", 2: "1"}
NUMBER_COL_LABELS = {0: "S", 1: "D", 2: "P"}
PADA_REF_LABELS = {
    "parasmaipada": "PARASMAI",
    "atmanepada": "ATMANE",
}


def load_referee_context(
    dhatu_root: Any = DEFAULT_DHATU_ROOT,
    goldset_metadata_path: Any = DEFAULT_GOLDSET_METADATA,
    semantic_overlay_path: Any = DEFAULT_SEMANTIC_OVERLAY,
    prakriya_refs_path: Any = DEFAULT_PRAKRIYA_REFS,
) -> Dict[str, Any]:
    records = load_all_dhatus(dhatu_root)
    goldset_metadata = _load_json(goldset_metadata_path)
    semantic_payload = load_semantic_overlay(semantic_overlay_path)
    prakriya_refs = _load_json(prakriya_refs_path)
    return {
        "registryRecords": {record["id"]: copy.deepcopy(record) for record in records},
        "goldsetIds": list(goldset_metadata.get("records", [])),
        "semanticPayload": semantic_payload,
        "prakriyaRefs": prakriya_refs,
    }


def resolve_prakriya_query(context: Dict[str, Any], query: Dict[str, Any]) -> Dict[str, Any]:
    normalized_query = validate_referee_query(query)
    dhatu_id = normalized_query["dhatuId"]
    records = context.get("registryRecords", {})
    record = records.get(dhatu_id) if isinstance(records, dict) else None

    if record is None:
        result = _base_result("missing-record", dhatu_id, None, normalized_query)
        result["notes"].append(f"Dhatu record not found: {dhatu_id}.")
        return _attach_context(result, context)

    target_form = get_target_form(
        record,
        normalized_query["prayoga"],
        normalized_query["pada"],
        normalized_query["lakara"],
        normalized_query["personRow"],
        normalized_query["numberCol"],
    )
    status = "ok" if target_form else "missing-form"
    result = _base_result(status, dhatu_id, record, normalized_query)
    result["targetForm"] = target_form
    result["registryRecordFound"] = True
    result["prakriyaRef"] = build_prakriya_ref_id(normalized_query)
    result["confidence"]["formFound"] = target_form is not None

    ref_payload = _lookup_prakriya_ref(context.get("prakriyaRefs", {}), result["prakriyaRef"])
    if ref_payload:
        canonical_ref = canonicalize_trace(ref_payload)
        result["sutraTrace"] = copy.deepcopy(canonical_ref["sutraTrace"])
        result["canonicalTrace"] = canonical_ref
        result["canonicalized"] = canonical_ref["canonicalized"]
        result["traceVersion"] = canonical_ref["traceVersion"]
        result["confidence"]["traceCompleteness"] = canonical_ref["traceCompleteness"]
    else:
        result["confidence"]["traceCompleteness"] = "stub"
        result["notes"].append("No canonical prakriya trace is available yet; returning deterministic stub.")

    if status == "missing-form":
        result["notes"].append(explain_missing_form(normalized_query, record))

    return _attach_context(result, context)


def get_target_form(record: Dict[str, Any], prayoga: str, pada: str, lakara: str, row: int, col: int) -> Optional[str]:
    validate_referee_query(
        {
            "dhatuId": record.get("id", "00.0000"),
            "lakara": lakara,
            "pada": pada,
            "prayoga": prayoga,
            "personRow": row,
            "numberCol": col,
        }
    )
    forms = record.get("forms", {}) if isinstance(record, dict) else {}
    matrix = forms.get(prayoga, {}).get(lakara, {}).get(pada) if isinstance(forms, dict) else None
    if not isinstance(matrix, list):
        return None
    try:
        value = matrix[row][col]
    except (IndexError, TypeError):
        return None
    return value if isinstance(value, str) and value else None


def build_prakriya_ref_id(query: Dict[str, Any]) -> str:
    normalized_query = validate_referee_query(query)
    dhatu_part = normalized_query["dhatuId"].replace(".", "_")
    lakara = normalized_query["lakara"].upper()
    prayoga = normalized_query["prayoga"].upper()
    pada = PADA_REF_LABELS.get(normalized_query["pada"], normalized_query["pada"].upper())
    person = PERSON_ROW_LABELS[normalized_query["personRow"]]
    number = NUMBER_COL_LABELS[normalized_query["numberCol"]]
    return f"PR_{dhatu_part}_{lakara}_{prayoga}_{pada}_{person}{number}"


def attach_semantic_overlay(result: Dict[str, Any], semantic_payload: Dict[str, Any]) -> Dict[str, Any]:
    enriched = copy.deepcopy(result)
    semantics = get_semantics_for_dhatu(semantic_payload, enriched.get("dhatuId"))
    enriched["semanticOverlayFound"] = semantics is not None
    enriched["semanticDomains"] = copy.deepcopy(semantics.get("semanticDomains", [])) if semantics else []
    enriched["confidence"]["semanticBacked"] = semantics is not None
    return enriched


def attach_goldset_status(result: Dict[str, Any], goldset_ids: Any) -> Dict[str, Any]:
    enriched = copy.deepcopy(result)
    goldset = set(goldset_ids) if isinstance(goldset_ids, list) else set()
    enriched["goldsetRecord"] = enriched.get("dhatuId") in goldset
    enriched["confidence"]["goldsetBacked"] = enriched["goldsetRecord"]
    return enriched


def validate_referee_query(query: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(query, dict):
        raise ValueError("Referee query must be a dict.")
    required = ["dhatuId", "lakara", "pada", "prayoga", "personRow", "numberCol"]
    missing = [field for field in required if field not in query]
    if missing:
        raise ValueError(f"Referee query missing fields: {', '.join(missing)}.")
    for field in ("dhatuId", "lakara", "pada", "prayoga"):
        if not isinstance(query[field], str) or not query[field]:
            raise ValueError(f"Referee query {field} must be a non-empty string.")
    row = query["personRow"]
    col = query["numberCol"]
    if not isinstance(row, int) or row not in PERSON_ROW_LABELS:
        raise ValueError("personRow must be 0, 1, or 2.")
    if not isinstance(col, int) or col not in NUMBER_COL_LABELS:
        raise ValueError("numberCol must be 0, 1, or 2.")
    return {
        "dhatuId": query["dhatuId"],
        "lakara": query["lakara"],
        "pada": query["pada"],
        "prayoga": query["prayoga"],
        "personRow": row,
        "numberCol": col,
    }


def explain_missing_form(query: Dict[str, Any], record: Dict[str, Any]) -> str:
    identity = record.get("identity", {}) if isinstance(record, dict) else {}
    root = identity.get("root", query.get("dhatuId"))
    return (
        f"No compact matrix form is available for {root} "
        f"{query['lakara']} {query['prayoga']} {query['pada']} "
        f"row={query['personRow']} col={query['numberCol']}."
    )


def _base_result(status: str, dhatu_id: str, record: Optional[Dict[str, Any]], query: Dict[str, Any]) -> Dict[str, Any]:
    identity = record.get("identity", {}) if isinstance(record, dict) else {}
    return {
        "status": status,
        "dhatuId": dhatu_id,
        "root": identity.get("root"),
        "targetForm": None,
        "query": {
            "lakara": query["lakara"],
            "pada": query["pada"],
            "prayoga": query["prayoga"],
            "personRow": query["personRow"],
            "numberCol": query["numberCol"],
        },
        "registryRecordFound": record is not None,
        "goldsetRecord": False,
        "semanticOverlayFound": False,
        "semanticDomains": [],
        "prakriyaRef": build_prakriya_ref_id(query),
        "sutraTrace": [],
        "canonicalTrace": None,
        "canonicalized": False,
        "traceVersion": None,
        "confidence": {
            "formFound": False,
            "goldsetBacked": False,
            "semanticBacked": False,
            "traceCompleteness": "stub",
        },
        "notes": [],
    }


def _attach_context(result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    with_goldset = attach_goldset_status(result, context.get("goldsetIds", []))
    return attach_semantic_overlay(with_goldset, context.get("semanticPayload", {}))


def _lookup_prakriya_ref(prakriya_refs: Dict[str, Any], ref_id: str) -> Optional[Dict[str, Any]]:
    records = prakriya_refs.get("records") if isinstance(prakriya_refs, dict) else None
    if not isinstance(records, dict):
        return None
    ref = records.get(ref_id)
    return copy.deepcopy(ref) if isinstance(ref, dict) else None


def _load_json(path: Any) -> Dict[str, Any]:
    json_path = Path(path)
    with json_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {json_path}")
    return payload
