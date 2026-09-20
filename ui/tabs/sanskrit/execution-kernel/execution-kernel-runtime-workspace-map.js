"use strict";

const WORKSPACE_SCHEMA = "sanskrit-runtime-workspace.v1";

const WORKSPACE_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  WORKSPACE_READY: "WORKSPACE_READY",
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

function normalizeRuntimeWorkspaceRecord(input = {}) {
  return freeze({
    workspaceId: String(input.workspaceId || "runtime-workspace"),
    createdAt: String(input.createdAt || "static"),

    sourceExplorerId: String(input.sourceExplorerId || "runtime-explorer"),
    sourceExplorerStatus: String(input.sourceExplorerStatus || "explorer-ready"),
    sourceExplorerMode: String(input.sourceExplorerMode || "inspection-explorer"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    workspaceStatus: String(input.workspaceStatus || "workspace-ready"),
    workspaceMode: String(input.workspaceMode || "inspection-workspace"),

    workspaceAllowed: false,
    explorerAllowed: false,
    navigatorAllowed: false,
    resolverAllowed: false,
    searchAllowed: false,
    queryAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    panelCount: asCount(input.panelCount),
    warningCount: asCount(input.warningCount),

    panels: freeze(Array.isArray(input.panels) ? input.panels : []),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeWorkspaceRecord(input = {}) {
  const normalized = normalizeRuntimeWorkspaceRecord(input);

  return freeze({
    schemaVersion: WORKSPACE_SCHEMA,
    state: normalized.panels.length > 0
      ? WORKSPACE_STATES.WORKSPACE_READY
      : WORKSPACE_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeWorkspaceRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.panels)) errors.push("panels");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  WORKSPACE_SCHEMA,
  WORKSPACE_STATES,
  normalizeRuntimeWorkspaceRecord,
  buildRuntimeWorkspaceRecord,
  validateRuntimeWorkspaceRecord
};