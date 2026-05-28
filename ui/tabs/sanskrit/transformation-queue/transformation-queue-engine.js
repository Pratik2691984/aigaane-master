"use strict";

const {
  TRANSFORMATION_QUEUE_SCHEMA_VERSION,
  TRANSFORMATION_QUEUE_CONTRACTS,
  TRANSFORMATION_QUEUE_FIELDS,
  getTransformationQueueSummary
} = require("./transformation-queue-map.js");

function normalizeTransformationQueueField(field) {
  return {
    id: String(field.id || ""),
    type: String(field.type || ""),
    summary: String(field.summary || ""),
    required: Boolean(field.required),
    diagnostics: Array.isArray(field.diagnostics)
      ? field.diagnostics.map(String)
      : []
  };
}

function buildTransformationQueueExport() {
  const summary = getTransformationQueueSummary();

  return {
    schemaVersion: TRANSFORMATION_QUEUE_SCHEMA_VERSION,
    contracts: { ...TRANSFORMATION_QUEUE_CONTRACTS },
    ready: true,
    fieldCount: TRANSFORMATION_QUEUE_FIELDS.length,
    itemTypes: Array.isArray(summary.itemTypes)
      ? summary.itemTypes.map(String)
      : [],
    fields: TRANSFORMATION_QUEUE_FIELDS.map(
      normalizeTransformationQueueField
    ),
    diagnostics: {
      normalized: true,
      deterministic: true,
      immutable: true,
      runtimeSafe: true,
      replaySafe: true,
      schedulerLinked: true,
      irCompatible: true,
      mutationFree: true
    }
  };
}

function createTransformationQueueSnapshot(input) {
  const safeInput =
    input && typeof input === "object" ? input : {};

  const queueItems = Array.isArray(safeInput.queueItems)
    ? safeInput.queueItems
    : [];

  return Object.freeze({
    schemaVersion: TRANSFORMATION_QUEUE_SCHEMA_VERSION,
    kind: "TRANSFORMATION_QUEUE_SNAPSHOT",
    queueItems: Object.freeze(
      queueItems.map((item, index) =>
        Object.freeze({
          index,
          id: String(item.id || `queue-item-${index}`),
          type: String(item.type || "RULE_APPLICATION"),
          ruleId: String(item.ruleId || ""),
          planned: true,
          diagnostics: Array.isArray(item.diagnostics)
            ? item.diagnostics.map(String)
            : []
        })
      )
    ),
    trace: Object.freeze({
      replaySafe: true,
      mutationFree: true,
      queueLength: queueItems.length
    })
  });
}

function getTransformationQueueDiagnostics() {
  const queueExport = buildTransformationQueueExport();

  return {
    schemaVersion: queueExport.schemaVersion,
    ready: queueExport.ready,
    fieldCount: queueExport.fieldCount,
    contractsSatisfied: Object.values(
      queueExport.contracts
    ).every(Boolean),
    diagnostics: { ...queueExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeTransformationQueueField,
    buildTransformationQueueExport,
    createTransformationQueueSnapshot,
    getTransformationQueueDiagnostics
  };
}