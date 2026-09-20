import { createEmptyChandasOverlaySnapshot } from "./chandas-overlay-snapshot-map.js";

function hasObject(value) {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function stableStringify(value) {
  if (Array.isArray(value)) {
    return `[${value.map(stableStringify).join(",")}]`;
  }

  if (hasObject(value)) {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`)
      .join(",")}}`;
  }

  return JSON.stringify(value);
}

function createDeterministicDigest(payload) {
  const text = stableStringify(payload);
  let hash = 0;

  for (let index = 0; index < text.length; index += 1) {
    hash = (hash * 31 + text.charCodeAt(index)) >>> 0;
  }

  return `chandas-overlay-snapshot-${hash.toString(16).padStart(8, "0")}`;
}

function normalizeConsistency(consistency) {
  if (!hasObject(consistency)) {
    return {};
  }

  return Object.keys(consistency)
    .sort()
    .reduce((normalized, key) => {
      normalized[key] = Boolean(consistency[key]);
      return normalized;
    }, {});
}

function normalizeDiagnostics(diagnostics) {
  if (!Array.isArray(diagnostics)) {
    return [];
  }

  return diagnostics.map((diagnostic, index) => ({
    id: String(diagnostic?.id || `snapshot-diagnostic-${index + 1}`),
    level: String(diagnostic?.level || "info"),
    message: String(diagnostic?.message || "Snapshot diagnostic unavailable."),
  }));
}

export function createChandasOverlaySnapshot(inspection, options = {}) {
  const snapshot = createEmptyChandasOverlaySnapshot();

  const summaries = Array.isArray(inspection?.summaries) ? inspection.summaries : [];
  const diagnostics = normalizeDiagnostics(inspection?.diagnostics);
  const consistency = normalizeConsistency(inspection?.consistency);

  snapshot.sequence = Number.isFinite(options.sequence) ? options.sequence : 1;
  snapshot.summaryCount = summaries.length;
  snapshot.diagnosticCount = diagnostics.length;
  snapshot.consistency = consistency;
  snapshot.diagnostics = diagnostics;
  snapshot.digest = createDeterministicDigest({
    sourceInspectionSchema: snapshot.sourceInspectionSchema,
    sequence: snapshot.sequence,
    summaryCount: snapshot.summaryCount,
    diagnosticCount: snapshot.diagnosticCount,
    consistency,
    diagnostics,
  });

  return Object.freeze(snapshot);
}

export function isChandasOverlaySnapshotReady(snapshot) {
  return Boolean(
    hasObject(snapshot) &&
      snapshot.deterministic &&
      snapshot.runtimeIsolated &&
      snapshot.staticPreviewCompatible &&
      snapshot.immutable &&
      snapshot.digest
  );
}