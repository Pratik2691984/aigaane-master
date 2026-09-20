"use strict";

/**
 * Deterministic Sanskrit Replay Trace Map
 *
 * Inspection-first replay trace metadata for planned Sanskrit derivations.
 * This layer does not execute transformations, mutate IR snapshots,
 * or produce surface forms.
 */

const REPLAY_TRACE_SCHEMA_VERSION = "sanskrit-replay-trace.v1";

const REPLAY_TRACE_EVENT_TYPES = Object.freeze({
  SCHEDULER_DECISION: "SCHEDULER_DECISION",
  IR_SNAPSHOT: "IR_SNAPSHOT",
  QUEUE_ITEM: "QUEUE_ITEM",
  CHECKPOINT: "CHECKPOINT",
  DIAGNOSTIC: "DIAGNOSTIC",
  TRACE_FINALIZATION: "TRACE_FINALIZATION"
});

const REPLAY_TRACE_CONTRACTS = Object.freeze({
  deterministic: true,
  immutable: true,
  inspectionOnly: true,
  nonPerformative: true,
  runtimeIsolated: true,
  schedulerLinked: true,
  irLinked: true,
  queueLinked: true,
  replaySafe: true,
  staticPreviewCompatible: true
});

const REPLAY_TRACE_FIELDS = Object.freeze([
  {
    id: "trace.scheduler-decision",
    type: REPLAY_TRACE_EVENT_TYPES.SCHEDULER_DECISION,
    summary: "Replay event for deterministic scheduler decisions.",
    required: true,
    diagnostics: ["scheduler-linked", "deterministic-order"]
  },
  {
    id: "trace.ir-snapshot",
    type: REPLAY_TRACE_EVENT_TYPES.IR_SNAPSHOT,
    summary: "Replay event referencing an immutable derivation IR snapshot.",
    required: true,
    diagnostics: ["ir-linked", "snapshot-reference"]
  },
  {
    id: "trace.queue-item",
    type: REPLAY_TRACE_EVENT_TYPES.QUEUE_ITEM,
    summary: "Replay event referencing a planned transformation queue item.",
    required: true,
    diagnostics: ["queue-linked", "planned-transition"]
  },
  {
    id: "trace.checkpoint",
    type: REPLAY_TRACE_EVENT_TYPES.CHECKPOINT,
    summary: "Replay checkpoint envelope for deterministic trace recovery.",
    required: true,
    diagnostics: ["checkpoint", "recovery-safe"]
  },
  {
    id: "trace.diagnostic",
    type: REPLAY_TRACE_EVENT_TYPES.DIAGNOSTIC,
    summary: "Normalized diagnostic event for trace inspection.",
    required: false,
    diagnostics: ["diagnostic-event", "inspection-safe"]
  },
  {
    id: "trace.finalization",
    type: REPLAY_TRACE_EVENT_TYPES.TRACE_FINALIZATION,
    summary: "Trace finalization event without surface-form execution.",
    required: true,
    diagnostics: ["finalization", "non-executing"]
  }
]);

function getReplayTraceSummary() {
  return {
    schemaVersion: REPLAY_TRACE_SCHEMA_VERSION,
    contracts: REPLAY_TRACE_CONTRACTS,
    fieldCount: REPLAY_TRACE_FIELDS.length,
    eventTypes: Object.values(REPLAY_TRACE_EVENT_TYPES),
    fields: REPLAY_TRACE_FIELDS.map((field) => ({ ...field }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    REPLAY_TRACE_SCHEMA_VERSION,
    REPLAY_TRACE_EVENT_TYPES,
    REPLAY_TRACE_CONTRACTS,
    REPLAY_TRACE_FIELDS,
    getReplayTraceSummary
  };
}