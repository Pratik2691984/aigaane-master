"use strict";

const {
  createExecutionKernelSnapshot
} = require("./execution-kernel-engine.js");

const EXECUTION_KERNEL_GUARD_BRIDGE_SCHEMA_VERSION =
  "sanskrit-execution-kernel-guard-bridge.v1";

function normalizeExecutionGuardReference(guard) {
  const isObject = guard && typeof guard === "object";
  const sourceAuthorizedObserved = Boolean(isObject && guard.authorized === true);
  const sourceExecutionBlocked = !(isObject && guard.executionBlocked === false);

  return Object.freeze({
    id: isObject
      ? String(guard.id || guard.referenceId || "guard.unresolved")
      : String(guard || ""),
    kind: isObject
      ? String(guard.kind || "EXECUTION_GUARD_REFERENCE")
      : "EXECUTION_GUARD_REFERENCE",
    schemaVersion: isObject ? String(guard.schemaVersion || "unknown") : "unknown",
    status: isObject ? String(guard.status || "REFERENCED") : "REFERENCED",
    authorized: Boolean(sourceAuthorizedObserved && !sourceExecutionBlocked),
    mutationAllowed: Boolean(isObject && guard.mutationAllowed === true),
    surfaceFormsAllowed: Boolean(isObject && guard.surfaceFormsAllowed === true),
    diagnostics: Object.freeze({
      normalized: true,
      guardLinked: true,
      sourceAuthorizedObserved,
      sourceExecutionBlocked,
      bridgeAuthorizationGranted: false,
      bridgeMutationGranted: false,
      bridgeSurfaceFormsGranted: false
    })
  });
}

function normalizeRuntimeEnvironmentReference(runtimeEnvironment) {
  const isObject = runtimeEnvironment && typeof runtimeEnvironment === "object";

  return Object.freeze({
    id: isObject
      ? String(runtimeEnvironment.id || runtimeEnvironment.referenceId || "runtime.unresolved")
      : String(runtimeEnvironment || ""),
    kind: isObject
      ? String(runtimeEnvironment.kind || "RUNTIME_ENVIRONMENT_REFERENCE")
      : "RUNTIME_ENVIRONMENT_REFERENCE",
    schemaVersion: isObject
      ? String(runtimeEnvironment.schemaVersion || "unknown")
      : "unknown",
    status: isObject ? String(runtimeEnvironment.status || "REFERENCED") : "REFERENCED"
  });
}

function createExecutionKernelGuardBridge(input) {
  const safeInput = input && typeof input === "object" ? input : {};
  const kernelSnapshot =
    safeInput.kernelSnapshot && typeof safeInput.kernelSnapshot === "object"
      ? safeInput.kernelSnapshot
      : {};
  const stages = Array.isArray(kernelSnapshot.stages) ? kernelSnapshot.stages : [];

  return Object.freeze({
    schemaVersion: EXECUTION_KERNEL_GUARD_BRIDGE_SCHEMA_VERSION,
    kind: "EXECUTION_KERNEL_GUARD_BRIDGE",
    kernel: Object.freeze({
      schemaVersion: kernelSnapshot.schemaVersion,
      kind: kernelSnapshot.kind,
      mode: String(kernelSnapshot.mode || "INSPECTION"),
      stageCount: stages.length
    }),
    guard: normalizeExecutionGuardReference(safeInput.guardSnapshot),
    runtimeEnvironment: normalizeRuntimeEnvironmentReference(
      safeInput.runtimeEnvironment
    ),
    linkage: Object.freeze({
      kernelLinked: true,
      guardLinked: true,
      runtimeLinked: true,
      executionBlocked: true,
      authorizationForwarded: false,
      mutationForwarded: false,
      surfaceFormForwarded: false
    }),
    diagnostics: Object.freeze({
      ready: true,
      deterministic: true,
      immutable: true,
      inspectionOnly: true,
      replaySafe: true,
      bridgeOnly: true,
      executionBlocked: true,
      mutationFree: true,
      surfaceFormBlocked: true,
      stageCount: stages.length
    })
  });
}

function buildExecutionKernelGuardBridgeSnapshot(input) {
  const safeInput = input && typeof input === "object" ? input : {};
  const kernelSnapshot =
    safeInput.kernelSnapshot ||
    createExecutionKernelSnapshot({
      mode: safeInput.mode || "INSPECTION",
      guard: safeInput.guardSnapshot || safeInput.guard || "guard.unresolved",
      runtimeEnvironment:
        safeInput.runtimeEnvironment || "runtime.unresolved",
      prakriyaPlan: safeInput.prakriyaPlan || "prakriya.unresolved",
      derivationGraph: safeInput.derivationGraph || "graph.unresolved",
      stages: safeInput.stages || []
    });

  return createExecutionKernelGuardBridge({
    kernelSnapshot,
    guardSnapshot:
      safeInput.guardSnapshot ||
      safeInput.guard ||
      (kernelSnapshot.references && kernelSnapshot.references.guard),
    runtimeEnvironment:
      safeInput.runtimeEnvironment ||
      (kernelSnapshot.references && kernelSnapshot.references.runtimeEnvironment)
  });
}

function getExecutionKernelGuardBridgeDiagnostics(input) {
  const bridge =
    input && input.kind === "EXECUTION_KERNEL_GUARD_BRIDGE"
      ? input
      : buildExecutionKernelGuardBridgeSnapshot(input);
  const linkage = bridge.linkage || {};
  const diagnostics = bridge.diagnostics || {};

  return {
    schemaVersion: bridge.schemaVersion,
    ready: Boolean(diagnostics.ready),
    guardLinked: Boolean(linkage.guardLinked),
    runtimeLinked: Boolean(linkage.runtimeLinked),
    kernelLinked: Boolean(linkage.kernelLinked),
    executionBlocked: Boolean(linkage.executionBlocked),
    mutationFree: Boolean(diagnostics.mutationFree),
    surfaceFormBlocked: Boolean(diagnostics.surfaceFormBlocked),
    authorizationForwarded: Boolean(linkage.authorizationForwarded),
    stageCount: Number.isFinite(Number(diagnostics.stageCount))
      ? Number(diagnostics.stageCount)
      : 0
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeExecutionGuardReference,
    createExecutionKernelGuardBridge,
    buildExecutionKernelGuardBridgeSnapshot,
    getExecutionKernelGuardBridgeDiagnostics
  };
}
