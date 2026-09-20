"use strict";

const {
  createExecutionKernelSnapshot
} = require("./execution-kernel-engine.js");

const EXECUTION_KERNEL_RUNTIME_BRIDGE_SCHEMA_VERSION =
  "sanskrit-execution-kernel-runtime-bridge.v1";

function normalizeRuntimeEnvironment(environment) {
  const isObject = environment && typeof environment === "object";
  const sourceExecutionAllowedObserved = Boolean(
    isObject && environment.executionAllowed === true
  );
  const sourceMutationAllowedObserved = Boolean(
    isObject && environment.mutationAllowed === true
  );
  const sourceRollbackAllowedObserved = Boolean(
    isObject && environment.rollbackAllowed === true
  );

  return Object.freeze({
    id: isObject
      ? String(environment.id || environment.referenceId || "runtime.unresolved")
      : String(environment || ""),
    kind: isObject
      ? String(environment.kind || "RUNTIME_ENVIRONMENT_REFERENCE")
      : "RUNTIME_ENVIRONMENT_REFERENCE",
    schemaVersion: isObject
      ? String(environment.schemaVersion || "unknown")
      : "unknown",
    status: isObject ? String(environment.status || "REFERENCED") : "REFERENCED",
    ready: Boolean(isObject && environment.ready === true),
    executionAllowed: sourceExecutionAllowedObserved,
    mutationAllowed: sourceMutationAllowedObserved,
    rollbackAllowed: sourceRollbackAllowedObserved,
    diagnostics: Object.freeze({
      normalized: true,
      runtimeLinked: true,
      sourceExecutionAllowedObserved,
      sourceMutationAllowedObserved,
      sourceRollbackAllowedObserved,
      bridgeExecutionGranted: false,
      bridgeMutationGranted: false,
      bridgeRollbackGranted: false
    })
  });
}

function normalizeGuardReference(guardReference) {
  const isObject = guardReference && typeof guardReference === "object";

  return Object.freeze({
    id: isObject
      ? String(guardReference.id || guardReference.referenceId || "guard.unresolved")
      : String(guardReference || "guard.unresolved"),
    linked: true
  });
}

function createExecutionKernelRuntimeBridge(input) {
  const safeInput = input && typeof input === "object" ? input : {};
  const kernelSnapshot =
    safeInput.kernelSnapshot && typeof safeInput.kernelSnapshot === "object"
      ? safeInput.kernelSnapshot
      : {};
  const stages = Array.isArray(kernelSnapshot.stages) ? kernelSnapshot.stages : [];

  return Object.freeze({
    schemaVersion: EXECUTION_KERNEL_RUNTIME_BRIDGE_SCHEMA_VERSION,
    kind: "EXECUTION_KERNEL_RUNTIME_BRIDGE",
    kernel: Object.freeze({
      schemaVersion: kernelSnapshot.schemaVersion,
      kind: kernelSnapshot.kind,
      mode: String(kernelSnapshot.mode || "INSPECTION"),
      stageCount: stages.length
    }),
    runtime: normalizeRuntimeEnvironment(safeInput.runtimeEnvironment),
    guard: normalizeGuardReference(safeInput.guardReference),
    linkage: Object.freeze({
      kernelLinked: true,
      runtimeLinked: true,
      guardLinked: true,
      executionBlocked: true,
      mutationBlocked: true,
      rollbackBlocked: true,
      authorizationForwarded: false,
      executionForwarded: false,
      mutationForwarded: false
    }),
    diagnostics: Object.freeze({
      ready: true,
      deterministic: true,
      immutable: true,
      runtimeSafe: true,
      inspectionOnly: true,
      replaySafe: true,
      executionBlocked: true,
      mutationFree: true,
      rollbackBlocked: true,
      queueCompatible: true,
      schedulerCompatible: true,
      checkpointCompatible: true,
      stageCount: stages.length
    })
  });
}

function buildExecutionKernelRuntimeBridgeSnapshot(input) {
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

  return createExecutionKernelRuntimeBridge({
    kernelSnapshot,
    runtimeEnvironment:
      safeInput.runtimeEnvironment ||
      (kernelSnapshot.references && kernelSnapshot.references.runtimeEnvironment),
    guardReference:
      safeInput.guardReference ||
      (kernelSnapshot.references && kernelSnapshot.references.guard)
  });
}

function getExecutionKernelRuntimeBridgeDiagnostics(bridge) {
  const safeBridge = bridge && typeof bridge === "object" ? bridge : {};
  const linkage = safeBridge.linkage || {};
  const diagnostics = safeBridge.diagnostics || {};

  return {
    schemaVersion: safeBridge.schemaVersion,
    ready: Boolean(diagnostics.ready),
    runtimeLinked: Boolean(linkage.runtimeLinked),
    guardLinked: Boolean(linkage.guardLinked),
    kernelLinked: Boolean(linkage.kernelLinked),
    executionBlocked: Boolean(linkage.executionBlocked),
    mutationFree: Boolean(diagnostics.mutationFree),
    rollbackBlocked: Boolean(diagnostics.rollbackBlocked),
    stageCount: Number.isFinite(Number(diagnostics.stageCount))
      ? Number(diagnostics.stageCount)
      : 0
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeRuntimeEnvironment,
    createExecutionKernelRuntimeBridge,
    buildExecutionKernelRuntimeBridgeSnapshot,
    getExecutionKernelRuntimeBridgeDiagnostics
  };
}
