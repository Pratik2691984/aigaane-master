import {
  CHANDAS_OVERLAY_VERIFICATION_INVARIANTS,
  createEmptyChandasOverlayVerification,
} from "./chandas-overlay-verification-map.js";

function hasObject(value) {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function buildInvariant(id, passed, message) {
  return {
    id,
    passed: Boolean(passed),
    message,
  };
}

function buildDiagnostics(verification) {
  if (verification.verified) {
    return [
      {
        id: "overlay-verification-passed",
        level: "info",
        message: "Overlay audit verification invariants passed.",
      },
    ];
  }

  return [
    {
      id: "overlay-verification-partial",
      level: "warning",
      message: "Overlay audit verification invariants are partial.",
    },
  ];
}

export function verifyChandasOverlayAudit(audit) {
  const verification = createEmptyChandasOverlayVerification();

  const auditAvailable = hasObject(audit);
  const checkpointsPresent = Array.isArray(audit?.checkpoints) && audit.checkpoints.length > 0;
  const integrityPresent = hasObject(audit?.integrity);
  const runtimeIsolated = Boolean(audit?.runtimeIsolated);
  const staticPreviewCompatible = Boolean(audit?.staticPreviewCompatible);

  verification.invariants = [
    buildInvariant(
      "audit-available",
      auditAvailable,
      auditAvailable ? "Audit payload is available." : "Audit payload is missing."
    ),
    buildInvariant(
      "audit-checkpoints-present",
      checkpointsPresent,
      checkpointsPresent ? "Audit checkpoints are present." : "Audit checkpoints are missing."
    ),
    buildInvariant(
      "audit-integrity-present",
      integrityPresent,
      integrityPresent ? "Audit integrity block is present." : "Audit integrity block is missing."
    ),
    buildInvariant(
      "audit-runtime-isolated",
      runtimeIsolated,
      runtimeIsolated ? "Audit is runtime isolated." : "Audit runtime isolation flag is missing."
    ),
    buildInvariant(
      "audit-static-preview-compatible",
      staticPreviewCompatible,
      staticPreviewCompatible
        ? "Audit is static preview compatible."
        : "Audit static preview compatibility flag is missing."
    ),
  ].filter((invariant) =>
    CHANDAS_OVERLAY_VERIFICATION_INVARIANTS.includes(invariant.id)
  );

  verification.invariantCount = verification.invariants.length;
  verification.passedInvariantCount = verification.invariants.filter(
    (invariant) => invariant.passed
  ).length;
  verification.summary = {
    total: verification.invariantCount,
    passed: verification.passedInvariantCount,
    failed: verification.invariantCount - verification.passedInvariantCount,
  };
  verification.verified = verification.summary.failed === 0;
  verification.diagnostics = buildDiagnostics(verification);

  return Object.freeze(verification);
}

export function isChandasOverlayVerificationReady(verification) {
  return Boolean(
    hasObject(verification) &&
      verification.deterministic &&
      verification.runtimeIsolated &&
      verification.staticPreviewCompatible &&
      verification.immutableVerificationSafe &&
      Array.isArray(verification.invariants)
  );
}