# Kuramoto Dynamics

## Overview

Collapse Lab begins with a synthetic Kuramoto oscillator system used to generate phase-coupled neural-like signals. The engine is a controlled phase-dynamics test harness: it produces oscillator phases, synchronization structure, and topology transitions that downstream graph, spectral, CPI, tensor, and UI layers can analyze.

The synthetic source is intentionally separate from the downstream extraction pipeline. Future empirical EEG or CSV inputs can replace the oscillator generator while preserving the PLV, graph, spectral, phase classification, and tensor projection layers.

## State Variables

| Variable | Runtime Meaning |
| --- | --- |
| `theta_i(t)` | Phase of oscillator `i` at time `t`. |
| `omega_i` | Natural frequency of oscillator `i`. |
| `K_ij` | Coupling matrix entry from oscillator `j` to oscillator `i`. |
| `eta_i(t)` | Stochastic noise term applied to oscillator `i`. |
| `dt` | Integration timestep. |

## Kuramoto Equation

The continuous-time oscillator model is:

```text
d theta_i / dt =
omega_i + sum_j K_ij sin(theta_j - theta_i) + eta_i(t)
```

Collapse Lab implements this as stochastic Euler-Maruyama integration. Each frame advances oscillator phases by applying intrinsic frequency, pairwise coupling, and bounded stochastic perturbation over the timestep `dt`.

```text
theta_i(t + dt) =
theta_i(t) + dt * [omega_i + sum_j K_ij sin(theta_j - theta_i)] + noise_step
```

After integration, phases are wrapped into the bounded interval `[0, 2π)`.

## Clustered Frequency Initialization

The synthetic oscillator population is initialized with two frequency-centered clusters:

| Cluster | Interpretation | Mean Frequency |
| --- | --- | --- |
| `C1` | Global field cluster | `8.0 Hz` |
| `C2` | Residual self-model cluster | `12.0 Hz` |

The cluster separation is:

```text
delta_mu = 4.0 Hz
```

Each cluster receives small Gaussian variance around its mean. This preserves local diversity while maintaining a clear initial symmetry break between `C1` and `C2`.

Clustered frequencies create the initial asymmetry needed for `k = 2` metastability. Without the split, the system can collapse too directly into global synchronization; with too much separation, it can remain fragmented. The two-cluster initialization gives the topology a controlled dual-boundary regime.

## Coupling Matrix

The coupling matrix `K_ij` controls how oscillator phases influence each other.

| Identifier | Role |
| --- | --- |
| `baseCoupling` | Controls intra-cluster synchronization. |
| `crossCoupling` | Controls inter-cluster bridge formation. |

Low `crossCoupling` preserves split clusters because the two oscillator populations remain weakly connected. High `crossCoupling` strengthens inter-cluster bridges and drives collapse toward global synchronization.

In conceptual terms:

```text
if oscillator_i and oscillator_j are in the same cluster:
  K_ij = baseCoupling
else:
  K_ij = crossCoupling
```

## Sigmoidal Cross-Coupling Ramp

The inter-cluster bridge can be modeled as a sigmoidal ramp:

```text
K_cross(t) =
K_max / (1 + exp(-s(t - t_c)))
```

Where:

| Identifier | Meaning |
| --- | --- |
| `K_max` | Upper bound for cross-cluster coupling. |
| `s` | Steepness of the transition. |
| `t_c` | Critical time at the center of the ramp. |

A sigmoid is preferred over a linear ramp because it creates a long pre-transition shoulder, a sharp critical transition band, and a bounded saturation region. This better matches metastable collapse behavior: the system can hover near the boundary before rapidly forming a bridge.

## Noise Injection

`noiseLevel` controls stochastic perturbation applied during phase integration. The noise term is a stress-test input, not corruption.

Noise supports:

- stochastic perturbation of oscillator phases
- critical intermittency near the transition boundary
- metastable boundary vibration
- robustness testing for PRE_COLLAPSE classification

Near the boundary, moderate noise can reveal whether `k = 2`, `lambda2`, `CPI`, `entropy`, and `clusterBalanceRatio` remain stable under perturbation.

## Simulation Phases

### NORMAL

`NORMAL` describes weak or fragmented synchronization:

- weak or fragmented synchronization
- typically `k > 2`
- no strict metastable two-component boundary

### PRE_COLLAPSE

`PRE_COLLAPSE` describes the metastable dual-boundary state:

- `k = 2`
- high `CPI`
- low `lambda2`
- balanced dual cluster split

### COLLAPSED

`COLLAPSED` describes globally connected synchronization:

- `k = 1`
- positive `lambda2`
- globally connected synchronization

## Output Pipeline

The synthetic dynamics feed the downstream topology and visualization pipeline:

```text
Kuramoto phases
-> phaseHistory
-> PLV matrix
-> threshold graph
-> connected components
-> lambda2
-> CPI
-> tensor projection
-> UI renderers
```

The downstream layers consume phase-derived structure rather than raw oscillator internals. This keeps topology extraction and visualization decoupled from the synthetic source.

## Numerical Safety

Collapse Lab uses numerical safeguards appropriate for high-frequency browser rendering:

- `Float64Array` usage for stable numeric vectors
- bounded phase wrapping to `[0, 2π)`
- `EPSILON` padding to avoid divide-by-zero and log singularities
- capped history windows for phase and metric buffers
- no external math libraries

These constraints keep the simulation deterministic enough for replay and review while remaining lightweight enough for browser-native execution.

## Research Notes

The Kuramoto engine is a controlled synthetic test harness. It gives Collapse Lab a reproducible way to study synchronization, metastability, and topological collapse without requiring empirical input data.

The same downstream pipeline can later accept empirical EEG or CSV input without changing the PLV, graph, spectral, CPI, or tensor layers. In that mode, the synthetic Kuramoto source would be replaced by measured phase or channel data, while downstream extraction remains stable.

## Documentation Boundary

This document does not modify Kuramoto dynamics, phase detection equations, CPI formulas, entropy logic, `lambda2` extraction, replay/export behavior, tensor projection, or UI rendering. It documents the research architecture associated with the stable Collapse Lab runtime.
