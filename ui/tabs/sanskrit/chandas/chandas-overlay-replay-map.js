export const CHANDAS_OVERLAY_REPLAY_SCHEMA_VERSION =
  "chandas-overlay-replay.v1";

export const CHANDAS_OVERLAY_REPLAY_LAYER =
  "chandas-overlay-replay";

export const CHANDAS_OVERLAY_REPLAY_HISTORY_SCHEMA =
  "chandas-overlay-history.v1";

export const CHANDAS_OVERLAY_REPLAY_FLAGS = Object.freeze({
  deterministic: true,
  authoritative: false,
  performative: false,
  runtimeIsolated: true,
  staticPreviewCompatible: true,
  immutableReplaySafe: true,
});

export function createEmptyChandasOverlayReplay() {
  return {
    schemaVersion: CHANDAS_OVERLAY_REPLAY_SCHEMA_VERSION,
    layer: CHANDAS_OVERLAY_REPLAY_LAYER,
    ...CHANDAS_OVERLAY_REPLAY_FLAGS,
    sourceHistorySchema: CHANDAS_OVERLAY_REPLAY_HISTORY_SCHEMA,
    cursor: {
      index: 0,
      sequence: 0,
      digest: "",
    },
    totalSteps: 0,
    hasPrevious: false,
    hasNext: false,
    current: null,
    diagnostics: [],
  };
}