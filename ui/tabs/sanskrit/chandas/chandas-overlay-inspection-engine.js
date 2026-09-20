import {
  CHANDAS_OVERLAY_INSPECTION_TARGETS,
  createEmptyChandasOverlayInspection,
} from "./chandas-overlay-inspection-map.js";

function hasObject(value) {
  return Boolean(value && typeof value === "object");
}

function hasArray(value) {
  return Array.isArray(value);
}

function summarizeTarget(target, source) {
  const available = hasObject(source) || hasArray(source);

  return {
    id: target.id,
    label: target.label,
    required: Boolean(target.required),
    available,
    status: available ? "available" : target.required ? "missing" : "optional-missing",
  };
}

function buildDiagnostics(summaries) {
  return summaries.map((summary) => ({
    id: `${summary.id}-inspection`,
    target: summary.id,
    level: summary.available ? "info" : summary.required ? "warning" : "info",
    message: summary.available
      ? `${summary.label} reachable for inspection.`
      : `${summary.label} not available in current static/runtime context.`,
  }));
}

function resolveConsistency(summaries) {
  const byId = Object.fromEntries(summaries.map((summary) => [summary.id, summary]));

  return {
    registryReachable: Boolean(byId["overlay-registry"]?.available),
    graphReachable: Boolean(byId["overlay-navigation"]?.available || byId["overlay-query"]?.available),
    dependencyReachable: Boolean(byId["overlay-dependencies"]?.available),
    schemaReachable: Boolean(byId["overlay-schema"]?.available),
  };
}

export function inspectChandasOverlayRegistry(context = {}) {
  const inspection = createEmptyChandasOverlayInspection();

  const sourceByTarget = {
    "overlay-registry": context.overlayRegistry,
    "overlay-capabilities": context.overlayCapabilities,
    "overlay-schema": context.overlaySchema,
    "overlay-dependencies": context.overlayDependencies,
    "overlay-navigation": context.overlayNavigation,
    "overlay-query": context.overlayQuery,
  };

  const summaries = CHANDAS_OVERLAY_INSPECTION_TARGETS.map((target) =>
    summarizeTarget(target, sourceByTarget[target.id])
  );

  inspection.summaries = summaries;
  inspection.diagnostics = buildDiagnostics(summaries);
  inspection.consistency = resolveConsistency(summaries);

  return inspection;
}

export function isChandasOverlayInspectionReady(inspection) {
  if (!hasObject(inspection)) {
    return false;
  }

  return Boolean(
    inspection.deterministic &&
      inspection.runtimeIsolated &&
      inspection.staticPreviewCompatible &&
      inspection.consistency?.registryReachable &&
      inspection.consistency?.dependencyReachable &&
      inspection.consistency?.schemaReachable
  );
}