"use strict";

const REGISTRY_SCHEMA = "sanskrit-runtime-registry.v1";

const REGISTRY_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  REGISTRY_READY: "REGISTRY_READY",
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

function normalizeRuntimeRegistryRecord(input = {}) {
  return freeze({
    registryId: String(input.registryId || "runtime-registry"),
    createdAt: String(input.createdAt || "static"),

    sourceCatalogId: String(input.sourceCatalogId || "runtime-catalog"),
    sourceCatalogStatus: String(input.sourceCatalogStatus || "catalog-ready"),
    sourceCatalogMode: String(input.sourceCatalogMode || "inspection-catalog"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    registryStatus: String(input.registryStatus || "registry-ready"),
    registryMode: String(input.registryMode || "inspection-registry"),

    registryAllowed: false,
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

    entryCount: asCount(input.entryCount),
    warningCount: asCount(input.warningCount),

    entries: freeze([
      ...(Array.isArray(input.entries) ? input.entries : [])
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

function buildRuntimeRegistryRecord(input = {}) {
  const normalized = normalizeRuntimeRegistryRecord(input);

  return freeze({
    schemaVersion: REGISTRY_SCHEMA,
    state: normalized.entries.length > 0
      ? REGISTRY_STATES.REGISTRY_READY
      : REGISTRY_STATES.EMPTY,

    ...normalized,

    registryStatus: "registry-ready",
    registryMode: "inspection-registry",

    registryAllowed: false,
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

function validateRuntimeRegistryRecord(record = {}) {
  const errors = [];

  if (!isObject(record)) errors.push("record");

  if (typeof record.registryStatus !== "string") errors.push("registryStatus");
  if (typeof record.registryMode !== "string") errors.push("registryMode");

  [
    "registryAllowed",
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
    !Number.isInteger(Number(record.entryCount)) ||
    Number(record.entryCount) < 0
  ) {
    errors.push("entryCount");
  }

  if (
    !Number.isInteger(Number(record.warningCount)) ||
    Number(record.warningCount) < 0
  ) {
    errors.push("warningCount");
  }

  if (!Array.isArray(record.entries)) errors.push("entries");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  REGISTRY_SCHEMA,
  REGISTRY_STATES,
  normalizeRuntimeRegistryRecord,
  buildRuntimeRegistryRecord,
  validateRuntimeRegistryRecord
};