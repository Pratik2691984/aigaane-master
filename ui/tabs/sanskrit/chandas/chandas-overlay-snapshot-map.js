export const CHANDAS_OVERLAY_SNAPSHOT_SCHEMA_VERSION =
  "chandas-overlay-snapshot.v1";

export const CHANDAS_OVERLAY_SNAPSHOT_LAYER =
  "chandas-overlay-snapshot";

export const CHANDAS_OVERLAY_SNAPSHOT_SOURCE_SCHEMA =
  "chandas-overlay-inspection.v1";

export const CHANDAS_OVERLAY_SNAPSHOT_FLAGS = Object.freeze({
  deterministic: true,
  authoritative: false,
  performative: false,
  runtimeIsolated: true,
  staticPreviewCompatible: true,
  immutable: true,
});

export function createEmptyChandasOverlaySnapshot() {
  return {
    schemaVersion: CHANDAS_OVERLAY_SNAPSHOT_SCHEMA_VERSION,
    layer: CHANDAS_OVERLAY_SNAPSHOT_LAYER,
    ...CHANDAS_OVERLAY_SNAPSHOT_FLAGS,
    sourceInspectionSchema: CHANDAS_OVERLAY_SNAPSHOT_SOURCE_SCHEMA,
    capturedAt: "static-deterministic",
    sequence: 1,
    summaryCount: 0,
    diagnosticCount: 0,
    consistency: {},
    digest: "",
    diagnostics: [],
  };
}