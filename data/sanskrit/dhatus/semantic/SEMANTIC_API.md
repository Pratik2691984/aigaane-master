# Dhatu Semantic API

The semantic query API exposes the canonical dhatu sidecar layer without changing `data/sanskrit/dhatus/index.json`.

## Endpoint

`GET /api/dhatu/semantic/search`

Supported query parameters:

- `dhatuId`
- `root`
- `iast`
- `cluster`
- `gloss`
- `action`

## CLI Examples

```powershell
python scripts/query_dhatu_semantics.py --cluster motion --json
python scripts/query_dhatu_semantics.py --action guidance --json
python scripts/query_dhatu_semantics.py --gloss stand --json
python scripts/query_dhatu_semantics.py --dhatu-id 01.0005 --json
```

## API Helper Examples

```python
from api.dhatu_semantic_query import query_payload, query_semantics
from api.kernel_api import build_dhatu_semantic_search_response

motion = query_payload(cluster="motion")
guidance = query_semantics(action="guidance")
api_payload = build_dhatu_semantic_search_response(gloss="stand")
```

## Response Shape

```json
{
  "schemaVersion": "1.0.0",
  "generatedBy": "api/kernel_api.py:/api/dhatu/semantic/search",
  "query": {
    "dhatuId": null,
    "root": null,
    "iast": null,
    "cluster": "motion",
    "gloss": null,
    "action": null
  },
  "resultCount": 1,
  "results": [
    {
      "dhatuId": "01.0005",
      "root": "गम्",
      "iast": "gam",
      "gloss": "to go",
      "semanticClusters": [],
      "actionVector": {},
      "glossTaxonomy": [],
      "paniniReferences": [],
      "derivationLinks": [],
      "rankScore": 75,
      "matchReasons": ["cluster"]
    }
  ]
}
```

Each result includes `dhatuId`, `root`, `iast`, `gloss`, `semanticClusters`, `actionVector`, `glossTaxonomy`, `paniniReferences`, `derivationLinks`, `rankScore`, and `matchReasons`.

## Reproducible Examples

- `examples/search_by_cluster_motion.response.v1.json`
- `examples/search_by_action_guidance.response.v1.json`
- `examples/search_by_gloss_stand.response.v1.json`
- `examples/search_empty_query.response.v1.json`

Regenerate them with:

```powershell
python scripts/export_dhatu_semantic_examples.py
```

## Safety

The semantic layer is sidecar-only. Querying, validating, documenting, and exporting examples must not mutate the canonical registry, promotion audit files, v50 archives, or approval fixtures.
