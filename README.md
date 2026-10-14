# Aigaane — Deterministic Pāṇinian Sanskrit Engine

Live: https://aigaane.in
Repo: https://github.com/Pratik2691984/aigaane-master

A Pāṇinian Sanskrit engine with rule-traceable derivation, served as a static site plus a FastAPI backend on Google Cloud Run.

---

## Architecture

Firebase Hosting serves the static UI from `public/`. Requests to `/api/**` are rewritten to the Cloud Run service `aigaane-engine` via `firebase.json`.

- Firebase project: `gen-lang-client-0991678000`
- Firebase site: `aigaane-sanctuary`
- Cloud Run service: `aigaane-engine`
- Region: `asia-south1`

Domains:
- `aigaane.in` — custom domain, connected, SSL active
- `www.aigaane.in` — GoDaddy forward to `https://aigaane.in`
- `aigaane-sanctuary.web.app` — Firebase default

---

## Deployed Engines

| Layer | Endpoint | Backend |
|---|---|---|
| Morphology — Subanta | `POST /api/v3/morphology/noun/inflect` | `engines/morphology/subanta.py` |
| Morphology — Tinanta | `POST /api/v3/morphology/verb/conjugate` | `engines/morphology/tinanta_engine.py` |
| Sandhi — Joiner | `POST /api/v3/sandhi` | `engines/phonology/sandhi.py` |
| Sandhi — Splitter | `POST /api/v3/sandhi/split` | `engines/phonology/sandhi_splitter.py` |
| Chandas — Scansion | `POST /api/v3/chandas/scan` | `engines/chandas/scansion.py` |
| Chandas — Anustubh | `POST /api/v3/chandas/anustubh` | `engines/chandas/anustubh.py` |
| Chandas — Trishtubh | `POST /api/v3/chandas/trishtubh` | `engines/chandas/trishtubh.py` |
| Chandas — Jagati | `POST /api/v3/chandas/jagati` | `engines/chandas/jagati.py` |
| Chandas — Vrtta | `POST /api/v3/chandas/vrtta` | `engines/chandas/vidyut_chandas.py` |
| Lexicon — Lookup | `GET /api/v3/lexicon/lookup?q=...` | `engines/lexicon/vidyut_kosha.py` |
| Lexicon — Exists | `GET /api/v3/lexicon/exists?q=...` | same |
| Lexicon — Stats | `GET /api/v3/lexicon/stats` | same |
| Corpus | `POST /api/v3/corpus/search` | `routers/corpus.py` |
| Changelog | `GET /api/v3/changelog` | `routers/changelog.py` |

---

## Sanskrit Engine Coverage

| Blueprint Layer | Coverage | Implementation |
|---|---|---|
| Phonetics / Transliteration | ~90% | `vidyut.lipi` (47 scripts) |
| Sandhi | ~75% | Vowel join + consonant/visarga split |
| Morphology | ~75% | Subanta (24 forms) + Tinanta (10 ganas x 10 lakaras) |
| Prosody | ~85% | Scansion + 4 validators + 145-vrtta classifier |
| Lexicon | live | 1.5M Kosha entries, 45k dhatus |
| Ashtadhyayi engine | ~15% | via Vidyut prakriya |
| Karaka parser | not started | — |

---

## Write Audit Pipeline

Every canonical write is gated by an environment flag and recorded with before/after SHA-256 hashes.

Files:
- `scripts/immutability.py` — `unchanged`, `authorized_write`, `audited_write`
- `scripts/audit_reconcile.py` — verifies the log against current file state
- `data/sanskrit/ingestion/write_audit.jsonl` — runtime log (untracked)

Gate: requires both `AIGAANE_ENABLE_CANONICAL_DHATU_WRITE=1` and `AIGAANE_ALLOW_TEST_CANONICAL_WRITE=1`.

Verify:

```powershell
python scripts\audit_reconcile.py
# Expected: clean: 12 paths match their last logged hashes