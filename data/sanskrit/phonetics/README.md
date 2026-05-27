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

## Paninian Symbolic Compression Layer

Status: READ_ONLY_DETERMINISTIC

Components:
- symbolic-compression-map.js
- symbolic-compression-engine.js

Capabilities:
- deterministic symbolic class expansion
- pratyāhāra-backed class inspection
- read-only UI preview
- safe structural grouping

Safety:
- no authoritative Paninian derivation claim
- no grammatical correctness guarantee
- no canonical mutation
- structural inspection only

## Phonetic Topology Visualization Layer

Status: READ_ONLY_DETERMINISTIC

Components:
- phonetic-topology-map.js
- phonetic-topology-engine.js

Capabilities:
- articulation topology nodes
- deterministic adjacency edges
- active articulation highlighting by input
- read-only UI preview

Safety:
- no pronunciation correctness claim
- no chanting validation
- no audio validation
- structural visualization only
- no canonical mutation

## Derivation Graph Overlay Layer

Status: READ_ONLY_DETERMINISTIC

Components:
- derivation-graph-map.js
- derivation-graph-engine.js
- derivation-overlay-renderer.js

Capabilities:
- symbolic overlay inspection
- topology overlay inspection
- sandhi overlay inspection
- deterministic graph preview
- read-only graph visualization

Safety:
- no authoritative derivation correctness claim
- no canonical mutation
- no automated grammar generation
- structural overlay inspection only

## Dhātu Semantic Graph Layer

Status: READ_ONLY_DETERMINISTIC_PLACEHOLDER

Components:
- dhatu-semantic-map.js
- dhatu-semantic-engine.js
- dhatu-semantic-renderer.js

Capabilities:
- deterministic dhātu semantic node preview
- semantic cluster inspection
- semantic edge inspection
- derivation overlay summary integration
- read-only UI panel

Safety:
- no authoritative semantic correctness claim
- no grammatical derivation correctness claim
- no canonical mutation
- placeholder-safe semantic metadata only
