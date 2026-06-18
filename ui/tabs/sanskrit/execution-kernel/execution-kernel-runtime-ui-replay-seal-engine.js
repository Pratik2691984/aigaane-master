"use strict";

const {
  buildRuntimeUiReplaySealRecord,
  normalizeRuntimeUiReplaySealRecord
} = require("./execution-kernel-runtime-ui-replay-seal-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiReplaySealEntries(record = {}) {
  const replaySealEntries = [
    "runtime-ui-replay-seal-surface",
    "runtime-ui-snapshot-seal-reference",
    "runtime-ui-seal-reference",
    "runtime-controller-reference",
    "runtime-readonly-reference",
    "replay-seal-metadata-only",
    "replay-seal-inspection-only",
    "replay-seal-immutable",
    "replay-seal-denied",
    "replay-execution-denied",
    "snapshot-seal-denied",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    replaySealEntries.push("warning-reference-ui-replay-seal");
  }

  return freeze(replaySealEntries);
}

function createRuntimeUiReplaySealRecord(record = {}) {
  const replaySealEntries = deriveRuntimeUiReplaySealEntries(record);

  return buildRuntimeUiReplaySealRecord({
    ...record,

    replaySealStatus: "replay-seal-ready",
    replaySealMode: "inspection-replay-seal",

    replaySealEntryCount: replaySealEntries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    replaySealEntries,

    diagnostics: {
      readOnly: true,
      replaySealBlocked: true,
      replayExecutionBlocked: true,
      snapshotSealBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      replaySealMetadataOnly: true,
      replayExecutionSuppressed: true,
      sourceLayer: "runtime-ui-snapshot-seal"
    }
  });
}

function inspectRuntimeUiReplaySealRecord(record = {}) {
  const normalized = normalizeRuntimeUiReplaySealRecord(record);

  return freeze({
    readOnly: true,
    replaySealEntryCount: normalized.replaySealEntries.length,
    replaySealBlocked: true,
    replayExecutionBlocked: true,
    snapshotSealBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiReplaySealRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiReplaySealEntries,
  createRuntimeUiReplaySealRecord,
  inspectRuntimeUiReplaySealRecord,
  compareRuntimeUiReplaySealRecords
};
