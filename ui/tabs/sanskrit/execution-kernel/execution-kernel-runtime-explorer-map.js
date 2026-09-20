"use strict";

const EXPLORER_SCHEMA = "sanskrit-runtime-explorer.v1";

const EXPLORER_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  EXPLORER_READY: "EXPLORER_READY",
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

function normalizeRuntimeExplorerRecord(input = {}) {
  return freeze({
    explorerId: String(input.explorerId || "runtime-explorer"),
    createdAt: String(input.createdAt || "static"),

    sourceNavigatorId: String(input.sourceNavigatorId || "runtime-navigator"),
    sourceNavigatorStatus: String(
      input.sourceNavigatorStatus || "navigator-ready"
    ),
    sourceNavigatorMode: String(
      input.sourceNavigatorMode || "inspection-navigator"
    ),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    explorerStatus: String(input.explorerStatus || "explorer-ready"),
    explorerMode: String(input.explorerMode || "inspection-explorer"),

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

    itemCount: asCount(input.itemCount),
    warningCount: asCount(input.warningCount),

    items: freeze(Array.isArray(input.items) ? input.items : []),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeExplorerRecord(input = {}) {
  const normalized = normalizeRuntimeExplorerRecord(input);

  return freeze({
    schemaVersion: EXPLORER_SCHEMA,
    state:
      normalized.items.length > 0
        ? EXPLORER_STATES.EXPLORER_READY
        : EXPLORER_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeExplorerRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.items)) errors.push("items");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  EXPLORER_SCHEMA,
  EXPLORER_STATES,
  normalizeRuntimeExplorerRecord,
  buildRuntimeExplorerRecord,
  validateRuntimeExplorerRecord
};