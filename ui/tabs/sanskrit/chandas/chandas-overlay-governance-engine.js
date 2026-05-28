import {
  CHANDAS_OVERLAY_GOVERNANCE_POLICIES,
  createEmptyChandasOverlayGovernance,
} from "./chandas-overlay-governance-map.js";

function hasObject(value) {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function buildPolicy(id, passed, message) {
  return {
    id,
    passed: Boolean(passed),
    message,
  };
}

function resolveClassification(governance) {
  if (!governance.policies.length) {
    return "unavailable";
  }

  if (governance.summary.failed === 0) {
    return "governed";
  }

  return "partial";
}

function buildDiagnostics(governance) {
  if (governance.governed) {
    return [
      {
        id: "overlay-governance-governed",
        level: "info",
        message: "Overlay certification governance policies passed.",
      },
    ];
  }

  return [
    {
      id: "overlay-governance-partial",
      level: "warning",
      message: "Overlay certification governance policies are partial.",
    },
  ];
}

export function governChandasOverlayCertification(certification) {
  const governance = createEmptyChandasOverlayGovernance();

  const certificationAvailable = hasObject(certification);
  const nonAuthoritative = certificationAvailable && certification.authoritative === false;
  const nonPerformative = certificationAvailable && certification.performative === false;
  const runtimeIsolated = Boolean(certification?.runtimeIsolated);
  const staticPreviewCompatible = Boolean(certification?.staticPreviewCompatible);

  governance.policies = [
    buildPolicy(
      "certification-available",
      certificationAvailable,
      certificationAvailable
        ? "Certification payload is available."
        : "Certification payload is missing."
    ),
    buildPolicy(
      "certification-non-authoritative",
      nonAuthoritative,
      nonAuthoritative
        ? "Certification remains non-authoritative."
        : "Certification authoritative flag is not safely false."
    ),
    buildPolicy(
      "certification-non-performative",
      nonPerformative,
      nonPerformative
        ? "Certification remains non-performative."
        : "Certification performative flag is not safely false."
    ),
    buildPolicy(
      "certification-runtime-isolated",
      runtimeIsolated,
      runtimeIsolated
        ? "Certification is runtime isolated."
        : "Certification runtime isolation flag is missing."
    ),
    buildPolicy(
      "certification-static-preview-compatible",
      staticPreviewCompatible,
      staticPreviewCompatible
        ? "Certification is static preview compatible."
        : "Certification static preview compatibility flag is missing."
    ),
  ].filter((policy) => CHANDAS_OVERLAY_GOVERNANCE_POLICIES.includes(policy.id));

  governance.policyCount = governance.policies.length;
  governance.passedPolicyCount = governance.policies.filter((policy) => policy.passed).length;
  governance.summary = {
    total: governance.policyCount,
    passed: governance.passedPolicyCount,
    failed: governance.policyCount - governance.passedPolicyCount,
  };
  governance.classification = resolveClassification(governance);
  governance.governed = governance.classification === "governed";
  governance.diagnostics = buildDiagnostics(governance);

  return Object.freeze(governance);
}

export function isChandasOverlayGovernanceReady(governance) {
  return Boolean(
    hasObject(governance) &&
      governance.deterministic &&
      governance.runtimeIsolated &&
      governance.staticPreviewCompatible &&
      governance.immutableGovernanceSafe &&
      Array.isArray(governance.policies)
  );
}