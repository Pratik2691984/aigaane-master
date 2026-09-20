"use strict";

const {
  buildRuntimeSearchRecord,
  normalizeRuntimeSearchRecord
} = require("./execution-kernel-runtime-search-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeSearchResults(record = {}) {
  const results = [
    "runtime-search-surface",
    "runtime-query-reference",
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
    results.push("warning-reference-search");
  }

  return freeze(results);
}

function createRuntimeSearchRecord(record = {}) {
  const results = deriveRuntimeSearchResults(record);

  return buildRuntimeSearchRecord({
    ...record,

    searchStatus: "search-ready",
    searchMode: "inspection-search",

    resultCount: results.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    results,

    diagnostics: {
      readOnly: true,
      searchBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      searchMetadataOnly: true
    }
  });
}

function inspectRuntimeSearchRecord(record = {}) {
  const normalized = normalizeRuntimeSearchRecord(record);

  return freeze({
    readOnly: true,
    searchBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true,

    resultCount: normalized.results.length
  });
}

function compareRuntimeSearchRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeSearchResults,
  createRuntimeSearchRecord,
  inspectRuntimeSearchRecord,
  compareRuntimeSearchRecords
};