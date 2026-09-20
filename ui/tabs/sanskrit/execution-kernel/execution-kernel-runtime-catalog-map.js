"use strict";

const CATALOG_SCHEMA = "sanskrit-runtime-catalog.v1";

const CATALOG_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  CATALOG_READY: "CATALOG_READY",
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
  if (!Number.isFinite(n)) return 0;
  return Math.max(0, Math.floor(n));
}

function normalizeRuntimeCatalogRecord(input = {}) {
  return freeze({
    catalogId: String(input.catalogId || "runtime-catalog"),
    createdAt: String(input.createdAt || "static"),

    sourceManifestId: String(input.sourceManifestId || "runtime-manifest"),
    sourceManifestStatus: String(input.sourceManifestStatus || "manifest-ready"),
    sourceManifestMode: String(input.sourceManifestMode || "inspection-manifest"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    catalogStatus: String(input.catalogStatus || "catalog-ready"),
    catalogMode: String(input.catalogMode || "inspection-catalog"),

    catalogAllowed: false,
    manifestAllowed: false,
    archiveAllowed: false,
    importAllowed: false,
    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    recordCount: asCount(input.recordCount),
    warningCount: asCount(input.warningCount),

    records: freeze([
      ...(Array.isArray(input.records) ? input.records : [])
    ]),

    warnings: freeze([
      ...(Array.isArray(input.warnings) ? input.warnings : [])
    ]),

    diagnostics: freeze({
      ...(isObject(input.diagnostics) ? input.diagnostics : {})
    }),

    metadata: freeze({
      ...(isObject(input.metadata) ? input.metadata : {})
    })
  });
}

function buildRuntimeCatalogRecord(input = {}) {
  const normalized = normalizeRuntimeCatalogRecord(input);

  return freeze({
    schemaVersion: CATALOG_SCHEMA,
    state: normalized.records.length > 0
      ? CATALOG_STATES.CATALOG_READY
      : CATALOG_STATES.EMPTY,

    ...normalized,

    catalogStatus: "catalog-ready",
    catalogMode: "inspection-catalog",

    catalogAllowed: false,
    manifestAllowed: false,
    archiveAllowed: false,
    importAllowed: false,
    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false
  });
}

function validateRuntimeCatalogRecord(record = {}) {
  const errors = [];

  if (!isObject(record)) errors.push("record");

  if (typeof record.catalogStatus !== "string") errors.push("catalogStatus");
  if (typeof record.catalogMode !== "string") errors.push("catalogMode");

  [
    "catalogAllowed",
    "manifestAllowed",
    "archiveAllowed",
    "importAllowed",
    "replayAllowed",
    "executionAllowed",
    "mutationAllowed",
    "publicationAllowed",
    "rollbackAllowed",
    "canonicalWriteAllowed"
  ].forEach((field) => {
    if (typeof record[field] !== "boolean") errors.push(field);
  });

  if (
    !Number.isInteger(Number(record.recordCount)) ||
    Number(record.recordCount) < 0
  ) {
    errors.push("recordCount");
  }

  if (
    !Number.isInteger(Number(record.warningCount)) ||
    Number(record.warningCount) < 0
  ) {
    errors.push("warningCount");
  }

  if (!Array.isArray(record.records)) errors.push("records");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  CATALOG_SCHEMA,
  CATALOG_STATES,
  normalizeRuntimeCatalogRecord,
  buildRuntimeCatalogRecord,
  validateRuntimeCatalogRecord
};