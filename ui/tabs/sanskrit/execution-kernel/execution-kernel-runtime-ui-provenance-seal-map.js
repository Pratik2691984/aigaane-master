"use strict";

const UI_PROVENANCE_SEAL_SCHEMA =
  "sanskrit-runtime-ui-provenance-seal.v1";

const UI_PROVENANCE_SEAL_STATES = Object.freeze({
  EMPTY: "EMPTY",
  UI_PROVENANCE_SEAL_READY: "UI_PROVENANCE_SEAL_READY",
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

function normalizeRuntimeUiProvenanceSealRecord(input = {}) {
  return freeze({
    uiProvenanceSealId: String(
      input.uiProvenanceSealId || "runtime-ui-provenance-seal"
    ),
    createdAt: String(input.createdAt || "static"),

    sourceIntegritySealId: String(
      input.sourceIntegritySealId || "runtime-ui-integrity-seal"
    ),
    sourceRegistrySealId: String(
      input.sourceRegistrySealId || "runtime-ui-registry-seal"
    ),
    sourceEvidenceSealId: String(
      input.sourceEvidenceSealId || "runtime-ui-evidence-seal"
    ),
    sourceLedgerSealId: String(
      input.sourceLedgerSealId || "runtime-ui-ledger-seal"
    ),

    uiProvenanceSealStatus: String(
      input.uiProvenanceSealStatus || "ui-provenance-seal-ready"
    ),
    uiProvenanceSealMode: String(
      input.uiProvenanceSealMode || "inspection-ui-provenance-seal"
    ),

    provenanceSealAllowed: false,
    integritySealAllowed: false,
    registrySealAllowed: false,
    evidenceSealAllowed: false,
    ledgerSealAllowed: false,
    controllerAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    provenanceSealEntryCount: asCount(input.provenanceSealEntryCount),
    warningCount: asCount(input.warningCount),

    provenanceSealEntries: freeze(
      Array.isArray(input.provenanceSealEntries)
        ? input.provenanceSealEntries
        : []
    ),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiProvenanceSealRecord(input = {}) {
  const normalized = normalizeRuntimeUiProvenanceSealRecord(input);

  return freeze({
    schemaVersion: UI_PROVENANCE_SEAL_SCHEMA,
    state: normalized.provenanceSealEntries.length
      ? UI_PROVENANCE_SEAL_STATES.UI_PROVENANCE_SEAL_READY
      : UI_PROVENANCE_SEAL_STATES.EMPTY,
    ...normalized
  });
}

module.exports = {
  UI_PROVENANCE_SEAL_SCHEMA,
  UI_PROVENANCE_SEAL_STATES,
  normalizeRuntimeUiProvenanceSealRecord,
  buildRuntimeUiProvenanceSealRecord
};