"use strict";

/**
 * Controlled Sanskrit Execution Kernel Map
 *
 * Wraps planned prakriya stages in deterministic inspection envelopes.
 * This layer does not execute rules, mutate snapshots, apply sandhi,
 * conjugate, inflect, or produce surface forms.
 */

const EXECUTION_KERNEL_SCHEMA_VERSION = "sanskrit-execution-kernel.v1";

const EXECUTION_KERNEL_STAGE_TYPES = Object.freeze({
  KERNEL_INITIALIZATION: "KERNEL_INITIALIZATION",
  GUARD_VERIFICATION: "GUARD_VERIFICATION",
  PRAKRIYA_STAGE_BINDING: "PRAKRIYA_STAGE_BINDING",
  EXECUTION_ENVELOPE: "EXECUTION_ENVELOPE",
  ROLLBACK_ENVELOPE: "ROLLBACK_ENVELOPE",
  FINALIZATION_ENVELOPE: "FINALIZATION_ENVELOPE"
});

const EXECUTION_KERNEL_CONTRACTS = Object.freeze({
  deterministic: true,
  immutable: true,
  inspectionOnly: true,
  nonPerformative: true,
  nonMutating: true,
  runtimeIsolated: true,
  executionGuardLinked: true,
  runtimeEnvironmentLinked: true,
  prakriyaPlanningLinked: true,
  derivationGraphLinked: true,
  schedulerLinked: true,
  queueLinked: true,
  traceLinked: true,
  checkpointLinked: true,
  replaySafe: true,
  staticPreviewCompatible: true
});

const EXECUTION_KERNEL_FIELDS = Object.freeze([
  {
    id: "kernel.initialization",
    type: EXECUTION_KERNEL_STAGE_TYPES.KERNEL_INITIALIZATION,
    order: 10,
    summary: "initialization envelope for controlled execution inspection",
    required: true,
    diagnostics: ["kernel-initialization", "inspection-safe"]
  },
  {
    id: "kernel.guard-verification",
    type: EXECUTION_KERNEL_STAGE_TYPES.GUARD_VERIFICATION,
    order: 20,
    summary: "verifies execution guard linkage before any future execution",
    required: true,
    diagnostics: ["guard-verification", "execution-blocked"]
  },
  {
    id: "kernel.prakriya-stage-binding",
    type: EXECUTION_KERNEL_STAGE_TYPES.PRAKRIYA_STAGE_BINDING,
    order: 30,
    summary: "binds ordered prakriya planning stages into kernel envelopes",
    required: true,
    diagnostics: ["prakriya-linked", "stage-binding"]
  },
  {
    id: "kernel.execution-envelope",
    type: EXECUTION_KERNEL_STAGE_TYPES.EXECUTION_ENVELOPE,
    order: 40,
    summary: "non-mutating execution envelope reserved for future controlled transformations",
    required: true,
    diagnostics: ["execution-envelope", "non-mutating"]
  },
  {
    id: "kernel.rollback-envelope",
    type: EXECUTION_KERNEL_STAGE_TYPES.ROLLBACK_ENVELOPE,
    order: 50,
    summary: "rollback envelope metadata for recovery-safe execution planning",
    required: true,
    diagnostics: ["rollback-envelope", "recovery-safe"]
  },
  {
    id: "kernel.finalization-envelope",
    type: EXECUTION_KERNEL_STAGE_TYPES.FINALIZATION_ENVELOPE,
    order: 60,
    summary: "finalization envelope without Sanskrit surface-form production",
    required: true,
    diagnostics: ["finalization-envelope", "surface-form-blocked"]
  }
]);

function getExecutionKernelSummary() {
  return {
    schemaVersion: EXECUTION_KERNEL_SCHEMA_VERSION,
    contracts: EXECUTION_KERNEL_CONTRACTS,
    fieldCount: EXECUTION_KERNEL_FIELDS.length,
    stageTypes: Object.values(EXECUTION_KERNEL_STAGE_TYPES),
    fields: EXECUTION_KERNEL_FIELDS.map((field) => ({ ...field }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    EXECUTION_KERNEL_SCHEMA_VERSION,
    EXECUTION_KERNEL_STAGE_TYPES,
    EXECUTION_KERNEL_CONTRACTS,
    EXECUTION_KERNEL_FIELDS,
    getExecutionKernelSummary
  };
}
