# Experimental Telemetry Export Schema

## Purpose

This document describes the stable telemetry export shape used by Collapse Lab experiments. It is intended for review, replication, and downstream analysis while keeping permanent documentation separate from runtime-generated telemetry in `experimental_logs/`.

## Top-Level Schema

```json
{
  "timestamp": "2026-05-17T00:00:00.000Z",
  "controls": {},
  "frames": [],
  "replayFrames": []
}
```

## Frame Schema

Each exported frame preserves the metrics required to analyze collapse topology, spectral behavior, entropy contraction, and replay history.

```json
{
  "timestamp": "2026-05-17T00:00:00.000Z",
  "CPI": 0.0,
  "lambda2": 0.0,
  "entropy": 0.0,
  "k": 0,
  "clusterBalanceRatio": 0.0
}
```

## Required Fields

| Field | Location | Type | Description |
| --- | --- | --- | --- |
| `timestamp` | top level, frame | string | ISO-8601 timestamp for export creation or frame capture. |
| `controls` | top level | object | Runtime control state used for the experiment. |
| `frames` | top level | array | Ordered telemetry frames captured during the run. |
| `replayFrames` | top level | array | Replay history supported by runtime exports. |
| `CPI` | frame | number | Collapse Probability Index. |
| `lambda2` | frame | number | Normalized Laplacian spectral gap. |
| `entropy` | frame | number | Entropy value for the current frame. |
| `k` | frame | number | Detected component or dominant-cluster count. |
| `clusterBalanceRatio` | frame | number | Balance ratio for dominant clusters. |

## Replay History

`replayFrames` stores replay-compatible frame history for deterministic review of exported experiments. It is part of the export contract and should remain present even when no replay frames are captured.

## Documentation Boundary

This schema reference does not change runtime export logic, replay buffers, telemetry capture, or simulation behavior. It documents the existing export capabilities versioned under tag `collapse-lab-v1`.
