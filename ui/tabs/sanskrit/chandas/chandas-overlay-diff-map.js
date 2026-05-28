export const CHANDAS_OVERLAY_DIFF_SCHEMA_VERSION =
  "chandas-overlay-diff.v1";

export const CHANDAS_OVERLAY_DIFF_LAYER =
  "chandas-overlay-diff";

export const CHANDAS_OVERLAY_DIFF_SOURCE_SCHEMA =
  "chandas-overlay-snapshot.v1";

export const CHANDAS_OVERLAY_DIFF_FLAGS = Object.freeze({
  deterministic: true,
  authoritative: false,
  performative: false,
  runtimeIsolated: true,
  staticPreviewCompatible: true,
  immutableComparisonSafe: true,
});

export const CHANDAS_OVERLAY_DIFF_FIELDS = Object.freeze([
  "summaryCount",
  "diagnosticCount",
  "consistency",
  "digest",
]);

export function createEmptyChandasOverlayDiff() {
  return {
    schemaVersion: CHANDAS_OVERLAY_DIFF_SCHEMA_VERSION,
    layer: CHANDAS_OVERLAY_DIFF_LAYER,
    ...CHANDAS_OVERLAY_DIFF_FLAGS,
    sourceSnapshotSchema: CHANDAS_OVERLAY_DIFF_SOURCE_SCHEMA,
    compared: false,
    baselineDigest: "",
    candidateDigest: "",
    changed: false,
    changeCount: 0,
    changes: [],
    diagnostics: [],
  };
}