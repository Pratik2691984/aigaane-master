from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "data" / "sanskrit" / "index" / "corpus_index.v1.json"
CANONICAL_ROOT = ROOT / "data" / "sanskrit" / "canonical"


def _load_index() -> Dict[str, Any]:
    if not INDEX_PATH.exists():
        return {"lookup": {}, "prefixIndex": {}, "phoneticIndex": {}, "semanticIndex": {}}
    with INDEX_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_canonical(corpus_type: str) -> Dict[str, Any]:
    path = CANONICAL_ROOT / corpus_type / f"{corpus_type}_registry.v1.json"
    if not path.exists():
        return {"records": []}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _normalize_query(value: Optional[str]) -> str:
    return str(value or "").strip().casefold()


def search_corpus(query: Optional[str] = None, corpus_type: Optional[str] = None, limit: int = 25) -> Dict[str, Any]:
    index = _load_index()
    lookup = index.get("lookup", {})
    q = _normalize_query(query)
    results: List[Dict[str, Any]] = []

    if not q:
        for rid, item in list(lookup.items())[:limit]:
            if corpus_type and item.get("type") != corpus_type:
                continue
            results.append({"recordId": rid, **item})
    else:
        matched_ids = set()
        for bucket in (index.get("prefixIndex", {}), index.get("phoneticIndex", {}), index.get("semanticIndex", {})):
            for key, ids in bucket.items():
                if q in key.casefold():
                    matched_ids.update(ids)
        for rid in matched_ids:
            item = lookup.get(rid)
            if not item:
                continue
            if corpus_type and item.get("type") != corpus_type:
                continue
            results.append({"recordId": rid, **item})
            if len(results) >= limit:
                break

    return {
        "valid": True,
        "query": query or "",
        "corpusType": corpus_type,
        "count": len(results),
        "results": results[:limit],
        "generatedBy": "api/sanskrit_corpus_api.py:/api/sanskrit/search",
        "previewOnly": True,
        "readOnly": True,
    }


def get_corpus_by_type(corpus_type: str, record_id: Optional[str] = None, limit: int = 25) -> Dict[str, Any]:
    payload = _load_canonical(corpus_type)
    records = payload.get("records", [])
    if record_id:
        records = [r for r in records if r.get("id") == record_id]
    return {
        "valid": True,
        "corpusType": corpus_type,
        "count": len(records[:limit]),
        "records": records[:limit],
        "readOnly": True,
        "previewOnly": True,
        "generatedBy": f"api/sanskrit_corpus_api.py:/api/sanskrit/{corpus_type}",
    }


def build_sanskrit_corpus_index_response() -> Dict[str, Any]:
    index = _load_index()
    return {
        "valid": True,
        "recordCount": index.get("recordCount", len(index.get("lookup", {}))),
        "endpoints": [
            {"path": "/api/sanskrit/search", "method": "GET"},
            {"path": "/api/sanskrit/dhatu", "method": "GET"},
            {"path": "/api/sanskrit/sutra", "method": "GET"},
            {"path": "/api/sanskrit/stotra", "method": "GET"},
        ],
        "previewOnly": True,
        "readOnly": True,
    }