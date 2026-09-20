"use strict";

const {
  createExecutionKernelSnapshot
} = require("./execution-kernel-engine.js");

const EXECUTION_KERNEL_QUEUE_BRIDGE_SCHEMA_VERSION =
  "sanskrit-execution-kernel-queue-bridge.v1";

function normalizeExecutionQueueReference(queue) {
  const isObject = queue && typeof queue === "object";
  const isNullish = queue === null || typeof queue === "undefined";
  const sourceQueuedObserved = Boolean(isObject && queue.queued === true);
  const sourceDequeueObserved = Boolean(isObject && queue.dequeueAllowed === true);

  return Object.freeze({
    id: isObject
      ? String(queue.id || queue.referenceId || "queue.unresolved")
      : String(isNullish ? "queue.unresolved" : queue),
    kind: isObject
      ? String(queue.kind || "EXECUTION_QUEUE_REFERENCE")
      : "EXECUTION_QUEUE_REFERENCE",
    schemaVersion: isObject ? String(queue.schemaVersion || "unknown") : "unknown",
    status: isObject
      ? String(queue.status || "REFERENCED")
      : isNullish
        ? "UNRESOLVED"
        : "REFERENCED",
    queued: sourceQueuedObserved,
    dequeueAllowed: sourceDequeueObserved,
    diagnostics: Object.freeze({
      normalized: true,
      queueLinked: true,
      sourceQueuedObserved,
      sourceDequeueObserved,
      bridgeQueueGranted: false,
      bridgeExecutionGranted: false,
      bridgeMutationGranted: false
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

function createExecutionKernelQueueBridge(input) {
  const safeInput = input && typeof input === "object" ? input : {};
  const kernelSnapshot =
    safeInput.kernelSnapshot && typeof safeInput.kernelSnapshot === "object"
      ? safeInput.kernelSnapshot
      : {};
  const stages = Array.isArray(kernelSnapshot.stages) ? kernelSnapshot.stages : [];

  return Object.freeze({
    schemaVersion: EXECUTION_KERNEL_QUEUE_BRIDGE_SCHEMA_VERSION,
    kind: "EXECUTION_KERNEL_QUEUE_BRIDGE",
    kernel: Object.freeze({
      schemaVersion: kernelSnapshot.schemaVersion,
      kind: kernelSnapshot.kind,
      mode: String(kernelSnapshot.mode || "INSPECTION"),
      stageCount: stages.length
    }),
    queue: normalizeExecutionQueueReference(safeInput.queue),
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
      queueLinked: true,
      replayLinked: true,
      checkpointLinked: true,
      runtimeLinked: true,
      executionBlocked: true,
      dequeueBlocked: true,
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
      queueOnly: true,
      replaySafe: true,
      executionBlocked: true,
      dequeueBlocked: true,
      rollbackBlocked: true,
      restoreBlocked: true,
      mutationFree: true,
      surfaceFormBlocked: true,
      schedulerCompatible: true,
      stageCount: stages.length
    })
  });
}

function buildExecutionKernelQueueBridgeSnapshot(input) {
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

  return createExecutionKernelQueueBridge({
    kernelSnapshot,
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
    guardReference:
      safeInput.guardReference ||
      (kernelSnapshot.references && kernelSnapshot.references.guard),
    runtimeEnvironment:
      safeInput.runtimeEnvironment ||
      (kernelSnapshot.references && kernelSnapshot.references.runtimeEnvironment)
  });
}

function getExecutionKernelQueueBridgeDiagnostics(bridge) {
  const safeBridge = bridge && typeof bridge === "object" ? bridge : {};
  const linkage = safeBridge.linkage || {};
  const diagnostics = safeBridge.diagnostics || {};

  return {
    schemaVersion: safeBridge.schemaVersion,
    ready: Boolean(diagnostics.ready),
    kernelLinked: Boolean(linkage.kernelLinked),
    queueLinked: Boolean(linkage.queueLinked),
    replayLinked: Boolean(linkage.replayLinked),
    checkpointLinked: Boolean(linkage.checkpointLinked),
    runtimeLinked: Boolean(linkage.runtimeLinked),
    executionBlocked: Boolean(linkage.executionBlocked),
    dequeueBlocked: Boolean(linkage.dequeueBlocked),
    rollbackBlocked: Boolean(linkage.rollbackBlocked),
    restoreBlocked: Boolean(linkage.restoreBlocked),
    mutationFree: Boolean(diagnostics.mutationFree),
    surfaceFormBlocked: Boolean(linkage.surfaceFormBlocked),
    schedulerCompatible: Boolean(diagnostics.schedulerCompatible),
    stageCount: Number.isFinite(Number(diagnostics.stageCount))
      ? Number(diagnostics.stageCount)
      : 0
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeExecutionQueueReference,
    createExecutionKernelQueueBridge,
    buildExecutionKernelQueueBridgeSnapshot,
    getExecutionKernelQueueBridgeDiagnostics
  };
}
