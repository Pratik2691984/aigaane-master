from pathlib import Path
from typing import Any, Dict, List, Optional
import copy
import json

try:
    from api.engines.dhatu_registry import load_all_dhatus
    from api.engines.dhatu_semantic_overlay import load_semantic_overlay
except ModuleNotFoundError:
    from engines.dhatu_registry import load_all_dhatus
    from engines.dhatu_semantic_overlay import load_semantic_overlay


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DHATU_ROOT = ROOT / "data" / "sanskrit" / "dhatus"
DEFAULT_SEMANTIC_OVERLAY = ROOT / "data" / "sanskrit" / "goldset" / "semantic_enrichment.v1.json"
DEFAULT_PRAKRIYA_REFS = ROOT / "data" / "sanskrit" / "goldset" / "expected_prakriya_refs.v1.json"


def load_query_context(
    dhatu_root: Any = DEFAULT_DHATU_ROOT,
    semantic_overlay_path: Any = DEFAULT_SEMANTIC_OVERLAY,
    prakriya_refs_path: Any = DEFAULT_PRAKRIYA_REFS,
) -> Dict[str, Any]:
    return {
        "records": load_all_dhatus(dhatu_root),
        "semanticOverlay": load_semantic_overlay(semantic_overlay_path) if Path(semantic_overlay_path).exists() else None,
        "prakriyaRefs": _load_json(prakriya_refs_path) if Path(prakriya_refs_path).exists() else None,
    }


def build_query_index(
    records: List[Dict[str, Any]],
    semantic_overlay: Optional[Dict[str, Any]] = None,
    prakriya_refs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not isinstance(records, list):
        raise ValueError("records must be a list.")
    semantic_records = semantic_overlay.get("records", {}) if isinstance(semantic_overlay, dict) else {}
    trace_index = _trace_completeness_by_dhatu(prakriya_refs)

    items = []
    for record in records:
        if not isinstance(record, dict):
            continue
        dhatu_id = record["id"]
        identity = record.get("identity", {})
        grammar = record.get("grammar", {})
        gana = grammar.get("gana", {})
        pada_profile = record.get("padaProfile", {})
        semantics = semantic_records.get(dhatu_id, {}) if isinstance(semantic_records, dict) else {}
        item = {
            "dhatuId": dhatu_id,
            "root": identity.get("root"),
            "canonicalForm": identity.get("canonicalForm"),
            "gana": {
                "id": gana.get("id"),
                "slug": gana.get("slug"),
            },
            "defaultPada": grammar.get("primaryPada") or pada_profile.get("primary"),
            "karmatva": grammar.get("karmatva"),
            "semanticDomains": copy.deepcopy(semantics.get("semanticDomains", [])) if isinstance(semantics, dict) else [],
            "actionType": semantics.get("actionType") if isinstance(semantics, dict) else None,
            "ruleTriggers": copy.deepcopy(pada_profile.get("ruleTriggers", [])) if isinstance(pada_profile, dict) else [],
            "traceCompleteness": trace_index.get(dhatu_id, "missing"),
            "tags": copy.deepcopy(record.get("tags", [])),
            "record": copy.deepcopy(record),
        }
        items.append(item)

    items.sort(key=lambda item: item["dhatuId"])
    return {"items": items}


def query_by_semantic_domain(index: Dict[str, Any], domain: Any) -> List[Dict[str, Any]]:
    needle = normalize_query_value(domain)
    return _filter_items(index, lambda item: needle in {normalize_query_value(value) for value in item.get("semanticDomains", [])})


def query_by_gana(index: Dict[str, Any], gana: Any) -> List[Dict[str, Any]]:
    needle = normalize_query_value(gana)
    return _filter_items(
        index,
        lambda item: needle in {normalize_query_value(item.get("gana", {}).get("id")), normalize_query_value(item.get("gana", {}).get("slug"))},
    )


def query_by_pada(index: Dict[str, Any], pada: Any) -> List[Dict[str, Any]]:
    needle = normalize_query_value(pada)
    return _filter_items(index, lambda item: normalize_query_value(item.get("defaultPada")) == needle)


def query_by_karmatva(index: Dict[str, Any], karmatva: Any) -> List[Dict[str, Any]]:
    needle = normalize_query_value(karmatva)
    return _filter_items(index, lambda item: normalize_query_value(item.get("karmatva")) == needle)


def query_by_rule_trigger(index: Dict[str, Any], sutra_id: Any) -> List[Dict[str, Any]]:
    needle = normalize_query_value(sutra_id)
    return _filter_items(index, lambda item: needle in {normalize_query_value(value) for value in item.get("ruleTriggers", [])})


def query_by_trace_completeness(index: Dict[str, Any], completeness: Any) -> List[Dict[str, Any]]:
    needle = normalize_query_value(completeness)
    return _filter_items(index, lambda item: normalize_query_value(item.get("traceCompleteness")) == needle)


def query_by_action_type(index: Dict[str, Any], action_type: Any) -> List[Dict[str, Any]]:
    needle = normalize_query_value(action_type)
    return _filter_items(index, lambda item: normalize_query_value(item.get("actionType")) == needle)


def query_by_root(index: Dict[str, Any], root: Any) -> List[Dict[str, Any]]:
    needle = str(root)
    return _filter_items(index, lambda item: item.get("root") == needle)


def query_by_tag(index: Dict[str, Any], tag: Any) -> List[Dict[str, Any]]:
    needle = normalize_query_value(tag)
    return _filter_items(index, lambda item: needle in {normalize_query_value(value) for value in item.get("tags", [])})


def combined_query(index: Dict[str, Any], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(filters, dict):
        raise ValueError("filters must be a dict.")
    results = _items(index)
    filter_functions = [
        ("semanticDomain", query_by_semantic_domain),
        ("gana", query_by_gana),
        ("pada", query_by_pada),
        ("karmatva", query_by_karmatva),
        ("ruleTrigger", query_by_rule_trigger),
        ("traceCompleteness", query_by_trace_completeness),
        ("actionType", query_by_action_type),
        ("root", query_by_root),
        ("tag", query_by_tag),
    ]
    for key, query_function in filter_functions:
        value = filters.get(key)
        if value is None or value == "":
            continue
        allowed = {item["dhatuId"] for item in query_function({"items": results}, value)}
        results = [item for item in results if item["dhatuId"] in allowed]
    return [_public_item(item) for item in sorted(results, key=lambda item: item["dhatuId"])]


def normalize_query_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def summarize_query_index(index: Dict[str, Any]) -> Dict[str, int]:
    items = _items(index)
    domains = {domain for item in items for domain in item.get("semanticDomains", [])}
    ganas = {item.get("gana", {}).get("id") for item in items if item.get("gana", {}).get("id")}
    return {
        "recordCount": len(items),
        "domainCount": len(domains),
        "ganaCount": len(ganas),
    }


def _filter_items(index: Dict[str, Any], predicate) -> List[Dict[str, Any]]:
    return [_public_item(item) for item in _items(index) if predicate(item)]


def _items(index: Dict[str, Any]) -> List[Dict[str, Any]]:
    items = index.get("items", []) if isinstance(index, dict) else []
    return [copy.deepcopy(item) for item in items if isinstance(item, dict)]


def _public_item(item: Dict[str, Any]) -> Dict[str, Any]:
    public = copy.deepcopy(item)
    public.pop("record", None)
    return public


def _trace_completeness_by_dhatu(prakriya_refs: Optional[Dict[str, Any]]) -> Dict[str, str]:
    records = prakriya_refs.get("records", {}) if isinstance(prakriya_refs, dict) else {}
    if not isinstance(records, dict):
        return {}
    completeness_by_dhatu = {}
    for ref in records.values():
        if not isinstance(ref, dict):
            continue
        dhatu_id = ref.get("dhatuId")
        if dhatu_id:
            completeness_by_dhatu[dhatu_id] = ref.get("traceCompleteness", "missing")
    return completeness_by_dhatu


def _load_json(path: Any) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload
