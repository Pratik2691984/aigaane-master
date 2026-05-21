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

## Graph Neighbor Endpoint

`GET /api/dhatu/semantic/neighbors`

Supported query parameters:

- `nodeId`
- `depth`
- `relationType`

Examples:

```powershell
/api/dhatu/semantic/neighbors?nodeId=01.0005
/api/dhatu/semantic/neighbors?nodeId=motion&depth=2
/api/dhatu/semantic/neighbors?nodeId=guidance&relationType=guides
/api/dhatu/semantic/neighbors
```

Response shape:

```json
{
  "schemaVersion": "1.0.0",
  "generatedBy": "api/kernel_api.py:/api/dhatu/semantic/neighbors",
  "query": {
    "nodeId": "01.0005",
    "depth": 1,
    "relationType": null
  },
  "nodeId": "01.0005",
  "depth": 1,
  "relationType": null,
  "neighborCount": 1,
  "neighbors": [
    {
      "nodeType": "semantic_cluster",
      "nodeId": "motion",
      "depth": 1,
      "viaEdgeIds": ["edge.semantic.0001"],
      "relationTypes": ["associated_with"]
    }
  ],
  "traversedEdgeIds": ["edge.semantic.0001"]
}
```

Empty graph-neighbor requests return `error.code` as `empty_semantic_graph_query` with an empty `neighbors` array.

## Graph And Neighbor Queries

Semantic graph edges live at `edges/semantic_edges.v1.json`. They are local semantic model placeholders and do not make exact grammatical or Paninian derivation claims.

Validate the graph:

```powershell
python scripts/validate_dhatu_semantic_graph.py
```

Query neighbors:

```powershell
python scripts/query_dhatu_semantic_neighbors.py --node-id 01.0005 --json
python scripts/query_dhatu_semantic_neighbors.py --node-id motion --depth 2 --json
python scripts/query_dhatu_semantic_neighbors.py --node-id guidance --relation-type guides --json
```

Neighbor responses include `schemaVersion`, `generatedBy`, `nodeId`, `depth`, `relationType`, `neighborCount`, `neighbors`, and `traversedEdgeIds`.

## Graph Reproducible Examples

- `examples/graph/neighbor_01_0005.response.v1.json`
- `examples/graph/neighbor_motion_depth2.response.v1.json`
- `examples/graph/neighbor_guidance_guides.response.v1.json`
- `examples/graph/neighbor_empty_query.response.v1.json`

Regenerate them with:

```powershell
python scripts/export_dhatu_semantic_graph_examples.py
```

Graph edges are foundation-placeholder semantic links only. They do not make exact Paninian derivation claims.

## Graph Traversal Endpoint

`GET /api/dhatu/semantic/traverse`

Supported query parameters:

- `nodeId`
- `maxDepth`
- `relationType`

Examples:

```powershell
/api/dhatu/semantic/traverse?nodeId=motion&maxDepth=2
/api/dhatu/semantic/traverse?nodeId=01.0005&maxDepth=2
/api/dhatu/semantic/traverse?nodeId=guidance&relationType=guides
```

Response shape:

```json
{
  "schemaVersion": "1.0.0",
  "generatedBy": "api/kernel_api.py:/api/dhatu/semantic/traverse",
  "query": {
    "nodeId": "01.0005",
    "maxDepth": 2,
    "relationType": null
  },
  "nodeId": "01.0005",
  "maxDepth": 2,
  "relationType": null,
  "traversalStatus": "OK",
  "visitedNodeCount": 4,
  "pathCount": 3,
  "paths": [
    {
      "pathId": "path.semantic.0001",
      "depth": 1,
      "nodes": [
        {"nodeType": "dhatu", "nodeId": "01.0005"},
        {"nodeType": "semantic_cluster", "nodeId": "motion"}
      ],
      "edges": ["edge.semantic.0001"],
      "terminalNodeId": "motion",
      "relationTypes": ["associated_with"]
    }
  ],
  "traversedEdgeIds": ["edge.semantic.0001", "edge.semantic.0004", "edge.semantic.0005"],
  "errorCode": null
}
```

Empty traversal requests return `traversalStatus` as `EMPTY_QUERY` and `errorCode` as `empty_semantic_traversal_query`. Unknown nodes return `traversalStatus` as `NODE_NOT_FOUND` and `errorCode` as `semantic_graph_node_not_found`.

Traversal examples:

- `examples/graph/traversal_motion_depth2.response.v1.json`
- `examples/graph/traversal_01_0005_depth2.response.v1.json`
- `examples/graph/traversal_guidance_guides.response.v1.json`
- `examples/graph/traversal_empty_query.response.v1.json`
- `examples/graph/traversal_unknown_node.response.v1.json`

Regenerate them with:

```powershell
python scripts/export_dhatu_semantic_traversal_examples.py
```

Traversal edges are foundation-placeholder semantic links and do not claim exact Paninian derivation.

## Safety

The semantic layer is sidecar-only. Querying, validating, documenting, and exporting examples must not mutate the canonical registry, promotion audit files, v50 archives, or approval fixtures.
