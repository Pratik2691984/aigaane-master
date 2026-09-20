"use strict";

const {
  EXECUTION_KERNEL_SCHEMA_VERSION,
  EXECUTION_KERNEL_CONTRACTS,
  EXECUTION_KERNEL_FIELDS,
  getExecutionKernelSummary
} = require("./execution-kernel-map.js");

function normalizeExecutionKernelField(field) {
  return {
    id: String(field.id || ""),
    type: String(field.type || ""),
    order: Number.isFinite(Number(field.order)) ? Number(field.order) : 0,
    summary: String(field.summary || ""),
    required: Boolean(field.required),
    diagnostics: Array.isArray(field.diagnostics)
      ? field.diagnostics.map(String)
      : []
  };
}

function buildExecutionKernelExport() {
  const summary = getExecutionKernelSummary();

  return {
    schemaVersion: EXECUTION_KERNEL_SCHEMA_VERSION,
    contracts: { ...EXECUTION_KERNEL_CONTRACTS },
    ready: true,
    fieldCount: EXECUTION_KERNEL_FIELDS.length,
    stageTypes: Array.isArray(summary.stageTypes)
      ? summary.stageTypes.map(String)
      : [],
    fields: EXECUTION_KERNEL_FIELDS
      .map(normalizeExecutionKernelField)
      .sort((a, b) => a.order - b.order),
    diagnostics: {
      normalized: true,
      deterministic: true,
      immutable: true,
      runtimeSafe: true,
      replaySafe: true,
      executionGuardLinked: true,
      runtimeEnvironmentLinked: true,
      prakriyaPlanningLinked: true,
      derivationGraphLinked: true,
      schedulerLinked: true,
      queueLinked: true,
      traceLinked: true,
      checkpointLinked: true,
      mutationFree: true,
      executionBlocked: true,
      kernelOnly: true
    }
  };
}

function createExecutionKernelSnapshot(input) {
  const safeInput = input && typeof input === "object" ? input : {};
  const stages = Array.isArray(safeInput.stages) ? safeInput.stages : [];
  const stageEnvelopes = stages
    .map((stage, index) =>
      Object.freeze({
        index,
        id: String(stage.id || `execution-kernel-stage-${index}`),
        type: String(stage.type || "EXECUTION_ENVELOPE"),
        order: Number.isFinite(Number(stage.order)) ? Number(stage.order) : index,
        referenceId: String(stage.referenceId || ""),
        planned: true,
        authorized: false,
        executed: false,
        diagnostics: Array.isArray(stage.diagnostics)
          ? stage.diagnostics.map(String)
          : ["execution-blocked", "inspection-only"]
      })
    )
    .sort((a, b) => a.order - b.order);

  return Object.freeze({
    schemaVersion: EXECUTION_KERNEL_SCHEMA_VERSION,
    kind: "EXECUTION_KERNEL_SNAPSHOT",
    mode: String(safeInput.mode || "INSPECTION"),
    references: Object.freeze({
      guard: String(safeInput.guard || ""),
      runtimeEnvironment: String(safeInput.runtimeEnvironment || ""),
      prakriyaPlan: String(safeInput.prakriyaPlan || ""),
      derivationGraph: String(safeInput.derivationGraph || "")
    }),
    stages: Object.freeze(stageEnvelopes),
    capabilities: Object.freeze({
      executeTransformations: false,
      mutateSnapshots: false,
      produceSurfaceForms: false,
      authorizeRollback: true,
      inspectOnly: true
    }),
    trace: Object.freeze({
      replaySafe: true,
      mutationFree: true,
      executionBlocked: true,
      stageCount: stages.length
    })
  });
}

function getExecutionKernelDiagnostics() {
  const kernelExport = buildExecutionKernelExport();

  return {
    schemaVersion: kernelExport.schemaVersion,
    ready: kernelExport.ready,
    fieldCount: kernelExport.fieldCount,
    contractsSatisfied: Object.values(kernelExport.contracts).every(Boolean),
    diagnostics: { ...kernelExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeExecutionKernelField,
    buildExecutionKernelExport,
    createExecutionKernelSnapshot,
    getExecutionKernelDiagnostics
  };
}
