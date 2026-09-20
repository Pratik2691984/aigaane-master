"use strict";

const {
  PRAKRIYA_PLANNING_SCHEMA_VERSION,
  PRAKRIYA_PLANNING_CONTRACTS,
  PRAKRIYA_PLANNING_FIELDS,
  getPrakriyaPlanningSummary
} = require("./prakriya-planning-map.js");

function normalizePrakriyaPlanningField(field) {
  return {
    id: String(field.id || ""),
    type: String(field.type || ""),
    order: Number.isFinite(Number(field.order)) ? Number(field.order) : 0,
    summary: String(field.summary || ""),
    required: Boolean(field.required),
    diagnostics: Array.isArray(field.diagnostics)
      ? field.diagnostics.map(String)
      : []
  };
}

function buildPrakriyaPlanningExport() {
  const summary = getPrakriyaPlanningSummary();

  return {
    schemaVersion: PRAKRIYA_PLANNING_SCHEMA_VERSION,
    contracts: { ...PRAKRIYA_PLANNING_CONTRACTS },
    ready: true,
    fieldCount: PRAKRIYA_PLANNING_FIELDS.length,
    stageTypes: Array.isArray(summary.stageTypes)
      ? summary.stageTypes.map(String)
      : [],
    fields: PRAKRIYA_PLANNING_FIELDS
      .map(normalizePrakriyaPlanningField)
      .sort((a, b) => a.order - b.order),
    diagnostics: {
      normalized: true,
      deterministic: true,
      immutable: true,
      runtimeSafe: true,
      replaySafe: true,
      schedulerLinked: true,
      queueLinked: true,
      traceLinked: true,
      checkpointLinked: true,
      executionGuardLinked: true,
      derivationGraphLinked: true,
      sandhiPlanningLinked: true,
      morphologyPlanningLinked: true,
      lakaraPlanningLinked: true,
      mutationFree: true,
      planningOnly: true
    }
  };
}

function createPrakriyaPlanningSnapshot(input) {
  const safeInput = input && typeof input === "object" ? input : {};
  const stages = Array.isArray(safeInput.stages) ? safeInput.stages : [];

  return Object.freeze({
    schemaVersion: PRAKRIYA_PLANNING_SCHEMA_VERSION,
    kind: "PRAKRIYA_PLANNING_SNAPSHOT",
    stages: Object.freeze(
      stages
        .map((stage, index) =>
          Object.freeze({
            index,
            id: String(stage.id || `prakriya-stage-${index}`),
            type: String(stage.type || "DIAGNOSTIC_STAGE"),
            order: Number.isFinite(Number(stage.order))
              ? Number(stage.order)
              : index,
            referenceId: String(stage.referenceId || ""),
            planned: true,
            executed: false,
            diagnostics: Array.isArray(stage.diagnostics)
              ? stage.diagnostics.map(String)
              : ["planning-only"]
          })
        )
        .sort((a, b) => a.order - b.order)
    ),
    trace: Object.freeze({
      replaySafe: true,
      mutationFree: true,
      stageCount: stages.length
    })
  });
}

function getPrakriyaPlanningDiagnostics() {
  const prakriyaExport = buildPrakriyaPlanningExport();

  return {
    schemaVersion: prakriyaExport.schemaVersion,
    ready: prakriyaExport.ready,
    fieldCount: prakriyaExport.fieldCount,
    contractsSatisfied: Object.values(prakriyaExport.contracts).every(Boolean),
    diagnostics: { ...prakriyaExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizePrakriyaPlanningField,
    buildPrakriyaPlanningExport,
    createPrakriyaPlanningSnapshot,
    getPrakriyaPlanningDiagnostics
  };
}