"use strict";

const UI_REPLAY_SCHEMA = "sanskrit-runtime-ui-replay.v1";

const UI_REPLAY_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  UI_REPLAY_READY: "UI_REPLAY_READY",
  BLOCKED: "BLOCKED",
  REVIEW_ONLY: "REVIEW_ONLY"
});

function freeze(v) {
  return Object.freeze(v);
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function asCount(v) {
  const n = Number(v || 0);
  return Number.isFinite(n) ? Math.max(0, Math.floor(n)) : 0;
}

function normalizeRuntimeUiReplayRecord(input = {}) {
  return freeze({
    uiReplayId: String(input.uiReplayId || "runtime-ui-replay"),
    createdAt: String(input.createdAt || "static"),

    sourceUiSnapshotId: String(input.sourceUiSnapshotId || "runtime-ui-snapshot"),
    sourceUiSnapshotStatus: String(input.sourceUiSnapshotStatus || "ui-snapshot-ready"),
    sourceUiSnapshotMode: String(input.sourceUiSnapshotMode || "inspection-ui-snapshot"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    uiReplayStatus: String(input.uiReplayStatus || "ui-replay-ready"),
    uiReplayMode: String(input.uiReplayMode || "inspection-ui-replay"),

    uiReplayAllowed: false,
    uiSnapshotAllowed: false,
    controllerAllowed: false,
    panelAllowed: false,
    viewAllowed: false,
    sessionAllowed: false,
    workspaceAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    replayFrameCount: asCount(input.replayFrameCount),
    warningCount: asCount(input.warningCount),

    replayFrames: freeze(Array.isArray(input.replayFrames) ? input.replayFrames : []),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiReplayRecord(input = {}) {
  const normalized = normalizeRuntimeUiReplayRecord(input);

  return freeze({
    schemaVersion: UI_REPLAY_SCHEMA,
    state: normalized.replayFrames.length > 0
      ? UI_REPLAY_STATES.UI_REPLAY_READY
      : UI_REPLAY_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeUiReplayRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.replayFrames)) errors.push("replayFrames");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  UI_REPLAY_SCHEMA,
  UI_REPLAY_STATES,
  normalizeRuntimeUiReplayRecord,
  buildRuntimeUiReplayRecord,
  validateRuntimeUiReplayRecord
};