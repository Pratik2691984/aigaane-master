"use strict";

/**
 * Deterministic Sanskrit Execution Guard Map
 *
 * Inspection-first execution guard metadata for future controlled derivation.
 * This layer does not execute Sanskrit transformations, mutate snapshots,
 * or produce surface forms.
 */

const EXECUTION_GUARD_SCHEMA_VERSION = "sanskrit-execution-guard.v1";

const EXECUTION_GUARD_TYPES = Object.freeze({
  CAPABILITY_GATE: "CAPABILITY_GATE",
  MUTATION_BLOCK: "MUTATION_BLOCK",
  TRANSFORMATION_AUTHORIZATION: "TRANSFORMATION_AUTHORIZATION",
  ROLLBACK_AUTHORIZATION: "ROLLBACK_AUTHORIZATION",
  RUNTIME_ISOLATION: "RUNTIME_ISOLATION",
  FINALIZATION_GUARD: "FINALIZATION_GUARD"
});

const EXECUTION_GUARD_CONTRACTS = Object.freeze({
  deterministic: true,
  immutable: true,
  inspectionOnly: true,
  nonPerformative: true,
  runtimeIsolated: true,
  runtimeEnvironmentLinked: true,
  schedulerLinked: true,
  irLinked: true,
  queueLinked: true,
  traceLinked: true,
  checkpointLinked: true,
  replaySafe: true,
  staticPreviewCompatible: true
});

const EXECUTION_GUARD_FIELDS = Object.freeze([
  {
    id: "guard.capability-gate",
    type: EXECUTION_GUARD_TYPES.CAPABILITY_GATE,
    summary: "Capability gate for future controlled transformation execution.",
    required: true,
    diagnostics: ["capability-gate", "execution-controlled"]
  },
  {
    id: "guard.mutation-block",
    type: EXECUTION_GUARD_TYPES.MUTATION_BLOCK,
    summary: "Mutation-blocking contract for snapshots, traces, queues, and checkpoints.",
    required: true,
    diagnostics: ["mutation-blocked", "immutable-safe"]
  },
  {
    id: "guard.transformation-authorization",
    type: EXECUTION_GUARD_TYPES.TRANSFORMATION_AUTHORIZATION,
    summary: "Authorization envelope reserved for future Sanskrit transformation execution.",
    required: true,
    diagnostics: ["authorization-envelope", "non-executing"]
  },
  {
    id: "guard.rollback-authorization",
    type: EXECUTION_GUARD_TYPES.ROLLBACK_AUTHORIZATION,
    summary: "Rollback authorization metadata for recovery-safe runtime inspection.",
    required: true,
    diagnostics: ["rollback-authorized", "recovery-safe"]
  },
  {
    id: "guard.runtime-isolation",
    type: EXECUTION_GUARD_TYPES.RUNTIME_ISOLATION,
    summary: "Runtime isolation guard preventing untracked transformation execution.",
    required: true,
    diagnostics: ["runtime-isolated", "guarded-runtime"]
  },
  {
    id: "guard.finalization",
    type: EXECUTION_GUARD_TYPES.FINALIZATION_GUARD,
    summary: "Finalization guard without Sanskrit transformation execution.",
    required: true,
    diagnostics: ["finalization", "non-transforming"]
  }
]);

function getExecutionGuardSummary() {
  return {
    schemaVersion: EXECUTION_GUARD_SCHEMA_VERSION,
    contracts: EXECUTION_GUARD_CONTRACTS,
    fieldCount: EXECUTION_GUARD_FIELDS.length,
    guardTypes: Object.values(EXECUTION_GUARD_TYPES),
    fields: EXECUTION_GUARD_FIELDS.map((field) => ({ ...field }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    EXECUTION_GUARD_SCHEMA_VERSION,
    EXECUTION_GUARD_TYPES,
    EXECUTION_GUARD_CONTRACTS,
    EXECUTION_GUARD_FIELDS,
    getExecutionGuardSummary
  };
}