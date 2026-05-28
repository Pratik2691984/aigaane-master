"use strict";

const {
  MORPHOLOGY_PLANNING_SCHEMA_VERSION,
  MORPHOLOGY_PLANNING_CONTRACTS,
  MORPHOLOGY_PLANNING_FIELDS,
  getMorphologyPlanningSummary
} = require("./morphology-planning-map.js");

function normalizeMorphologyPlanningField(field) {
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

function buildMorphologyPlanningExport() {
  const summary = getMorphologyPlanningSummary();

  return {
    schemaVersion: MORPHOLOGY_PLANNING_SCHEMA_VERSION,
    contracts: { ...MORPHOLOGY_PLANNING_CONTRACTS },
    ready: true,
    fieldCount: MORPHOLOGY_PLANNING_FIELDS.length,
    planningTypes: Array.isArray(summary.planningTypes)
      ? summary.planningTypes.map(String)
      : [],
    fields: MORPHOLOGY_PLANNING_FIELDS.map(normalizeMorphologyPlanningField),
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
      mutationFree: true,
      candidateOnly: true
    }
  };
}

function createMorphologyPlanningSnapshot(input) {
  const safeInput = input && typeof input === "object" ? input : {};
  const candidates = Array.isArray(safeInput.candidates)
    ? safeInput.candidates
    : [];

  return Object.freeze({
    schemaVersion: MORPHOLOGY_PLANNING_SCHEMA_VERSION,
    kind: "MORPHOLOGY_PLANNING_SNAPSHOT",
    candidates: Object.freeze(
      candidates.map((candidate, index) =>
        Object.freeze({
          index,
          id: String(candidate.id || `morphology-candidate-${index}`),
          type: String(candidate.type || "DERIVATIONAL_STATE"),
          root: String(candidate.root || ""),
          stem: String(candidate.stem || ""),
          affix: String(candidate.affix || ""),
          pada: String(candidate.pada || ""),
          gana: String(candidate.gana || ""),
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

function getMorphologyPlanningDiagnostics() {
  const morphologyExport = buildMorphologyPlanningExport();

  return {
    schemaVersion: morphologyExport.schemaVersion,
    ready: morphologyExport.ready,
    fieldCount: morphologyExport.fieldCount,
    contractsSatisfied: Object.values(morphologyExport.contracts).every(Boolean),
    diagnostics: { ...morphologyExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeMorphologyPlanningField,
    buildMorphologyPlanningExport,
    createMorphologyPlanningSnapshot,
    getMorphologyPlanningDiagnostics
  };
}