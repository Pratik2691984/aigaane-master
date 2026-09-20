#!/usr/bin/env python
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 11 corpus pipeline (11A-11L).")
    parser.add_argument("--skip-raw-build", action="store_true")
    args = parser.parse_args()

    if not args.skip_raw_build:
        builder = _load("build_real_corpus_raw_batches", "scripts/build_real_corpus_raw_batches.py")
        build_result = builder.build_real_corpus_raw_batches()
        if not build_result.get("valid"):
            print(json.dumps(build_result, ensure_ascii=False, indent=2))
            return 1

    pipeline = _load("corpus_pipeline", "api/engines/corpus_pipeline.py")
    status = pipeline.run_phase11_pipeline()

    loader = _load("load_real_corpus_from_raw", "scripts/load_real_corpus_from_raw.py")
    staging = loader.load_real_corpus_from_raw(dry_run=False)
    status["corpusStaging"] = {k: v for k, v in staging.items() if k != "errors" or v}

    orchestrator = _load("run_real_corpus_loading_pipeline", "scripts/run_real_corpus_loading_pipeline.py")
    legacy = orchestrator.run_real_corpus_loading_pipeline(write_manifest=False)
    status["governancePipeline"] = {
        "valid": legacy.get("valid"),
        "canonicalStatus": legacy.get("canonicalStatus"),
        "acceptedRecordCount": legacy.get("acceptedRecordCount"),
    }

    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0 if status.get("valid") and staging.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())