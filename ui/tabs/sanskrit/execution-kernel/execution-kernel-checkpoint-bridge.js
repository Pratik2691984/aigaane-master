"use strict";

const {
  createExecutionKernelSnapshot
} = require("./execution-kernel-engine.js");

const EXECUTION_KERNEL_CHECKPOINT_BRIDGE_SCHEMA_VERSION =
  "sanskrit-execution-kernel-checkpoint-bridge.v1";

function normalizeExecutionCheckpointReference(checkpoint) {
  const isObject = checkpoint && typeof checkpoint === "object";
  const isNullish = checkpoint === null || typeof checkpoint === "undefined";
  const sourceRestorableObserved = Boolean(isObject && checkpoint.restorable === true);
  const sourceRollbackEligibleObserved = Boolean(
    isObject && checkpoint.rollbackEligible === true
  );

  return Object.freeze({
    id: isObject
      ? String(checkpoint.id || checkpoint.referenceId || "checkpoint.unresolved")
      : String(isNullish ? "checkpoint.unresolved" : checkpoint),
    kind: isObject
      ? String(checkpoint.kind || "EXECUTION_CHECKPOINT_REFERENCE")
      : "EXECUTION_CHECKPOINT_REFERENCE",
    schemaVersion: isObject
      ? String(checkpoint.schemaVersion || "unknown")
      : "unknown",
    status: isObject
      ? String(checkpoint.status || "REFERENCED")
      : isNullish
        ? "UNRESOLVED"
        : "REFERENCED",
    restorable: sourceRestorableObserved,
    rollbackEligible: sourceRollbackEligibleObserved,
    diagnostics: Object.freeze({
      normalized: true,
      checkpointLinked: true,
      sourceRestorableObserved,
      sourceRollbackEligibleObserved,
      bridgeRestoreGranted: false,
      bridgeRollbackGranted: false,
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

function createExecutionKernelCheckpointBridge(input) {
  const safeInput = input && typeof input === "object" ? input : {};
  const kernelSnapshot =
    safeInput.kernelSnapshot && typeof safeInput.kernelSnapshot === "object"
      ? safeInput.kernelSnapshot
      : {};
  const stages = Array.isArray(kernelSnapshot.stages) ? kernelSnapshot.stages : [];

  return Object.freeze({
    schemaVersion: EXECUTION_KERNEL_CHECKPOINT_BRIDGE_SCHEMA_VERSION,
    kind: "EXECUTION_KERNEL_CHECKPOINT_BRIDGE",
    kernel: Object.freeze({
      schemaVersion: kernelSnapshot.schemaVersion,
      kind: kernelSnapshot.kind,
      mode: String(kernelSnapshot.mode || "INSPECTION"),
      stageCount: stages.length
    }),
    checkpoint: normalizeExecutionCheckpointReference(safeInput.checkpoint),
    guard: normalizeLinkedReference(safeInput.guardReference, "guard.unresolved"),
    runtimeEnvironment: normalizeLinkedReference(
      safeInput.runtimeEnvironment,
      "runtime.unresolved"
    ),
    linkage: Object.freeze({
      kernelLinked: true,
      checkpointLinked: true,
      guardLinked: true,
      runtimeLinked: true,
      replaySafe: true,
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
      checkpointOnly: true,
      replaySafe: true,
      restoreBlocked: true,
      rollbackBlocked: true,
      executionBlocked: true,
      mutationFree: true,
      surfaceFormBlocked: true,
      stageCount: stages.length
    })
  });
}

function buildExecutionKernelCheckpointBridgeSnapshot(input) {
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

  return createExecutionKernelCheckpointBridge({
    kernelSnapshot,
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

function getExecutionKernelCheckpointBridgeDiagnostics(bridge) {
  const safeBridge = bridge && typeof bridge === "object" ? bridge : {};
  const linkage = safeBridge.linkage || {};
  const diagnostics = safeBridge.diagnostics || {};

  return {
    schemaVersion: safeBridge.schemaVersion,
    ready: Boolean(diagnostics.ready),
    kernelLinked: Boolean(linkage.kernelLinked),
    checkpointLinked: Boolean(linkage.checkpointLinked),
    guardLinked: Boolean(linkage.guardLinked),
    runtimeLinked: Boolean(linkage.runtimeLinked),
    replaySafe: Boolean(linkage.replaySafe),
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
    normalizeExecutionCheckpointReference,
    createExecutionKernelCheckpointBridge,
    buildExecutionKernelCheckpointBridgeSnapshot,
    getExecutionKernelCheckpointBridgeDiagnostics
  };
}
