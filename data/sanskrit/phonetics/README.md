# Śikṣā Phonetic Classification Layer

## Status
READ_ONLY_DETERMINISTIC

## Components

### phoneme-map.js
Static deterministic phonetic metadata registry.

### shiksha-engine.js
Read-only Śikṣā character classifier.

Capabilities:
- deterministic character classification
- articulation grouping
- phonetic group grouping
- unknown symbol isolation

Non-goals:
- no Vedic accent validation
- no audio correctness validation
- no chanting verification
- no pronunciation guarantee

## UI Integration

Integrated into:
- ui/tabs/sanskrit/controller.js
- ui/tabs/sanskrit/view.html
- ui/tabs/sanskrit/style.css

## Safety Model

The Śikṣā layer is:
- client-side only
- deterministic only
- read-only
- non-canonical
- non-authoritative
- isolated from canonical dhātu writes

## Māheśvara-Sūtra / Pratyāhāra Layer

Status: READ_ONLY_DETERMINISTIC

Components:
- `maheshvara-sutras.js` — static 14-sūtra structural registry
- `shiva-sutra-map.js` — sound-to-sūtra lookup helpers
- `pratyahara-engine.js` — deterministic pratyāhāra expansion helper

Current UI examples:
- `अच्`
- `हल्`
- `इक्`

Safety:
- structural expansion only
- no full grammar derivation claim
- no authoritative Pāṇinian correctness guarantee
- no canonical mutation

## Sandhi Transition Inspector

Status: READ_ONLY_DETERMINISTIC

Components:
- sandhi-rules.js
- sandhi-transition-map.js
- sandhi-engine.js

Capabilities:
- deterministic adjacent-token boundary inspection
- limited transition matching
- matched/unmatched boundary summary
- read-only UI panel

Safety:
- no authoritative grammar correctness claim
- no full Paninian derivation claim
- no canonical mutation
- structural inspection only

## Transliteration + IPA Inspection Layer

Status: READ_ONLY_DETERMINISTIC

Components:
- transliteration-map.js
- ipa-map.js
- transliteration-engine.js

Capabilities:
- Devanāgarī to IAST inspection
- Devanāgarī to approximate IPA inspection
- unknown character isolation
- deterministic UI preview

Safety:
- no pronunciation correctness claim
- no audio validation
- no chanting validation
- structural inspection only
- no canonical mutation
