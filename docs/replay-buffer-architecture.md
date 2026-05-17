# Replay Buffer Architecture and Memory Lifecycle

## 1. Overview

Collapse Lab maintains bounded in-memory replay buffers to store high-frequency time-series datasets during execution. These buffers support real-time rendering, deterministic session replay, and standardized analytical exports without unbounded browser memory growth.

The replay layer stores tensor snapshots, phase states, scalar metrics, and exported trajectories. It is designed for inspection and analysis, not for changing the live simulation after the fact.

## 2. Runtime Replay Pipeline

```text
Simulation Frame (Kuramoto Phases)
->
Metrics Extraction (lambda2, CPI, entropy)
->
Tensor Projection (7x7 Matrix)
->
Replay Snapshot Generation
->
Export Buffer Integration
->
Visualization Render (Canvas/Charts)
```

Live simulation generates the current frame, extracts topology and synchronization metrics, projects those metrics into tensor space, then writes bounded snapshots for replay and export.

## 3. Replay Buffer Types

| Buffer | Purpose |
| --- | --- |
| `phaseHistory` | Recent phase labels used to inspect state transitions. |
| `exportFrames` | Scalar metric frames prepared for JSON and CSV export. |
| `replayFrames` | Historical snapshots used to repaint replay views without advancing simulation. |
| timeline metric buffers | Short rolling histories for `cpi`, `lambda2`, and `entropy` timeline rendering. |

## 4. Replay Snapshot Structure

```json
{
  "t": 12.42,
  "phase": "PRE_COLLAPSE",
  "cpi": 0.91,
  "lambda2": 0.000001,
  "entropy": 0.12,
  "k": 2,
  "modularity": 0.08,
  "clusterBalanceRatio": 0.88,
  "syncRatio": 0.93
}
```

Full replay snapshots may also include tensor data, residual mass, and phase-space indexing metadata. Export frames keep the scalar view compact for downstream analysis.

## 5. Capped Buffer Strategy

The current implementation uses capped rolling buffers to prevent unbounded browser memory growth. Future versions may replace push/shift behavior with pointer-wrapped fixed arrays for lower allocation pressure.

Documented caps and constraints:

- UI timeline buffer cap: 120 samples
- `exportFrames` cap: 5000 samples
- `replayFrames` cap: implementation-defined / capped snapshot stream if present
- capping avoids memory leaks during long sessions

Without caps, long-running browser sessions could accumulate unbounded frame history and degrade rendering, replay, and export performance.

## 6. Timeline Buffers

Timeline buffers support live monitoring rendering:

- CPI history
- `lambda2` history
- `entropy` history
- 120-frame visualization cap

Timeline rendering is for live monitoring, not full archival storage. Long-horizon analysis should use exported telemetry rather than the on-screen timeline buffer.

## 7. Export Recording

Collapse Lab records export-ready histories for post-session analysis:

- JSON export
- CSV export
- `frames`
- `replayFrames`
- controls metadata
- export history capped to avoid memory degradation

JSON exports preserve structured session context, while CSV exports provide a compact scalar table for external analysis.

## 8. Replay Controls

Replay mode supports:

- play
- pause
- reset
- scrub
- step forward
- step backward

These controls allow historical review without forcing new simulation frames.

## 9. Deterministic Replay Mechanics

Replay Mode bypasses live simulation evolution. Historical snapshots repaint renderers directly. Replay state must not mutate Kuramoto physics. Replay exists for inspection, not simulation.

This isolation keeps replay deterministic: frame stepping should inspect previously captured state rather than recomputing stochastic dynamics, `lambda2`, `syncRatio`, `clusterBalanceRatio`, or tensor projection from live inputs.

## 10. Numerical Safety

Replay and export stability rely on:

- immutable snapshot copies
- `Float64Array` where applicable
- serialization safeguards
- bounded memory allocation

Snapshot copies prevent later live frames from mutating historical replay state.

## 11. Runtime Contract Warning

This document describes the current Collapse Lab architecture and should be updated whenever runtime contracts change.

## 12. Future Work

Future replay work may include:

- compressed replay streams
- NDJSON export
- indexed replay events
- time-window bookmarks
- WebWorker replay decoding

## Documentation Boundary

This document does not modify runtime code, phase detection equations, CPI formulas, entropy logic, `lambda2` extraction, replay/export behavior, tensor projection, or UI rendering.
