# Topological & Spectral Extraction Metrics

## Purpose

This document defines the topology, synchronization, and spectral metrics used by Collapse Lab to describe non-equilibrium phase-space behavior. It is a permanent documentation reference and remains separate from runtime-generated files in `experimental_logs/`.

## Metric Table

| Metric | Symbol | Runtime Key | Meaning |
| --- | --- | --- | --- |
| Component count | `k` | `k` | Number of detected dominant connected components. |
| Spectral gap | `lambda2` | `lambda2` | Second-smallest eigenvalue of the normalized graph Laplacian. |
| Collapse Probability Index | `CPI` | `cpi` | Bounded collapse-likelihood score derived from topology, synchronization, and spectral signals. |
| Entropy | `H` | `entropy` | Information dispersion measure for the current phase/topology state. |
| Sync ratio | `R_sync` | `syncRatio` | Bounded synchronization ratio for oscillator phase coherence. |
| Cluster balance ratio | `B` | `clusterBalanceRatio` | Balance ratio measuring whether the two dominant clusters are both substantial. |
| Residual mass | `M_residual` | `residualMass` | Remaining non-dominant or boundary mass retained by the topology. |
| Modularity | `Q` | `modularity` | Approximate modular structure score for the current graph state. |

## Synchronization Notation

Sync ratio must be written as `R_sync`, with runtime key `syncRatio`.

Do not use sigma for sync ratio. Sigma is reserved for entropy production and dissipation in the broader thermodynamic model.

## Spectral Extraction

The spectral gap is extracted from the normalized graph Laplacian so connectivity estimates remain comparable across frames with changing topology. The `lambda2` value is interpreted as algebraic connectivity: values near zero indicate that the graph is weakly connected or approaching separation into independent components.

## Cluster Balance

`clusterBalanceRatio` hardens topology classification by requiring the two dominant clusters to be sufficiently balanced. This prevents a large connected component plus a small singleton from being treated as a meaningful dual-collapse configuration.

## Numerical Stability Constraints

The engine applies:

- epsilon padding (`EPSILON = 1e-12`)
- normalized Laplacian scaling
- capped metric histories
- `Float64Array` typed vectors
- bounded gamma transforms
- deterministic UI cadence
- cached canvas contexts

to preserve stable spectral extraction under high-frequency rendering conditions.

## Documentation Boundary

This document does not modify metric extraction, graph construction, Kuramoto evolution, CPI logic, entropy logic, PRE_COLLAPSE thresholds, replay behavior, or export behavior. It describes the stable behavior versioned under tag `collapse-lab-v1`.
