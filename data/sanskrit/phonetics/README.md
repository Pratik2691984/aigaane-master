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