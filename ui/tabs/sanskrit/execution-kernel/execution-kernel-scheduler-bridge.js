"use strict";

const {
  createExecutionKernelSnapshot
} = require("./execution-kernel-engine.js");

const EXECUTION_KERNEL_SCHEDULER_BRIDGE_SCHEMA_VERSION =
  "sanskrit-execution-kernel-scheduler-bridge.v1";

function normalizeExecutionSchedulerReference(scheduler) {
  const isObject = scheduler && typeof scheduler === "object";
  const isNullish = scheduler === null || typeof scheduler === "undefined";
  const sourceScheduledObserved = Boolean(
    isObject && scheduler.scheduled === true
  );
  const sourceDispatchObserved = Boolean(
    isObject && scheduler.dispatchAllowed === true
  );

  return Object.freeze({
    id: isObject
      ? String(scheduler.id || scheduler.referenceId || "scheduler.unresolved")
      : String(isNullish ? "scheduler.unresolved" : scheduler),
    kind: isObject
      ? String(scheduler.kind || "EXECUTION_SCHEDULER_REFERENCE")
      : "EXECUTION_SCHEDULER_REFERENCE",
    schemaVersion: isObject
      ? String(scheduler.schemaVersion || "unknown")
      : "unknown",
    status: isObject
      ? String(scheduler.status || "REFERENCED")
      : isNullish
        ? "UNRESOLVED"
        : "REFERENCED",
    scheduled: sourceScheduledObserved,
    dispatchAllowed: sourceDispatchObserved,
    diagnostics: Object.freeze({
      normalized: true,
      schedulerLinked: true,
      sourceScheduledObserved,
      sourceDispatchObserved,
      bridgeScheduleGranted: false,
      bridgeDispatchGranted: false,
      bridgeExecutionGranted: false
    })
  });
}

function normalizeLinkedReference(reference, fallbackId) {
  const isObject = reference && typeof reference === "object";

  return Object.freeze({
    id: isObject
      ? String(reference.id || reference.referenceId || fallbackId)
      : String(reference || fallbackId),
    linked: true
  });
}

function createExecutionKernelSchedulerBridge(input) {
  const safeInput = input && typeof input === "object" ? input : {};
  const kernelSnapshot =
    safeInput.kernelSnapshot && typeof safeInput.kernelSnapshot === "object"
      ? safeInput.kernelSnapshot
      : {};
  const stages = Array.isArray(kernelSnapshot.stages) ? kernelSnapshot.stages : [];

  return Object.freeze({
    schemaVersion: EXECUTION_KERNEL_SCHEDULER_BRIDGE_SCHEMA_VERSION,
    kind: "EXECUTION_KERNEL_SCHEDULER_BRIDGE",
    kernel: Object.freeze({
      schemaVersion: kernelSnapshot.schemaVersion,
      kind: kernelSnapshot.kind,
      mode: String(kernelSnapshot.mode || "INSPECTION"),
      stageCount: stages.length
    }),
    scheduler: normalizeExecutionSchedulerReference(safeInput.scheduler),
    queue: normalizeLinkedReference(safeInput.queue, "queue.unresolved"),
    replay: normalizeLinkedReference(safeInput.replay, "replay.unresolved"),
    checkpoint: normalizeLinkedReference(
      safeInput.checkpoint,
      "checkpoint.unresolved"
    ),
    runtimeEnvironment: normalizeLinkedReference(
      safeInput.runtimeEnvironment,
      "runtime.unresolved"
    ),
    linkage: Object.freeze({
      kernelLinked: true,
      schedulerLinked: true,
      queueLinked: true,
      replayLinked: true,
      checkpointLinked: true,
      runtimeLinked: true,
      executionBlocked: true,
      schedulingBlocked: true,
      dispatchBlocked: true,
      rollbackBlocked: true,
      restoreBlocked: true,
      mutationBlocked: true,
      surfaceFormBlocked: true
    }),
    diagnostics: Object.freeze({
      ready: true,
      deterministic: true,
      immutable: true,
      inspectionOnly: true,
      schedulerOnly: true,
      replaySafe: true,
      executionBlocked: true,
      schedulingBlocked: true,
      dispatchBlocked: true,
      rollbackBlocked: true,
      restoreBlocked: true,
      mutationFree: true,
      surfaceFormBlocked: true,
      queueCompatible: true,
      stageCount: stages.length
    })
  });
}

function buildExecutionKernelSchedulerBridgeSnapshot(input) {
  const safeInput = input && typeof input === "object" ? input : {};
  const kernelSnapshot =
    safeInput.kernelSnapshot ||
    createExecutionKernelSnapshot({
      mode: safeInput.mode || "INSPECTION",
      guard: safeInput.guardReference || "guard.unresolved",
      runtimeEnvironment:
        safeInput.runtimeEnvironment || "runtime.unresolved",
      prakriyaPlan: safeInput.prakriyaPlan || "prakriya.unresolved",
      derivationGraph: safeInput.derivationGraph || "graph.unresolved",
      stages: safeInput.stages || []
    });

  return createExecutionKernelSchedulerBridge({
    kernelSnapshot,
    scheduler:
      safeInput.scheduler ||
      safeInput.schedulerReference ||
      "scheduler.unresolved",
    queue:
      safeInput.queue ||
      safeInput.queueReference ||
      "queue.unresolved",
    replay:
      safeInput.replay ||
      safeInput.replayReference ||
      "replay.unresolved",
    checkpoint:
      safeInput.checkpoint ||
      safeInput.checkpointReference ||
      "checkpoint.unresolved",
    runtimeEnvironment:
      safeInput.runtimeEnvironment ||
      (kernelSnapshot.references && kernelSnapshot.references.runtimeEnvironment)
  });
}

function getExecutionKernelSchedulerBridgeDiagnostics(bridge) {
  const safeBridge = bridge && typeof bridge === "object" ? bridge : {};
  const linkage = safeBridge.linkage || {};
  const diagnostics = safeBridge.diagnostics || {};

  return {
    schemaVersion: safeBridge.schemaVersion,
    ready: Boolean(diagnostics.ready),
    kernelLinked: Boolean(linkage.kernelLinked),
    schedulerLinked: Boolean(linkage.schedulerLinked),
    queueLinked: Boolean(linkage.queueLinked),
    replayLinked: Boolean(linkage.replayLinked),
    checkpointLinked: Boolean(linkage.checkpointLinked),
    runtimeLinked: Boolean(linkage.runtimeLinked),
    executionBlocked: Boolean(linkage.executionBlocked),
    schedulingBlocked: Boolean(linkage.schedulingBlocked),
    dispatchBlocked: Boolean(linkage.dispatchBlocked),
    rollbackBlocked: Boolean(linkage.rollbackBlocked),
    restoreBlocked: Boolean(linkage.restoreBlocked),
    mutationFree: Boolean(diagnostics.mutationFree),
    surfaceFormBlocked: Boolean(linkage.surfaceFormBlocked),
    queueCompatible: Boolean(diagnostics.queueCompatible),
    stageCount: Number.isFinite(Number(diagnostics.stageCount))
      ? Number(diagnostics.stageCount)
      : 0
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeExecutionSchedulerReference,
    createExecutionKernelSchedulerBridge,
    buildExecutionKernelSchedulerBridgeSnapshot,
    getExecutionKernelSchedulerBridgeDiagnostics
  };
}
