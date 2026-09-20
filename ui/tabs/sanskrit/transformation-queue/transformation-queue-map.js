"use strict";

/**
 * Deterministic Sanskrit Transformation Queue Map
 *
 * Inspection-first queue metadata for planned Sanskrit transformations.
 * This layer does not execute sandhi, morphology, lakāra derivation,
 * or surface-form production.
 */

const TRANSFORMATION_QUEUE_SCHEMA_VERSION = "sanskrit-transformation-queue.v1";

const TRANSFORMATION_QUEUE_ITEM_TYPES = Object.freeze({
  RULE_APPLICATION: "RULE_APPLICATION",
  SANDHI_PLAN: "SANDHI_PLAN",
  MORPHOLOGY_PLAN: "MORPHOLOGY_PLAN",
  LAKARA_PLAN: "LAKARA_PLAN",
  SNAPSHOT_LINK: "SNAPSHOT_LINK",
  TRACE_LINK: "TRACE_LINK"
});

const TRANSFORMATION_QUEUE_CONTRACTS = Object.freeze({
  deterministic: true,
  immutable: true,
  inspectionOnly: true,
  nonPerformative: true,
  runtimeIsolated: true,
  schedulerLinked: true,
  irCompatible: true,
  replaySafe: true,
  staticPreviewCompatible: true
});

const TRANSFORMATION_QUEUE_FIELDS = Object.freeze([
  {
    id: "queue.rule-application",
    type: TRANSFORMATION_QUEUE_ITEM_TYPES.RULE_APPLICATION,
    summary: "Planned rule application envelope linked to scheduler precedence output.",
    required: true,
    diagnostics: ["rule-envelope", "scheduler-linked"]
  },
  {
    id: "queue.sandhi-plan",
    type: TRANSFORMATION_QUEUE_ITEM_TYPES.SANDHI_PLAN,
    summary: "Reserved non-executing sandhi planning item.",
    required: false,
    diagnostics: ["sandhi-placeholder", "non-executing"]
  },
  {
    id: "queue.morphology-plan",
    type: TRANSFORMATION_QUEUE_ITEM_TYPES.MORPHOLOGY_PLAN,
    summary: "Reserved non-executing morphology planning item.",
    required: false,
    diagnostics: ["morphology-placeholder", "non-executing"]
  },
  {
    id: "queue.lakara-plan",
    type: TRANSFORMATION_QUEUE_ITEM_TYPES.LAKARA_PLAN,
    summary: "Reserved non-executing lakāra planning item.",
    required: false,
    diagnostics: ["lakara-placeholder", "non-executing"]
  },
  {
    id: "queue.snapshot-link",
    type: TRANSFORMATION_QUEUE_ITEM_TYPES.SNAPSHOT_LINK,
    summary: "Immutable link to a derivation IR snapshot.",
    required: true,
    diagnostics: ["snapshot-linked", "replay-safe"]
  },
  {
    id: "queue.trace-link",
    type: TRANSFORMATION_QUEUE_ITEM_TYPES.TRACE_LINK,
    summary: "Trace metadata connecting planned queue items to deterministic replay.",
    required: true,
    diagnostics: ["trace-linked", "deterministic-replay"]
  }
]);

function getTransformationQueueSummary() {
  return {
    schemaVersion: TRANSFORMATION_QUEUE_SCHEMA_VERSION,
    contracts: TRANSFORMATION_QUEUE_CONTRACTS,
    fieldCount: TRANSFORMATION_QUEUE_FIELDS.length,
    itemTypes: Object.values(TRANSFORMATION_QUEUE_ITEM_TYPES),
    fields: TRANSFORMATION_QUEUE_FIELDS.map((field) => ({ ...field }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    TRANSFORMATION_QUEUE_SCHEMA_VERSION,
    TRANSFORMATION_QUEUE_ITEM_TYPES,
    TRANSFORMATION_QUEUE_CONTRACTS,
    TRANSFORMATION_QUEUE_FIELDS,
    getTransformationQueueSummary
  };
}