export const CHANDAS_OVERLAY_INSPECTION_SCHEMA_VERSION =
  "chandas-overlay-inspection.v1";

export const CHANDAS_OVERLAY_INSPECTION_LAYER =
  "chandas-overlay-inspection";

export const CHANDAS_OVERLAY_INSPECTION_FLAGS = Object.freeze({
  deterministic: true,
  authoritative: false,
  performative: false,
  runtimeIsolated: true,
  staticPreviewCompatible: true,
});

export const CHANDAS_OVERLAY_INSPECTION_TARGETS = Object.freeze([
  {
    id: "overlay-registry",
    label: "Overlay Registry",
    required: true,
  },
  {
    id: "overlay-capabilities",
    label: "Overlay Capability Registry",
    required: true,
  },
  {
    id: "overlay-schema",
    label: "Overlay Schema Discovery",
    required: true,
  },
  {
    id: "overlay-dependencies",
    label: "Overlay Dependency Registry",
    required: true,
  },
  {
    id: "overlay-navigation",
    label: "Overlay Navigation Layer",
    required: false,
  },
  {
    id: "overlay-query",
    label: "Overlay Query Layer",
    required: false,
  },
]);

export function createEmptyChandasOverlayInspection() {
  return {
    schemaVersion: CHANDAS_OVERLAY_INSPECTION_SCHEMA_VERSION,
    layer: CHANDAS_OVERLAY_INSPECTION_LAYER,
    ...CHANDAS_OVERLAY_INSPECTION_FLAGS,
    summaries: [],
    diagnostics: [],
    consistency: {
      registryReachable: false,
      graphReachable: false,
      dependencyReachable: false,
      schemaReachable: false,
    },
  };
}