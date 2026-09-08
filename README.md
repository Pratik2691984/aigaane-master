# aigaane-master

Aigaane V3 PRO — Vedic Resonance Engine (static SPA + FastAPI/Mangum).

**Status:** historical deploy. Last feature push 19 Jun 2026.
Current matrix / Malkauns work lives in [`aigaane-vedic-matrix`](https://github.com/Pratik2691984/aigaane-vedic-matrix).
Do not extend raga tables here.

- Live: https://aigaane-master.vercel.app
- Ruleset: Protect main (no delete, no force-push; Admin bypass)
- Sanskrit corpus: Phase 10/11 **read-only**. Canonical writes are locked.

## Sanskrit workflow

Phase 10 = promotion governance (preview only).
Phase 11 = real corpus load → normalize → validate → dedupe → certify → index → derivation hooks.

Hard barrier:

```
canonicalWrite   = false
promotionAllowed = false
importAllowed    = false
previewOnly      = true
readOnly         = true
```

Targets (metadata, not proof of load): Dhātu 1400 / Sūtra 400 / Stotra 200 = 2000.
Discovered inventory in `corpus/manifest.json` is **45**. That is INCOMPLETE — do not treat the target as loaded count.

See `docs/PHASE-10-11-SANSKRIT-WORKFLOW.md` and `shared/sanskritCorpusGovernance.js`.

## Run locally

```
pip install -r requirements.txt
# Windows: start.bat / start_api.bat
```

API is in-memory on Vercel. Do not expect kernel history to persist across invocations.
