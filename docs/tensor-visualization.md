# Tensor Visualization Mechanics and Perceptual Mapping

## 1. Overview

Collapse Lab renders a 49D tensor as a `7x7` heatmap. The visualization system provides:

- deterministic visual mapping
- topology-to-color translation
- `TensorHeatmap.jsx` as the main renderer

The heatmap is a visual interpretation layer. It does not replace invariant detection based on graph state, `lambda2`, `syncRatio`, `clusterBalanceRatio`, entropy, or `cpi`.

## 2. Tensor Geometry

The tensor is generated from an outer-product projection:

```text
T = outer_product(b, b)
```

Each `tensor[i][j]` cell maps the interaction between channel `i` and channel `j`.

Nonlinear contrast sharpening is represented as:

```text
T_ij = (b_i * b_j)^1.5
```

The exponent emphasizes strong channel interactions while suppressing low-energy background terms.

## 3. Channel Definitions

| Channel | Meaning |
| --- | --- |
| `0` | Global Coherence |
| `1` | Boundary Tension |
| `2` | Informational Disorder |
| `3` | Topological Fragmentation |
| `4` | Cross-Network Energy |
| `5` | Stochastic Fluctuation |
| `6` | Phase Momentum |

Machine-readable related identifiers include `lambda2`, `crossCoupling`, `phaseMomentum`, `clusterBalanceRatio`, and `syncRatio`.

## 4. Color Mapping

The current palette maps tensor semantics into stable color families:

- green = coherence
- orange = boundary tension
- violet = entropy
- blue = fragmentation
- red = coupling
- white = stochasticity
- yellow = momentum

Off-diagonal cells blend the row and column channel colors so that each pixel represents an interaction between two metrics.

Color is a reading aid, not a separate classifier.

## 5. Heatmap Rendering Loop

The heatmap renderer uses direct canvas drawing:

- discrete cell rendering
- `cellWidth` / `cellHeight`
- `tensor[row][col]` maps to one grid cell
- direct tensor intensity mapping
- canvas repaint flow

Each frame maps tensor values into color intensity and repaints the `7x7` field.

## 6. Adaptive Gamma

Adaptive gamma adjusts heatmap intensity to preserve readability:

- gamma adaptation
- PRE_COLLAPSE visibility enhancement
- collapse sharpening
- gamma values should remain bounded

Gamma affects visual legibility. It should not change tensor values or phase classification.

## 7. Temporal Glow Buffer

The temporal glow buffer adds short visual memory:

- exponential decay memory
- previous frame blending
- alpha persistence factor
- glow shows metastable persistence

This makes boundary transitions visible across high-frequency frame updates without making replay state non-deterministic.

## 8. Phase Appearance Profiles

### NORMAL

`NORMAL` appears as:

- dispersed low-energy tensor
- blue/violet fragmentation and entropy channels

### PRE_COLLAPSE

`PRE_COLLAPSE` appears as:

- concentrated boundary tension cells
- orange `[1][1]`
- interaction bands `[1][4]` and `[4][1]`

### COLLAPSED

`COLLAPSED` appears as:

- axis-dominant coherence ignition at `[0][0]`
- globally connected synchronized topology

This should not be overstated as total network integration or consciousness.

## 9. Timeline Visualization

Timeline visualization is handled by `MetricTimeline.jsx` and tracks:

- CPI
- `lambda2`
- entropy
- 120-frame rolling history
- canvas timeline renderer

The timeline gives local temporal context for phase changes without requiring a full export.

## 10. Phase Space Projection

Phase-space visualization is handled by `PhaseSpaceView.jsx` and uses:

- deterministic 2D projection
- CPI/lambda2 or tensor-derived trajectory depending on current implementation
- non-PCA scaffold
- future PCA should not alter invariant detection

The current scaffold is interpretable and deterministic. Adaptive embedding layers can be added later without changing phase detection logic.

## 11. Runtime Safety

The visualization layer is optimized for browser-native rendering:

- cached canvas contexts
- bounded histories
- no heavy chart libraries
- no SVG dependency for high-frequency charts
- lightweight browser rendering

Canvas rendering keeps the heatmap responsive while avoiding DOM-heavy updates.

## 12. Runtime Contract Warning

This document describes the current Collapse Lab architecture and should be updated whenever runtime contracts change.

## 13. Future Visualization Work

Future visualization work may include:

- PCA trajectories
- eigentrajectory overlays
- GPU shaders
- WebGL tensor rendering
- manifold embeddings

## Documentation Boundary

This document does not modify runtime code, phase detection equations, CPI formulas, entropy logic, `lambda2` extraction, replay/export behavior, tensor projection, or UI rendering.
