# Numerical Stability and Error Bound Constraints

## 1. Overview

Collapse Lab uses bounded coordinate transforms and controlled numerical methods to prevent floating-point degradation, accumulator overflow, and divergence during high-frequency browser execution.

The stability layer protects oscillator updates, graph metrics, spectral extraction, tensor projection, replay buffers, exports, and canvas renderers.

## 2. Floating-Point Precision

Collapse Lab relies on browser-native JavaScript number semantics and typed numeric vectors where stable repeated computation is needed:

- `Float64Array` usage
- typed vectors
- reduced precision drift
- browser-native JavaScript number semantics

Typed arrays make numeric intent explicit and reduce accidental allocation churn in high-frequency paths.

## 3. EPSILON Padding

Small epsilon constants protect numerically sensitive operations:

- `EPSILON = 1e-12`
- divide-by-zero prevention
- logarithm protection
- entropy stability
- denominator safety

`EPSILON` padding is especially important when probabilities, graph degrees, cluster masses, or normalized values approach zero.

## 4. Phase Wrapping

Oscillator phases are wrapped into a bounded range:

```text
[0, 2*pi)
```

This prevents runaway oscillator values and keeps trigonometric operations stable over long sessions.

## 5. Bounded Metric Normalization

Metric normalization prevents one runtime signal from overwhelming tensor geometry:

- `tanh` normalization
- clamping to `[0, 1]`
- bounded tensor values
- preventing sudden metric spikes from dominating the 49D tensor

This applies to metrics such as `lambda2`, `crossCoupling`, `phaseMomentum`, entropy, and noise.

## 6. Spectral Solver Stability

Spectral extraction is stabilized by graph normalization and bounded estimation:

- normalized Laplacian
- bounded eigenvalue range
- `lambda2` extraction
- projected power iteration / bounded eigenvalue estimation if used

The solver uses bounded iteration counts and convergence tolerance as defined in `app/core/neuro-collapse-engine.js`.

The normalized Laplacian keeps spectral values comparable across changing graph density and component count. This is essential for PRE_COLLAPSE and COLLAPSED boundary interpretation.

## 7. Replay and Export Isolation

Replay and export stability require historical state to remain isolated from active simulation:

- capped replay histories
- snapshot isolation
- stable export serialization
- export must not mutate active simulation state

Replay should repaint stored frames without advancing simulation, recomputing stochastic terms, or mutating historical tensor snapshots.

## 8. Canvas Runtime Safety

Canvas renderers are designed for high-frequency updates:

- cached canvas contexts
- `alpha:false` contexts where used
- frame reuse
- avoiding allocation churn
- avoiding unnecessary SVG/DOM node creation in high-frequency paths

Reducing per-frame allocation keeps animation smoother and lowers garbage-collection pressure.

## 9. Adaptive Gamma Stability

Adaptive gamma controls visual intensity without allowing luminance blowout:

- bounded gamma range
- avoiding luminance blowout
- preserving PRE_COLLAPSE visibility

Gamma adaptation should make boundary transitions legible while keeping NORMAL and COLLAPSED states visually comparable.

## 10. Stochastic Integration Stability

The synthetic oscillator layer relies on controlled stochastic integration:

- Euler-Maruyama integration
- controlled `dt`
- bounded stochastic noise
- metastable preservation

Noise acts as a stress test for topology classification. It should perturb the boundary without destroying the interpretability of `lambda2`, `syncRatio`, `clusterBalanceRatio`, or `cpi`.

## 11. Browser Runtime Constraints

Collapse Lab is designed for browser-safe execution:

- no external math libraries
- browser-safe execution
- deterministic fallback logic
- static Vercel deployment compatibility

These constraints keep deployment simple and reduce dependency-related reproducibility risks.

## 12. Runtime Contract Warning

This document describes the current Collapse Lab architecture and should be updated whenever runtime contracts change.

## 13. Future Stability Work

Future stability work may include:

- WebWorkers
- GPU tensor rendering
- online PCA
- sparse tensor compression
- larger node-count scaling

## Documentation Boundary

This document does not modify runtime code, phase detection equations, CPI formulas, entropy logic, `lambda2` extraction, replay/export behavior, tensor projection, or UI rendering.
