"use strict";

const {
  createExecutionKernelSnapshot
} = require("./execution-kernel-engine.js");

const EXECUTION_KERNEL_REPLAY_BRIDGE_SCHEMA_VERSION =
  "sanskrit-execution-kernel-replay-bridge.v1";

function normalizeExecutionReplayReference(replay) {
  const isObject = replay && typeof replay === "object";
  const isNullish = replay === null || typeof replay === "undefined";
  const sourceReplayableObserved = Boolean(isObject && replay.replayable === true);
  const sourceDeterministicReplayObserved = Boolean(
    isObject && replay.deterministicReplay === true
  );

  return Object.freeze({
    id: isObject
      ? String(replay.id || replay.referenceId || "replay.unresolved")
      : String(isNullish ? "replay.unresolved" : replay),
    kind: isObject
      ? String(replay.kind || "EXECUTION_REPLAY_REFERENCE")
      : "EXECUTION_REPLAY_REFERENCE",
    schemaVersion: isObject ? String(replay.schemaVersion || "unknown") : "unknown",
    status: isObject
      ? String(replay.status || "REFERENCED")
      : isNullish
        ? "UNRESOLVED"
        : "REFERENCED",
    replayable: sourceReplayableObserved,
    deterministicReplay: sourceDeterministicReplayObserved,
    diagnostics: Object.freeze({
      normalized: true,
      replayLinked: true,
      sourceReplayableObserved,
      sourceDeterministicReplayObserved,
      bridgeReplayGranted: false,
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

function normalizeTraceReference(trace) {
  const reference = normalizeLinkedReference(trace, "trace.unresolved");

  return Object.freeze({
    id: reference.id,
    linked: true,
    replaySafe: true,
    mutationFree: true
  });
}

function createExecutionKernelReplayBridge(input) {
  const safeInput = input && typeof input === "object" ? input : {};
  const kernelSnapshot =
    safeInput.kernelSnapshot && typeof safeInput.kernelSnapshot === "object"
      ? safeInput.kernelSnapshot
      : {};
  const stages = Array.isArray(kernelSnapshot.stages) ? kernelSnapshot.stages : [];

  return Object.freeze({
    schemaVersion: EXECUTION_KERNEL_REPLAY_BRIDGE_SCHEMA_VERSION,
    kind: "EXECUTION_KERNEL_REPLAY_BRIDGE",
    kernel: Object.freeze({
      schemaVersion: kernelSnapshot.schemaVersion,
      kind: kernelSnapshot.kind,
      mode: String(kernelSnapshot.mode || "INSPECTION"),
      stageCount: stages.length
    }),
    replay: normalizeExecutionReplayReference(safeInput.replay),
    checkpoint: normalizeLinkedReference(
      safeInput.checkpoint,
      "checkpoint.unresolved"
    ),
    trace: normalizeTraceReference(safeInput.trace),
    guard: normalizeLinkedReference(safeInput.guardReference, "guard.unresolved"),
    runtimeEnvironment: normalizeLinkedReference(
      safeInput.runtimeEnvironment,
      "runtime.unresolved"
    ),
    linkage: Object.freeze({
      kernelLinked: true,
      replayLinked: true,
      checkpointLinked: true,
      traceLinked: true,
      guardLinked: true,
      runtimeLinked: true,
      replaySafe: true,
      replayBlocked: true,
      restoreBlocked: true,
      rollbackBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      surfaceFormBlocked: true
    }),
    diagnostics: Object.freeze({
      ready: true,
      deterministic: true,
      immutable: true,
      inspectionOnly: true,
      replayOnly: true,
      replaySafe: true,
      replayBlocked: true,
      restoreBlocked: true,
      rollbackBlocked: true,
      executionBlocked: true,
      mutationFree: true,
      surfaceFormBlocked: true,
      stageCount: stages.length
    })
  });
}

function buildExecutionKernelReplayBridgeSnapshot(input) {
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

  return createExecutionKernelReplayBridge({
    kernelSnapshot,
    replay:
      safeInput.replay ||
      safeInput.replayReference ||
      "replay.unresolved",
    checkpoint:
      safeInput.checkpoint ||
      safeInput.checkpointReference ||
      "checkpoint.unresolved",
    trace:
      safeInput.trace ||
      safeInput.traceReference ||
      "trace.unresolved",
    guardReference:
      safeInput.guardReference ||
      (kernelSnapshot.references && kernelSnapshot.references.guard),
    runtimeEnvironment:
      safeInput.runtimeEnvironment ||
      (kernelSnapshot.references && kernelSnapshot.references.runtimeEnvironment)
  });
}

function getExecutionKernelReplayBridgeDiagnostics(bridge) {
  const safeBridge = bridge && typeof bridge === "object" ? bridge : {};
  const linkage = safeBridge.linkage || {};
  const diagnostics = safeBridge.diagnostics || {};

  return {
    schemaVersion: safeBridge.schemaVersion,
    ready: Boolean(diagnostics.ready),
    kernelLinked: Boolean(linkage.kernelLinked),
    replayLinked: Boolean(linkage.replayLinked),
    checkpointLinked: Boolean(linkage.checkpointLinked),
    traceLinked: Boolean(linkage.traceLinked),
    guardLinked: Boolean(linkage.guardLinked),
    runtimeLinked: Boolean(linkage.runtimeLinked),
    replaySafe: Boolean(linkage.replaySafe),
    replayBlocked: Boolean(linkage.replayBlocked),
    restoreBlocked: Boolean(linkage.restoreBlocked),
    rollbackBlocked: Boolean(linkage.rollbackBlocked),
    executionBlocked: Boolean(linkage.executionBlocked),
    mutationFree: Boolean(diagnostics.mutationFree),
    surfaceFormBlocked: Boolean(linkage.surfaceFormBlocked),
    stageCount: Number.isFinite(Number(diagnostics.stageCount))
      ? Number(diagnostics.stageCount)
      : 0
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeExecutionReplayReference,
    createExecutionKernelReplayBridge,
    buildExecutionKernelReplayBridgeSnapshot,
    getExecutionKernelReplayBridgeDiagnostics
  };
}
