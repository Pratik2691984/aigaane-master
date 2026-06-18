"use strict";

const {
  buildRuntimeUiExportSealRecord,
  normalizeRuntimeUiExportSealRecord
} = require("./execution-kernel-runtime-ui-export-seal-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiExportSealEntries(record = {}) {
  const entries = [
    "runtime-ui-export-surface",
    "runtime-ui-certification-reference",
    "runtime-ui-governance-reference",
    "runtime-ui-audit-reference",
    "runtime-ui-replay-reference",
    "runtime-ui-snapshot-reference",
    "runtime-export-reference",
    "runtime-controller-reference",

    "export-inspection-only",
    "export-evidence-immutable",
    "export-metadata-only",

    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    entries.push("warning-reference-ui-export");
  }

  return freeze(entries);
}

function createRuntimeUiExportSealRecord(record = {}) {
  const entries = deriveRuntimeUiExportSealEntries(record);

  return buildRuntimeUiExportSealRecord({
    ...record,

    uiExportSealStatus: "ui-export-seal-ready",
    uiExportSealMode: "inspection-ui-export-seal",

    exportSealEntryCount: entries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    exportSealEntries: entries,

    diagnostics: {
      readOnly: true,

      exportSealBlocked: true,
      certificationSealBlocked: true,
      governanceSealBlocked: true,
      auditSealBlocked: true,
      replaySealBlocked: true,
      snapshotSealBlocked: true,

      exportExecutionBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,

      canonicalWriteBlocked: true
    },

    metadata: {
      exportMetadataOnly: true
    }
  });
}

function inspectRuntimeUiExportSealRecord(record = {}) {
  const normalized = normalizeRuntimeUiExportSealRecord(record);

  return freeze({
    readOnly: true,

    entryCount: normalized.exportSealEntries.length,

    exportSealBlocked: true,
    certificationSealBlocked: true,
    governanceSealBlocked: true,
    auditSealBlocked: true,
    replaySealBlocked: true,
    snapshotSealBlocked: true,

    exportExecutionBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,

    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiExportSealRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiExportSealEntries,
  createRuntimeUiExportSealRecord,
  inspectRuntimeUiExportSealRecord,
  compareRuntimeUiExportSealRecords
};