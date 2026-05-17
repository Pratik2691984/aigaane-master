# Topological & Spectral Extraction Metrics

## Purpose

This document defines the topology, synchronization, and spectral metrics used by Collapse Lab to describe non-equilibrium phase-space behavior. It is a permanent documentation reference and is separate from runtime-generated files in `experimental_logs/`.

## Metric Table

| Metric | Runtime Field | Definition | Interpretation |
| --- | --- | --- | --- |
| Component count | `k` | Number of detected dominant connected components or clusters. | `k = 2` indicates dual topology during pre-collapse classification. |
| Spectral gap | `lambda2` | Second-smallest eigenvalue of the normalized graph Laplacian. | Lower values indicate weaker global connectivity; `lambda2 <= 1e-4` supports pre-collapse classification. |
| Collapse Probability Index | `CPI` | Bounded collapse-likelihood score derived from topology, synchronization, and spectral signals. | `CPI >= 0.85` indicates high collapse likelihood. |
| Entropy | `entropy` | Information dispersion measure for the current phase/topology state. | Lower entropy indicates contraction or compression of system state. |
| Sync ratio | `R_sync` | Bounded synchronization ratio for oscillator phase coherence. | Higher values indicate stronger collective phase alignment. |
| Cluster balance ratio | `clusterBalanceRatio` | Ratio measuring whether dominant clusters are meaningfully balanced. | `clusterBalanceRatio >= 0.35` rejects giant-component + singleton degeneracy. |

## Spectral Extraction

The spectral gap is extracted from the normalized graph Laplacian so that connectivity estimates remain comparable across frames with changing topology. The `lambda2` value is interpreted as algebraic connectivity: values near zero indicate that the graph is weakly connected or approaching separation into independent components.

## Synchronization Extraction

`R_sync` represents phase coherence across the oscillator population. It should be read as a synchronization ratio, not as a standard deviation or variance term. This notation avoids ambiguity with sigma-based statistical notation.

## Cluster Balance

`clusterBalanceRatio` hardens topology classification by requiring the two dominant clusters to be sufficiently balanced. This prevents a large connected component plus a small singleton from being treated as a meaningful dual-collapse configuration.

## Numerical Stability Constraints

The engine applies:

* epsilon padding (`EPSILON = 1e-12`)
* normalized Laplacian scaling
* capped metric histories
* `Float64Array` typed vectors
* bounded gamma transforms

to preserve stable spectral extraction under high-frequency rendering conditions.

## Documentation Boundary

This document does not modify metric extraction, graph construction, Kuramoto evolution, CPI logic, entropy logic, PRE_COLLAPSE thresholds, replay behavior, or export behavior. It describes the stable behavior versioned under tag `collapse-lab-v1`.
