"use strict";

const UI_LEDGER_SEAL_SCHEMA = "sanskrit-runtime-ui-ledger-seal.v1";

const UI_LEDGER_SEAL_STATES = Object.freeze({
  EMPTY: "EMPTY",
  UI_LEDGER_SEAL_READY: "UI_LEDGER_SEAL_READY",
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

function normalizeRuntimeUiLedgerSealRecord(input = {}) {
  return freeze({
    uiLedgerSealId: String(input.uiLedgerSealId || "runtime-ui-ledger-seal"),
    createdAt: String(input.createdAt || "static"),

    sourceArchiveSealId: String(
      input.sourceArchiveSealId || "runtime-ui-archive-seal"
    ),
    sourceImportSealId: String(input.sourceImportSealId || "runtime-ui-import-seal"),
    sourceExportSealId: String(input.sourceExportSealId || "runtime-ui-export-seal"),
    sourceCertificationSealId: String(
      input.sourceCertificationSealId || "runtime-ui-certification-seal"
    ),

    uiLedgerSealStatus: String(input.uiLedgerSealStatus || "ui-ledger-seal-ready"),
    uiLedgerSealMode: String(input.uiLedgerSealMode || "inspection-ui-ledger-seal"),

    ledgerSealAllowed: false,
    archiveSealAllowed: false,
    importSealAllowed: false,
    exportSealAllowed: false,
    certificationSealAllowed: false,
    controllerAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    ledgerSealEntryCount: asCount(input.ledgerSealEntryCount),
    warningCount: asCount(input.warningCount),

    ledgerSealEntries: freeze(
      Array.isArray(input.ledgerSealEntries) ? input.ledgerSealEntries : []
    ),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiLedgerSealRecord(input = {}) {
  const normalized = normalizeRuntimeUiLedgerSealRecord(input);

  return freeze({
    schemaVersion: UI_LEDGER_SEAL_SCHEMA,
    state: normalized.ledgerSealEntries.length
      ? UI_LEDGER_SEAL_STATES.UI_LEDGER_SEAL_READY
      : UI_LEDGER_SEAL_STATES.EMPTY,
    ...normalized
  });
}

module.exports = {
  UI_LEDGER_SEAL_SCHEMA,
  UI_LEDGER_SEAL_STATES,
  normalizeRuntimeUiLedgerSealRecord,
  buildRuntimeUiLedgerSealRecord
};