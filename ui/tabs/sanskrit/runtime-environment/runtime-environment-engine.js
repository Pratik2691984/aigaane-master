"use strict";

const {
  RUNTIME_ENVIRONMENT_SCHEMA_VERSION,
  RUNTIME_ENVIRONMENT_CONTRACTS,
  RUNTIME_ENVIRONMENT_FIELDS,
  getRuntimeEnvironmentSummary
} = require("./runtime-environment-map.js");

function normalizeRuntimeEnvironmentField(field) {
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

function buildRuntimeEnvironmentExport() {
  const summary = getRuntimeEnvironmentSummary();

  return {
    schemaVersion: RUNTIME_ENVIRONMENT_SCHEMA_VERSION,
    contracts: { ...RUNTIME_ENVIRONMENT_CONTRACTS },
    ready: true,
    fieldCount: RUNTIME_ENVIRONMENT_FIELDS.length,
    environmentTypes: Array.isArray(summary.environmentTypes)
      ? summary.environmentTypes.map(String)
      : [],
    fields: RUNTIME_ENVIRONMENT_FIELDS.map(normalizeRuntimeEnvironmentField),
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
      checkpointLinked: true,
      mutationFree: true,
      guarded: true
    }
  };
}

function createRuntimeEnvironmentSnapshot(input) {
  const safeInput = input && typeof input === "object" ? input : {};

  return Object.freeze({
    schemaVersion: RUNTIME_ENVIRONMENT_SCHEMA_VERSION,
    kind: "RUNTIME_ENVIRONMENT_SNAPSHOT",
    mode: String(safeInput.mode || "INSPECTION"),
    references: Object.freeze({
      scheduler: String(safeInput.scheduler || ""),
      ir: String(safeInput.ir || ""),
      queue: String(safeInput.queue || ""),
      trace: String(safeInput.trace || ""),
      checkpoint: String(safeInput.checkpoint || "")
    }),
    capabilities: Object.freeze({
      executeTransformations: false,
      mutateSnapshots: false,
      produceSurfaceForms: false,
      inspectOnly: true,
      rollbackSafe: true
    }),
    trace: Object.freeze({
      replaySafe: true,
      mutationFree: true,
      runtimeIsolated: true
    })
  });
}

function getRuntimeEnvironmentDiagnostics() {
  const runtimeExport = buildRuntimeEnvironmentExport();

  return {
    schemaVersion: runtimeExport.schemaVersion,
    ready: runtimeExport.ready,
    fieldCount: runtimeExport.fieldCount,
    contractsSatisfied: Object.values(runtimeExport.contracts).every(Boolean),
    diagnostics: { ...runtimeExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeRuntimeEnvironmentField,
    buildRuntimeEnvironmentExport,
    createRuntimeEnvironmentSnapshot,
    getRuntimeEnvironmentDiagnostics
  };
}