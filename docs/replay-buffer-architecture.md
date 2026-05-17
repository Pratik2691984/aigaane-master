# Replay Buffer Architecture

## Overview

Collapse Lab maintains bounded in-memory replay buffers for live review, export, and deterministic renderer repainting. These buffers store:

- tensor snapshots
- phase states
- scalar metrics
- exported trajectories

The replay layer is runtime-local and bounded so browser memory does not grow without limit during long sessions.

## Runtime Replay Pipeline

The replay pipeline follows the live simulation frame:

```text
simulation frame
-> metrics extraction
-> tensor projection
-> replay snapshot
-> export buffer
-> visualization render
```

Live simulation writes current metrics and tensor state into replay-safe buffers. Replay mode reads from those historical snapshots rather than advancing the simulation.

## Replay Buffer Types

| Buffer | Purpose |
| --- | --- |
| `phaseHistory` | Recent phase labels used for phase-state review and transition context. |
| `exportFrames` | Flattened scalar metric frames used for JSON and CSV export. |
| `replayFrames` | Replay snapshots containing phase, metrics, tensor data, and phase-space index. |
| timeline metric buffers | Short histories for `cpi`, `lambda2`, and `entropy` timeline rendering. |

## Replay Snapshot Structure

A scalar replay/export frame has this representative shape:

```json
{
  "t": 12.42,
  "phase": "PRE_COLLAPSE",
  "cpi": 0.91,
  "lambda2": 0.000001,
  "entropy": 0.12,
  "k": 2,
  "modularity": 0.08,
  "clusterBalanceRatio": 0.88
}
```

Full replay frames may also include tensor snapshots, `syncRatio`, residual mass, and phase-space indexing metadata used by replay renderers.

## Ring Buffer Strategy

Collapse Lab uses ring-style bounded histories to avoid unbounded browser memory growth:

- capped metric histories
- fixed-size arrays
- overwrite or truncate behavior after caps are reached
- predictable memory usage during long browser sessions

When a buffer exceeds its cap, the oldest entries are removed and the newest frame remains available for live inspection.

## Timeline Buffers

Timeline rendering uses short scalar histories:

- `cpi` history
- `lambda2` history
- `entropy` history
- 120-frame visualization cap

The cap keeps the timeline readable and prevents the canvas renderer from redrawing arbitrarily large histories.

## Export Recording

Export recording separates compact metric frames from richer replay snapshots:

- `exportFrames` are capped at 5000 frames.
- JSON export includes session metadata, controls, `frames`, and `replayFrames`.
- CSV export writes scalar metric columns for tabular analysis.
- `replayFrames` are included in the JSON schema for deterministic review.

Export buffers are intended for post-session analysis, not as a replacement for permanent telemetry storage in `experimental_logs/`.

## Replay Controls

Replay mode supports:

- play
- pause
- reset
- scrub
- frame stepping

These controls allow review of historical frames without perturbing the live simulation state.

## Deterministic Replay

Replay bypasses live simulation. Historical frames directly repaint renderers using stored phase, metric, tensor, and phase-space data.

Replay state is isolated from live simulation state so scrubbing or stepping through history does not create new frames, change `crossCoupling`, alter `lambda2`, or mutate phase detection results.

## Numerical Safety

Replay safety depends on stable snapshot handling:

- immutable snapshot copies where frame history is stored
- `Float64Array` use for stable numeric vectors where applicable
- replay-safe tensor serialization into plain array structures for export
- bounded memory allocation through capped histories

Snapshot isolation prevents later live frames from accidentally modifying historical replay data.

## Future Work

Future replay architecture may include:

- compressed replay streams
- NDJSON export
- indexed replay events
- time-window bookmarks
- WebWorker replay decoding

These additions should preserve the current invariant detection layer and export schema compatibility.

## Documentation Boundary

This document describes replay and buffering architecture. It does not modify runtime code, phase detection equations, CPI formulas, entropy logic, `lambda2` extraction, tensor projection, or UI rendering.
