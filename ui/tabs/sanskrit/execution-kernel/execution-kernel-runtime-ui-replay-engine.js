"use strict";

const {
  buildRuntimeUiReplayRecord,
  normalizeRuntimeUiReplayRecord
} = require("./execution-kernel-runtime-ui-replay-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiReplayFrames(record = {}) {
  const replayFrames = [
    "runtime-ui-replay-surface",
    "runtime-ui-snapshot-reference",
    "runtime-controller-reference",
    "runtime-panel-reference",
    "runtime-view-reference",
    "runtime-session-reference",
    "runtime-workspace-reference",
    "runtime-readonly-reference",
    "ui-replay-inspection-only",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    replayFrames.push("warning-reference-ui-replay");
  }

  return freeze(replayFrames);
}

function createRuntimeUiReplayRecord(record = {}) {
  const replayFrames = deriveRuntimeUiReplayFrames(record);

  return buildRuntimeUiReplayRecord({
    ...record,

    uiReplayStatus: "ui-replay-ready",
    uiReplayMode: "inspection-ui-replay",

    replayFrameCount: replayFrames.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    replayFrames,

    diagnostics: {
      readOnly: true,
      uiReplayBlocked: true,
      replayBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      uiReplayMetadataOnly: true
    }
  });
}

function inspectRuntimeUiReplayRecord(record = {}) {
  const normalized = normalizeRuntimeUiReplayRecord(record);

  return freeze({
    readOnly: true,
    replayFrameCount: normalized.replayFrames.length,
    uiReplayBlocked: true,
    replayBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeUiReplayRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeUiReplayFrames,
  createRuntimeUiReplayRecord,
  inspectRuntimeUiReplayRecord,
  compareRuntimeUiReplayRecords
};