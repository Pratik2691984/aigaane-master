"use strict";

const UI_REPLAY_SEAL_SCHEMA = "sanskrit-runtime-ui-replay-seal.v1";

const UI_REPLAY_SEAL_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  UI_REPLAY_SEAL_READY: "UI_REPLAY_SEAL_READY",
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

function normalizeRuntimeUiReplaySealRecord(input = {}) {
  return freeze({
    replaySealId: String(input.replaySealId || "runtime-ui-replay-seal"),
    createdAt: String(input.createdAt || "static"),

    sourceUiSnapshotSealId: String(
      input.sourceUiSnapshotSealId || "runtime-ui-snapshot-seal"
    ),
    sourceUiSnapshotSealStatus: String(
      input.sourceUiSnapshotSealStatus || "ui-snapshot-seal-ready"
    ),
    sourceUiSnapshotSealMode: String(
      input.sourceUiSnapshotSealMode || "inspection-ui-snapshot-seal"
    ),

    sourceUiSealId: String(input.sourceUiSealId || "runtime-ui-seal"),
    sourceUiSealStatus: String(input.sourceUiSealStatus || "ui-seal-ready"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    replaySealStatus: String(input.replaySealStatus || "replay-seal-ready"),
    replaySealMode: String(input.replaySealMode || "inspection-replay-seal"),

    replaySealAllowed: false,
    uiSnapshotSealAllowed: false,
    uiSealAllowed: false,
    controllerAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    replaySealEntryCount: asCount(input.replaySealEntryCount),
    warningCount: asCount(input.warningCount),

    replaySealEntries: freeze(
      Array.isArray(input.replaySealEntries) ? input.replaySealEntries : []
    ),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiReplaySealRecord(input = {}) {
  const normalized = normalizeRuntimeUiReplaySealRecord(input);

  return freeze({
    schemaVersion: UI_REPLAY_SEAL_SCHEMA,
    state: normalized.replaySealEntries.length > 0
      ? UI_REPLAY_SEAL_STATES.UI_REPLAY_SEAL_READY
      : UI_REPLAY_SEAL_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeUiReplaySealRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.replaySealEntries)) {
    errors.push("replaySealEntries");
  }
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  UI_REPLAY_SEAL_SCHEMA,
  UI_REPLAY_SEAL_STATES,
  normalizeRuntimeUiReplaySealRecord,
  buildRuntimeUiReplaySealRecord,
  validateRuntimeUiReplaySealRecord
};
