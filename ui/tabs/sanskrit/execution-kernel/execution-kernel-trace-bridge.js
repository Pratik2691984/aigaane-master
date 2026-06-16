"use strict";

const {
  createExecutionKernelSnapshot,
} = require("./execution-kernel-engine.js");

const TRACE_BRIDGE_SCHEMA_VERSION = "sanskrit-execution-kernel-trace-bridge.v1";

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

function normalizeExecutionTraceReference(trace) {
  const isObject = trace && typeof trace === "object";
  const isString = typeof trace === "string";

  const normalized = {
    id: isString ? trace : isObject ? String(trace.id || trace.referenceId || "trace.unresolved") : "trace.unresolved",
    kind: isString ? "EXECUTION_TRACE_REFERENCE" : isObject ? String(trace.kind || "EXECUTION_TRACE_REFERENCE") : "EXECUTION_TRACE_REFERENCE",
    schemaVersion: isString ? "unknown" : isObject ? String(trace.schemaVersion || "unknown") : "unknown",
    status: isString ? "REFERENCED" : isObject ? String(trace.status || "REFERENCED") : "UNRESOLVED",
    traceable: Boolean(isObject && trace.traceable === true),
    replaySafe: Boolean(isObject && trace.replaySafe === true),
    mutationFree: Boolean(isObject && trace.mutationFree === true),
    diagnostics: freezeObject({
      normalized: true,
      traceLinked: true,
      sourceTraceableObserved: Boolean(isObject && trace.traceable === true),
      sourceReplaySafeObserved: Boolean(isObject && trace.replaySafe === true),
      sourceMutationFreeObserved: Boolean(isObject && trace.mutationFree === true),
      bridgeTraceGranted: false,
      bridgeReplayGranted: false,
      bridgeMutationGranted: false,
    }),
  };

  return freezeObject(normalized);
}

function createExecutionKernelTraceBridge(input = {}) {
  const kernelSnapshot = input.kernelSnapshot || {};
  const stages = Array.isArray(kernelSnapshot.stages) ? kernelSnapshot.stages : [];
  const trace = normalizeExecutionTraceReference(input.trace);

  const bridge = {
    schemaVersion: TRACE_BRIDGE_SCHEMA_VERSION,
    kind: "EXECUTION_KERNEL_TRACE_BRIDGE",

    kernel: freezeObject({
      schemaVersion: String(kernelSnapshot.schemaVersion || "unknown"),
      kind: String(kernelSnapshot.kind || "EXECUTION_KERNEL_SNAPSHOT"),
      mode: String(kernelSnapshot.mode || "INSPECTION"),
      stageCount: stages.length,
    }),

    trace,

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
      traceLinked: true,
      schedulerLinked: true,
      queueLinked: true,
      replayLinked: true,
      checkpointLinked: true,
      runtimeLinked: true,

      traceInspectionOnly: true,
      replaySafe: true,
      executionBlocked: true,
      schedulingBlocked: true,
      dispatchBlocked: true,
      dequeueBlocked: true,
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
      traceOnly: true,
      replaySafe: true,

      executionBlocked: true,
      schedulingBlocked: true,
      dispatchBlocked: true,
      dequeueBlocked: true,
      rollbackBlocked: true,
      restoreBlocked: true,

      mutationFree: true,
      surfaceFormBlocked: true,

      queueCompatible: true,
      schedulerCompatible: true,
      checkpointCompatible: true,

      stageCount: stages.length,
    }),
  };

  return freezeObject(bridge);
}

function buildExecutionKernelTraceBridgeSnapshot(input = {}) {
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

  return createExecutionKernelTraceBridge({
    kernelSnapshot,
    trace: input.trace || input.traceReference || "trace.unresolved",
    scheduler: input.scheduler || input.schedulerReference || "scheduler.unresolved",
    queue: input.queue || input.queueReference || "queue.unresolved",
    replay: input.replay || input.replayReference || "replay.unresolved",
    checkpoint: input.checkpoint || input.checkpointReference || "checkpoint.unresolved",
    runtimeEnvironment: input.runtimeEnvironment || kernelSnapshot.references.runtimeEnvironment,
  });
}

function getExecutionKernelTraceBridgeDiagnostics(bridge = {}) {
  const linkage = bridge.linkage || {};
  const diagnostics = bridge.diagnostics || {};

  return freezeObject({
    schemaVersion: String(bridge.schemaVersion || TRACE_BRIDGE_SCHEMA_VERSION),
    ready: Boolean(diagnostics.ready),
    kernelLinked: Boolean(linkage.kernelLinked),
    traceLinked: Boolean(linkage.traceLinked),
    schedulerLinked: Boolean(linkage.schedulerLinked),
    queueLinked: Boolean(linkage.queueLinked),
    replayLinked: Boolean(linkage.replayLinked),
    checkpointLinked: Boolean(linkage.checkpointLinked),
    runtimeLinked: Boolean(linkage.runtimeLinked),
    replaySafe: Boolean(linkage.replaySafe),
    executionBlocked: Boolean(linkage.executionBlocked),
    schedulingBlocked: Boolean(linkage.schedulingBlocked),
    dispatchBlocked: Boolean(linkage.dispatchBlocked),
    dequeueBlocked: Boolean(linkage.dequeueBlocked),
    rollbackBlocked: Boolean(linkage.rollbackBlocked),
    restoreBlocked: Boolean(linkage.restoreBlocked),
    mutationFree: Boolean(diagnostics.mutationFree),
    surfaceFormBlocked: Boolean(linkage.surfaceFormBlocked),
    stageCount: Number(diagnostics.stageCount || 0),
  });
}

module.exports = {
  TRACE_BRIDGE_SCHEMA_VERSION,
  normalizeExecutionTraceReference,
  createExecutionKernelTraceBridge,
  buildExecutionKernelTraceBridgeSnapshot,
  getExecutionKernelTraceBridgeDiagnostics,
};