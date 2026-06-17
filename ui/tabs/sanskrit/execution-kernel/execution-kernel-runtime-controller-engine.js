"use strict";

const {
  buildRuntimeControllerRecord,
  normalizeRuntimeControllerRecord
} = require("./execution-kernel-runtime-controller-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeControllerBindings(record = {}) {
  const bindings = [
    "runtime-controller-surface",
    "runtime-panel-reference",
    "runtime-view-reference",
    "runtime-session-reference",
    "runtime-workspace-reference",
    "runtime-explorer-reference",
    "runtime-navigator-reference",
    "runtime-resolver-reference",
    "runtime-search-reference",
    "runtime-query-reference",
    "runtime-readonly-reference",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    bindings.push("warning-reference-controller");
  }

  return freeze(bindings);
}

function createRuntimeControllerRecord(record = {}) {
  const bindings = deriveRuntimeControllerBindings(record);

  return buildRuntimeControllerRecord({
    ...record,

    controllerStatus: "controller-ready",
    controllerMode: "inspection-controller",

    bindingCount: bindings.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    bindings,

    diagnostics: {
      readOnly: true,
      controllerBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      controllerMetadataOnly: true
    }
  });
}

function inspectRuntimeControllerRecord(record = {}) {
  const normalized = normalizeRuntimeControllerRecord(record);

  return freeze({
    readOnly: true,
    bindingCount: normalized.bindings.length,
    controllerBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeControllerRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeControllerBindings,
  createRuntimeControllerRecord,
  inspectRuntimeControllerRecord,
  compareRuntimeControllerRecords
};