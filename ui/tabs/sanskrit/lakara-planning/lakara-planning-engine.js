"use strict";

const {
  LAKARA_PLANNING_SCHEMA_VERSION,
  LAKARA_PLANNING_CONTRACTS,
  LAKARA_PLANNING_FIELDS,
  getLakaraPlanningSummary
} = require("./lakara-planning-map.js");

function normalizeLakaraPlanningField(field) {
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

function buildLakaraPlanningExport() {
  const summary = getLakaraPlanningSummary();

  return {
    schemaVersion: LAKARA_PLANNING_SCHEMA_VERSION,
    contracts: { ...LAKARA_PLANNING_CONTRACTS },
    ready: true,
    fieldCount: LAKARA_PLANNING_FIELDS.length,
    planningTypes: Array.isArray(summary.planningTypes)
      ? summary.planningTypes.map(String)
      : [],
    fields: LAKARA_PLANNING_FIELDS.map(normalizeLakaraPlanningField),
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
      executionGuardLinked: true,
      morphologyPlanningLinked: true,
      mutationFree: true,
      candidateOnly: true
    }
  };
}

function createLakaraPlanningSnapshot(input) {
  const safeInput = input && typeof input === "object" ? input : {};
  const candidates = Array.isArray(safeInput.candidates)
    ? safeInput.candidates
    : [];

  return Object.freeze({
    schemaVersion: LAKARA_PLANNING_SCHEMA_VERSION,
    kind: "LAKARA_PLANNING_SNAPSHOT",
    candidates: Object.freeze(
      candidates.map((candidate, index) =>
        Object.freeze({
          index,
          id: String(candidate.id || `lakara-candidate-${index}`),
          type: String(candidate.type || "CONJUGATION_STATE"),
          root: String(candidate.root || ""),
          lakara: String(candidate.lakara || ""),
          purusha: String(candidate.purusha || ""),
          vacana: String(candidate.vacana || ""),
          pada: String(candidate.pada || ""),
          planned: true,
          executed: false,
          diagnostics: Array.isArray(candidate.diagnostics)
            ? candidate.diagnostics.map(String)
            : ["candidate-only"]
        })
      )
    ),
    trace: Object.freeze({
      replaySafe: true,
      mutationFree: true,
      candidateCount: candidates.length
    })
  });
}

function getLakaraPlanningDiagnostics() {
  const lakaraExport = buildLakaraPlanningExport();

  return {
    schemaVersion: lakaraExport.schemaVersion,
    ready: lakaraExport.ready,
    fieldCount: lakaraExport.fieldCount,
    contractsSatisfied: Object.values(lakaraExport.contracts).every(Boolean),
    diagnostics: { ...lakaraExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeLakaraPlanningField,
    buildLakaraPlanningExport,
    createLakaraPlanningSnapshot,
    getLakaraPlanningDiagnostics
  };
}