# Numerical Stability

## Overview

Collapse Lab uses bounded transforms and controlled numerical methods to prevent instability during high-frequency browser execution. The runtime is designed to keep graph metrics, tensor values, replay buffers, and canvas renderers stable without external math libraries.

## Float Precision

Collapse Lab uses typed numeric vectors where stable repeated computation is needed:

- `Float64Array` usage
- typed vectors
- reduced precision drift across repeated frame updates

Typed arrays also make numeric intent explicit and reduce accidental object-shape churn during animation.

## EPSILON Padding

Small epsilon constants protect numerically sensitive operations:

- `EPSILON = 1e-12`
- divide-by-zero prevention
- logarithm protection
- entropy stability

`EPSILON` padding is especially important when probabilities, graph degrees, cluster masses, or normalized values approach zero.

## Phase Wrapping

Oscillator phases are wrapped into a bounded range:

```text
[0, 2π)
```

Phase wrapping prevents runaway oscillator values and keeps trigonometric operations stable over long sessions.

## Bounded Metric Normalization

Metric normalization prevents one runtime signal from overwhelming the geometry:

- `tanh` normalization
- clamping
- bounded tensor values

This applies to metrics such as `lambda2`, `crossCoupling`, `phaseMomentum`, entropy, and noise. Bounded ranges improve visual comparability and reduce frame-to-frame discontinuities.

## Spectral Stability

Spectral extraction is stabilized by graph normalization:

- normalized Laplacian construction
- bounded eigenvalue ranges
- `lambda2` extraction constraints

The normalized Laplacian keeps spectral values comparable across changing graph density and component count. This is essential for PRE_COLLAPSE and COLLAPSED boundary interpretation.

## Replay Stability

Replay stability depends on bounded histories and snapshot isolation:

- capped replay histories
- snapshot isolation
- stable export serialization

Replay mode should repaint stored frames without advancing simulation, recomputing stochastic terms, or mutating historical tensor snapshots.

## Canvas Runtime Safety

Canvas renderers are designed for high-frequency updates:

- cached canvas contexts
- `alpha:false` contexts where opaque rendering is appropriate
- frame reuse
- avoiding allocation churn

Reducing per-frame allocation keeps animation smoother and lowers garbage-collection pressure.

## Adaptive Gamma Stability

Adaptive gamma controls visual intensity without allowing luminance blowout:

- bounded gamma range
- avoiding luminance blowout
- preserving PRE_COLLAPSE visibility

Gamma adaptation should make boundary transitions legible while keeping NORMAL and COLLAPSED states visually comparable.

## Stochastic Integration Stability

The synthetic oscillator layer relies on controlled stochastic integration:

- Euler-Maruyama integration
- controlled `dt`
- bounded stochastic noise
- metastable preservation

Noise acts as a stress test for topology classification. It should perturb the boundary without destroying the interpretability of `lambda2`, `syncRatio`, `clusterBalanceRatio`, or `cpi`.

## Browser Runtime Constraints

Collapse Lab is designed for browser-safe execution:

- no external math libraries
- browser-safe execution
- deterministic fallback logic

These constraints keep deployment simple and reduce dependency-related reproducibility risks.

## Future Stability Work

Future stability work may include:

- WebWorkers
- GPU tensor rendering
- online PCA
- sparse tensor compression

These additions should preserve existing runtime invariants and export semantics.

## Documentation Boundary

This document describes numerical stability constraints. It does not modify runtime code, phase detection equations, CPI formulas, entropy logic, `lambda2` extraction, replay/export behavior, tensor projection, or UI rendering.
