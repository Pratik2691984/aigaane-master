# Neuroscience Mapping

## Overview

Collapse Lab is a computational graph-topology model, not a validated neuroscience biomarker. Its biological interpretation layer should be read as a conservative hypothesis map between synthetic topology dynamics and possible neural network observables.

The runtime phase labels describe graph and synchronization structure. They do not diagnose brain states, clinical conditions, enlightenment, selfhood, awareness, or consciousness.

## Synthetic vs Biological Layer

The current Kuramoto engine is a controlled surrogate used to generate phase-coupled neural-like signals. It provides reproducible input for testing topology extraction, spectral connectivity, CPI behavior, tensor projection, replay, and visualization.

Future empirical EEG or fMRI data can replace the synthetic source while preserving downstream layers:

- PLV extraction
- graph construction
- `lambda2` spectral connectivity
- `CPI` or boundary-dissolution scoring
- tensor projection
- replay and export review

In this architecture, the input source can change without requiring the graph, spectral, `syncRatio`, `clusterBalanceRatio`, or tensor layers to be rewritten.

## Recommended EEG Pipeline

Primary research-grade path:

```text
EEG
-> ICA/artifact cleaning
-> source reconstruction
-> ROI atlas
-> source-space PLV
-> graph metrics
```

Fallback screening path:

```text
EEG
-> ICA/artifact cleaning
-> surface Laplacian
-> sensor-space PLV
-> graph metrics
```

Source-space reconstruction is preferred when making anatomical interpretations because it maps signals into estimated cortical or regional sources before graph construction. This helps reduce linear instantaneous mixing, but it does not eliminate leakage or all reconstruction artifacts.

Surface Laplacian filtering is acceptable for quick validation or screening when source reconstruction is not available. It can improve local sensor contrast, but it does not resolve precise anatomical localization.

Both approaches help reduce volume-conduction artifacts, but neither eliminates all confounds. Any biological claim should be treated as provisional until tested against appropriate controls and independent datasets.

## ROI / Graph Mapping

Collapse Lab graph terms can be mapped cautiously onto EEG or source-space data:

| Collapse Lab Term | Conservative Biological Mapping |
| --- | --- |
| graph nodes | Electrodes or source-space ROIs. |
| graph edges | PLV or phase synchrony between nodes. |
| `k` | Connected components in the thresholded synchrony graph. |
| `lambda2` | Spectral connectivity of the graph. |
| `CPI` | Boundary dissolution index derived from graph and synchrony features. |
| `syncRatio` | Aggregate phase synchronization ratio. |
| `clusterBalanceRatio` | Balance between two dominant network components. |

The mapping is structural and computational. It should not be read as a direct claim about subjective experience.

## C1 and C2 Interpretation

`C1` serves as a proxy for global sensory/frontoparietal integration.

`C2` serves as a proxy for residual self-referential or DMN-like dynamics.

This language is intentionally cautious. `C2` does not literally equal the Default Mode Network, ego, selfhood, or consciousness. It is a model component that may be compared with self-referential network hypotheses in future empirical work.

## DMN Caveat

The Default Mode Network may serve as a useful interpretive proxy for self-referential processing, but Collapse Lab does not claim that DMN activity is identical to selfhood, awareness, or consciousness.

## Phase Interpretation

### NORMAL

`NORMAL` may correspond to fragmented or distributed network coordination.

### PRE_COLLAPSE

`PRE_COLLAPSE` may correspond to a metastable two-component topology with high cross-boundary synchronization pressure.

Useful machine-readable indicators include:

- `k = 2`
- low `lambda2`
- high `syncRatio`
- balanced `clusterBalanceRatio`

### PRE_COLLAPSE Detection Constraints

The runtime classifies a state as PRE_COLLAPSE only when all invariant conditions are satisfied simultaneously:

- `k === 2`
- `lambda2 <= 1e-4`
- `CPI >= 0.85`
- `syncRatio >= 0.9`
- `entropy <= 0.25`
- `clusterBalanceRatio >= 0.35`

These constraints prevent false-positive metastable classifications caused by degenerate singleton residual clusters or noisy synchronization leakage.

### COLLAPSED

`COLLAPSED` may correspond to a globally connected synchronized manifold.

This should not be described as enlightenment, diagnosis, conscious unity, or proof of a specific biological mechanism.

## Empirical Observables

Possible empirical observables for future validation include:

- EEG PLV
- source-space phase-locking
- fMRI functional connectivity
- modularity
- `lambda2`
- component count `k`

These observables should be analyzed with appropriate controls, subject-level statistics, and replication procedures before any biological interpretation is strengthened.

## Volume Conduction Controls

Recommended controls include:

- artifact rejection
- ICA where appropriate
- surface Laplacian for sensor-space screening
- source reconstruction for anatomical claims
- comparison of PLV with less volume-conduction-sensitive metrics later, such as imaginary coherence or phase lag index

Volume conduction is a major confound in EEG phase-synchrony analysis. Controls reduce risk but do not remove the need for cautious interpretation.

## Research Limitations

Collapse Lab currently operates as a topology-analysis framework rather than a validated neurophysiological inference engine.

Collapse Lab currently makes:

- no clinical claims
- no diagnostic claims
- no validated biomarker claims
- no claim that Collapse Lab proves consciousness mechanisms

All biological mappings are hypotheses requiring empirical validation. The current runtime is best understood as a computational model for topology, synchronization, and phase-transition research.

## Future Work

Future documentation and implementation work may include:

- real EEG CSV importer
- source-space ROI mapping
- DMN/frontoparietal templates
- trial-level replay
- subject-level export schema

## Documentation Boundary

This document does not modify runtime simulation physics, CPI formulas, entropy logic, `lambda2` extraction, `syncRatio`, `clusterBalanceRatio`, replay/export systems, tensor projection, or UI rendering.
