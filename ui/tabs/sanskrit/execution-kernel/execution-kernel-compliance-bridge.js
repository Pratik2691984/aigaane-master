"use strict";

const {
  createExecutionKernelSnapshot,
} = require("./execution-kernel-engine.js");

const COMPLIANCE_BRIDGE_SCHEMA_VERSION = "sanskrit-execution-kernel-compliance-bridge.v1";

function freezeObject(value) {
  return Object.freeze(value);
}

function referenceId(value, fallback) {
  if (typeof value === "string") return value;
  if (value && typeof value === "object") {
    return String(value.id || value.referenceId || fallback);
  }
  return fallback;
}

function normalizeExecutionComplianceReference(compliance) {
  const isObject = compliance && typeof compliance === "object";
  const isString = typeof compliance === "string";

  return freezeObject({
    id: isString ? compliance : isObject ? String(compliance.id || compliance.referenceId || "compliance.unresolved") : "compliance.unresolved",
    kind: isString ? "EXECUTION_COMPLIANCE_REFERENCE" : isObject ? String(compliance.kind || "EXECUTION_COMPLIANCE_REFERENCE") : "EXECUTION_COMPLIANCE_REFERENCE",
    schemaVersion: isString ? "unknown" : isObject ? String(compliance.schemaVersion || "unknown") : "unknown",
    status: isString ? "REFERENCED" : isObject ? String(compliance.status || "REFERENCED") : "UNRESOLVED",

    compliant: Boolean(isObject && compliance.compliant === true),
    enforcementAllowed: Boolean(isObject && compliance.enforcementAllowed === true),
    mutationAllowed: Boolean(isObject && compliance.mutationAllowed === true),

    diagnostics: freezeObject({
      normalized: true,
      complianceLinked: true,
      sourceCompliantObserved: Boolean(isObject && compliance.compliant === true),
      sourceEnforcementObserved: Boolean(isObject && compliance.enforcementAllowed === true),
      sourceMutationObserved: Boolean(isObject && compliance.mutationAllowed === true),
      bridgeComplianceGranted: false,
      bridgeEnforcementGranted: false,
      bridgeMutationGranted: false,
      bridgeExecutionGranted: false,
    }),
  });
}

function createExecutionKernelComplianceBridge(input = {}) {
  const kernelSnapshot = input.kernelSnapshot || {};
  const stages = Array.isArray(kernelSnapshot.stages) ? kernelSnapshot.stages : [];
  const compliance = normalizeExecutionComplianceReference(input.compliance);

  return freezeObject({
    schemaVersion: COMPLIANCE_BRIDGE_SCHEMA_VERSION,
    kind: "EXECUTION_KERNEL_COMPLIANCE_BRIDGE",

    kernel: freezeObject({
      schemaVersion: String(kernelSnapshot.schemaVersion || "unknown"),
      kind: String(kernelSnapshot.kind || "EXECUTION_KERNEL_SNAPSHOT"),
      mode: String(kernelSnapshot.mode || "INSPECTION"),
      stageCount: stages.length,
    }),

    compliance,

    policy: freezeObject({ id: referenceId(input.policy, "policy.unresolved"), linked: true }),
    audit: freezeObject({ id: referenceId(input.audit, "audit.unresolved"), linked: true }),
    trace: freezeObject({ id: referenceId(input.trace, "trace.unresolved"), linked: true }),
    scheduler: freezeObject({ id: referenceId(input.scheduler, "scheduler.unresolved"), linked: true }),
    queue: freezeObject({ id: referenceId(input.queue, "queue.unresolved"), linked: true }),
    replay: freezeObject({ id: referenceId(input.replay, "replay.unresolved"), linked: true }),
    checkpoint: freezeObject({ id: referenceId(input.checkpoint, "checkpoint.unresolved"), linked: true }),
    runtimeEnvironment: freezeObject({ id: referenceId(input.runtimeEnvironment, "runtime.unresolved"), linked: true }),

    linkage: freezeObject({
      kernelLinked: true,
      complianceLinked: true,
      policyLinked: true,
      auditLinked: true,
      traceLinked: true,
      schedulerLinked: true,
      queueLinked: true,
      replayLinked: true,
      checkpointLinked: true,
      runtimeLinked: true,

      complianceInspectionOnly: true,
      enforcementBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      rollbackBlocked: true,
      replayBlocked: true,
      schedulingBlocked: true,
      dispatchBlocked: true,
      dequeueBlocked: true,
      surfaceFormBlocked: true,
    }),

    diagnostics: freezeObject({
      ready: true,
      deterministic: true,
      immutable: true,
      inspectionOnly: true,
      complianceOnly: true,

      enforcementBlocked: true,
      executionBlocked: true,
      mutationFree: true,
      rollbackBlocked: true,
      replayBlocked: true,
      schedulingBlocked: true,
      dispatchBlocked: true,
      dequeueBlocked: true,
      surfaceFormBlocked: true,

      policyCompatible: true,
      auditCompatible: true,
      traceCompatible: true,
      schedulerCompatible: true,
      queueCompatible: true,
      checkpointCompatible: true,
      replayCompatible: true,
      runtimeCompatible: true,

      stageCount: stages.length,
    }),
  });
}

function buildExecutionKernelComplianceBridgeSnapshot(input = {}) {
  const kernelSnapshot =
    input.kernelSnapshot ||
    createExecutionKernelSnapshot({
      mode: input.mode || "INSPECTION",
      guard: input.guardReference || "guard.unresolved",
      runtimeEnvironment: input.runtimeEnvironment || "runtime.unresolved",
      prakriyaPlan: input.prakriyaPlan || "prakriya.unresolved",
      derivationGraph: input.derivationGraph || "graph.unresolved",
      stages: input.stages || [],
    });

  return createExecutionKernelComplianceBridge({
    kernelSnapshot,
    compliance: input.compliance || input.complianceReference || "compliance.unresolved",
    policy: input.policy || input.policyReference || "policy.unresolved",
    audit: input.audit || input.auditReference || "audit.unresolved",
    trace: input.trace || input.traceReference || "trace.unresolved",
    scheduler: input.scheduler || input.schedulerReference || "scheduler.unresolved",
    queue: input.queue || input.queueReference || "queue.unresolved",
    replay: input.replay || input.replayReference || "replay.unresolved",
    checkpoint: input.checkpoint || input.checkpointReference || "checkpoint.unresolved",
    runtimeEnvironment: input.runtimeEnvironment || kernelSnapshot.references.runtimeEnvironment,
  });
}

function getExecutionKernelComplianceBridgeDiagnostics(bridge = {}) {
  const linkage = bridge.linkage || {};
  const diagnostics = bridge.diagnostics || {};

  return freezeObject({
    schemaVersion: String(bridge.schemaVersion || COMPLIANCE_BRIDGE_SCHEMA_VERSION),
    ready: Boolean(diagnostics.ready),

    kernelLinked: Boolean(linkage.kernelLinked),
    complianceLinked: Boolean(linkage.complianceLinked),
    policyLinked: Boolean(linkage.policyLinked),
    auditLinked: Boolean(linkage.auditLinked),
    traceLinked: Boolean(linkage.traceLinked),
    schedulerLinked: Boolean(linkage.schedulerLinked),
    queueLinked: Boolean(linkage.queueLinked),
    replayLinked: Boolean(linkage.replayLinked),
    checkpointLinked: Boolean(linkage.checkpointLinked),
    runtimeLinked: Boolean(linkage.runtimeLinked),

    complianceInspectionOnly: Boolean(linkage.complianceInspectionOnly),
    enforcementBlocked: Boolean(linkage.enforcementBlocked),
    executionBlocked: Boolean(linkage.executionBlocked),
    mutationFree: Boolean(diagnostics.mutationFree),
    rollbackBlocked: Boolean(linkage.rollbackBlocked),
    replayBlocked: Boolean(linkage.replayBlocked),
    schedulingBlocked: Boolean(linkage.schedulingBlocked),
    dispatchBlocked: Boolean(linkage.dispatchBlocked),
    dequeueBlocked: Boolean(linkage.dequeueBlocked),
    surfaceFormBlocked: Boolean(linkage.surfaceFormBlocked),

    stageCount: Number(diagnostics.stageCount || 0),
  });
}

module.exports = {
  COMPLIANCE_BRIDGE_SCHEMA_VERSION,
  normalizeExecutionComplianceReference,
  createExecutionKernelComplianceBridge,
  buildExecutionKernelComplianceBridgeSnapshot,
  getExecutionKernelComplianceBridgeDiagnostics,
};