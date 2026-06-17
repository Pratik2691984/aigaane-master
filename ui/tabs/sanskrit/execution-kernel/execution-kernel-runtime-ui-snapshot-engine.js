"use strict";

const {
  buildRuntimeUiSnapshotRecord,
  normalizeRuntimeUiSnapshotRecord
} = require("./execution-kernel-runtime-ui-snapshot-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiSnapshots(record = {}) {
  const snapshots = [
    "runtime-ui-snapshot-surface",
    "runtime-controller-reference",
    "runtime-panel-reference",
    "runtime-view-reference",
    "runtime-session-reference",
    "runtime-workspace-reference",
    "runtime-readonly-reference",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    snapshots.push("warning-reference-ui-snapshot");
  }

  return freeze(snapshots);
}

function createRuntimeUiSnapshotRecord(record = {}) {
  const snapshots = deriveRuntimeUiSnapshots(record);

  return buildRuntimeUiSnapshotRecord({
    ...record,

    uiSnapshotStatus: "ui-snapshot-ready",
    uiSnapshotMode: "inspection-ui-snapshot",

    snapshotCount: snapshots.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    snapshots,

    diagnostics: {
      readOnly: true,
      uiSnapshotBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      uiSnapshotMetadataOnly: true
    }
  });
}

function inspectRuntimeUiSnapshotRecord(record = {}) {
  const normalized = normalizeRuntimeUiSnapshotRecord(record);

  return freeze({
    readOnly: true,
    snapshotCount: normalized.snapshots.length,
    uiSnapshotBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiSnapshotRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiSnapshots,
  createRuntimeUiSnapshotRecord,
  inspectRuntimeUiSnapshotRecord,
  compareRuntimeUiSnapshotRecords
};