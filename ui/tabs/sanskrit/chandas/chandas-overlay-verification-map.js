export const CHANDAS_OVERLAY_VERIFICATION_SCHEMA_VERSION =
  "chandas-overlay-verification.v1";

export const CHANDAS_OVERLAY_VERIFICATION_LAYER =
  "chandas-overlay-verification";

export const CHANDAS_OVERLAY_VERIFICATION_AUDIT_SCHEMA =
  "chandas-overlay-audit.v1";

export const CHANDAS_OVERLAY_VERIFICATION_FLAGS = Object.freeze({
  deterministic: true,
  authoritative: false,
  performative: false,
  runtimeIsolated: true,
  staticPreviewCompatible: true,
  immutableVerificationSafe: true,
});

export const CHANDAS_OVERLAY_VERIFICATION_INVARIANTS = Object.freeze([
  "audit-available",
  "audit-checkpoints-present",
  "audit-integrity-present",
  "audit-runtime-isolated",
  "audit-static-preview-compatible",
]);

export function createEmptyChandasOverlayVerification() {
  return {
    schemaVersion: CHANDAS_OVERLAY_VERIFICATION_SCHEMA_VERSION,
    layer: CHANDAS_OVERLAY_VERIFICATION_LAYER,
    ...CHANDAS_OVERLAY_VERIFICATION_FLAGS,
    sourceAuditSchema: CHANDAS_OVERLAY_VERIFICATION_AUDIT_SCHEMA,
    verified: false,
    invariantCount: 0,
    passedInvariantCount: 0,
    invariants: [],
    summary: {
      total: 0,
      passed: 0,
      failed: 0,
    },
    diagnostics: [],
  };
}