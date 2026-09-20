"use strict";

const {
  buildRuntimeQueryRecord,
  normalizeRuntimeQueryRecord
} = require("./execution-kernel-runtime-query-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeQueryEntries(record = {}) {
  const entries = [
    "runtime-query-surface",
    "runtime-lookup-reference",
    "runtime-directory-reference",
    "runtime-index-reference",
    "runtime-registry-reference",
    "runtime-catalog-reference",
    "runtime-manifest-reference",
    "runtime-archive-reference",
    "runtime-import-reference",
    "runtime-export-reference",
    "runtime-readonly-reference",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    entries.push("warning-reference-query");
  }

  return freeze(entries);
}

function createRuntimeQueryRecord(record = {}) {
  const entries = deriveRuntimeQueryEntries(record);

  return buildRuntimeQueryRecord({
    ...record,

    queryStatus: "query-ready",
    queryMode: "inspection-query",

    entryCount: entries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    entries,

    diagnostics: {
      readOnly: true,
      queryBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      queryMetadataOnly: true
    }
  });
}

function inspectRuntimeQueryRecord(record = {}) {
  const normalized = normalizeRuntimeQueryRecord(record);

  return freeze({
    readOnly: true,
    queryBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true,

    entryCount: normalized.entries.length
  });
}

function compareRuntimeQueryRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeQueryEntries,
  createRuntimeQueryRecord,
  inspectRuntimeQueryRecord,
  compareRuntimeQueryRecords
};