export const CHANDAS_OVERLAY_AUDIT_SCHEMA_VERSION =
  "chandas-overlay-audit.v1";

export const CHANDAS_OVERLAY_AUDIT_LAYER =
  "chandas-overlay-audit";

export const CHANDAS_OVERLAY_AUDIT_REPLAY_SCHEMA =
  "chandas-overlay-replay.v1";

export const CHANDAS_OVERLAY_AUDIT_FLAGS = Object.freeze({
  deterministic: true,
  authoritative: false,
  performative: false,
  runtimeIsolated: true,
  staticPreviewCompatible: true,
  immutableAuditSafe: true,
});

export function createEmptyChandasOverlayAudit() {
  return {
    schemaVersion: CHANDAS_OVERLAY_AUDIT_SCHEMA_VERSION,
    layer: CHANDAS_OVERLAY_AUDIT_LAYER,
    ...CHANDAS_OVERLAY_AUDIT_FLAGS,
    sourceReplaySchema: CHANDAS_OVERLAY_AUDIT_REPLAY_SCHEMA,
    verified: false,
    checkpointCount: 0,
    checkpoints: [],
    integrity: {
      replayAvailable: false,
      cursorAvailable: false,
      digestAvailable: false,
      traversalBounded: false,
    },
    diagnostics: [],
  };
}