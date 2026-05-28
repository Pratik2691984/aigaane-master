# Deterministic Sandhi Execution Core

This module is a read-only execution preview layer for the Sanskrit tab. It supports a small, explicit sandhi rule map for deterministic inspection and rendering. It does not perform probabilistic NLP, hidden grammatical inference, or authoritative grammatical reconstruction.

## Scope

Supported classes:

- Vowel sandhi: `a+a`, `a+i`, `a+ī`, `a+u`, `a+ū`, `a+ṛ`, `a+e`, `a+o`
- Visarga sandhi: `aḥ+a`, `aḥ+i`
- Consonant sandhi: `t+t`, `n+d`, `m+p`

Each rule carries an id, category, boundary pair, result, placeholder reference, priority, reversibility flag, notes, deterministic confidence, and display color.

## Rule Ordering

Rules are selected only by deterministic priority order. If priorities tie, ids provide a stable secondary sort. The engine does not resolve ambiguity through context, grammar guessing, frequency, or probability.

## Reverse Preview

Reverse preview entries are structural metadata only. They show which original boundary produced a transformed boundary in this execution pass. They are not canonical reconstructions and must not be treated as grammatical proof.

## Trace Rendering

`renderSandhiExecution(containerOrId, execution)` renders diagnostics, matched transitions, unmatched transitions, trace timeline, reverse preview entries, and rule category summaries. Rendering is read-only and does not mutate the execution object.

## Runtime Isolation

`executeSandhi(input)` accepts partial input safely, clones token text into local arrays, and never mutates source text, token objects, canonical registries, or backend state. Identical input produces identical output.
