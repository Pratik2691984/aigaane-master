import json
from pathlib import Path

from simulate_bulk_corpus_execution import simulate_bulk_corpus_execution


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_bulk_corpus_forecast(data):
    simulation = simulate_bulk_corpus_execution(data)

    total_records = int(simulation.get("totalRecords", 0))
    total_seconds = float(simulation.get("totalEstimatedSeconds", 0) or 0)

    throughput = float(
        simulation.get(
            "estimatedThroughputPerSecond",
            round(total_records / total_seconds, 1) if total_seconds else 0,
        )
    )
    final_percent = float(simulation.get("finalCompletionPercent", 0) or 0)

    forecast_ready = (
        simulation.get("valid") is True
        and final_percent == 100.0
        and simulation.get("simulationExecutionAllowed") is False
        and simulation.get("canonicalWriteAllowed") is False
    )

    return {
        "valid": forecast_ready,
        "forecastStatus": "forecast-ready" if forecast_ready else "forecast-blocked",
        "totalRecords": total_records,
        "projectedFinishSecond": total_seconds,
        "projectedThroughputPerSecond": throughput,
        "projectedCompletionPercent": final_percent,
        "queueExhaustionSecond": total_seconds,
        "importReadinessForecast": forecast_ready,
        "simulation": simulation,
        "previewOnly": True,
        "readOnly": True,
        "forecastExecutionAllowed": False,
        "simulationExecutionAllowed": False,
        "executionAllowed": False,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False
    }


def main():
    result = build_bulk_corpus_forecast(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())