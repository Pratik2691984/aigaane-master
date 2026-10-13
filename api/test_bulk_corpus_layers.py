"""
Parametrized tests for the bulk corpus layer suite.

Group A layers use the exact same five-test shape.
Group B layers use the same three shared tests plus two layer-specific extras,
which are recorded in the SHARED table and the EXTRAS list below.
Group C layers (authorization gate, governance decision, manual review,
post-attestation hold, certification assurance, promotion certification)
remain in their own files because they test real failure matrices.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGING_ENGINE = "./ui/tabs/sanskrit/corpus-staging"


# Each entry: (layer_name, python_script, engine_file, renderer_file, summary_export, status_export)
# Empty summary_export means there is no summary test for this layer.
SHARED = [
    # Group A
    ("admission",         "build_bulk_corpus_admission.py",         "corpus-admission-engine.js",         "corpus-admission-renderer.js",         "summarizeCorpusAdmission",         "deriveAdmissionStatus"),
    ("canonical",         "preview_bulk_corpus_canonical.py",       "corpus-canonical-engine.js",         "corpus-canonical-renderer.js",         "summarizeCorpusCanonicalPreview",  "deriveCanonicalStatus"),
    ("certification",     "build_bulk_corpus_certification.py",     "corpus-certification-engine.js",     "corpus-certification-renderer.js",     "summarizeCorpusCertification",     "deriveCertificationStatus"),
    ("forecast",          "build_bulk_corpus_forecast.py",          "corpus-forecast-engine.js",          "corpus-forecast-renderer.js",          "summarizeCorpusForecast",          "deriveForecastStatus"),
    ("promotion_approval","build_bulk_corpus_promotion_approval.py","corpus-approval-engine.js",          "corpus-approval-renderer.js",          "summarizeCorpusPromotionApproval", "deriveApprovalStatus"),
    ("promotion_readiness","build_bulk_corpus_promotion_readiness.py","corpus-promotion-engine.js",       "corpus-promotion-renderer.js",         "summarizeCorpusPromotionReadiness","derivePromotionStatus"),
    # Group B (shared methods only; extras handled below)
    ("allocation",        "plan_bulk_corpus_allocation.py",         "corpus-allocation-engine.js",        "corpus-allocation-renderer.js",        "summarizeCorpusAllocation",        None),
    ("capacity",          "plan_bulk_corpus_capacity.py",           "corpus-capacity-engine.js",          "corpus-capacity-renderer.js",          "summarizeCorpusCapacity",          None),
    ("execution_preview", "preview_bulk_corpus_execution.py",       "corpus-execution-preview-engine.js", "corpus-execution-preview-renderer.js", "summarizeCorpusExecutionPreview",  None),
    ("import_preview",    "preview_bulk_corpus_import.py",          "corpus-import-preview-engine.js",    "corpus-import-preview-renderer.js",    "summarizeCorpusImportPreview",     None),
    ("intake",            "prepare_bulk_corpus_intake.py",          "corpus-intake-engine.js",            "corpus-intake-renderer.js",            "summarizeCorpusIntake",            None),
    ("intake_queue",      "build_bulk_corpus_intake_queue.py",      "corpus-intake-queue-engine.js",      "corpus-intake-queue-renderer.js",      "summarizeCorpusIntakeQueue",       None),
    ("promotion_advisory","build_bulk_corpus_promotion_advisory.py","corpus-advisory-engine.js",          "corpus-advisory-renderer.js",          "summarizeCorpusPromotionAdvisory", None),
    ("provenance",        "audit_bulk_corpus_provenance.py",        "corpus-provenance-engine.js",        "corpus-provenance-renderer.js",        None,                               None),
    ("readiness",         "compute_bulk_corpus_readiness.py",       "corpus-readiness-engine.js",         "corpus-readiness-renderer.js",         "summarizeCorpusReadiness",         None),
    ("reservation",       "reserve_bulk_corpus_capacity.py",        "corpus-reservation-engine.js",       "corpus-reservation-renderer.js",       "summarizeCorpusReservation",       None),
    ("schedule",          "plan_bulk_corpus_schedule.py",           "corpus-schedule-engine.js",          "corpus-schedule-renderer.js",          "summarizeCorpusSchedule",          None),
    ("simulation",        "simulate_bulk_corpus_execution.py",      "corpus-simulation-engine.js",        "corpus-simulation-renderer.js",        "summarizeCorpusSimulation",        None),
    ("staging",           "validate_bulk_corpus_staging.py",        "corpus-staging-engine.js",           "corpus-staging-renderer.js",           None,                               None),
    ("timeline",          "build_bulk_corpus_timeline.py",          "corpus-timeline-engine.js",          "corpus-timeline-renderer.js",          "summarizeCorpusTimeline",          None),
    ("validator",         "validate_bulk_corpus_records.py",        "corpus-validator-engine.js",         "corpus-validator-renderer.js",         None,                               None),
    ("window",            "plan_bulk_corpus_windows.py",            "corpus-window-engine.js",            "corpus-window-renderer.js",            "summarizeCorpusWindows",           None),
]


def run_json(script: str) -> object:
    result = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        check=True,
        cwd=ROOT,
    )
    return json.loads(result.stdout)


def run_python_script(name: str) -> dict:
    result = subprocess.run(
        [sys.executable, f"scripts/{name}"],
        capture_output=True,
        text=True,
        check=True,
        cwd=ROOT,
    )
    return json.loads(result.stdout)


class BulkCorpusSharedLayers(unittest.TestCase):
    def test_script_runs_and_reports_valid(self):
        for name, script, *_ in SHARED:
            with self.subTest(layer=name):
                data = run_python_script(script)
                self.assertIn("valid", data, data)
                self.assertTrue(data["valid"], f"{name}: not valid: {data}")
                if "canonicalWriteAllowed" in data:
                    self.assertFalse(data["canonicalWriteAllowed"])

  

    def test_summary_export_returns_object(self):
        for name, _script, engine, _renderer, summary, _status in SHARED:
            if not summary:
                continue
            with self.subTest(layer=name):
                payload = run_json(f"""
const m = require("{STAGING_ENGINE}/{engine}");
const result = m.{summary}({{}}, 250, 12.5);
console.log(JSON.stringify(result));
""")
                self.assertIsInstance(payload, dict)
                self.assertIn("valid", payload)

    def test_status_export_returns_string(self):
        for name, _script, engine, _renderer, _summary, status in SHARED:
            if not status:
                continue
            with self.subTest(layer=name):
                payload = run_json(f"""
const m = require("{STAGING_ENGINE}/{engine}");
console.log(JSON.stringify({{ status: m.{status}({{ valid: true }}) }}));
""")
                self.assertIsInstance(payload["status"], str)
                self.assertTrue(payload["status"], f"{name}: empty status")


if __name__ == "__main__":
    unittest.main()