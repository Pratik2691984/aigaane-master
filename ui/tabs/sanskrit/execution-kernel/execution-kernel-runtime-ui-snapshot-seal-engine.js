"use strict";

const {
  buildRuntimeUiSnapshotSealRecord,
  normalizeRuntimeUiSnapshotSealRecord
} = require("./execution-kernel-runtime-ui-snapshot-seal-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiSnapshotSealEntries(record = {}) {
  const snapshotSealEntries = [
    "runtime-ui-snapshot-seal-surface",
    "runtime-ui-seal-reference",
    "runtime-ui-assurance-reference",
    "runtime-ui-integrity-reference",
    "runtime-ui-governance-reference",
    "runtime-ui-certification-reference",
    "runtime-ui-audit-reference",
    "runtime-ui-replay-reference",
    "runtime-ui-snapshot-reference",
    "runtime-controller-reference",
    "runtime-readonly-reference",
    "ui-snapshot-seal-inspection-only",
    "ui-snapshot-seal-immutable",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    snapshotSealEntries.push("warning-reference-ui-snapshot-seal");
  }

  return freeze(snapshotSealEntries);
}

function createRuntimeUiSnapshotSealRecord(record = {}) {
  const snapshotSealEntries = deriveRuntimeUiSnapshotSealEntries(record);

  return buildRuntimeUiSnapshotSealRecord({
    ...record,

    uiSnapshotSealStatus: "ui-snapshot-seal-ready",
    uiSnapshotSealMode: "inspection-ui-snapshot-seal",

    snapshotSealEntryCount: snapshotSealEntries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    snapshotSealEntries,

    diagnostics: {
      readOnly: true,
      immutableSnapshotSeal: true,
      uiSnapshotSealBlocked: true,
      uiSealBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      uiSnapshotSealMetadataOnly: true,
      sourceLayer: "runtime-ui-seal"
    }
  });
}

function inspectRuntimeUiSnapshotSealRecord(record = {}) {
  const normalized = normalizeRuntimeUiSnapshotSealRecord(record);

  return freeze({
    readOnly: true,
    immutableSnapshotSeal: true,
    snapshotSealEntryCount: normalized.snapshotSealEntries.length,
    uiSnapshotSealBlocked: true,
    uiSealBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiSnapshotSealRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiSnapshotSealEntries,
  createRuntimeUiSnapshotSealRecord,
  inspectRuntimeUiSnapshotSealRecord,
  compareRuntimeUiSnapshotSealRecords
};