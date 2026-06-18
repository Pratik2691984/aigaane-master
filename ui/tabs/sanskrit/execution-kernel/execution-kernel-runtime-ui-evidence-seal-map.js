"use strict";

const UI_EVIDENCE_SEAL_SCHEMA = "sanskrit-runtime-ui-evidence-seal.v1";

const UI_EVIDENCE_SEAL_STATES = Object.freeze({
  EMPTY: "EMPTY",
  UI_EVIDENCE_SEAL_READY: "UI_EVIDENCE_SEAL_READY",
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

function normalizeRuntimeUiEvidenceSealRecord(input = {}) {
  return freeze({
    uiEvidenceSealId: String(input.uiEvidenceSealId || "runtime-ui-evidence-seal"),
    createdAt: String(input.createdAt || "static"),

    sourceLedgerSealId: String(input.sourceLedgerSealId || "runtime-ui-ledger-seal"),
    sourceArchiveSealId: String(
      input.sourceArchiveSealId || "runtime-ui-archive-seal"
    ),
    sourceImportSealId: String(input.sourceImportSealId || "runtime-ui-import-seal"),
    sourceExportSealId: String(input.sourceExportSealId || "runtime-ui-export-seal"),

    uiEvidenceSealStatus: String(
      input.uiEvidenceSealStatus || "ui-evidence-seal-ready"
    ),
    uiEvidenceSealMode: String(
      input.uiEvidenceSealMode || "inspection-ui-evidence-seal"
    ),

    evidenceSealAllowed: false,
    ledgerSealAllowed: false,
    archiveSealAllowed: false,
    importSealAllowed: false,
    exportSealAllowed: false,
    controllerAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    evidenceSealEntryCount: asCount(input.evidenceSealEntryCount),
    warningCount: asCount(input.warningCount),

    evidenceSealEntries: freeze(
      Array.isArray(input.evidenceSealEntries) ? input.evidenceSealEntries : []
    ),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiEvidenceSealRecord(input = {}) {
  const normalized = normalizeRuntimeUiEvidenceSealRecord(input);

  return freeze({
    schemaVersion: UI_EVIDENCE_SEAL_SCHEMA,
    state: normalized.evidenceSealEntries.length
      ? UI_EVIDENCE_SEAL_STATES.UI_EVIDENCE_SEAL_READY
      : UI_EVIDENCE_SEAL_STATES.EMPTY,
    ...normalized
  });
}

module.exports = {
  UI_EVIDENCE_SEAL_SCHEMA,
  UI_EVIDENCE_SEAL_STATES,
  normalizeRuntimeUiEvidenceSealRecord,
  buildRuntimeUiEvidenceSealRecord
};