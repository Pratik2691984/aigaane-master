# Experimental Telemetry Export Schema

## Purpose

This document describes the stable telemetry export shape used by Collapse Lab experiments. It supports review, replication, and downstream analysis while keeping permanent documentation separate from runtime-generated telemetry in `experimental_logs/`.

## Top-Level JSON Schema

```json
{
  "timestamp": "ISO-8601 string",
  "totalFrames": 0,
  "controls": {
    "noise": 0,
    "coupling": 0,
    "gamma": 0,
    "speed": 0
  },
  "frames": [],
  "replayFrames": []
}
```

## Frame Schema

Each exported frame preserves the metrics required to analyze collapse topology, spectral behavior, entropy contraction, and replay history.

```json
{
  "t": 0,
  "phase": "NORMAL | PRE_COLLAPSE | COLLAPSED",
  "cpi": 0,
  "lambda2": 0,
  "entropy": 0,
  "residualMass": 0,
  "clusterBalanceRatio": 0,
  "syncRatio": 0,
  "k": 0,
  "modularity": 0
}
```

## Required Fields

| Field | Location | Type | Description |
| --- | --- | --- | --- |
| `timestamp` | top level | string | ISO-8601 timestamp for export creation. |
| `totalFrames` | top level | number | Count of exported live telemetry frames. |
| `controls` | top level | object | Runtime control state used for the experiment. |
| `frames` | top level | array | Ordered telemetry frames captured during the run. |
| `replayFrames` | top level | array | Replay history supported by runtime exports. |
| `t` | frame | number | Runtime frame time. |
| `phase` | frame | string | `NORMAL`, `PRE_COLLAPSE`, or `COLLAPSED`. |
| `cpi` | frame | number | Collapse Probability Index. |
| `lambda2` | frame | number | Normalized Laplacian spectral gap. |
| `entropy` | frame | number | Entropy value for the current frame. |
| `residualMass` | frame | number | Residual cluster or boundary mass. |
| `clusterBalanceRatio` | frame | number | Balance ratio for dominant clusters. |
| `syncRatio` | frame | number | Runtime synchronization ratio. |
| `k` | frame | number | Detected component or dominant-cluster count. |
| `modularity` | frame | number | Approximate modular structure score. |

## CSV Columns

The documented CSV analysis column order is:

```csv
t,phase,cpi,lambda2,entropy,residualMass,clusterBalanceRatio,syncRatio,k,modularity
```

## Replay History

`replayFrames` stores replay-compatible frame history for deterministic review of exported experiments. It is part of the export contract and should remain present even when no replay frames are captured.

## Documentation Boundary

This schema reference does not change runtime export logic, replay buffers, telemetry capture, or simulation behavior. It documents the existing export capabilities versioned under tag `collapse-lab-v1`.
