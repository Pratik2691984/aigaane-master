"use strict";

const {
  buildRuntimeUiIntegrityRecord,
  normalizeRuntimeUiIntegrityRecord
} = require("./execution-kernel-runtime-ui-integrity-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiIntegrityEntries(record = {}) {
  const integrityEntries = [
    "runtime-ui-integrity-surface",
    "runtime-ui-governance-reference",
    "runtime-ui-certification-reference",
    "runtime-ui-audit-reference",
    "runtime-ui-replay-reference",
    "runtime-ui-snapshot-reference",
    "runtime-controller-reference",
    "runtime-panel-reference",
    "runtime-view-reference",
    "runtime-readonly-reference",
    "ui-integrity-inspection-only",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    integrityEntries.push("warning-reference-ui-integrity");
  }

  return freeze(integrityEntries);
}

function createRuntimeUiIntegrityRecord(record = {}) {
  const integrityEntries = deriveRuntimeUiIntegrityEntries(record);

  return buildRuntimeUiIntegrityRecord({
    ...record,

    uiIntegrityStatus: "ui-integrity-ready",
    uiIntegrityMode: "inspection-ui-integrity",

    integrityEntryCount: integrityEntries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    integrityEntries,

    diagnostics: {
      readOnly: true,
      uiIntegrityBlocked: true,
      integrityBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      uiIntegrityMetadataOnly: true
    }
  });
}

function inspectRuntimeUiIntegrityRecord(record = {}) {
  const normalized = normalizeRuntimeUiIntegrityRecord(record);

  return freeze({
    readOnly: true,
    integrityEntryCount: normalized.integrityEntries.length,
    uiIntegrityBlocked: true,
    integrityBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiIntegrityRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiIntegrityEntries,
  createRuntimeUiIntegrityRecord,
  inspectRuntimeUiIntegrityRecord,
  compareRuntimeUiIntegrityRecords
};