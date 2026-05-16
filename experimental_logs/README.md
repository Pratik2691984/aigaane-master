# Collapse Lab Experimental Logs

This folder stores exported data from the Anumana Collapse Lab.

## Folder Structure

- json/sessions/
  Full JSON session exports containing metadata, controls, frame history, and replay data.

- json/replay_snapshots/
  Curated replay windows around important transition events.

- csv/metrics/
  Scalar telemetry streams exported from live runs.

- csv/phase_events/
  Filtered transition-only logs such as NORMAL -> PRE_COLLAPSE or PRE_COLLAPSE -> COLLAPSED.

- manifests/session_index.json
  Optional index of curated experiment sessions.

## Key Metrics

- CPI
- lambda2
- entropy
- residualMass
- syncRatio
- modularity
- k

## Phase Semantics

NORMAL:
  Fragmented or non-critical topology.

PRE_COLLAPSE:
  Strict metastable two-component boundary.
  Required:
  - k === 2
  - lambda2 <= 1e-4
  - CPI >= 0.85
  - syncRatio >= 0.9
  - residualMass <= 0.25

COLLAPSED:
  Globally connected synchronized manifold.
  Required:
  - k === 1
  - lambda2 > 1e-4

## Git Policy

Raw generated experiment logs should usually not be committed.
Commit only curated benchmark datasets when needed for papers, demos, or validation.
