"use strict";

const PANEL_SCHEMA = "sanskrit-runtime-panel.v1";

const PANEL_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  PANEL_READY: "PANEL_READY",
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

function normalizeRuntimePanelRecord(input = {}) {
  return freeze({
    panelId: String(input.panelId || "runtime-panel"),
    createdAt: String(input.createdAt || "static"),

    sourceViewId: String(input.sourceViewId || "runtime-view"),
    sourceViewStatus: String(input.sourceViewStatus || "view-ready"),
    sourceViewMode: String(input.sourceViewMode || "inspection-view"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    panelStatus: String(input.panelStatus || "panel-ready"),
    panelMode: String(input.panelMode || "inspection-panel"),

    panelAllowed: false,
    viewAllowed: false,
    sessionAllowed: false,
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

    sectionCount: asCount(input.sectionCount),
    warningCount: asCount(input.warningCount),

    sections: freeze(Array.isArray(input.sections) ? input.sections : []),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimePanelRecord(input = {}) {
  const normalized = normalizeRuntimePanelRecord(input);

  return freeze({
    schemaVersion: PANEL_SCHEMA,
    state: normalized.sections.length > 0
      ? PANEL_STATES.PANEL_READY
      : PANEL_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimePanelRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.sections)) errors.push("sections");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  PANEL_SCHEMA,
  PANEL_STATES,
  normalizeRuntimePanelRecord,
  buildRuntimePanelRecord,
  validateRuntimePanelRecord
};