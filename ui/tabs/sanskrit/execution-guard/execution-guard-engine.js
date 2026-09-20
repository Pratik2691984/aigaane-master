"use strict";

const {
  EXECUTION_GUARD_SCHEMA_VERSION,
  EXECUTION_GUARD_CONTRACTS,
  EXECUTION_GUARD_FIELDS,
  getExecutionGuardSummary
} = require("./execution-guard-map.js");

function normalizeExecutionGuardField(field) {
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

function buildExecutionGuardExport() {
  const summary = getExecutionGuardSummary();

  return {
    schemaVersion: EXECUTION_GUARD_SCHEMA_VERSION,
    contracts: { ...EXECUTION_GUARD_CONTRACTS },
    ready: true,
    fieldCount: EXECUTION_GUARD_FIELDS.length,
    guardTypes: Array.isArray(summary.guardTypes)
      ? summary.guardTypes.map(String)
      : [],
    fields: EXECUTION_GUARD_FIELDS.map(normalizeExecutionGuardField),
    diagnostics: {
      normalized: true,
      deterministic: true,
      immutable: true,
      runtimeSafe: true,
      replaySafe: true,
      runtimeEnvironmentLinked: true,
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

function createExecutionGuardSnapshot(input) {
  const safeInput = input && typeof input === "object" ? input : {};

  return Object.freeze({
    schemaVersion: EXECUTION_GUARD_SCHEMA_VERSION,
    kind: "EXECUTION_GUARD_SNAPSHOT",
    mode: String(safeInput.mode || "INSPECTION"),
    permissions: Object.freeze({
      executeTransformations: false,
      mutateSnapshots: false,
      produceSurfaceForms: false,
      authorizeRollback: true,
      inspectOnly: true
    }),
    references: Object.freeze({
      runtimeEnvironment: String(safeInput.runtimeEnvironment || ""),
      scheduler: String(safeInput.scheduler || ""),
      ir: String(safeInput.ir || ""),
      queue: String(safeInput.queue || ""),
      trace: String(safeInput.trace || ""),
      checkpoint: String(safeInput.checkpoint || "")
    }),
    trace: Object.freeze({
      replaySafe: true,
      mutationFree: true,
      runtimeIsolated: true,
      guarded: true
    })
  });
}

function getExecutionGuardDiagnostics() {
  const guardExport = buildExecutionGuardExport();

  return {
    schemaVersion: guardExport.schemaVersion,
    ready: guardExport.ready,
    fieldCount: guardExport.fieldCount,
    contractsSatisfied: Object.values(guardExport.contracts).every(Boolean),
    diagnostics: { ...guardExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeExecutionGuardField,
    buildExecutionGuardExport,
    createExecutionGuardSnapshot,
    getExecutionGuardDiagnostics
  };
}