import json
from pathlib import Path

from build_bulk_corpus_forecast import build_bulk_corpus_forecast


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_bulk_corpus_admission(data):
    forecast = build_bulk_corpus_forecast(data)

    accepted = (
        forecast.get("valid") is True
        and forecast.get("importReadinessForecast") is True
        and forecast.get("forecastExecutionAllowed") is False
        and forecast.get("canonicalWriteAllowed") is False
    )

    admission_reasons = []
    rejection_reasons = []

    if accepted:
        admission_reasons.append("forecastReady")
        admission_reasons.append("previewOnly")
        admission_reasons.append("canonicalWriteLocked")
    else:
        rejection_reasons.append("forecastBlocked")

    return {
        "valid": accepted,
        "admissionStatus": "admission-ready" if accepted else "admission-blocked",
        "acceptedRecordCount": forecast.get("totalRecords", 0) if accepted else 0,
        "rejectedRecordCount": 0 if accepted else forecast.get("totalRecords", 0),
        "admissionReasons": admission_reasons,
        "rejectionReasons": rejection_reasons,
        "forecast": forecast,
        "previewOnly": True,
        "readOnly": True,
        "admissionExecutionAllowed": False,
        "forecastExecutionAllowed": False,
        "executionAllowed": False,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False
    }


def main():
    result = build_bulk_corpus_admission(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())