# Non-Equilibrium Neuro-Collapse Theorem

## Purpose

This document states the Collapse Lab theorem used to interpret topology transitions in non-equilibrium neural phase-space simulations. It is a human-authored scientific reference and is intentionally separate from runtime-generated telemetry in `experimental_logs/`.

## Theorem Statement

In a finite phase-coupled neural system with adaptive interaction topology, a reproducible pre-collapse regime exists when local synchronization, spectral degeneracy, information compression, and cluster balance jointly satisfy bounded metastability conditions.

The system enters a `PRE_COLLAPSE` state when the topology has bifurcated into two coherent macroscopic components while the spectral gap approaches zero, the Collapse Probability Index is high, entropy has contracted, and cluster mass remains balanced enough to exclude degenerate fragmentation.

## Core Variables

| Symbol | Runtime Field | Meaning |
| --- | --- | --- |
| `k` | `k` | Number of detected connected components or dominant clusters. |
| `lambda2` | `lambda2` | Algebraic connectivity extracted from the normalized graph Laplacian. |
| `CPI` | `CPI` | Collapse Probability Index, a bounded indicator of pre-collapse likelihood. |
| `H` | `entropy` | Entropy of the current phase/topology state. |
| `B` | `clusterBalanceRatio` | Balance ratio between dominant cluster masses. |

## PRE_COLLAPSE Conditions

The runtime classifies a frame as `PRE_COLLAPSE` only when all required conditions are satisfied:

1. Dual topology (`k = 2`)
   The system has separated into two dominant coherent components.

2. Spectral degeneracy (`lambda2 <= 1e-4`)
   The normalized Laplacian spectral gap has collapsed toward zero, indicating weak global connectivity between the two components.

3. High collapse likelihood (`CPI >= 0.85`)
   The Collapse Probability Index reports a high probability of transition into the pre-collapse regime.

4. Balanced Duality (`clusterBalanceRatio >= 0.35`)
   Prevents degenerate giant-component + singleton configurations from falsely satisfying metastable bifurcation conditions.

## Interpretation

The theorem treats collapse as a topological and spectral transition rather than a single scalar event. A valid pre-collapse frame must show both global graph weakening and coherent dual-structure formation. The balance requirement prevents trivial graph splits from being mistaken for meaningful metastable bifurcation.

## Boundary Conditions

The theorem does not redefine the runtime simulation physics, Kuramoto evolution, entropy extraction, CPI logic, spectral gap extraction, or export/replay systems. It documents the already-versioned Collapse Lab behavior under tag `collapse-lab-v1`.

## Review Notes

This file is intended for peer review, replication notes, and future theoretical extensions. Runtime evidence supporting the theorem should be exported from the application and stored outside this document, with generated telemetry remaining under `experimental_logs/`.
