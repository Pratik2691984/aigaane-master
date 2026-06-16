"use strict";

const {
  buildRuntimeExplorerRecord,
  normalizeRuntimeExplorerRecord
} = require("./execution-kernel-runtime-explorer-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeExplorerItems(record = {}) {
  const items = [
    "runtime-explorer-surface",
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
    items.push("warning-reference-explorer");
  }

  return freeze(items);
}

function createRuntimeExplorerRecord(record = {}) {
  const items = deriveRuntimeExplorerItems(record);

  return buildRuntimeExplorerRecord({
    ...record,

    explorerStatus: "explorer-ready",
    explorerMode: "inspection-explorer",

    itemCount: items.length,
    warningCount: (record.warnings || []).length,

    items,

    diagnostics: {
      readOnly: true,
      explorerBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      explorerMetadataOnly: true
    }
  });
}

function inspectRuntimeExplorerRecord(record = {}) {
  const normalized = normalizeRuntimeExplorerRecord(record);

  return freeze({
    readOnly: true,
    itemCount: normalized.items.length,
    explorerBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeExplorerRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeExplorerItems,
  createRuntimeExplorerRecord,
  inspectRuntimeExplorerRecord,
  compareRuntimeExplorerRecords
};