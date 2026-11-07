# Stage 3 Audit — v1.1.1-api-cleanup

**Date:** 2026-11-07
**Baseline:** v1.1.1-api-cleanup (commit 4a53240)
**Auditor:** DeepSeek + local verification
**Attestation source:** `_lexicon.lookup()` (in-code, ~2,500–5,000 stems)

## Test Inputs and Results

| Input | Expected | Actual | Status |
|---|---|---|---|
| `rAjaputraH` | 1 ṣaṣṭhī-tatpuruṣa candidate | ✅ 1 candidate (0.95), 1 rejection (`rājaputra` unattested) | PASS |
| `candramukhaH` | 1–3 candidates | Depends on lexicon coverage | PARTIAL |
| `rAmasyaputraH` | 0 candidates (invalid compound) | ✅ 0 candidates, 1 rejection (`rāmāsyaputra` unattested) | PASS |
| `devamanuSyanAgAH` | 3-token itaretara-dvandva | ❌ 2-token tatpuruṣa (engine recursion stops at depth 1) | FAIL |
| `rAjendraH` | `rājan + indra` compound | ❌ 0 candidates, 1 rejection (`indra` not in lexicon) | FAIL |

## Findings

### Finding 1 — Engine does not recurse past depth 1 for multi-token compounds

- **Input:** `devamanuSyanAgAH`
- **Expected:** `deva + manuSya + nAga` (3-token itaretara-dvandva)
- **Actual:** `deva + manuSyanāgāḥ` (2-token tatpuruṣa)
- **Root cause:** `_samasa.py` recursion stops at depth 1; also possibly restricted by missing `manuSya` / `nAga` stems
- **Fix location:** `C:\aigaane-master\_samasa.py`
- **Priority:** Medium — affects only 3+ token compounds
- **Effort:** 1–2 hours (must re-run 398 existing tests)

### Finding 2 — `_lexicon.py` missing ~80% of common proper nouns

Tested stems: `indra`, `agni`, `varuṇa`, `soma`, `yama`, `kṛṣṇa`, `arjuna`, `bhīma`, `rājan`, `rāma`.
- **Attested:** `rājan`, `rāma` (2/10)
- **Missing:** 8/10 (80%)
- **Root cause:** `_lexicon.py` is 57 KB, curated for the 398 existing tests, not for general Sanskrit vocabulary
- **Fix:** Curate + add 500–1,000 proper nouns; OR wire `canon.db` (701 Gītā verses) as a secondary attestation source
- **Priority:** High — blocks any input containing proper nouns
- **Effort:** 2–4 hours (curation) or 2 hours (canon.db FTS integration)

### Finding 3 — Critic correctly rejects unattested stems

The Critic's behavior is correct in every failure case:
- Rejects `manuSyanāgāḥ` — genuinely not in `_lexicon`
- Rejects `indra` — genuinely not in `_lexicon`
- Rejects `rājaputra` (compound as atomic) — not a single lexicon entry

**The Critic is the only component fully working as designed.** Both failures surface infrastructure gaps, not Critic bugs.

## Finding 4 — canon.db is a verse corpus, not a proper-noun lexicon

- **File:** `C:\aigaane-master\frontend\public\sqlite\canon.db` (568 KB, 701 Gītā verses)
- **FTS rebuild performed:** `INSERT INTO verses_fts(verses_fts) VALUES('rebuild')`
- **Verified match counts after rebuild:** dharma (22), karma (113), yoga (51), rājan (3), deva (27), putra (6), rāma (4), **indra (0)**
- **Conclusion:** The Gītā is a philosophical corpus, not a Vedic invocation. It contains `indriya` (senses), not `indra` (the deva).
- **Implication:** `canon.db` cannot attest `indra`. It **IS** usable for `/corpus/search` (verse search) and as supplementary attestation for words that actually appear (dharma, karma, yoga, deva, putra, rāma).
- **Next steps:** Wire `/corpus/search`; move proper-noun attestation to lexicon expansion (E2) or dedicated Kosha DB (A1b).

## On the "1.5M Kosha" claim

- **`kosha_1.5m.db` does not exist on disk.** Discovery via `Get-ChildItem -Recurse -Filter "*.db"` found only `C:\aigaane-master\frontend\public\sqlite\canon.db` (568 KB, 701 Gītā verses).
- **The live `aigaane.in` production service** may use a compiled 1.5M-entry lexicon (tries, packed indices, FTS5) deployed to Cloud Run. **The local repo does not.**
- **Local attestation source:** `_lexicon.lookup()` with approximately 2,500–5,000 stems.
- **The "1.5M Kosha" is a target, not a fact.**

## Current Honest Scope (v1.1.1)

**Verified working:**
- 2-token tatpuruṣa compounds with attested stems
- Compound inversions where the engine returns full-pada splits
- Rejection of invalid stems with `UNATTESTED_STEM` reason code
- Dual-mount API (`/api/v1` and `/api/v3`)
- Version-truthful health probes

**Not verified:**
- 3+ token compounds (engine recursion bug)
- Inputs containing proper nouns outside `_lexicon.py`
- Anything requiring the full 1.5M Kosha (not on local disk)

## v1.2.0 Priorities (from this audit)

1. **[A1a]** Write this document — DONE
2. **[A4]** Write JSON schemas reflecting real scope — DONE in v1.2.0
3. **[A3]** Seed 3 verified golden cases — DONE in v1.2.0
4. **[C1]** Expand corpus to 72 cases (4–6 hrs, needs scholar review)
5. **[A1c]** Wire `canon.db` FTS as secondary attestation (2 hrs)
6. **[Engine]** Fix `_samasa.py` recursion for 3+ tokens (1–2 hrs)
7. **[A1b]** Build real `kosha_1.5m.db` (4–8 hrs, data engineering)

## Invariants Preserved

- ✅ Zero LLM in the deterministic path
- ✅ Fail-closed Critic design
- ✅ Dual-mount routing (drift structurally impossible)
- ✅ Git ladder provides 1-command rollback from any tag
- ✅ Version strings match git tags