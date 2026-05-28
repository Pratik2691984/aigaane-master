export const CHANDAS_OVERLAY_CERTIFICATION_SCHEMA_VERSION =
  "chandas-overlay-certification.v1";

export const CHANDAS_OVERLAY_CERTIFICATION_LAYER =
  "chandas-overlay-certification";

export const CHANDAS_OVERLAY_CERTIFICATION_VERIFICATION_SCHEMA =
  "chandas-overlay-verification.v1";

export const CHANDAS_OVERLAY_CERTIFICATION_FLAGS = Object.freeze({
  deterministic: true,
  authoritative: false,
  performative: false,
  runtimeIsolated: true,
  staticPreviewCompatible: true,
  immutableCertificationSafe: true,
});

export const CHANDAS_OVERLAY_CERTIFICATION_LEVELS = Object.freeze({
  CERTIFIED: "certified",
  PARTIAL: "partial",
  UNAVAILABLE: "unavailable",
});

export function createEmptyChandasOverlayCertification() {
  return {
    schemaVersion: CHANDAS_OVERLAY_CERTIFICATION_SCHEMA_VERSION,
    layer: CHANDAS_OVERLAY_CERTIFICATION_LAYER,
    ...CHANDAS_OVERLAY_CERTIFICATION_FLAGS,
    sourceVerificationSchema: CHANDAS_OVERLAY_CERTIFICATION_VERIFICATION_SCHEMA,
    certified: false,
    level: CHANDAS_OVERLAY_CERTIFICATION_LEVELS.UNAVAILABLE,
    readiness: {
      verificationAvailable: false,
      verified: false,
      invariantCount: 0,
      passedInvariantCount: 0,
      failedInvariantCount: 0,
    },
    summaries: [],
    diagnostics: [],
  };
}