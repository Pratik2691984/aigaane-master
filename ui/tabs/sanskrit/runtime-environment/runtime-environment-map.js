"use strict";

/**
 * Deterministic Sanskrit Runtime Environment Map
 *
 * Inspection-first runtime environment metadata for future guarded derivation.
 * This layer does not execute Sanskrit transformations, mutate IR snapshots,
 * or produce surface forms.
 */

const RUNTIME_ENVIRONMENT_SCHEMA_VERSION = "sanskrit-runtime-environment.v1";

const RUNTIME_ENVIRONMENT_TYPES = Object.freeze({
  INSPECTION: "INSPECTION",
  PLANNING: "PLANNING",
  GUARDED_RUNTIME: "GUARDED_RUNTIME",
  ROLLBACK: "ROLLBACK",
  DIAGNOSTIC: "DIAGNOSTIC",
  FINALIZATION: "FINALIZATION"
});

const RUNTIME_ENVIRONMENT_CONTRACTS = Object.freeze({
  deterministic: true,
  immutable: true,
  inspectionOnly: true,
  nonPerformative: true,
  runtimeIsolated: true,
  schedulerLinked: true,
  irLinked: true,
  queueLinked: true,
  traceLinked: true,
  checkpointLinked: true,
  replaySafe: true,
  staticPreviewCompatible: true
});

const RUNTIME_ENVIRONMENT_FIELDS = Object.freeze([
  {
    id: "runtime.inspection",
    type: RUNTIME_ENVIRONMENT_TYPES.INSPECTION,
    summary: "Inspection-mode runtime environment envelope.",
    required: true,
    diagnostics: ["inspection-mode", "safe-envelope"]
  },
  {
    id: "runtime.planning",
    type: RUNTIME_ENVIRONMENT_TYPES.PLANNING,
    summary: "Planning-mode runtime context linked to scheduler, IR, queue, trace, and checkpoint layers.",
    required: true,
    diagnostics: ["planning-mode", "orchestration-linked"]
  },
  {
    id: "runtime.guarded",
    type: RUNTIME_ENVIRONMENT_TYPES.GUARDED_RUNTIME,
    summary: "Reserved guarded runtime context for future controlled transformation execution.",
    required: true,
    diagnostics: ["guarded-runtime", "non-executing"]
  },
  {
    id: "runtime.rollback",
    type: RUNTIME_ENVIRONMENT_TYPES.ROLLBACK,
    summary: "Rollback envelope metadata for future recovery-safe execution.",
    required: false,
    diagnostics: ["rollback-envelope", "recovery-safe"]
  },
  {
    id: "runtime.diagnostic",
    type: RUNTIME_ENVIRONMENT_TYPES.DIAGNOSTIC,
    summary: "Normalized runtime diagnostic envelope.",
    required: false,
    diagnostics: ["diagnostic-envelope", "inspection-safe"]
  },
  {
    id: "runtime.finalization",
    type: RUNTIME_ENVIRONMENT_TYPES.FINALIZATION,
    summary: "Runtime finalization envelope without Sanskrit transformation execution.",
    required: true,
    diagnostics: ["finalization", "non-executing"]
  }
]);

function getRuntimeEnvironmentSummary() {
  return {
    schemaVersion: RUNTIME_ENVIRONMENT_SCHEMA_VERSION,
    contracts: RUNTIME_ENVIRONMENT_CONTRACTS,
    fieldCount: RUNTIME_ENVIRONMENT_FIELDS.length,
    environmentTypes: Object.values(RUNTIME_ENVIRONMENT_TYPES),
    fields: RUNTIME_ENVIRONMENT_FIELDS.map((field) => ({ ...field }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    RUNTIME_ENVIRONMENT_SCHEMA_VERSION,
    RUNTIME_ENVIRONMENT_TYPES,
    RUNTIME_ENVIRONMENT_CONTRACTS,
    RUNTIME_ENVIRONMENT_FIELDS,
    getRuntimeEnvironmentSummary
  };
}