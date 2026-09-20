"use strict";

const UI_CLOSURE_SEAL_SCHEMA =
  "sanskrit-runtime-ui-closure-seal.v1";

const UI_CLOSURE_SEAL_STATES = Object.freeze({
  EMPTY: "EMPTY",
  UI_CLOSURE_SEAL_READY: "UI_CLOSURE_SEAL_READY",
  BLOCKED: "BLOCKED",
  REVIEW_ONLY: "REVIEW_ONLY"
});

function freeze(v) {
  return Object.freeze(v);
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function asCount(v) {
  const n = Number(v || 0);
  return Number.isFinite(n) ? Math.max(0, Math.floor(n)) : 0;
}

function normalizeRuntimeUiClosureSealRecord(input = {}) {
  return freeze({
    uiClosureSealId: String(
      input.uiClosureSealId || "runtime-ui-closure-seal"
    ),
    createdAt: String(input.createdAt || "static"),

    sourceAttestationSealId: String(
      input.sourceAttestationSealId || "runtime-ui-attestation-seal"
    ),
    sourceProvenanceSealId: String(
      input.sourceProvenanceSealId || "runtime-ui-provenance-seal"
    ),
    sourceIntegritySealId: String(
      input.sourceIntegritySealId || "runtime-ui-integrity-seal"
    ),
    sourceRegistrySealId: String(
      input.sourceRegistrySealId || "runtime-ui-registry-seal"
    ),

    uiClosureSealStatus: String(
      input.uiClosureSealStatus || "ui-closure-seal-ready"
    ),
    uiClosureSealMode: String(
      input.uiClosureSealMode || "inspection-ui-closure-seal"
    ),

    closureSealAllowed: false,
    attestationSealAllowed: false,
    provenanceSealAllowed: false,
    integritySealAllowed: false,
    registrySealAllowed: false,
    controllerAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    closureSealEntryCount: asCount(input.closureSealEntryCount),
    warningCount: asCount(input.warningCount),

    closureSealEntries: freeze(
      Array.isArray(input.closureSealEntries)
        ? input.closureSealEntries
        : []
    ),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiClosureSealRecord(input = {}) {
  const normalized = normalizeRuntimeUiClosureSealRecord(input);

  return freeze({
    schemaVersion: UI_CLOSURE_SEAL_SCHEMA,
    state: normalized.closureSealEntries.length
      ? UI_CLOSURE_SEAL_STATES.UI_CLOSURE_SEAL_READY
      : UI_CLOSURE_SEAL_STATES.EMPTY,
    ...normalized
  });
}

module.exports = {
  UI_CLOSURE_SEAL_SCHEMA,
  UI_CLOSURE_SEAL_STATES,
  normalizeRuntimeUiClosureSealRecord,
  buildRuntimeUiClosureSealRecord
};