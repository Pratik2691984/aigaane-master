"use strict";

/**
 * Deterministic Sanskrit Checkpoint Map
 *
 * Inspection-first checkpoint metadata for planned Sanskrit derivation recovery.
 * This layer does not execute transformations, mutate IR snapshots,
 * or produce surface forms.
 */

const CHECKPOINT_SCHEMA_VERSION = "sanskrit-checkpoint.v1";

const CHECKPOINT_EVENT_TYPES = Object.freeze({
  SCHEDULER_CHECKPOINT: "SCHEDULER_CHECKPOINT",
  IR_CHECKPOINT: "IR_CHECKPOINT",
  QUEUE_CHECKPOINT: "QUEUE_CHECKPOINT",
  TRACE_CHECKPOINT: "TRACE_CHECKPOINT",
  RECOVERY_POINT: "RECOVERY_POINT",
  FINAL_CHECKPOINT: "FINAL_CHECKPOINT"
});

const CHECKPOINT_CONTRACTS = Object.freeze({
  deterministic: true,
  immutable: true,
  inspectionOnly: true,
  nonPerformative: true,
  runtimeIsolated: true,
  schedulerLinked: true,
  irLinked: true,
  queueLinked: true,
  traceLinked: true,
  replaySafe: true,
  staticPreviewCompatible: true
});

const CHECKPOINT_FIELDS = Object.freeze([
  {
    id: "checkpoint.scheduler",
    type: CHECKPOINT_EVENT_TYPES.SCHEDULER_CHECKPOINT,
    summary: "Checkpoint reference for deterministic scheduler state.",
    required: true,
    diagnostics: ["scheduler-linked", "deterministic-state"]
  },
  {
    id: "checkpoint.ir",
    type: CHECKPOINT_EVENT_TYPES.IR_CHECKPOINT,
    summary: "Checkpoint reference for immutable derivation IR state.",
    required: true,
    diagnostics: ["ir-linked", "snapshot-state"]
  },
  {
    id: "checkpoint.queue",
    type: CHECKPOINT_EVENT_TYPES.QUEUE_CHECKPOINT,
    summary: "Checkpoint reference for planned transformation queue state.",
    required: true,
    diagnostics: ["queue-linked", "planned-state"]
  },
  {
    id: "checkpoint.trace",
    type: CHECKPOINT_EVENT_TYPES.TRACE_CHECKPOINT,
    summary: "Checkpoint reference for deterministic replay trace state.",
    required: true,
    diagnostics: ["trace-linked", "replay-state"]
  },
  {
    id: "checkpoint.recovery",
    type: CHECKPOINT_EVENT_TYPES.RECOVERY_POINT,
    summary: "Recovery checkpoint envelope for replay-safe derivation inspection.",
    required: true,
    diagnostics: ["recovery-safe", "replay-safe"]
  },
  {
    id: "checkpoint.final",
    type: CHECKPOINT_EVENT_TYPES.FINAL_CHECKPOINT,
    summary: "Final checkpoint envelope without Sanskrit transformation execution.",
    required: true,
    diagnostics: ["finalization", "non-executing"]
  }
]);

function getCheckpointSummary() {
  return {
    schemaVersion: CHECKPOINT_SCHEMA_VERSION,
    contracts: CHECKPOINT_CONTRACTS,
    fieldCount: CHECKPOINT_FIELDS.length,
    eventTypes: Object.values(CHECKPOINT_EVENT_TYPES),
    fields: CHECKPOINT_FIELDS.map((field) => ({ ...field }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    CHECKPOINT_SCHEMA_VERSION,
    CHECKPOINT_EVENT_TYPES,
    CHECKPOINT_CONTRACTS,
    CHECKPOINT_FIELDS,
    getCheckpointSummary
  };
}