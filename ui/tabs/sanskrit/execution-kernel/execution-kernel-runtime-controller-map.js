"use strict";

const CONTROLLER_SCHEMA = "sanskrit-runtime-controller.v1";

const CONTROLLER_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  CONTROLLER_READY: "CONTROLLER_READY",
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

function normalizeRuntimeControllerRecord(input = {}) {
  return freeze({
    controllerId: String(input.controllerId || "runtime-controller"),
    createdAt: String(input.createdAt || "static"),

    sourcePanelId: String(input.sourcePanelId || "runtime-panel"),
    sourcePanelStatus: String(input.sourcePanelStatus || "panel-ready"),
    sourcePanelMode: String(input.sourcePanelMode || "inspection-panel"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    controllerStatus: String(input.controllerStatus || "controller-ready"),
    controllerMode: String(input.controllerMode || "inspection-controller"),

    controllerAllowed: false,
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

    bindingCount: asCount(input.bindingCount),
    warningCount: asCount(input.warningCount),

    bindings: freeze(Array.isArray(input.bindings) ? input.bindings : []),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeControllerRecord(input = {}) {
  const normalized = normalizeRuntimeControllerRecord(input);

  return freeze({
    schemaVersion: CONTROLLER_SCHEMA,
    state: normalized.bindings.length > 0
      ? CONTROLLER_STATES.CONTROLLER_READY
      : CONTROLLER_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeControllerRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.bindings)) errors.push("bindings");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  CONTROLLER_SCHEMA,
  CONTROLLER_STATES,
  normalizeRuntimeControllerRecord,
  buildRuntimeControllerRecord,
  validateRuntimeControllerRecord
};