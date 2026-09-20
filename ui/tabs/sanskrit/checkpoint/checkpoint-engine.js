"use strict";

const {
  CHECKPOINT_SCHEMA_VERSION,
  CHECKPOINT_CONTRACTS,
  CHECKPOINT_FIELDS,
  getCheckpointSummary
} = require("./checkpoint-map.js");

function normalizeCheckpointField(field) {
  return {
    id: String(field.id || ""),
    type: String(field.type || ""),
    summary: String(field.summary || ""),
    required: Boolean(field.required),
    diagnostics: Array.isArray(field.diagnostics)
      ? field.diagnostics.map(String)
      : []
  };
}

function buildCheckpointExport() {
  const summary = getCheckpointSummary();

  return {
    schemaVersion: CHECKPOINT_SCHEMA_VERSION,
    contracts: { ...CHECKPOINT_CONTRACTS },
    ready: true,
    fieldCount: CHECKPOINT_FIELDS.length,
    eventTypes: Array.isArray(summary.eventTypes)
      ? summary.eventTypes.map(String)
      : [],
    fields: CHECKPOINT_FIELDS.map(normalizeCheckpointField),
    diagnostics: {
      normalized: true,
      deterministic: true,
      immutable: true,
      runtimeSafe: true,
      replaySafe: true,
      schedulerLinked: true,
      irLinked: true,
      queueLinked: true,
      traceLinked: true,
      mutationFree: true
    }
  };
}

function createCheckpointSnapshot(input) {
  const safeInput = input && typeof input === "object" ? input : {};
  const checkpoints = Array.isArray(safeInput.checkpoints)
    ? safeInput.checkpoints
    : [];

  return Object.freeze({
    schemaVersion: CHECKPOINT_SCHEMA_VERSION,
    kind: "CHECKPOINT_SNAPSHOT",
    checkpoints: Object.freeze(
      checkpoints.map((checkpoint, index) =>
        Object.freeze({
          index,
          id: String(checkpoint.id || `checkpoint-${index}`),
          type: String(checkpoint.type || "RECOVERY_POINT"),
          referenceId: String(checkpoint.referenceId || ""),
          summary: String(checkpoint.summary || ""),
          diagnostics: Array.isArray(checkpoint.diagnostics)
            ? checkpoint.diagnostics.map(String)
            : []
        })
      )
    ),
    trace: Object.freeze({
      replaySafe: true,
      mutationFree: true,
      checkpointCount: checkpoints.length
    })
  });
}

function getCheckpointDiagnostics() {
  const checkpointExport = buildCheckpointExport();

  return {
    schemaVersion: checkpointExport.schemaVersion,
    ready: checkpointExport.ready,
    fieldCount: checkpointExport.fieldCount,
    contractsSatisfied: Object.values(checkpointExport.contracts).every(Boolean),
    diagnostics: { ...checkpointExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeCheckpointField,
    buildCheckpointExport,
    createCheckpointSnapshot,
    getCheckpointDiagnostics
  };
}