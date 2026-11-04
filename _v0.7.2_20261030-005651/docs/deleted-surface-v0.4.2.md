# Deleted surface, v0.4.2-cleanup (`aa51ff7`)

The following modules were removed from `api/engines/` and `engines/` and never replaced
in the consolidated tree. Tests that referenced them were archived to
`scripts/migrations/archive/api-tests-v0.4.2/`.

## Deleted engine modules (34)

- ambiguity.py
- ambiguity_resolver.py
- consonant_sandhi.py
- corpus_pipeline.py
- cross_engine_linker.py
- derivation_graph_exporter.py
- derivation_replay_exporter.py
- derivation_session.py
- dhatu_canonical_preference_resolver.py
- dhatu_editorial_resolution.py
- dhatu_registry.py
- dhatu_semantic_overlay.py
- dhatu_semantic_query.py
- dhatu_source_attribution.py
- dhatu_variant_readings.py
- lexical_governance.py
- lexical_registry.py
- morphology.py
- prakriya_referee.py
- provenance_scoring_engine.py
- replay_analytics_engine.py
- replay_diff_engine.py
- sandhi.py
- scholarly_export_engine.py
- semantic_query_engine.py
- semantic_rule_attribution_engine.py
- session_storage.py
- sutra_linker.py
- sutra_registry.py
- sutra_trace_canonicalizer.py
- trace_graph.py
- visarga_sandhi.py
- vyakarana.py

## Deleted debug routes

- /api/v3/debug/ambiguity-demo
- /api/v3/debug/lexicon/samples
- /api/v3/debug/lexicon/sources
- /api/v3/debug/lexicon/validate
- /api/v3/debug/trace/demo
- /api/v3/debug/trace/link
- /api/v3/debug/sutras/samples
- /api/v3/debug/sutras/sources
- /api/v3/debug/sutras/validate
- /api/v3/morphology/verb/conjugate  (never existed; subanta only)
- /api/v3/analyze  (removed; chandas now at /api/v3/chandas)

## Routes that still exist under different paths

- Corpus search is POST /api/v3/corpus/search
- Morphology subanta is POST /api/v3/morphology/noun/inflect
- Changelog is GET /api/v3/changelog
