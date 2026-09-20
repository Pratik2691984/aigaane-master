"use strict";

const {
  createExecutionKernelSnapshot,
} = require("./execution-kernel-engine.js");

const AUDIT_BRIDGE_SCHEMA_VERSION = "sanskrit-execution-kernel-audit-bridge.v1";

function freezeObject(value) {
  return Object.freeze(value);
}

function referenceId(value, fallback) {
  if (typeof value === "string") {
    return value;
  }
  if (value && typeof value === "object") {
    return String(value.id || value.referenceId || fallback);
  }
  return fallback;
}

function normalizeExecutionAuditReference(audit) {
  const isObject = audit && typeof audit === "object";
  const isString = typeof audit === "string";

  const normalized = {
    id: isString ? audit : isObject ? String(audit.id || audit.referenceId || "audit.unresolved") : "audit.unresolved",
    kind: isString ? "EXECUTION_AUDIT_REFERENCE" : isObject ? String(audit.kind || "EXECUTION_AUDIT_REFERENCE") : "EXECUTION_AUDIT_REFERENCE",
    schemaVersion: isString ? "unknown" : isObject ? String(audit.schemaVersion || "unknown") : "unknown",
    status: isString ? "REFERENCED" : isObject ? String(audit.status || "REFERENCED") : "UNRESOLVED",
    auditable: Boolean(isObject && audit.auditable === true),
    auditMutationAllowed: Boolean(isObject && audit.auditMutationAllowed === true),
    diagnostics: freezeObject({
      normalized: true,
      auditLinked: true,
      sourceAuditableObserved: Boolean(isObject && audit.auditable === true),
      sourceAuditMutationObserved: Boolean(isObject && audit.auditMutationAllowed === true),
      bridgeAuditGranted: false,
      bridgeAuditMutationGranted: false,
      bridgeExecutionGranted: false,
    }),
  };

  return freezeObject(normalized);
}

function createExecutionKernelAuditBridge(input = {}) {
  const kernelSnapshot = input.kernelSnapshot || {};
  const stages = Array.isArray(kernelSnapshot.stages) ? kernelSnapshot.stages : [];
  const audit = normalizeExecutionAuditReference(input.audit);

  const bridge = {
    schemaVersion: AUDIT_BRIDGE_SCHEMA_VERSION,
    kind: "EXECUTION_KERNEL_AUDIT_BRIDGE",

    kernel: freezeObject({
      schemaVersion: String(kernelSnapshot.schemaVersion || "unknown"),
      kind: String(kernelSnapshot.kind || "EXECUTION_KERNEL_SNAPSHOT"),
      mode: String(kernelSnapshot.mode || "INSPECTION"),
      stageCount: stages.length,
    }),

    audit,

    trace: freezeObject({
      id: referenceId(input.trace, "trace.unresolved"),
      linked: true,
    }),

    scheduler: freezeObject({
      id: referenceId(input.scheduler, "scheduler.unresolved"),
      linked: true,
    }),

    queue: freezeObject({
      id: referenceId(input.queue, "queue.unresolved"),
      linked: true,
    }),

    replay: freezeObject({
      id: referenceId(input.replay, "replay.unresolved"),
      linked: true,
    }),

    checkpoint: freezeObject({
      id: referenceId(input.checkpoint, "checkpoint.unresolved"),
      linked: true,
    }),

    runtimeEnvironment: freezeObject({
      id: referenceId(input.runtimeEnvironment, "runtime.unresolved"),
      linked: true,
    }),

    linkage: freezeObject({
      kernelLinked: true,
      auditLinked: true,
      traceLinked: true,
      schedulerLinked: true,
      queueLinked: true,
      replayLinked: true,
      checkpointLinked: true,
      runtimeLinked: true,

      auditInspectionOnly: true,
      auditMutationBlocked: true,
      replaySafe: true,
      executionBlocked: true,
      schedulingBlocked: true,
      dispatchBlocked: true,
      dequeueBlocked: true,
      replayBlocked: true,
      rollbackBlocked: true,
      restoreBlocked: true,
      mutationBlocked: true,
      surfaceFormBlocked: true,
    }),

    diagnostics: freezeObject({
      ready: true,
      deterministic: true,
      immutable: true,
      inspectionOnly: true,
      auditOnly: true,
      replaySafe: true,

      auditMutationBlocked: true,
      executionBlocked: true,
      schedulingBlocked: true,
      dispatchBlocked: true,
      dequeueBlocked: true,
      replayBlocked: true,
      rollbackBlocked: true,
      restoreBlocked: true,

      mutationFree: true,
      surfaceFormBlocked: true,

      traceCompatible: true,
      schedulerCompatible: true,
      queueCompatible: true,
      checkpointCompatible: true,
      replayCompatible: true,
      runtimeCompatible: true,

      stageCount: stages.length,
    }),
  };

  return freezeObject(bridge);
}

function buildExecutionKernelAuditBridgeSnapshot(input = {}) {
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

  return createExecutionKernelAuditBridge({
    kernelSnapshot,
    audit: input.audit || input.auditReference || "audit.unresolved",
    trace: input.trace || input.traceReference || "trace.unresolved",
    scheduler: input.scheduler || input.schedulerReference || "scheduler.unresolved",
    queue: input.queue || input.queueReference || "queue.unresolved",
    replay: input.replay || input.replayReference || "replay.unresolved",
    checkpoint: input.checkpoint || input.checkpointReference || "checkpoint.unresolved",
    runtimeEnvironment: input.runtimeEnvironment || kernelSnapshot.references.runtimeEnvironment,
  });
}

function getExecutionKernelAuditBridgeDiagnostics(bridge = {}) {
  const linkage = bridge.linkage || {};
  const diagnostics = bridge.diagnostics || {};

  return freezeObject({
    schemaVersion: String(bridge.schemaVersion || AUDIT_BRIDGE_SCHEMA_VERSION),
    ready: Boolean(diagnostics.ready),
    kernelLinked: Boolean(linkage.kernelLinked),
    auditLinked: Boolean(linkage.auditLinked),
    traceLinked: Boolean(linkage.traceLinked),
    schedulerLinked: Boolean(linkage.schedulerLinked),
    queueLinked: Boolean(linkage.queueLinked),
    replayLinked: Boolean(linkage.replayLinked),
    checkpointLinked: Boolean(linkage.checkpointLinked),
    runtimeLinked: Boolean(linkage.runtimeLinked),
    auditInspectionOnly: Boolean(linkage.auditInspectionOnly),
    auditMutationBlocked: Boolean(linkage.auditMutationBlocked),
    replaySafe: Boolean(linkage.replaySafe),
    executionBlocked: Boolean(linkage.executionBlocked),
    schedulingBlocked: Boolean(linkage.schedulingBlocked),
    dispatchBlocked: Boolean(linkage.dispatchBlocked),
    dequeueBlocked: Boolean(linkage.dequeueBlocked),
    replayBlocked: Boolean(linkage.replayBlocked),
    rollbackBlocked: Boolean(linkage.rollbackBlocked),
    restoreBlocked: Boolean(linkage.restoreBlocked),
    mutationFree: Boolean(diagnostics.mutationFree),
    surfaceFormBlocked: Boolean(linkage.surfaceFormBlocked),
    stageCount: Number(diagnostics.stageCount || 0),
  });
}

module.exports = {
  AUDIT_BRIDGE_SCHEMA_VERSION,
  normalizeExecutionAuditReference,
  createExecutionKernelAuditBridge,
  buildExecutionKernelAuditBridgeSnapshot,
  getExecutionKernelAuditBridgeDiagnostics,
};