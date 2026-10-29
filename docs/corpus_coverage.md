# Aigaane Corpus Generator Coverage Report (v0.6.4)

## Executive Summary
This document records the empirical firing and branching status of the algorithmic Paninian sandhi inverter (_sandhi_gen.py) against the 106 golden corpus cases (corpus/golden_corpus_manifest.json).

### Metrics Summary
Total Corpus Cases: 106
Generator Active (Single Split, fires_1): 21 cases
Generator Active (Multi-Candidate, fires_2plus): 1 case (A03 himālayaḥ - spelling variant)
Legacy Fallback Path (fallback): 84 cases
Category A Native Resolution Rate: 13/15 active in generator (86.7%), 1 intentional fallback (A05 vāgīśaḥ, Jastva pending morphological boundaries).

---

## Firing Taxonomy

### 1. Active Generator Categories
* Category A (Simple Sandhi): Directly resolved via algorithmic rule inversion for Savarna-dirgha, Guna, Yan (including Yan-r), Scutva, and Visarga-o.
* Category I (Transliteration Parallels): Native resolution across multi-script surfaces (rāmāpi, nāsti, etc.).

### 2. Fallback Path Intentionality
The 84 fallback cases cleanly route through legacy deterministic components:
* Category C (Samasa Compounds): Handled by the recursive compound tree builder (_samasa.py).
* Category D & E (Dhatupatha / Subanta Morphology): Handled by generative inflection tables in _lexicon.py.
* Category B (Curated Ambiguities): Handled by static prioritized tables in _ambiguity.py pending generative rule competition.
* Category J (Chhandas Prosody): Handled by syllabic meter evaluation (_chhandas.py).

---

## Architectural Decision Record: Deferred Ambiguity Injection
Dynamic ambiguity injection via ambiguous_parses is intentionally deferred. Rule intersection across current disjoint sutra families yields a branching factor of 1 for 99% of inputs. Dynamic ambiguity injection will only be introduced once overlapping rule families (e.g. Visarga vs. Purvarupa vs. Yan homophonic cuts) are algorithmically modeled.

## Milestone v0.7.1 Truth-Audit Footprint

### Dhātupāṭha Coverage
- **Total Roots Registered**: 15 canonical roots across classical gaṇas 1, 2, 3, 6, 8, 9, 10.
- **Root Attribution Invariant**: 100% of registered roots have at least one verified inflected surface test in `test_lexicon_coverage.py`.
- **Defective Root Fencing**: Root `as` (2P) strictly excludes ārdhadhātuka borrowed stems (*bhaviṣya*, *babhūv*), enforcing Pāṇini 2.4.52 (*aster bhūḥ*).
- **Liṭ Ākārānta Rule**: Enforces Pāṇini 3.4.82 (*āto ṇala auḥ*) for diphthong perfect singulars (`dadau`).

### Verified Lakāra Forms
- **Laṭ**: *ekavacana*, *dvivacana*, *bahuvacana* across thematic and athematic present bases.
- **Laṅ**: Secondary endings with *aṭ-āgama* (6.4.71) differentiated by pada (`_LAN_PARASMAI`, `_LAN_ATMANE`).
- **Lṛṭ**: Thematic future stem resolution via `stem_fut` (3.3.133).
- **Liṭ**: Reduplicated base stem mappings (*abhyāsa*, 3.2.115 & 6.1.8) covering *ṇal*, *atus*, *us*, *eś*, and *irec*.
