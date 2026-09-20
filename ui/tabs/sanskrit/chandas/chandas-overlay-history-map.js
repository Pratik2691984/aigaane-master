export const CHANDAS_OVERLAY_HISTORY_SCHEMA_VERSION =
  "chandas-overlay-history.v1";

export const CHANDAS_OVERLAY_HISTORY_LAYER =
  "chandas-overlay-history";

export const CHANDAS_OVERLAY_HISTORY_SNAPSHOT_SCHEMA =
  "chandas-overlay-snapshot.v1";

export const CHANDAS_OVERLAY_HISTORY_DIFF_SCHEMA =
  "chandas-overlay-diff.v1";

export const CHANDAS_OVERLAY_HISTORY_FLAGS = Object.freeze({
  deterministic: true,
  authoritative: false,
  performative: false,
  runtimeIsolated: true,
  staticPreviewCompatible: true,
  immutableTimelineSafe: true,
});

export function createEmptyChandasOverlayHistory() {
  return {
    schemaVersion: CHANDAS_OVERLAY_HISTORY_SCHEMA_VERSION,
    layer: CHANDAS_OVERLAY_HISTORY_LAYER,
    ...CHANDAS_OVERLAY_HISTORY_FLAGS,
    sourceSnapshotSchema: CHANDAS_OVERLAY_HISTORY_SNAPSHOT_SCHEMA,
    sourceDiffSchema: CHANDAS_OVERLAY_HISTORY_DIFF_SCHEMA,
    timeline: [],
    diffChain: [],
    summary: {
      snapshotCount: 0,
      diffCount: 0,
      changedDiffCount: 0,
    },
    diagnostics: [],
  };
}