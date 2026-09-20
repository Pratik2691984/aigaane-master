export const CHANDAS_OVERLAY_GOVERNANCE_SCHEMA_VERSION =
  "chandas-overlay-governance.v1";

export const CHANDAS_OVERLAY_GOVERNANCE_LAYER =
  "chandas-overlay-governance";

export const CHANDAS_OVERLAY_GOVERNANCE_CERTIFICATION_SCHEMA =
  "chandas-overlay-certification.v1";

export const CHANDAS_OVERLAY_GOVERNANCE_FLAGS = Object.freeze({
  deterministic: true,
  authoritative: false,
  performative: false,
  runtimeIsolated: true,
  staticPreviewCompatible: true,
  immutableGovernanceSafe: true,
});

export const CHANDAS_OVERLAY_GOVERNANCE_POLICIES = Object.freeze([
  "certification-available",
  "certification-non-authoritative",
  "certification-non-performative",
  "certification-runtime-isolated",
  "certification-static-preview-compatible",
]);

export function createEmptyChandasOverlayGovernance() {
  return {
    schemaVersion: CHANDAS_OVERLAY_GOVERNANCE_SCHEMA_VERSION,
    layer: CHANDAS_OVERLAY_GOVERNANCE_LAYER,
    ...CHANDAS_OVERLAY_GOVERNANCE_FLAGS,
    sourceCertificationSchema: CHANDAS_OVERLAY_GOVERNANCE_CERTIFICATION_SCHEMA,
    governed: false,
    classification: "unavailable",
    policyCount: 0,
    passedPolicyCount: 0,
    policies: [],
    summary: {
      total: 0,
      passed: 0,
      failed: 0,
    },
    diagnostics: [],
  };
}