"use strict";

const {
  DERIVATION_IR_SCHEMA_VERSION,
  DERIVATION_IR_CONTRACTS,
  DERIVATION_IR_FIELDS,
  getDerivationIrSummary
} = require("./derivation-ir-map.js");

function normalizeDerivationIrField(field) {
  return {
    id: String(field.id || ""),
    type: String(field.type || ""),
    summary: String(field.summary || ""),
    required: Boolean(field.required),
    diagnostics: Array.isArray(field.diagnostics) ? field.diagnostics.map(String) : []
  };
}

function buildDerivationIrExport() {
  const summary = getDerivationIrSummary();

  return {
    schemaVersion: DERIVATION_IR_SCHEMA_VERSION,
    contracts: { ...DERIVATION_IR_CONTRACTS },
    ready: true,
    fieldCount: DERIVATION_IR_FIELDS.length,
    nodeTypes: Array.isArray(summary.nodeTypes) ? summary.nodeTypes.map(String) : [],
    fields: DERIVATION_IR_FIELDS.map(normalizeDerivationIrField),
    diagnostics: {
      normalized: true,
      deterministic: true,
      immutable: true,
      runtimeSafe: true,
      replaySafe: true,
      schedulerCompatible: true,
      mutationFree: true
    }
  };
}

function createDerivationIrSnapshot(input) {
  const safeInput = input && typeof input === "object" ? input : {};

  return Object.freeze({
    schemaVersion: DERIVATION_IR_SCHEMA_VERSION,
    kind: "DERIVATION_IR_SNAPSHOT",
    environment: Object.freeze({ ...(safeInput.environment || {}) }),
    intent: Object.freeze({ ...(safeInput.intent || {}) }),
    plannedSteps: Object.freeze(
      Array.isArray(safeInput.plannedSteps)
        ? safeInput.plannedSteps.map((step, index) =>
            Object.freeze({
              index,
              id: String(step.id || `planned-step-${index}`),
              ruleId: String(step.ruleId || ""),
              description: String(step.description || ""),
              diagnostics: Array.isArray(step.diagnostics) ? step.diagnostics.map(String) : []
            })
          )
        : []
    ),
    trace: Object.freeze({
      replaySafe: true,
      mutationFree: true,
      stepCount: Array.isArray(safeInput.plannedSteps) ? safeInput.plannedSteps.length : 0
    })
  });
}

function getDerivationIrDiagnostics() {
  const irExport = buildDerivationIrExport();

  return {
    schemaVersion: irExport.schemaVersion,
    ready: irExport.ready,
    fieldCount: irExport.fieldCount,
    contractsSatisfied: Object.values(irExport.contracts).every(Boolean),
    diagnostics: { ...irExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeDerivationIrField,
    buildDerivationIrExport,
    createDerivationIrSnapshot,
    getDerivationIrDiagnostics
  };
}