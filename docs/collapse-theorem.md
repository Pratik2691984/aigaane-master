# Non-Equilibrium Neuro-Collapse Theorem

## Purpose

This document states the Collapse Lab theorem used to interpret topology transitions in non-equilibrium neural phase-space simulations. It is permanent, human-authored research documentation and is intentionally separate from runtime-generated telemetry in `experimental_logs/`.

## Theorem Statement

In a finite phase-coupled neural system with adaptive interaction topology, a reproducible pre-collapse regime exists when synchronization, spectral degeneracy, information compression, and cluster balance jointly satisfy bounded metastability conditions.

`PRE_COLLAPSE` is a strict metastable two-component boundary. The system must show a dual topology, a near-zero spectral gap, high collapse probability, high synchronization, low entropy, and enough cluster balance to exclude trivial fragmentation.

## Runtime Identifiers

| Concept | Machine-Readable Identifier | Meaning |
| --- | --- | --- |
| Component count | `k` | Number of detected dominant connected components. |
| Spectral gap | `lambda2` | Algebraic connectivity from the normalized graph Laplacian. |
| Collapse Probability Index | `CPI` | Bounded collapse-likelihood score used in theorem notation. |
| Synchronization ratio | `R_sync` | Phase coherence ratio used in theorem notation. |
| Entropy | `entropy` | Information dispersion or contraction measure for the current state. |
| Cluster balance | `clusterBalanceRatio` | Balance ratio between the two dominant clusters. |

Use `lambda2`, `clusterBalanceRatio`, and `R_sync` for machine-readable theorem identifiers. Unicode lambda notation is allowed only in explanatory prose, not in JSON keys, filenames, or parser-facing examples.

## PRE_COLLAPSE Conditions

The runtime classifies a frame as `PRE_COLLAPSE` only when all required conditions are satisfied:

```text
k === 2
lambda2 <= 1e-4
CPI >= 0.85
R_sync >= 0.9
entropy <= 0.25
clusterBalanceRatio >= 0.35
```

These conditions mean:

| Condition | Interpretation |
| --- | --- |
| `k === 2` | The graph has a strict two-component topology. |
| `lambda2 <= 1e-4` | The spectral gap is near zero, indicating a weakly connected or split boundary. |
| `CPI >= 0.85` | Collapse probability is high enough to enter the metastable boundary. |
| `R_sync >= 0.9` | Oscillator phase coherence is high. |
| `entropy <= 0.25` | State dispersion has contracted. |
| `clusterBalanceRatio >= 0.35` | Both components are substantial enough to reject degenerate splits. |

## Balanced Duality Constraint

`clusterBalanceRatio >= 0.35` prevents degenerate giant-component + singleton configurations from falsely satisfying metastable bifurcation conditions.

This constraint was added to prevent false `PRE_COLLAPSE` states when `k = 2` but one cluster contains almost all nodes.

## Interpretation

The theorem treats collapse as a topological and spectral transition rather than a single scalar event. A valid pre-collapse frame must show both global graph weakening and coherent dual-structure formation. The balance requirement prevents trivial graph splits from being mistaken for meaningful metastable bifurcation.

## Documentation Boundary

This document does not redefine runtime simulation physics, Kuramoto evolution, entropy extraction, CPI logic, spectral gap extraction, PRE_COLLAPSE thresholds, replay behavior, or export behavior. It documents the stable Collapse Lab behavior versioned under tag `collapse-lab-v1`.
