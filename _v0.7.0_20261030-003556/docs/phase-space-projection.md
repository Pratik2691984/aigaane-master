# Phase-Space Projection

## Overview

Phase-space projection converts scalar runtime metrics into a distributed `7x7` tensor field. Collapse Lab uses this tensor as a compact geometric representation of topology, synchronization, entropy, coupling pressure, stochastic fluctuation, and phase momentum.

The tensor is not a replacement for phase detection. It is a visualization and trajectory layer built from stable runtime metrics. The invariant detection layer remains controlled by graph topology, `lambda2`, `cpi`, entropy, synchronization, and cluster balance.

## Low-Dimensional Runtime State

The projection begins with a low-dimensional runtime state:

| Input | Meaning |
| --- | --- |
| `lambda2` | Normalized Laplacian spectral gap. |
| `cpi` | Collapse Probability Index. |
| `entropy` | Information disorder or contraction measure. |
| `k` | Component count or dominant-fragmentation count. |
| `crossCoupling` | Inter-cluster coupling pressure. |
| `noise` | Stochastic perturbation level. |
| `phaseMomentum` | Frame-to-frame change in collapse pressure, derived from `cpi` movement. |

These inputs are normalized before tensor construction so the projection remains stable across frames.

## Normalization Strategy

The projection maps runtime values into bounded coordinates:

| Input | Normalization |
| --- | --- |
| `lambda2` | Uses `tanh` normalization. |
| `cpi` | Clamped to `[0, 1]`. |
| `entropy` | Clamped to `[0, 1]`. |
| `k` | Normalized by maximum expected fragmentation. |
| `crossCoupling` | Uses `tanh` normalization. |
| `noise` | Clamped to a bounded range. |
| `phaseMomentum` | Computed from frame-to-frame `cpi` change, then bounded. |

The `tanh` normalization is not only a numerical overflow guard. Its main role is to map unbounded or highly variable runtime quantities into a stable geometric coordinate range `[0, 1)`. This preserves visual comparability across frames and prevents one metric, such as a sudden `lambda2` spike, from dominating the entire 49D tensor field.

Conceptually:

```text
lambda2_norm = tanh(lambda2_scale * lambda2)
crossCoupling_norm = tanh(coupling_scale * crossCoupling)
cpi_norm = clamp(cpi, 0, 1)
entropy_norm = clamp(entropy, 0, 1)
noise_norm = clamp(noise, 0, 1)
phaseMomentum = clamp(abs(cpi_t - cpi_t_minus_1), 0, 1)
```

## The 7D Basis Vector

The normalized state becomes a seven-channel basis vector:

```text
b = [
  lambda2_norm,
  cpi_norm,
  entropy_norm,
  k_norm,
  crossCoupling_norm,
  noise_norm,
  phaseMomentum
]
```

Channel meanings:

| Channel | Name | Source |
| --- | --- | --- |
| `0` | Global Coherence | `lambda2_norm` |
| `1` | Boundary Tension | `cpi_norm` |
| `2` | Informational Disorder | `entropy_norm` |
| `3` | Topological Fragmentation | `k_norm` |
| `4` | Cross-Network Energy | `crossCoupling_norm` |
| `5` | Stochastic Fluctuation | `noise_norm` |
| `6` | Phase Momentum | `phaseMomentum` |

## Outer-Product Tensor Mapping

The tensor is built as an outer product over the basis vector:

```text
T = b ⊗ b
```

A contrast-sharpened form is:

```text
T_ij = (b_i * b_j)^1.5
```

The exponent `1.5` acts as nonlinear contrast sharpening. It makes phase-boundary interactions visually and numerically separable by suppressing weak cross-channel terms while preserving strong interactions.

## Geometric Meaning of Quadrants

Important tensor cells have interpretable meanings:

| Cell | Meaning |
| --- | --- |
| `[0][0]` | Global coherence axis. |
| `[1][1]` | Boundary tension. |
| `[2][2]` | Entropy and informational disorder. |
| `[3][3]` | Topological fragmentation. |
| `[1][4]` and `[4][1]` | Boundary tension crossed with coupling energy. |
| `[6][*]` | Phase momentum interactions across all channels. |

Diagonal cells describe self-energy in a channel. Off-diagonal cells describe interactions between channels.

## Phase Behavior

### NORMAL

During `NORMAL` behavior, energy is distributed across entropy and fragmentation channels:

- informational disorder remains visible
- fragmentation channels retain weight
- no single global coherence axis dominates

### PRE_COLLAPSE

During `PRE_COLLAPSE`, energy concentrates around boundary tension and cross-coupling cells:

- `[1][1]` increases as boundary tension rises
- `[1][4]` and `[4][1]` strengthen as bridge formation pressure grows
- momentum cells may brighten if `cpi` changes rapidly near the boundary

### COLLAPSED

During `COLLAPSED`, energy becomes rank-concentrated around `[0][0]`:

- `[0][0]` becomes the dominant global coherence axis
- fragmentation and entropy channels contract
- the tensor reads as axis-dominant global coherence

This should not be described as isotropic. The collapsed tensor is rank-concentrated and coherence-axis dominant.

## 2D Phase-Space Projection

The current scaffold projects tensor energy into a deterministic two-dimensional trajectory:

```text
x = tensor[1][1] + tensor[1][4] + tensor[4][1] - tensor[0][0]

y = tensor[2][2] + tensor[3][3] + tensor[6][6] - tensor[0][0]
```

Then the coordinates are bounded:

```text
nx = 0.5 + 0.35 * tanh(x * 3)
ny = 0.5 + 0.35 * tanh(y * 3)
```

This projection is deterministic and interpretable. It is not PCA yet. The `x` axis compares boundary/coupling pressure against global coherence, while the `y` axis compares disorder, fragmentation, and momentum against global coherence.

## Future PCA Layer

Future versions may replace the deterministic projection with learned or adaptive manifold methods:

- online PCA
- Laplacian eigenmaps
- tensor eigentrajectories
- manifold embedding

These future projection layers should not change the invariant detection layer. `lambda2`, `cpi`, entropy, synchronization, component count, and cluster balance remain the source of phase-state classification.

## Numerical Safety

The projection is designed for stable browser-native rendering:

- bounded tensor values
- `Float64Array` use for numeric state where applicable
- no external math libraries
- capped trajectory histories
- replay-safe tensor snapshots

The tensor and projection layers should remain deterministic for a given runtime frame so replay and export review can reconstruct phase-space behavior.

## Documentation Boundary

This document describes the phase-space projection architecture. It does not modify runtime code, tensor projection, phase detection equations, CPI formulas, entropy logic, `lambda2` extraction, replay/export behavior, or UI rendering.
