"use strict";

const {
  buildRuntimeViewRecord,
  normalizeRuntimeViewRecord
} = require("./execution-kernel-runtime-view-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeViews(record = {}) {
  const views = [
    "runtime-view-surface",
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
    views.push("warning-reference-view");
  }

  return freeze(views);
}

function createRuntimeViewRecord(record = {}) {
  const views = deriveRuntimeViews(record);

  return buildRuntimeViewRecord({
    ...record,

    viewStatus: "view-ready",
    viewMode: "inspection-view",

    viewCount: views.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    views,

    diagnostics: {
      readOnly: true,
      viewBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      viewMetadataOnly: true
    }
  });
}

function inspectRuntimeViewRecord(record = {}) {
  const normalized = normalizeRuntimeViewRecord(record);

  return freeze({
    readOnly: true,
    viewCount: normalized.views.length,
    viewBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeViewRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeViews,
  createRuntimeViewRecord,
  inspectRuntimeViewRecord,
  compareRuntimeViewRecords
};