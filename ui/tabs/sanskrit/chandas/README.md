# Chandas Prosody Inspection

Status: READ_ONLY_DETERMINISTIC_OVERLAY

This layer provides deterministic Chandas-oriented prosody inspection from explicit phonetic text. It is not canonical scansion, does not infer poetic intent, and does not claim authoritative metre correctness.

## Laghu/Guru Classification

- long vowel -> guru
- short vowel followed by consonant cluster -> guru
- anusvāra after vowel -> guru
- visarga after vowel -> guru
- otherwise short open syllable -> laghu

## Mātrā Counting

Laghu counts as one mātrā. Guru counts as two mātrā. Totals are computed directly from deterministic syllable weights.

## Gaṇa Grouping

Complete triples of syllables are grouped against the deterministic gaṇa registry. Incomplete trailing syllables remain unresolved candidates.

## Pāda and Metre Limits

Eight-syllable windows are shown as structural pāda candidates. Metre candidates require explicit deterministic pattern matches; the layer never guesses canonical metre.

## Linkage

The engine accepts phonetic analysis, sandhi transitions, symbolic compression, phonetic topology, morphology transitions, Sandarbha overlays, and derivation graphs as read-only context. It does not mutate those inputs.

## Runtime Isolation

- no canonical mutation
- no probabilistic metre detection
- no hidden poetic intent inference
- no unrestricted semantic interpretation
- no runtime architecture changes
- read-only DOM rendering
