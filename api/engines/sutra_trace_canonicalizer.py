from typing import Any, Dict, List
import copy
import json
import re


TRACE_VERSION = "0.2.0"
VALID_COMPLETENESS = {"stub", "partial", "complete"}
SUTRA_ID_RE = re.compile(r"^\d+\.\d+\.\d+$")
STEP_ID_RE = re.compile(r"^STEP_\d{3}$")


def canonicalize_trace(trace: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(trace, dict):
        raise ValueError("Trace must be a dict.")
    trace_id = trace.get("traceId") or trace.get("prakriyaRef")
    if not isinstance(trace_id, str) or not trace_id:
        raise ValueError("traceId is required.")
    completeness = trace.get("traceCompleteness", "stub")
    if completeness not in VALID_COMPLETENESS:
        raise ValueError("traceCompleteness must be stub, partial, or complete.")

    raw_steps = trace.get("sutraTrace", [])
    if not isinstance(raw_steps, list):
        raise ValueError("sutraTrace must be a list.")
    sorted_steps = sort_trace_steps(raw_steps)
    canonical_steps = [canonicalize_step(step, index) for index, step in enumerate(sorted_steps, start=1)]

    return {
        "traceId": trace_id,
        "dhatuId": trace.get("dhatuId"),
        "targetForm": trace.get("targetForm"),
        "traceCompleteness": completeness,
        "sutraTrace": canonical_steps,
        "canonicalized": True,
        "traceVersion": TRACE_VERSION,
    }


def canonicalize_step(step: Dict[str, Any], index: int) -> Dict[str, Any]:
    if not isinstance(step, dict):
        raise ValueError("Trace step must be a dict.")
    seq = step.get("seq", index)
    if not isinstance(seq, int) or seq < 1:
        raise ValueError("Trace step seq must be a positive integer.")
    step_id = step.get("stepId") or build_step_id(index)
    if not validate_step_id(step_id):
        raise ValueError(f"Invalid stepId: {step_id}.")
    sutra = step.get("sutra")
    if sutra is not None and not validate_sutra_id(sutra):
        raise ValueError(f"Invalid sutra id: {sutra}.")
    confidence = step.get("confidence", "stub")
    if confidence not in VALID_COMPLETENESS:
        raise ValueError("Trace step confidence must be stub, partial, or complete.")
    notes = step.get("notes", [])
    if not isinstance(notes, list):
        raise ValueError("Trace step notes must be a list.")

    return {
        "stepId": step_id,
        "seq": seq,
        "sutra": sutra,
        "name": step.get("name"),
        "role": step.get("role"),
        "inputState": step.get("inputState"),
        "outputState": step.get("outputState"),
        "operation": step.get("operation"),
        "confidence": confidence,
        "notes": copy.deepcopy(notes),
    }


def canonicalize_trace_map(trace_map: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(trace_map, dict):
        raise ValueError("Trace map must be a dict.")
    records = trace_map.get("records", {})
    if not isinstance(records, dict):
        raise ValueError("Trace map records must be a dict.")
    canonical_records = {}
    for trace_id, trace in sorted(records.items()):
        payload = copy.deepcopy(trace)
        payload["traceId"] = payload.get("traceId") or trace_id
        canonical_records[trace_id] = canonicalize_trace(payload)
    return {
        "goldsetVersion": trace_map.get("goldsetVersion"),
        "traceVersion": TRACE_VERSION,
        "records": canonical_records,
    }


def validate_sutra_id(sutra_id: str) -> bool:
    return isinstance(sutra_id, str) and bool(SUTRA_ID_RE.match(sutra_id))


def validate_step_id(step_id: str) -> bool:
    return isinstance(step_id, str) and bool(STEP_ID_RE.match(step_id))


def build_step_id(index: int) -> str:
    if not isinstance(index, int) or index < 1:
        raise ValueError("Step index must be a positive integer.")
    return f"STEP_{index:03d}"


def sort_trace_steps(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not isinstance(steps, list):
        raise ValueError("Trace steps must be a list.")
    for step in steps:
        if not isinstance(step, dict):
            raise ValueError("Trace steps must be dicts.")
        seq = step.get("seq", 0)
        if seq is not None and (not isinstance(seq, int) or seq < 1):
            raise ValueError("Trace step seq must be a positive integer.")
    return sorted(copy.deepcopy(steps), key=lambda step: step.get("seq", 10**9))


def compare_canonical_traces(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    left = canonicalize_trace(a)
    right = canonicalize_trace(b)
    differences = []
    if left["traceId"] != right["traceId"]:
        differences.append({"field": "traceId", "a": left["traceId"], "b": right["traceId"]})
    if left["traceCompleteness"] != right["traceCompleteness"]:
        differences.append({"field": "traceCompleteness", "a": left["traceCompleteness"], "b": right["traceCompleteness"]})
    max_steps = max(len(left["sutraTrace"]), len(right["sutraTrace"]))
    for index in range(max_steps):
        if index >= len(left["sutraTrace"]):
            differences.append({"field": "sutraTrace", "index": index, "a": None, "b": right["sutraTrace"][index]})
            continue
        if index >= len(right["sutraTrace"]):
            differences.append({"field": "sutraTrace", "index": index, "a": left["sutraTrace"][index], "b": None})
            continue
        left_step = left["sutraTrace"][index]
        right_step = right["sutraTrace"][index]
        for field in ("seq", "sutra", "role", "operation", "inputState", "outputState"):
            if left_step.get(field) != right_step.get(field):
                differences.append({"field": field, "index": index, "a": left_step.get(field), "b": right_step.get(field)})
    return {"equal": len(differences) == 0, "differences": differences}


def summarize_trace(trace: Dict[str, Any]) -> Dict[str, Any]:
    canonical = canonicalize_trace(trace)
    sutras = {step.get("sutra") for step in canonical["sutraTrace"] if step.get("sutra")}
    return {
        "traceId": canonical["traceId"],
        "stepCount": len(canonical["sutraTrace"]),
        "sutraCount": len(sutras),
        "completeness": canonical["traceCompleteness"],
    }


def stable_trace_json(trace: Dict[str, Any]) -> str:
    return json.dumps(canonicalize_trace(trace), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
