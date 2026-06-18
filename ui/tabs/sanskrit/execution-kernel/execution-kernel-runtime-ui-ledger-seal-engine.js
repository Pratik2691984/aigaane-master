"use strict";

const {
  buildRuntimeUiLedgerSealRecord,
  normalizeRuntimeUiLedgerSealRecord
} = require("./execution-kernel-runtime-ui-ledger-seal-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiLedgerSealEntries(record = {}) {
  const entries = [
    "runtime-ui-ledger-surface",

    "runtime-ui-archive-reference",
    "runtime-ui-import-reference",
    "runtime-ui-export-reference",
    "runtime-ui-certification-reference",

    "runtime-ledger-reference",

    "ledger-inspection-only",
    "ledger-evidence-immutable",
    "ledger-metadata-only",

    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    entries.push("warning-reference-ui-ledger");
  }

  return freeze(entries);
}

function createRuntimeUiLedgerSealRecord(record = {}) {
  const entries = deriveRuntimeUiLedgerSealEntries(record);

  return buildRuntimeUiLedgerSealRecord({
    ...record,

    uiLedgerSealStatus: "ui-ledger-seal-ready",
    uiLedgerSealMode: "inspection-ui-ledger-seal",

    ledgerSealEntryCount: entries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    ledgerSealEntries: entries,

    diagnostics: {
      readOnly: true,

      ledgerSealBlocked: true,
      archiveSealBlocked: true,
      importSealBlocked: true,
      exportSealBlocked: true,
      certificationSealBlocked: true,

      ledgerExecutionBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,

      canonicalWriteBlocked: true
    },

    metadata: {
      ledgerMetadataOnly: true
    }
  });
}

function inspectRuntimeUiLedgerSealRecord(record = {}) {
  const normalized = normalizeRuntimeUiLedgerSealRecord(record);

  return freeze({
    readOnly: true,

    entryCount: normalized.ledgerSealEntries.length,

    ledgerSealBlocked: true,
    archiveSealBlocked: true,
    importSealBlocked: true,
    exportSealBlocked: true,
    certificationSealBlocked: true,

    ledgerExecutionBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,

    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiLedgerSealRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiLedgerSealEntries,
  createRuntimeUiLedgerSealRecord,
  inspectRuntimeUiLedgerSealRecord,
  compareRuntimeUiLedgerSealRecords
};