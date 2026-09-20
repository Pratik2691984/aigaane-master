import {
  CHANDAS_OVERLAY_CERTIFICATION_LEVELS,
  createEmptyChandasOverlayCertification,
} from "./chandas-overlay-certification-map.js";

function hasObject(value) {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function resolveLevel(readiness) {
  if (!readiness.verificationAvailable) {
    return CHANDAS_OVERLAY_CERTIFICATION_LEVELS.UNAVAILABLE;
  }

  if (readiness.verified && readiness.failedInvariantCount === 0) {
    return CHANDAS_OVERLAY_CERTIFICATION_LEVELS.CERTIFIED;
  }

  return CHANDAS_OVERLAY_CERTIFICATION_LEVELS.PARTIAL;
}

function buildSummaries(certification) {
  return [
    {
      id: "overlay-certification-readiness",
      label: "Overlay Certification Readiness",
      value: certification.level,
    },
    {
      id: "overlay-certification-invariants",
      label: "Verification Invariants",
      value: `${certification.readiness.passedInvariantCount}/${certification.readiness.invariantCount}`,
    },
  ];
}

function buildDiagnostics(certification) {
  if (certification.certified) {
    return [
      {
        id: "overlay-certification-certified",
        level: "info",
        message: "Overlay verification chain is certified for deterministic inspection.",
      },
    ];
  }

  return [
    {
      id: "overlay-certification-partial",
      level: "warning",
      message: "Overlay verification chain is not fully certified.",
    },
  ];
}

export function certifyChandasOverlayVerification(verification) {
  const certification = createEmptyChandasOverlayCertification();

  const verificationAvailable = hasObject(verification);
  const invariantCount = Number.isFinite(verification?.invariantCount)
    ? verification.invariantCount
    : 0;
  const passedInvariantCount = Number.isFinite(verification?.passedInvariantCount)
    ? verification.passedInvariantCount
    : 0;
  const failedInvariantCount = Math.max(invariantCount - passedInvariantCount, 0);

  certification.readiness = {
    verificationAvailable,
    verified: Boolean(verification?.verified),
    invariantCount,
    passedInvariantCount,
    failedInvariantCount,
  };

  certification.level = resolveLevel(certification.readiness);
  certification.certified =
    certification.level === CHANDAS_OVERLAY_CERTIFICATION_LEVELS.CERTIFIED;
  certification.summaries = buildSummaries(certification);
  certification.diagnostics = buildDiagnostics(certification);

  return Object.freeze(certification);
}

export function isChandasOverlayCertificationReady(certification) {
  return Boolean(
    hasObject(certification) &&
      certification.deterministic &&
      certification.runtimeIsolated &&
      certification.staticPreviewCompatible &&
      certification.immutableCertificationSafe &&
      hasObject(certification.readiness)
  );
}