"use strict";

const {
  buildRuntimeNavigatorRecord,
  normalizeRuntimeNavigatorRecord
} = require("./execution-kernel-runtime-navigator-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeNavigatorRoutes(record = {}) {
  const routes = [
    "runtime-navigator-surface",
    "runtime-resolver-reference",
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
    routes.push("warning-reference-navigator");
  }

  return freeze(routes);
}

function createRuntimeNavigatorRecord(record = {}) {
  const routes = deriveRuntimeNavigatorRoutes(record);

  return buildRuntimeNavigatorRecord({
    ...record,

    navigatorStatus: "navigator-ready",
    navigatorMode: "inspection-navigator",

    routeCount: routes.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    routes,

    diagnostics: {
      readOnly: true,
      navigatorBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      navigatorMetadataOnly: true
    }
  });
}

function inspectRuntimeNavigatorRecord(record = {}) {
  const normalized = normalizeRuntimeNavigatorRecord(record);

  return freeze({
    readOnly: true,
    navigatorBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true,

    routeCount: normalized.routes.length
  });
}

function compareRuntimeNavigatorRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeNavigatorRoutes,
  createRuntimeNavigatorRecord,
  inspectRuntimeNavigatorRecord,
  compareRuntimeNavigatorRecords
};