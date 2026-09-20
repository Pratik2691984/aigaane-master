"use strict";

const {
  buildRuntimeResolverRecord,
  normalizeRuntimeResolverRecord
} = require("./execution-kernel-runtime-resolver-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeResolverResolutions(record = {}) {
  const resolutions = [
    "runtime-resolver-surface",
    "runtime-search-reference",
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
    resolutions.push("warning-reference-resolver");
  }

  return freeze(resolutions);
}

function createRuntimeResolverRecord(record = {}) {
  const resolutions = deriveRuntimeResolverResolutions(record);

  return buildRuntimeResolverRecord({
    ...record,

    resolverStatus: "resolver-ready",
    resolverMode: "inspection-resolver",

    resolutionCount: resolutions.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    resolutions,

    diagnostics: {
      readOnly: true,
      resolverBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      resolverMetadataOnly: true
    }
  });
}

function inspectRuntimeResolverRecord(record = {}) {
  const normalized = normalizeRuntimeResolverRecord(record);

  return freeze({
    readOnly: true,
    resolverBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true,

    resolutionCount: normalized.resolutions.length
  });
}

function compareRuntimeResolverRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeResolverResolutions,
  createRuntimeResolverRecord,
  inspectRuntimeResolverRecord,
  compareRuntimeResolverRecords
};