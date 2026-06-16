"use strict";

const {
  createExecutionKernelSnapshot,
} = require("./execution-kernel-engine.js");

const POLICY_BRIDGE_SCHEMA_VERSION = "sanskrit-execution-kernel-policy-bridge.v1";

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

function normalizeExecutionPolicyReference(policy) {
  const isObject = policy && typeof policy === "object";
  const isString = typeof policy === "string";

  return freezeObject({
    id: isString ? policy : isObject ? String(policy.id || policy.referenceId || "policy.unresolved") : "policy.unresolved",
    kind: isString ? "EXECUTION_POLICY_REFERENCE" : isObject ? String(policy.kind || "EXECUTION_POLICY_REFERENCE") : "EXECUTION_POLICY_REFERENCE",
    schemaVersion: isString ? "unknown" : isObject ? String(policy.schemaVersion || "unknown") : "unknown",
    status: isString ? "REFERENCED" : isObject ? String(policy.status || "REFERENCED") : "UNRESOLVED",

    executionPermitted: Boolean(isObject && policy.executionPermitted === true),
    mutationPermitted: Boolean(isObject && policy.mutationPermitted === true),
    rollbackPermitted: Boolean(isObject && policy.rollbackPermitted === true),
    replayPermitted: Boolean(isObject && policy.replayPermitted === true),

    diagnostics: freezeObject({
      normalized: true,
      policyLinked: true,
      sourceExecutionObserved: Boolean(isObject && policy.executionPermitted === true),
      sourceMutationObserved: Boolean(isObject && policy.mutationPermitted === true),
      sourceRollbackObserved: Boolean(isObject && policy.rollbackPermitted === true),
      sourceReplayObserved: Boolean(isObject && policy.replayPermitted === true),
      bridgeExecutionGranted: false,
      bridgeMutationGranted: false,
      bridgeRollbackGranted: false,
      bridgeReplayGranted: false,
    }),
  });
}

function createExecutionKernelPolicyBridge(input = {}) {
  const kernelSnapshot = input.kernelSnapshot || {};
  const stages = Array.isArray(kernelSnapshot.stages) ? kernelSnapshot.stages : [];
  const policy = normalizeExecutionPolicyReference(input.policy);

  return freezeObject({
    schemaVersion: POLICY_BRIDGE_SCHEMA_VERSION,
    kind: "EXECUTION_KERNEL_POLICY_BRIDGE",

    kernel: freezeObject({
      schemaVersion: String(kernelSnapshot.schemaVersion || "unknown"),
      kind: String(kernelSnapshot.kind || "EXECUTION_KERNEL_SNAPSHOT"),
      mode: String(kernelSnapshot.mode || "INSPECTION"),
      stageCount: stages.length,
    }),

    policy,

    audit: freezeObject({ id: referenceId(input.audit, "audit.unresolved"), linked: true }),
    trace: freezeObject({ id: referenceId(input.trace, "trace.unresolved"), linked: true }),
    scheduler: freezeObject({ id: referenceId(input.scheduler, "scheduler.unresolved"), linked: true }),
    queue: freezeObject({ id: referenceId(input.queue, "queue.unresolved"), linked: true }),
    replay: freezeObject({ id: referenceId(input.replay, "replay.unresolved"), linked: true }),
    checkpoint: freezeObject({ id: referenceId(input.checkpoint, "checkpoint.unresolved"), linked: true }),
    runtimeEnvironment: freezeObject({ id: referenceId(input.runtimeEnvironment, "runtime.unresolved"), linked: true }),

    linkage: freezeObject({
      kernelLinked: true,
      policyLinked: true,
      auditLinked: true,
      traceLinked: true,
      schedulerLinked: true,
      queueLinked: true,
      replayLinked: true,
      checkpointLinked: true,
      runtimeLinked: true,

      policyInspectionOnly: true,
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
      policyOnly: true,

      executionBlocked: true,
      mutationFree: true,
      rollbackBlocked: true,
      replayBlocked: true,
      schedulingBlocked: true,
      dispatchBlocked: true,
      dequeueBlocked: true,
      surfaceFormBlocked: true,

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

function buildExecutionKernelPolicyBridgeSnapshot(input = {}) {
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

  return createExecutionKernelPolicyBridge({
    kernelSnapshot,
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

function getExecutionKernelPolicyBridgeDiagnostics(bridge = {}) {
  const linkage = bridge.linkage || {};
  const diagnostics = bridge.diagnostics || {};

  return freezeObject({
    schemaVersion: String(bridge.schemaVersion || POLICY_BRIDGE_SCHEMA_VERSION),
    ready: Boolean(diagnostics.ready),

    kernelLinked: Boolean(linkage.kernelLinked),
    policyLinked: Boolean(linkage.policyLinked),
    auditLinked: Boolean(linkage.auditLinked),
    traceLinked: Boolean(linkage.traceLinked),
    schedulerLinked: Boolean(linkage.schedulerLinked),
    queueLinked: Boolean(linkage.queueLinked),
    replayLinked: Boolean(linkage.replayLinked),
    checkpointLinked: Boolean(linkage.checkpointLinked),
    runtimeLinked: Boolean(linkage.runtimeLinked),

    policyInspectionOnly: Boolean(linkage.policyInspectionOnly),
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
  POLICY_BRIDGE_SCHEMA_VERSION,
  normalizeExecutionPolicyReference,
  createExecutionKernelPolicyBridge,
  buildExecutionKernelPolicyBridgeSnapshot,
  getExecutionKernelPolicyBridgeDiagnostics,
};