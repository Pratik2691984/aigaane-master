"use strict";

const {
  buildRuntimeUiEvidenceSealRecord,
  normalizeRuntimeUiEvidenceSealRecord
} = require("./execution-kernel-runtime-ui-evidence-seal-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiEvidenceSealEntries(record = {}) {
  const entries = [
    "runtime-ui-evidence-surface",

    "runtime-ui-ledger-reference",
    "runtime-ui-archive-reference",
    "runtime-ui-import-reference",
    "runtime-ui-export-reference",

    "runtime-evidence-reference",

    "evidence-inspection-only",
    "evidence-chain-immutable",
    "evidence-metadata-only",

    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    entries.push("warning-reference-ui-evidence");
  }

  return freeze(entries);
}

function createRuntimeUiEvidenceSealRecord(record = {}) {
  const entries = deriveRuntimeUiEvidenceSealEntries(record);

  return buildRuntimeUiEvidenceSealRecord({
    ...record,

    uiEvidenceSealStatus: "ui-evidence-seal-ready",
    uiEvidenceSealMode: "inspection-ui-evidence-seal",

    evidenceSealEntryCount: entries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    evidenceSealEntries: entries,

    diagnostics: {
      readOnly: true,

      evidenceSealBlocked: true,
      ledgerSealBlocked: true,
      archiveSealBlocked: true,
      importSealBlocked: true,
      exportSealBlocked: true,

      evidenceExecutionBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,

      canonicalWriteBlocked: true
    },

    metadata: {
      evidenceMetadataOnly: true
    }
  });
}

function inspectRuntimeUiEvidenceSealRecord(record = {}) {
  const normalized = normalizeRuntimeUiEvidenceSealRecord(record);

  return freeze({
    readOnly: true,

    entryCount: normalized.evidenceSealEntries.length,

    evidenceSealBlocked: true,
    ledgerSealBlocked: true,
    archiveSealBlocked: true,
    importSealBlocked: true,
    exportSealBlocked: true,

    evidenceExecutionBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,

    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiEvidenceSealRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiEvidenceSealEntries,
  createRuntimeUiEvidenceSealRecord,
  inspectRuntimeUiEvidenceSealRecord,
  compareRuntimeUiEvidenceSealRecords
};