"use strict";

const {
  buildRuntimeUiSealRecord,
  normalizeRuntimeUiSealRecord
} = require("./execution-kernel-runtime-ui-seal-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiSealEntries(record = {}) {
  const sealEntries = [
    "runtime-ui-seal-surface",
    "runtime-ui-assurance-reference",
    "runtime-ui-integrity-reference",
    "runtime-ui-governance-reference",
    "runtime-ui-certification-reference",
    "runtime-ui-audit-reference",
    "runtime-ui-replay-reference",
    "runtime-ui-snapshot-reference",
    "runtime-controller-reference",
    "runtime-readonly-reference",
    "ui-seal-inspection-only",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    sealEntries.push("warning-reference-ui-seal");
  }

  return freeze(sealEntries);
}

function createRuntimeUiSealRecord(record = {}) {
  const sealEntries = deriveRuntimeUiSealEntries(record);

  return buildRuntimeUiSealRecord({
    ...record,

    uiSealStatus: "ui-seal-ready",
    uiSealMode: "inspection-ui-seal",

    sealEntryCount: sealEntries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    sealEntries,

    diagnostics: {
      readOnly: true,
      uiSealBlocked: true,
      sealBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      uiSealMetadataOnly: true
    }
  });
}

function inspectRuntimeUiSealRecord(record = {}) {
  const normalized = normalizeRuntimeUiSealRecord(record);

  return freeze({
    readOnly: true,
    sealEntryCount: normalized.sealEntries.length,
    uiSealBlocked: true,
    sealBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiSealRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiSealEntries,
  createRuntimeUiSealRecord,
  inspectRuntimeUiSealRecord,
  compareRuntimeUiSealRecords
};