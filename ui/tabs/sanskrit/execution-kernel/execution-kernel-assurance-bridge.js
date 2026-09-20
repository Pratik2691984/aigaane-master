"use strict";

const {
  createExecutionKernelSnapshot,
} = require("./execution-kernel-engine.js");

const ASSURANCE_BRIDGE_SCHEMA_VERSION =
  "sanskrit-execution-kernel-assurance-bridge.v1";

function freezeObject(v) {
  return Object.freeze(v);
}

function ref(v, fallback) {
  if (typeof v === "string") return v;
  if (v && typeof v === "object") {
    return String(v.id || v.referenceId || fallback);
  }
  return fallback;
}

function normalizeExecutionAssuranceReference(assurance) {
  const isObject = assurance && typeof assurance === "object";
  const isString = typeof assurance === "string";

  return freezeObject({
    id:
      isString
        ? assurance
        : isObject
          ? String(assurance.id || assurance.referenceId || "assurance.unresolved")
          : "assurance.unresolved",

    kind:
      isString
        ? "EXECUTION_ASSURANCE_REFERENCE"
        : isObject
          ? String(assurance.kind || "EXECUTION_ASSURANCE_REFERENCE")
          : "EXECUTION_ASSURANCE_REFERENCE",

    schemaVersion:
      isString
        ? "unknown"
        : isObject
          ? String(assurance.schemaVersion || "unknown")
          : "unknown",

    status:
      isString
        ? "REFERENCED"
        : isObject
          ? String(assurance.status || "REFERENCED")
          : "UNRESOLVED",

    assured:
      Boolean(isObject && assurance.assured === true),

    validationAllowed:
      Boolean(isObject && assurance.validationAllowed === true),

    executionAllowed:
      Boolean(isObject && assurance.executionAllowed === true),

    diagnostics: freezeObject({
      normalized: true,
      assuranceLinked: true,

      sourceAssuredObserved:
        Boolean(isObject && assurance.assured === true),

      sourceValidationObserved:
        Boolean(isObject && assurance.validationAllowed === true),

      sourceExecutionObserved:
        Boolean(isObject && assurance.executionAllowed === true),

      bridgeAssuranceGranted: false,
      bridgeValidationGranted: false,
      bridgeExecutionGranted: false,
    }),
  });
}

function createExecutionKernelAssuranceBridge(input = {}) {
  const kernelSnapshot = input.kernelSnapshot || {};
  const stages =
    Array.isArray(kernelSnapshot.stages)
      ? kernelSnapshot.stages
      : [];

  return freezeObject({
    schemaVersion:
      ASSURANCE_BRIDGE_SCHEMA_VERSION,

    kind:
      "EXECUTION_KERNEL_ASSURANCE_BRIDGE",

    kernel: freezeObject({
      schemaVersion:
        String(
          kernelSnapshot.schemaVersion ||
          "unknown"
        ),

      kind:
        String(
          kernelSnapshot.kind ||
          "EXECUTION_KERNEL_SNAPSHOT"
        ),

      mode:
        String(
          kernelSnapshot.mode ||
          "INSPECTION"
        ),

      stageCount:
        stages.length,
    }),

    assurance:
      normalizeExecutionAssuranceReference(
        input.assurance
      ),

    compliance:
      freezeObject({
        id: ref(
          input.compliance,
          "compliance.unresolved"
        ),
        linked: true,
      }),

    policy:
      freezeObject({
        id: ref(
          input.policy,
          "policy.unresolved"
        ),
        linked: true,
      }),

    audit:
      freezeObject({
        id: ref(
          input.audit,
          "audit.unresolved"
        ),
        linked: true,
      }),

    runtimeEnvironment:
      freezeObject({
        id: ref(
          input.runtimeEnvironment,
          "runtime.unresolved"
        ),
        linked: true,
      }),

    linkage: freezeObject({
      kernelLinked: true,

      assuranceLinked: true,
      complianceLinked: true,
      policyLinked: true,
      auditLinked: true,

      runtimeLinked: true,

      assuranceInspectionOnly: true,

      validationBlocked: true,
      executionBlocked: true,

      mutationBlocked: true,
      rollbackBlocked: true,
      replayBlocked: true,

      surfaceFormBlocked: true,
    }),

    diagnostics: freezeObject({
      ready: true,

      deterministic: true,
      immutable: true,

      inspectionOnly: true,
      assuranceOnly: true,

      validationBlocked: true,
      executionBlocked: true,

      mutationFree: true,
      rollbackBlocked: true,
      replayBlocked: true,

      surfaceFormBlocked: true,

      complianceCompatible: true,
      policyCompatible: true,
      auditCompatible: true,
      runtimeCompatible: true,

      stageCount:
        stages.length,
    }),
  });
}

function buildExecutionKernelAssuranceBridgeSnapshot(
  input = {}
) {
  const kernelSnapshot =
    input.kernelSnapshot ||
    createExecutionKernelSnapshot({
      mode:
        input.mode ||
        "INSPECTION",

      guard:
        input.guardReference ||
        "guard.unresolved",

      runtimeEnvironment:
        input.runtimeEnvironment ||
        "runtime.unresolved",

      prakriyaPlan:
        input.prakriyaPlan ||
        "prakriya.unresolved",

      derivationGraph:
        input.derivationGraph ||
        "graph.unresolved",

      stages:
        input.stages || [],
    });

  return createExecutionKernelAssuranceBridge({
    kernelSnapshot,

    assurance:
      input.assurance ||
      "assurance.unresolved",

    compliance:
      input.compliance,

    policy:
      input.policy,

    audit:
      input.audit,

    runtimeEnvironment:
      input.runtimeEnvironment ||
      kernelSnapshot.references
        .runtimeEnvironment,
  });
}

function getExecutionKernelAssuranceBridgeDiagnostics(
  bridge = {}
) {
  const linkage =
    bridge.linkage || {};

  const diagnostics =
    bridge.diagnostics || {};

  return freezeObject({
    schemaVersion:
      bridge.schemaVersion,

    ready:
      Boolean(
        diagnostics.ready
      ),

    assuranceLinked:
      Boolean(
        linkage.assuranceLinked
      ),

    complianceLinked:
      Boolean(
        linkage.complianceLinked
      ),

    policyLinked:
      Boolean(
        linkage.policyLinked
      ),

    auditLinked:
      Boolean(
        linkage.auditLinked
      ),

    runtimeLinked:
      Boolean(
        linkage.runtimeLinked
      ),

    validationBlocked:
      Boolean(
        linkage.validationBlocked
      ),

    executionBlocked:
      Boolean(
        linkage.executionBlocked
      ),

    mutationFree:
      Boolean(
        diagnostics.mutationFree
      ),

    rollbackBlocked:
      Boolean(
        linkage.rollbackBlocked
      ),

    replayBlocked:
      Boolean(
        linkage.replayBlocked
      ),

    surfaceFormBlocked:
      Boolean(
        linkage.surfaceFormBlocked
      ),

    stageCount:
      Number(
        diagnostics.stageCount || 0
      ),
  });
}

module.exports = {
  ASSURANCE_BRIDGE_SCHEMA_VERSION,
  normalizeExecutionAssuranceReference,
  createExecutionKernelAssuranceBridge,
  buildExecutionKernelAssuranceBridgeSnapshot,
  getExecutionKernelAssuranceBridgeDiagnostics,
};