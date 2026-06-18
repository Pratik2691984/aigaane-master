"use strict";

const {
  buildRuntimeUiImportSealRecord,
  normalizeRuntimeUiImportSealRecord
} = require("./execution-kernel-runtime-ui-import-seal-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiImportSealEntries(record = {}) {
  const entries = [
    "runtime-ui-import-surface",
    "runtime-ui-export-reference",
    "runtime-ui-certification-reference",
    "runtime-ui-governance-reference",
    "runtime-ui-audit-reference",
    "runtime-ui-replay-reference",
    "runtime-ui-snapshot-reference",
    "runtime-import-reference",
    "runtime-controller-reference",

    "import-inspection-only",
    "import-evidence-immutable",
    "import-metadata-only",

    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    entries.push("warning-reference-ui-import");
  }

  return freeze(entries);
}

function createRuntimeUiImportSealRecord(record = {}) {
  const entries = deriveRuntimeUiImportSealEntries(record);

  return buildRuntimeUiImportSealRecord({
    ...record,

    uiImportSealStatus: "ui-import-seal-ready",
    uiImportSealMode: "inspection-ui-import-seal",

    importSealEntryCount: entries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    importSealEntries: entries,

    diagnostics: {
      readOnly: true,

      importSealBlocked: true,
      exportSealBlocked: true,
      certificationSealBlocked: true,
      governanceSealBlocked: true,
      auditSealBlocked: true,
      replaySealBlocked: true,
      snapshotSealBlocked: true,

      importExecutionBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,

      canonicalWriteBlocked: true
    },

    metadata: {
      importMetadataOnly: true
    }
  });
}

function inspectRuntimeUiImportSealRecord(record = {}) {
  const normalized = normalizeRuntimeUiImportSealRecord(record);

  return freeze({
    readOnly: true,

    entryCount: normalized.importSealEntries.length,

    importSealBlocked: true,
    exportSealBlocked: true,
    certificationSealBlocked: true,
    governanceSealBlocked: true,
    auditSealBlocked: true,
    replaySealBlocked: true,
    snapshotSealBlocked: true,

    importExecutionBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,

    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiImportSealRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiImportSealEntries,
  createRuntimeUiImportSealRecord,
  inspectRuntimeUiImportSealRecord,
  compareRuntimeUiImportSealRecords
};