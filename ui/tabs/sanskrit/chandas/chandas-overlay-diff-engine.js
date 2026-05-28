import {
  CHANDAS_OVERLAY_DIFF_FIELDS,
  createEmptyChandasOverlayDiff,
} from "./chandas-overlay-diff-map.js";

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

function valuesEqual(left, right) {
  return stableStringify(left) === stableStringify(right);
}

function normalizeDigest(snapshot) {
  return String(snapshot?.digest || "");
}

function buildChange(field, beforeValue, afterValue) {
  return {
    field,
    before: stableStringify(beforeValue),
    after: stableStringify(afterValue),
  };
}

function buildDiagnostics(diff) {
  if (!diff.compared) {
    return [
      {
        id: "overlay-diff-not-compared",
        level: "warning",
        message: "Overlay diff could not compare missing snapshots.",
      },
    ];
  }

  if (!diff.changed) {
    return [
      {
        id: "overlay-diff-stable",
        level: "info",
        message: "Overlay snapshot comparison is stable.",
      },
    ];
  }

  return [
    {
      id: "overlay-diff-changed",
      level: "info",
      message: `${diff.changeCount} deterministic overlay snapshot change(s) detected.`,
    },
  ];
}

export function diffChandasOverlaySnapshots(baselineSnapshot, candidateSnapshot) {
  const diff = createEmptyChandasOverlayDiff();

  if (!hasObject(baselineSnapshot) || !hasObject(candidateSnapshot)) {
    diff.diagnostics = buildDiagnostics(diff);
    return diff;
  }

  const changes = CHANDAS_OVERLAY_DIFF_FIELDS
    .filter((field) => !valuesEqual(baselineSnapshot[field], candidateSnapshot[field]))
    .map((field) => buildChange(field, baselineSnapshot[field], candidateSnapshot[field]));

  diff.compared = true;
  diff.baselineDigest = normalizeDigest(baselineSnapshot);
  diff.candidateDigest = normalizeDigest(candidateSnapshot);
  diff.changed = changes.length > 0;
  diff.changeCount = changes.length;
  diff.changes = changes;
  diff.diagnostics = buildDiagnostics(diff);

  return Object.freeze(diff);
}

export function isChandasOverlayDiffReady(diff) {
  return Boolean(
    hasObject(diff) &&
      diff.deterministic &&
      diff.runtimeIsolated &&
      diff.staticPreviewCompatible &&
      diff.immutableComparisonSafe &&
      diff.compared
  );
}