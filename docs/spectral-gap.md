# Spectral Gap (`λ₂`) in the Collapse Lab

## Overview

The Collapse Lab uses the second-smallest eigenvalue of the normalized graph Laplacian (`λ₂`) as the primary topological invariant governing phase classification.

This value is commonly called:

- the **Fiedler eigenvalue**
- the **spectral gap**
- the **algebraic connectivity**

Within the Collapse Lab architecture, `λ₂` acts as the hard mathematical discriminator between:

- fragmented topology
- metastable dual-boundary topology
- globally connected synchronization

---

# Mathematical Definition

Let:

- `A` be the adjacency matrix
- `D` be the degree matrix
- `L` be the graph Laplacian

Standard Laplacian:

```math
L = D - A
```

Normalized symmetric Laplacian:

```math
L_{norm} = I - D^{-1/2} A D^{-1/2}
```

The eigenvalues satisfy:

```math
0 = λ_1 \le λ_2 \le ... \le λ_n \le 2
```

The Collapse Lab tracks:

```math
λ_2
```

because it encodes global connectivity structure.

---

# Core Topological Interpretation

## Case 1 — Fragmented Graph (`k > 2`)

When the graph contains multiple disconnected components:

```math
λ_2 = 0
```

The network is not globally connected.

Interpretation:

- fragmented cognitive topology
- separated oscillator assemblies
- unresolved synchronization manifold

---

## Case 2 — PRE_COLLAPSE (`k = 2`)

The metastable boundary state occurs when:

```math
k = 2
```

and:

```math
λ_2 \approx 0
```

This represents:

- near-global synchronization
- preserved residual self-boundary
- dual-network tension
- unstable bifurcation regime

The system is mathematically close to full synchronization but retains one remaining topological split.

This is the defining condition of the PRE_COLLAPSE phase.

---

## Case 3 — COLLAPSED (`k = 1`)

When the final bridge forms:

```math
λ_2 > 0
```

The graph becomes globally connected.

Interpretation:

- unified synchronization manifold
- no disconnected components
- complete phase-locking topology

This transition is discontinuous.

The system snaps from:

```math
λ_2 \to 0
```

to:

```math
λ_2 > 0
```

at the exact collapse boundary.

---

# Collapse Lab Runtime Thresholds

## PRE_COLLAPSE

The runtime engine classifies PRE_COLLAPSE when:

```text
k === 2
lambda2 <= 1e-4
CPI >= 0.85
syncRatio >= 0.9
entropy <= 0.25
clusterBalanceRatio >= 0.35
```

---

## COLLAPSED

The runtime engine classifies COLLAPSED when:

```text
k === 1
lambda2 > 1e-4
```

---

# Numerical Solver

The engine estimates `λ₂` using:

- normalized Laplacian construction
- projected power iteration
- orthogonalization against the constant eigenvector

Implementation file:

```text
/app/core/neuro-collapse-engine.js
```

Core functions:

```javascript
computeNormalizedLaplacian()
estimateFiedlerEigenvalue()
computeSpectralGap()
```

---

# Why the Spectral Gap Matters

`λ₂` is the mathematically strictest invariant in the Collapse Lab because it is:

- topology-sensitive
- scale-independent
- graph-structural
- resistant to visual ambiguity

Unlike entropy or CPI, which are statistical aggregates, `λ₂` directly encodes whether the synchronization graph is globally connected.

This makes it the central invariant controlling:

- phase transitions
- replay labeling
- PRE_COLLAPSE detection
- collapse verification

---

# Relationship to Kuramoto Synchronization

The Collapse Lab derives synchronization topology from Kuramoto oscillator dynamics.

Pipeline:

```text
Kuramoto Oscillators
    ↓
Sliding-window phase extraction
    ↓
PLV matrix
    ↓
Threshold graph
    ↓
Adjacency matrix
    ↓
Normalized Laplacian
    ↓
λ₂ spectral gap
```

As cross-coupling increases:

```math
K_{cross} ↑
```

the spectral gap approaches the collapse threshold.

---

# Relationship to the 49D Tensor Projection

The 49D tensor projection maps:

```text
Axis 0 = λ₂ (global coherence)
```

During collapse:

- entropy channels extinguish
- fragmentation channels collapse
- tensor energy concentrates into the coherence origin

Visual consequence:

```text
[0][0] ignition dominance
```

inside the TensorHeatmap renderer.

---

# Research Interpretation

The spectral gap acts as a topological order parameter.

It formalizes:

- emergence of global synchronization
- preservation of residual self-boundaries
- discontinuous topology collapse
- metastable dual-network tension

In the Collapse Lab architecture:

```math
λ_2
```

is the mathematical hinge separating:

```text
NORMAL
→ PRE_COLLAPSE
→ COLLAPSED
```

states.

---

# References

1. Miroslav Fiedler — Algebraic Connectivity of Graphs
2. Fan Chung — Spectral Graph Theory
3. Steven Strogatz — Sync
4. Kuramoto — Chemical Oscillations, Waves, and Turbulence
5. Friston — Active Inference and Free Energy
6. Newman — Networks: An Introduction