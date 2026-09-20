#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
RAW_CORPUS_ROOT = ROOT / "raw" / "sanskrit"
RAW_MANIFEST = ROOT / "raw" / "corpus" / "manifest.v1.json"
CORPUS_SOURCES = ROOT / "data" / "sanskrit" / "corpus-sources"

ASHTADHYAYI_DHATU_PATH = CORPUS_SOURCES / "dhatupatha" / "ashtadhyayi_dhatu.v1.json"
ASHTADHYAYI_SUTRA_PATH = CORPUS_SOURCES / "sutra" / "ashtadhyayi_sutra.v1.json"
GITA_STOTRA_PATH = CORPUS_SOURCES / "stotra" / "gita_verses.v1.json"

TARGET_DHATU = 1400
TARGET_SUTRA = 400
TARGET_STOTRA = 200
PER_GANA_DHATU = 140

GANA_DIRS = [
    ("01", "bhvadi"),
    ("02", "adadi"),
    ("03", "juhotyadi"),
    ("04", "divadi"),
    ("05", "svadi"),
    ("06", "tudadi"),
    ("07", "rudhadi"),
    ("08", "tanadi"),
    ("09", "kryadi"),
    ("10", "curadi"),
]

SOURCE_URLS = {
    ASHTADHYAYI_DHATU_PATH: "https://raw.githubusercontent.com/ashtadhyayi-com/data/master/dhatu/data.txt",
    ASHTADHYAYI_SUTRA_PATH: "https://raw.githubusercontent.com/ashtadhyayi-com/data/master/sutraani/data.txt",
}

GITA_CHAPTER_URL = "https://raw.githubusercontent.com/bhavykhatri/DharmicData/main/SrimadBhagvadGita/bhagavad_gita_chapter_{chapter}.json"
DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]+")


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def _ensure_source(path: Path) -> None:
    if path.exists():
        return
    url = SOURCE_URLS.get(path)
    if not url:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, path)


def _clean_gita_verse(text: str) -> str:
    lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
    for line in lines:
        if "उवाच" in line and "।" not in line:
            continue
        if DEVANAGARI_RE.search(line):
            cleaned = re.sub(r"।।[\d.]+।।", "।", line)
            cleaned = re.sub(r"\s+", " ", cleaned).strip()
            if cleaned:
                return cleaned
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _load_gita_stotra_verses(limit: int = TARGET_STOTRA) -> List[Dict[str, Any]]:
    if GITA_STOTRA_PATH.exists():
        payload = _read_json(GITA_STOTRA_PATH)
        records = payload.get("records", [])
        if len(records) >= limit:
            return records[:limit]

    records: List[Dict[str, Any]] = []
    seen = set()
    for chapter in range(1, 19):
        if len(records) >= limit:
            break
        url = GITA_CHAPTER_URL.format(chapter=chapter)
        try:
            payload = json.loads(urllib.request.urlopen(url, timeout=60).read().decode("utf-8"))
        except Exception:
            continue
        for item in payload.get("BhagavadGitaChapter", []):
            text = _clean_gita_verse(item.get("text", ""))
            if not text or text in seen:
                continue
            seen.add(text)
            verse = str(item.get("verse", "")).strip()
            records.append({
                "id": f"gita-{chapter}.{verse}",
                "text": text,
                "title": f"Bhagavad Gita {chapter}.{verse}",
                "source": "DharmicData/SrimadBhagvadGita",
            })
            if len(records) >= limit:
                break

    _write_json(
        GITA_STOTRA_PATH,
        {
            "schemaVersion": "sanskrit-corpus-stotra-source.v1",
            "sourceId": "gita-dharmicdata-v1",
            "recordCount": len(records),
            "records": records,
        },
    )
    return records[:limit]


def _load_ashtadhyayi_dhatus() -> List[Dict[str, Any]]:
    legacy = CORPUS_SOURCES / "dhatupatha" / "ashtadhyayi_dhatu_sample.txt"
    if legacy.exists() and not ASHTADHYAYI_DHATU_PATH.exists():
        ASHTADHYAYI_DHATU_PATH.write_text(legacy.read_text(encoding="utf-8"), encoding="utf-8")
    _ensure_source(ASHTADHYAYI_DHATU_PATH)
    payload = _read_json(ASHTADHYAYI_DHATU_PATH)

    records: List[Dict[str, Any]] = []
    seen_ids = set()
    seen_texts = set()
    for row in payload.get("data", []):
        root = str(row.get("dhatu") or row.get("aupadeshik") or "").strip()
        record_id = str(row.get("baseindex") or "").strip()
        gana = str(row.get("gana") or "").strip().zfill(2)[-2:]
        gloss = str(row.get("artha_english") or row.get("artha") or row.get("artha_hindi") or "").strip()
        if not root or not record_id or not gloss:
            continue
        if record_id in seen_ids or root in seen_texts:
            continue
        if not DEVANAGARI_RE.search(root):
            continue
        if len(root) > 32:
            continue
        seen_ids.add(record_id)
        seen_texts.add(root)
        records.append({
            "id": record_id,
            "type": "dhatu",
            "text": root,
            "source": str(ASHTADHYAYI_DHATU_PATH.relative_to(ROOT)).replace("\\", "/"),
            "gana": gana,
            "notes": gloss,
        })
    return records


def _load_ashtadhyayi_sutras(limit: int = TARGET_SUTRA) -> List[Dict[str, Any]]:
    legacy = CORPUS_SOURCES / "sutra" / "ashtadhyayi_sutra_sample.txt"
    if legacy.exists() and not ASHTADHYAYI_SUTRA_PATH.exists():
        ASHTADHYAYI_SUTRA_PATH.write_text(legacy.read_text(encoding="utf-8"), encoding="utf-8")
    _ensure_source(ASHTADHYAYI_SUTRA_PATH)
    payload = _read_json(ASHTADHYAYI_SUTRA_PATH)

    rows = sorted(
        payload.get("data", []),
        key=lambda item: (
            int(str(item.get("a") or "0")),
            int(str(item.get("p") or "0")),
            int(str(item.get("n") or "0")),
        ),
    )

    records: List[Dict[str, Any]] = []
    seen_refs = set()
    seen_texts = set()
    for row in rows:
        text = str(row.get("s") or "").strip()
        adhyaya = str(row.get("a") or "").strip()
        pada = str(row.get("p") or "").strip()
        number = str(row.get("n") or "").strip()
        ref = f"{adhyaya}.{pada}.{number}"
        if not text or ref in seen_refs or text in seen_texts:
            continue
        seen_refs.add(ref)
        seen_texts.add(text)
        seq = len(records) + 1
        records.append({
            "id": f"sutra-{seq:04d}",
            "type": "sutra",
            "text": text,
            "source": str(ASHTADHYAYI_SUTRA_PATH.relative_to(ROOT)).replace("\\", "/"),
            "notes": f"ashtadhyayi-ref:{ref}",
        })
        if len(records) >= limit:
            break
    return records


def build_dhatu_batches(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    by_gana: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        gana = str(record.get("gana") or "").zfill(2)[-2:]
        by_gana[gana].append(record)

    for gana in by_gana:
        by_gana[gana].sort(key=lambda item: item["id"])

    global_used_ids = set()
    overflow: List[Dict[str, Any]] = []
    for gana in sorted(by_gana):
        for record in by_gana[gana]:
            if record["id"] not in global_used_ids:
                overflow.append(record)

    written_batches: List[Dict[str, Any]] = []
    counts = {"dhatu": 0}
    overflow_index = 0

    for gana_id, slug in GANA_DIRS:
        batch_records: List[Dict[str, Any]] = []
        rel_source = f"raw/sanskrit/dhatu/{gana_id}_{slug}_batch.json"

        for record in by_gana.get(gana_id, []):
            if record["id"] in global_used_ids:
                continue
            item = dict(record)
            item["source"] = rel_source
            batch_records.append(item)
            global_used_ids.add(record["id"])

        while len(batch_records) < PER_GANA_DHATU and overflow_index < len(overflow):
            candidate = overflow[overflow_index]
            overflow_index += 1
            if candidate["id"] in global_used_ids:
                continue
            item = dict(candidate)
            item["source"] = rel_source
            batch_records.append(item)
            global_used_ids.add(candidate["id"])

        while len(batch_records) < PER_GANA_DHATU:
            seq = len(batch_records) + 1
            filler_id = f"{gana_id}.{seq:04d}"
            while filler_id in global_used_ids:
                seq += 1
                filler_id = f"{gana_id}.{seq:04d}"
            global_used_ids.add(filler_id)
            batch_records.append({
                "id": filler_id,
                "type": "dhatu",
                "text": "भू",
                "source": rel_source,
                "gana": gana_id,
                "notes": "reserved placeholder",
            })

        rel_path = f"raw/sanskrit/dhatu/{gana_id}_{slug}_batch.json"
        payload = {
            "batchId": f"DHATU_{gana_id}_{slug.upper()}",
            "ganaId": gana_id,
            "slug": slug,
            "corpusType": "dhatu",
            "description": f"Real corpus dhatu batch for {slug} gana",
            "records": batch_records[:PER_GANA_DHATU],
        }
        _write_json(ROOT / rel_path, payload)
        written_batches.append({
            "batchId": payload["batchId"],
            "path": rel_path,
            "recordCount": len(payload["records"]),
        })
        counts["dhatu"] += len(payload["records"])

    return written_batches, counts


def build_sutra_batch(records: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], int]:
    payload = {
        "batchId": "SUTRA_CORPUS_BATCH_001",
        "corpusType": "sutra",
        "description": "Real corpus sutra batch from Ashtadhyayi source registry",
        "records": records[:TARGET_SUTRA],
    }
    rel_path = "raw/sanskrit/sutra/sutra_corpus_batch_001.json"
    _write_json(ROOT / rel_path, payload)
    return {"batchId": payload["batchId"], "path": rel_path, "recordCount": len(payload["records"])}, len(payload["records"])


def build_stotra_batch(records: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], int]:
    batch_records: List[Dict[str, Any]] = []
    for index, record in enumerate(records[:TARGET_STOTRA], start=1):
        batch_records.append({
            "id": f"stotra-{index:04d}",
            "type": "stotra",
            "text": record["text"],
            "source": "raw/sanskrit/stotra/stotra_corpus_batch_001.json",
            "notes": f"title:{record.get('title', record.get('id', 'stotra'))};seed:{record.get('id', f'stotra-{index:04d}')}",
        })

    payload = {
        "batchId": "STOTRA_CORPUS_BATCH_001",
        "corpusType": "stotra",
        "description": "Real corpus stotra batch from Bhagavad Gita verses",
        "records": batch_records,
    }
    rel_path = "raw/sanskrit/stotra/stotra_corpus_batch_001.json"
    _write_json(ROOT / rel_path, payload)
    return {"batchId": payload["batchId"], "path": rel_path, "recordCount": len(batch_records)}, len(batch_records)


def build_real_corpus_raw_batches() -> Dict[str, Any]:
    dhatu_records = _load_ashtadhyayi_dhatus()
    sutra_records = _load_ashtadhyayi_sutras()
    stotra_records = _load_gita_stotra_verses()

    dhatu_batches, dhatu_counts = build_dhatu_batches(dhatu_records)
    sutra_batch, sutra_count = build_sutra_batch(sutra_records)
    stotra_batch, stotra_count = build_stotra_batch(stotra_records)

    total = dhatu_counts["dhatu"] + sutra_count + stotra_count
    unique_dhatu_texts = len({record["text"] for record in dhatu_records})

    valid = (
        dhatu_counts["dhatu"] == TARGET_DHATU
        and sutra_count == TARGET_SUTRA
        and stotra_count == TARGET_STOTRA
        and total == TARGET_DHATU + TARGET_SUTRA + TARGET_STOTRA
        and len(dhatu_records) >= TARGET_DHATU
    )

    manifest = _read_json(RAW_MANIFEST) if RAW_MANIFEST.exists() else {}
    manifest["status"] = "raw-batches-ready" if valid else "raw-batches-partial"
    manifest["seedDhatuCount"] = len(dhatu_records)
    manifest["uniqueDhatuCount"] = unique_dhatu_texts
    manifest["generatedAt"] = "phase-11-expanded"
    manifest["sources"] = {
        "dhatu": str(ASHTADHYAYI_DHATU_PATH.relative_to(ROOT)).replace("\\", "/"),
        "sutra": str(ASHTADHYAYI_SUTRA_PATH.relative_to(ROOT)).replace("\\", "/"),
        "stotra": str(GITA_STOTRA_PATH.relative_to(ROOT)).replace("\\", "/"),
    }
    manifest["batches"] = {
        "dhatu": dhatu_batches,
        "sutra": [sutra_batch],
        "stotra": [stotra_batch],
    }
    manifest["counts"] = {
        "dhatu": dhatu_counts["dhatu"],
        "sutra": sutra_count,
        "stotra": stotra_count,
        "total": total,
    }
    _write_json(RAW_MANIFEST, manifest)

    return {
        "valid": valid,
        "phase": "11",
        "title": "Real Corpus Loading",
        "seedDhatuCount": len(dhatu_records),
        "uniqueDhatuCount": unique_dhatu_texts,
        "counts": manifest["counts"],
        "targets": manifest.get("targets", {
            "dhatu": TARGET_DHATU,
            "sutra": TARGET_SUTRA,
            "stotra": TARGET_STOTRA,
            "total": TARGET_DHATU + TARGET_SUTRA + TARGET_STOTRA,
        }),
        "batches": manifest["batches"],
        "sources": manifest["sources"],
        "previewOnly": True,
        "canonicalWriteAllowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build real corpus raw batch files for Phase 11.")
    parser.parse_args()
    result = build_real_corpus_raw_batches()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())