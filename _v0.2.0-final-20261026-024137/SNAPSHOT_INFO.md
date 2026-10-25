
## Corpus coverage

| Category | Cases | Status |
|---|---|---|
| A — Simple Sandhi | 15 | PASS |
| B — Ambiguity | 15 | PASS |
| C — Samasa | 15 | PASS |
| D — Dhatu/Gana (tinanta) | 10 | PASS |
| E — Indeclinables | 10 | PASS |
| F — Nyaya Syllogism | 10 | PASS |
| G — Chhandas Prosody | 10 | PASS |
| H — Cross-Domain | 10 | PASS |
| Meta tests | 9 | PASS |
| **Total** | **104** | **PASS** |

## Engine modules

- `engine.py` — orchestrator (parse + route)
- `_lexicon.py` — pada/stem lookup
- `_sandhi.py` — exact sandhi split table
- `_samasa.py` — recursive compound tree builder
- `_ambiguity.py` — alternate parse generator
- `_f_parses.py` — Category F parse structures
- `_nyaya.py` — deterministic 5-step syllogism engine
- `_chhandas.py` — Category G prosody table
- `_h_cross.py` — Category H cross-domain mapping

## Schemas (3-file modular)

- `schemas/sanskrit_contract.json` — main document contract
- `schemas/samasa_node.json` — recursive compound node, self-$ref
- `schemas/router_policy.json` — routing + RoutingDecision + NyayaSyllogism

## Rules for future changes

1. **No change without a failing test.** Any modification to engine, modules, schemas, or corpus must begin with a new failing test in `tests/contract/test_contract.py`.

2. **The corpus is canonical.** If engine and corpus disagree, the corpus is right.

3. **Branch order in parse() is load-bearing.** Ambiguity runs before sandhi, sandhi before samasa, samasa before single-pada, single-pada before F-parse, F-parse before Nyaya. Reordering breaks the rājaputraḥ overlap (B14 ↔ C01).

4. **Re-verify after any file save.** `python -m pytest ...` must show 104 passed before commit.

## Snapshot metadata

- Snapshot folder: `_v0.2.0-final-20261026-024137`
- Created: 2026-10-26 02:41:37
- Test result at creation: **104 passed in 0.38s**
- Corpus: 95 cases (A15 + B15 + C15 + D10 + E10 + F10 + G10 + H10), zero missing, zero duplicates
- Schema versions: contract 0.2.0, samasa_node 0.2.0, router_policy 0.2.0