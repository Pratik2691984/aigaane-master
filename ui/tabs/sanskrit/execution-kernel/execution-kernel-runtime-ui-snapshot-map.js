"use strict";

const UI_SNAPSHOT_SCHEMA = "sanskrit-runtime-ui-snapshot.v1";

const UI_SNAPSHOT_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  UI_SNAPSHOT_READY: "UI_SNAPSHOT_READY",
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

function normalizeRuntimeUiSnapshotRecord(input = {}) {
  return freeze({
    uiSnapshotId: String(input.uiSnapshotId || "runtime-ui-snapshot"),
    createdAt: String(input.createdAt || "static"),

    sourceControllerId: String(input.sourceControllerId || "runtime-controller"),
    sourceControllerStatus: String(input.sourceControllerStatus || "controller-ready"),
    sourceControllerMode: String(input.sourceControllerMode || "inspection-controller"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    uiSnapshotStatus: String(input.uiSnapshotStatus || "ui-snapshot-ready"),
    uiSnapshotMode: String(input.uiSnapshotMode || "inspection-ui-snapshot"),

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

    snapshotCount: asCount(input.snapshotCount),
    warningCount: asCount(input.warningCount),

    snapshots: freeze(Array.isArray(input.snapshots) ? input.snapshots : []),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiSnapshotRecord(input = {}) {
  const normalized = normalizeRuntimeUiSnapshotRecord(input);

  return freeze({
    schemaVersion: UI_SNAPSHOT_SCHEMA,
    state: normalized.snapshots.length > 0
      ? UI_SNAPSHOT_STATES.UI_SNAPSHOT_READY
      : UI_SNAPSHOT_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeUiSnapshotRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.snapshots)) errors.push("snapshots");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  UI_SNAPSHOT_SCHEMA,
  UI_SNAPSHOT_STATES,
  normalizeRuntimeUiSnapshotRecord,
  buildRuntimeUiSnapshotRecord,
  validateRuntimeUiSnapshotRecord
};