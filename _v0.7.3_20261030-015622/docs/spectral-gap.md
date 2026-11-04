# Spectral Gap

## Purpose

This document defines the role of `lambda2` in Collapse Lab phase classification. The filename is `spectral-gap.md`, and the runtime key is always `lambda2`.

Explanatory prose may refer to lambda two as the spectral gap or algebraic connectivity. Parser-facing identifiers, JSON examples, filenames, and runtime keys must use `lambda2`, not Unicode notation.

## Definition

`lambda2` is the second-smallest eigenvalue of the normalized graph Laplacian. It is commonly called the Fiedler eigenvalue, spectral gap, or algebraic connectivity.

For a normalized graph Laplacian:

```text
0 = lambda1 <= lambda2 <= ... <= lambdan <= 2
```

`lambda2` encodes global graph connectivity. When `lambda2` approaches zero, the graph is disconnected or close to a metastable split topology.

## Runtime Phase Rules

Collapse Lab uses `lambda2` together with component count `k` and other metrics to classify phase state.

| Phase | Required Topology | Spectral Rule | Meaning |
| --- | --- | --- | --- |
| `NORMAL` | Usually `k > 2` or thresholds not satisfied | no collapse boundary satisfied | Fragmented or non-boundary topology. |
| `PRE_COLLAPSE` | `k === 2` | `lambda2 <= 1e-4` | Metastable two-component boundary. |
| `COLLAPSED` | `k === 1` | `lambda2 > 1e-4` | Globally connected collapsed topology. |

## Required Statements

- `lambda2 ≈ 0` means disconnected or metastable split topology.
- `lambda2 > 1e-4` with `k === 1` means globally connected collapsed topology.
- `PRE_COLLAPSE` requires `k === 2` and `lambda2 <= 1e-4`.
- `COLLAPSED` requires `k === 1` and `lambda2 > 1e-4`.

## PRE_COLLAPSE Boundary

The full PRE_COLLAPSE condition is:

```text
k === 2
lambda2 <= 1e-4
cpi >= 0.85
syncRatio >= 0.9
entropy <= 0.25
clusterBalanceRatio >= 0.35
```

The spectral term is necessary but not sufficient. A near-zero `lambda2` only becomes a valid PRE_COLLAPSE signal when the graph has exactly two dominant components and the supporting synchronization, entropy, CPI, and balance thresholds are also satisfied.

## COLLAPSED Boundary

The COLLAPSED condition is:

```text
k === 1
lambda2 > 1e-4
```

This identifies a globally connected topology after the split boundary has resolved.

## Research Interpretation

`lambda2` is the central topological order parameter in Collapse Lab. It distinguishes fragmented topology, metastable dual topology, and globally connected topology without relying on visual interpretation alone.

## Documentation Boundary

This document does not modify the spectral solver, Laplacian construction, CPI logic, entropy logic, phase detection equations, replay buffers, export schema, or visualization runtime. It documents the stable behavior versioned under tag `collapse-lab-v1`.
