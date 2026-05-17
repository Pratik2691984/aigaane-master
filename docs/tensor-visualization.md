# Tensor Visualization

## Overview

Collapse Lab renders a 49D tensor as a `7x7` heatmap. The visualization is deterministic: scalar topology and synchronization metrics are projected into tensor channels, then translated into color and intensity on canvas.

The heatmap is a topology-to-color translation layer. It does not replace invariant detection based on graph state, `lambda2`, `syncRatio`, `clusterBalanceRatio`, entropy, or `cpi`.

## Tensor Geometry

The tensor is generated from an outer-product projection:

```text
T = b ⊗ b
```

Each `tensor[i][j]` cell represents an interaction between channel `i` and channel `j`. A nonlinear contrast sharpening step can emphasize strong interactions while suppressing low-energy background terms.

```text
T_ij = (b_i * b_j)^1.5
```

## Channel Definitions

| Channel | Meaning |
| --- | --- |
| `0` | Global Coherence |
| `1` | Boundary Tension |
| `2` | Informational Disorder |
| `3` | Topological Fragmentation |
| `4` | Cross-Network Energy |
| `5` | Stochastic Fluctuation |
| `6` | Phase Momentum |

Machine-readable related identifiers include `lambda2`, `crossCoupling`, `phaseMomentum`, and `clusterBalanceRatio`.

## Color Mapping

The current palette maps tensor semantics into stable color families:

- green = coherence
- orange = boundary tension
- violet = entropy
- blue = fragmentation
- red = coupling
- white = stochasticity
- yellow = momentum

Color is used as a reading aid, not as a separate classifier.

## Heatmap Rendering

The heatmap renderer uses direct canvas drawing:

- discrete cell rendering
- `cellWidth` / `cellHeight`
- direct tensor intensity mapping
- canvas repaint flow

Each frame clears or updates the canvas, maps tensor values into color intensity, and paints the `7x7` field.

## Adaptive Gamma

Adaptive gamma adjusts heatmap intensity to preserve readability:

- gamma adaptation
- PRE_COLLAPSE visibility enhancement
- collapse sharpening

The purpose is visual legibility. Gamma should not change the underlying tensor values or phase classification.

## Temporal Glow Buffer

The temporal glow buffer adds short visual memory:

- exponential decay memory
- previous frame blending
- alpha persistence factor

This helps transitions remain visible across high-frequency frame updates without making the replay state non-deterministic.

## Phase Appearance

### NORMAL

`NORMAL` appears as a dispersed low-energy tensor:

- entropy and fragmentation channels remain visible
- no single coherence cell dominates
- energy is spread across multiple channels

### PRE_COLLAPSE

`PRE_COLLAPSE` appears as concentrated boundary tension cells:

- `[1][1]` brightens
- `[1][4]` and `[4][1]` show boundary tension coupled with cross-network energy
- phase-boundary interactions become easier to distinguish

### COLLAPSED

`COLLAPSED` appears as axis-dominant coherence ignition at `[0][0]`:

- `[0][0]` becomes the dominant global coherence cell
- entropy and fragmentation channels contract
- the tensor reads as rank-concentrated rather than isotropic

## Timeline Visualization

The timeline renderer tracks short metric histories:

- `CPI`
- `lambda2`
- `entropy`
- canvas timeline renderer
- 120-frame history

The timeline gives local temporal context for phase changes without requiring a full export.

## Phase Space Projection

The phase-space view uses deterministic 2D projection:

- deterministic 2D projection
- `CPI` / `lambda2` trajectory
- non-PCA scaffold

The current scaffold is interpretable and deterministic. Future PCA or manifold methods can be added without changing the invariant detection layer.

## Runtime Safety

The visualization layer is optimized for browser-native rendering:

- cached canvas contexts
- bounded histories
- no SVG dependency
- lightweight browser rendering

Canvas rendering keeps the heatmap responsive while avoiding DOM-heavy updates.

## Future Visualization Work

Future visualization work may include:

- PCA trajectories
- eigentrajectory overlays
- GPU shaders
- WebGL tensor rendering
- manifold embeddings

These improvements should preserve existing runtime metrics, export schemas, and phase classification rules.

## Documentation Boundary

This document describes tensor visualization behavior. It does not modify runtime code, phase detection equations, CPI formulas, entropy logic, `lambda2` extraction, replay/export behavior, tensor projection, or UI rendering.
