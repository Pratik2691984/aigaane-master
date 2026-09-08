# Phase 10 / 11 — Sanskrit corpus architecture

Governed, read-only pipeline. Not a linear load → write path.
Canonical mutation stays blocked for the entire documented workflow.

## Two branches

| Phase | Question |
|---|---|
| 10 | Can this corpus safely reach promotion *review*? |
| 11 | Can the real corpus be loaded, normalized, validated, deduplicated, certified, indexed, and exposed — without mutating canonical data? |

The Corpus Browser is the bridge from the Phase 11 index to Sandhi / Morphology / Prakriya / Chandas. It is not itself those engines.

## Phase 10 — promotion governance

RAW / STAGED → Reservation (quota) → Allocation (type quotas) → Capacity (max 2000) → Window (250 / window) → Schedule → Timeline → Simulation (preview only) → Forecast → Admission → Promotion Readiness → Advisory → Approval → Certification → Canonical Preview → **WRITE BLOCKED**

Readiness requires: admission ready, accepted records, zero rejected records, locked writes. Still no canonical write.

## Phase 11 — real corpus load

11A Source registry → 11B Raw landing → 11C Normalize → 11D Validate → 11E Dedupe → 11F Enrich → 11G Certify → 11H Canonical preview → 11I Index → 11L Derivation hooks → Dhātu / Sūtra / Stotra browsers → Search → Trace → Preview → language engines.

Derivation hooks (browser supplies recordId / type / text; engines stay separate):

- `/api/v3/sandhi`
- `/api/v3/morphology/verb/conjugate`
- `/api/v3/morphology/noun/inflect`
- Prakriya
- Chandas

Local fallback when backend is unavailable must not flip write flags.

## Inventory vs target

| | Target | Discovered (manifest) |
|---|---:|---:|
| Dhātu | 1400 | 37 |
| Sūtra | 400 | 5 |
| Stotra | 200 | 3 |
| Total | 2000 | 45 |

If discovered < target → **BLOCK / INCOMPLETE**.
Do not treat metadata targets as proof that 2000 records loaded.
A documented pipeline figure of 1341 unique after dedupe is a *design report*, not this repo's on-disk inventory.

## Safety barrier

```
USER / UI
  → read / preview pipeline
  → governance / validation
  → canonical preview
  → HARD BARRIER
       canonicalWrite   = false
       promotionAllowed = false
       importAllowed    = false
```

Source of flags: `shared/sanskritCorpusGovernance.js` and `corpus/manifest.json`.

## Current tab vs target

`ui/tabs/sanskrit/` is still the 49-phoneme Mātṛkā grid. Corpus browser sections (Dhātu, Sūtra, Stotra, Search, Trace, Preview) are the next UI checkpoint, not present on main as of this commit.
