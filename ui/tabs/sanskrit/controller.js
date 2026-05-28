import { buildChandasProsodyOverlay } from "./chandas/chandas-prosody-engine.js";
import { renderChandasProsodyOverlay } from "./chandas/chandas-prosody-renderer.js";
import { inspectDerivationGraph } from "./derivation/derivation-graph-engine.js";
import { renderDerivationOverlayList } from "./derivation/derivation-overlay-renderer.js";
import { buildKarakaOverlay } from "./karaka/karaka-overlay-engine.js";
import { renderKarakaOverlay } from "./karaka/karaka-overlay-renderer.js";
import { inspectMorphologyTransitions } from "./morphology/morphology-transition-engine.js";
import { renderMorphologyTransitionList } from "./morphology/morphology-transition-renderer.js";
import { expandPratyahara } from "./phonetics/pratyahara-engine.js";
import { inspectInputTopology } from "./phonetics/phonetic-topology-engine.js";
import { inspectSandhiText } from "./phonetics/sandhi-engine.js";
import { analyzeShikshaText } from "./phonetics/shiksha-engine.js";
import { inspectSymbolicCompression } from "./phonetics/symbolic-compression-engine.js";
import { inspectTransliteration } from "./phonetics/transliteration-engine.js";
import { executePrakriya } from "./prakriya/prakriya-composition-engine.js";
import { renderPrakriya } from "./prakriya/prakriya-renderer.js";
import { executeSandhi } from "./sandhi/sandhi-execution-engine.js";
import { renderSandhiExecution } from "./sandhi/sandhi-trace-renderer.js";
import { inspectDhatuSemanticGraph } from "./semantic/dhatu-semantic-engine.js";
import { renderDhatuSemanticList } from "./semantic/dhatu-semantic-renderer.js";
import { generateSubanta } from "./subanta/subanta-generator-engine.js";
import { renderSubanta } from "./subanta/subanta-renderer.js";
import { generateTinanta, generateTinantaParadigm } from "./tinanta/tinanta-generator-engine.js";
import { renderTinanta, renderTinantaParadigm } from "./tinanta/tinanta-renderer.js";
import { buildSandarbhaContextOverlay } from "./sandarbha/sandarbha-context-engine.js";
import { renderSandarbhaContextOverlay } from "./sandarbha/sandarbha-context-renderer.js";
import { inspectSutraReferenceOverlay } from "./sutra/sutra-reference-engine.js";
import { renderSutraReferenceList } from "./sutra/sutra-reference-renderer.js";
import { inspectRuleTrace } from "./trace/rule-trace-engine.js";
import { renderRuleTraceList } from "./trace/rule-trace-renderer.js";
import { buildVakyaDependencyOverlay } from "./vakya/vakya-dependency-engine.js";
import { renderVakyaDependencyOverlay } from "./vakya/vakya-dependency-renderer.js";
// Sanskrit Tab - deterministic linguistic analysis UI.

let mountNode = null;
let analyzeButton = null;
let sandhiButton = null;
let morphologyButton = null;
let inputNode = null;
let debugCreateButton = null;
let debugAppendButton = null;
let debugAmbiguityButton = null;
let debugPipelineButton = null;
let debugSaveButton = null;
let debugRefreshSessionsButton = null;
let lexiconSamplesButton = null;
let lexiconSourcesButton = null;
let lexiconValidateButton = null;
let sutraSamplesButton = null;
let sutraSourcesButton = null;
let sutraValidateButton = null;
let semanticTraceDemoButton = null;
let semanticTraceCustomButton = null;
let graphDemoButton = null;
let graphExportButton = null;
let semanticGraphZoomInButton = null;
let semanticGraphZoomOutButton = null;
let semanticGraphResetCameraButton = null;
let semanticGraphFitViewButton = null;
let semanticGraphCameraStatus = null;
let semanticGraphMinimapCanvas = null;
let semanticGraphPresetHomeButton = null;
let semanticGraphPresetDetailButton = null;
let semanticGraphPresetOverviewButton = null;
let replayDemoButton = null;
let replayExportButton = null;
let semanticSearchInput = null;
let semanticClusterFilter = null;
let semanticActionFilter = null;
let semanticGlossFilter = null;
let semanticDepthSelect = null;
let semanticRelationFilter = null;
let semanticResetButton = null;
let semanticDerivationFamilyFilter = null;
let semanticDerivationDomainFilter = null;
let semanticDerivationRelationFilter = null;
let semanticDerivationResetButton = null;
let semanticDerivationGraphFamilyFilter = null;
let semanticDerivationGraphDomainFilter = null;
let semanticDerivationGraphRelationFilter = null;
let semanticDerivationGraphResetButton = null;
let staticFixtureClusterFilter = null;
let staticFixtureDhatuFilter = null;
let staticFixtureNodeFilter = null;
let staticFixtureSectionFilter = null;
let staticFixtureCopyLinkButton = null;
let staticFixtureExportJsonButton = null;
let staticFixtureExportMarkdownButton = null;
let staticFixtureExportTextButton = null;
let staticFixtureImportSnapshotButton = null;
let staticFixtureImportFileInput = null;
let staticFixtureResetImportButton = null;
let staticFixtureImportStatus = null;
let staticFixtureComparisonSummary = null;
let staticFixtureImportedMetadata = null;
let staticFixtureComparisonResults = null;
let importedStaticFixtureSnapshot = null;
let currentDebugSession = null;
let semanticPanelData = null;
let semanticDerivationData = null;
let semanticDerivationGraphData = null;
let semanticPlatformStatusData = null;
let staticSemanticFixtureBrowserActive = false;
let staticFixtureHashRestored = false;
let backendRuntimeAvailable = false;
let selectedSemanticGraphNodeId = "01.0005";
let selectedDerivationGraphNodeId = "motion";
let semanticGraphStore = null;
let semanticGraphExpansionHistory = [];
let semanticGraphHoverNodeId = null;
let semanticGraphHoverEdgeId = null;
let semanticGraphMousePosition = { x: 0, y: 0 };
let semanticGraphPanState = null;
let semanticGraphMinimapState = null;
let semanticGraphRenderPending = false;
let semanticGraphInteractionAttached = false;
let semanticGraphCamera = { x: 0, y: 0, zoom: 1 };

const SEMANTIC_GRAPH_MIN_ZOOM = 0.35;
const SEMANTIC_GRAPH_MAX_ZOOM = 3.5;
const SEMANTIC_GRAPH_WHEEL_ZOOM_SPEED = 0.0015;
const SEMANTIC_GRAPH_BUTTON_ZOOM_FACTOR = 1.2;
const SEMANTIC_GRAPH_PAN_CLICK_TOLERANCE = 4;
const SEMANTIC_GRAPH_EDGE_HOVER_TOLERANCE = 8;
const SEMANTIC_GRAPH_FIT_PADDING = 48;
const SEMANTIC_GRAPH_KEYBOARD_PAN_STEP = 24;
const DEFAULT_PAYLOAD = {
  input_text: "agnim ile purohitam yajnasya devam rtvijam hotaram ratnadhatamam",
};

const SEMANTIC_DHATU_PANEL_FIXTURE = "data/sanskrit/dhatus/semantic/examples/ui/ui_semantic_combined_panel.v1.json";
const SEMANTIC_GRAPH_PANEL_FIXTURE = "data/sanskrit/dhatus/semantic/examples/graph/neighbor_01_0005.response.v1.json";
const SEMANTIC_PLATFORM_STATUS_PANEL_FIXTURE = "data/sanskrit/dhatus/semantic/examples/ui/ui_semantic_platform_status_panel.v1.json";
const SEMANTIC_DERIVATION_DATA_FIXTURE = "data/sanskrit/dhatus/semantic/derivations/semantic_derivations.v1.json";
const SEMANTIC_DERIVATION_GRAPH_PANEL_FIXTURE = "data/sanskrit/dhatus/semantic/derivations/examples/graph/ui_semantic_derivation_graph_panel.v1.json";
const SEMANTIC_DERIVATION_PLACEHOLDER_WARNING = "Placeholder-only: all derivation claims require future review. No exact Paninian derivation claim is made.";
const SEMANTIC_DERIVATION_GRAPH_PLACEHOLDER_WARNING = "Placeholder-only derivation graph bridge. No exact Paninian derivation claim, exact sutra assertion, or grammatical correctness guarantee is made.";
const SEMANTIC_PLATFORM_STATUS_SAFETY_WARNING = "Placeholder-safe: no exact sutra guarantees, no authoritative grammatical claims, and no canonical write hooks.";
const SEMANTIC_DHATU_FALLBACK_PANEL = {
  schemaVersion: "1.0.0",
  generatedBy: "ui/tabs/sanskrit/controller.js:fallback",
  panelType: "semanticCombined",
  title: "Semantic Combined Panel",
  description: "Static read-only fallback for Semantic Dhātu Intelligence.",
  primaryDhatu: {
    dhatuId: "01.0005",
    root: "गम्",
    iast: "gam",
    gloss: "to go",
  },
  cards: [
    {
      cardId: "fallback.search.01",
      cardType: "searchResult",
      label: "Search Results",
      value: "gam / गम्",
      metadata: {
        section: "Search Results",
        dhatuId: "01.0005",
        gloss: "to go",
        matchReasons: ["cluster"],
      },
    },
    {
      cardId: "fallback.neighbor.01",
      cardType: "semanticNeighbor",
      label: "Semantic Neighbors",
      value: "motion",
      metadata: {
        section: "Semantic Neighbors",
        relationTypes: ["associated_with"],
        traversedEdgeIds: ["edge.semantic.0001"],
      },
    },
    {
      cardId: "fallback.traversal.01",
      cardType: "traversalPath",
      label: "Traversal Paths",
      value: "motion -> guidance",
      metadata: {
        section: "Traversal Paths",
        depth: 2,
        relationTypes: ["associated_with"],
        traversedEdgeIds: ["edge.semantic.0004"],
      },
    },
  ],
  links: [
    { label: "Semantic search API", href: "/api/dhatu/semantic/search?cluster=motion", linkType: "api" },
    { label: "Semantic neighbors API", href: "/api/dhatu/semantic/neighbors?nodeId=01.0005", linkType: "api" },
    { label: "Semantic traversal API", href: "/api/dhatu/semantic/traverse?nodeId=motion&maxDepth=2", linkType: "api" },
  ],
  safetyNote: "Semantic graph links are foundation-placeholder UI context only; no exact Pāṇinian derivation claim is made.",
};

const SEMANTIC_PLATFORM_STATUS_FALLBACK_PANEL = {
  schemaVersion: "1.0.0",
  generatedBy: "ui/tabs/sanskrit/controller.js:fallback",
  panelType: "semanticPlatformStatus",
  platformStatus: "READY",
  milestoneSpan: "v53-v72",
  canonicalRegistryRecordCount: 13,
  semanticRecordCount: 3,
  uiReadiness: {
    status: "READY",
    mode: "client-side-read-only",
    backendFetchRequired: false,
    mutationHooksPresent: false,
  },
  checkpoint: {
    releaseTag: "sanskrit-v72-semantic-api-index-stable",
    jsonPath: "data/sanskrit/dhatus/semantic/releases/v70/semantic_platform_checkpoint.v70.json",
    markdownPath: "data/sanskrit/dhatus/semantic/releases/v70/semantic_platform_checkpoint.v70.md",
  },
  endpoints: [
    { path: "/api/dhatu/semantic/search", label: "Semantic Search API", method: "GET", readOnly: true },
    { path: "/api/dhatu/semantic/neighbors", label: "Semantic Neighbors API", method: "GET", readOnly: true },
    { path: "/api/dhatu/semantic/traverse", label: "Semantic Traversal API", method: "GET", readOnly: true },
    { path: "/api/dhatu/semantic/derivations", label: "Semantic Derivations API", method: "GET", readOnly: true },
    { path: "/api/dhatu/semantic/derivation-graph", label: "Semantic Derivation Graph API", method: "GET", readOnly: true },
  ],
  validators: [
    { name: "semanticLayer", status: "PASS", command: "python scripts/validate_dhatu_semantic_layer.py" },
    { name: "semanticGraph", status: "PASS", command: "python scripts/validate_dhatu_semantic_graph.py" },
    { name: "semanticDerivation", status: "PASS", command: "python scripts/validate_dhatu_semantic_derivations.py" },
    { name: "semanticDerivationGraph", status: "PASS", command: "python scripts/validate_dhatu_semantic_derivation_graph.py" },
  ],
  docs: [
    "data/sanskrit/dhatus/semantic/SEMANTIC_PLATFORM.md",
    "data/sanskrit/dhatus/semantic/SEMANTIC_API.md",
    "data/sanskrit/dhatus/semantic/DERIVATION_API.md",
    "data/sanskrit/dhatus/semantic/UI_INTEGRATION.md",
  ],
  examples: [
    "data/sanskrit/dhatus/semantic/examples/ui/ui_semantic_platform_status_panel.v1.json",
    "data/sanskrit/dhatus/semantic/examples/ui/",
    "data/sanskrit/dhatus/semantic/derivations/examples/graph/",
  ],
  safetyPolicy: {
    readOnlySemanticArchitecture: true,
    exactSutraAssertionsAllowed: false,
    exactPaninianDerivationClaimsAllowed: false,
    grammaticalCorrectnessGuarantee: false,
    canonicalRegistryMutation: false,
    canonicalWriteEnvironmentFlagsRequired: false,
  },
  safetyNote: SEMANTIC_PLATFORM_STATUS_SAFETY_WARNING,
};

const SEMANTIC_QUERY_DEFAULTS = {
  searchText: "",
  cluster: "motion",
  action: "",
  gloss: "",
  traversalDepth: 2,
  relationType: "",
};

const SEMANTIC_DHATU_RECORDS = [
  {
    dhatuId: "01.0005",
    root: "\u0917\u092e\u094d",
    iast: "gam",
    gloss: "to go",
    cluster: "motion",
    action: "motion",
    neighbors: [
      { nodeId: "motion", relationType: "associated_with", edgeId: "edge.semantic.0001" },
    ],
    traversalPaths: {
      1: [
        { terminalNodeId: "motion", value: "gam -> motion", relationTypes: ["associated_with"], edgeIds: ["edge.semantic.0001"] },
      ],
      2: [
        { terminalNodeId: "motion", value: "gam -> motion", relationTypes: ["associated_with"], edgeIds: ["edge.semantic.0001"] },
        { terminalNodeId: "guidance", value: "motion -> guidance", relationTypes: ["associated_with"], edgeIds: ["edge.semantic.0004"] },
        { terminalNodeId: "stability", value: "motion -> stability", relationTypes: ["transitions_to"], edgeIds: ["edge.semantic.0005"] },
      ],
    },
  },
  {
    dhatuId: "01.0008",
    root: "\u0928\u0940",
    iast: "n\u012b",
    gloss: "to lead",
    cluster: "guidance",
    action: "guidance",
    neighbors: [
      { nodeId: "guidance", relationType: "associated_with", edgeId: "edge.semantic.0003" },
      { nodeId: "motion", relationType: "guides", edgeId: "edge.semantic.0006" },
    ],
    traversalPaths: {
      1: [
        { terminalNodeId: "guidance", value: "n\u012b -> guidance", relationTypes: ["associated_with"], edgeIds: ["edge.semantic.0003"] },
      ],
      2: [
        { terminalNodeId: "guidance", value: "n\u012b -> guidance", relationTypes: ["associated_with"], edgeIds: ["edge.semantic.0003"] },
        { terminalNodeId: "motion", value: "guidance -> motion", relationTypes: ["guides"], edgeIds: ["edge.semantic.0006"] },
      ],
    },
  },
  {
    dhatuId: "01.0013",
    root: "\u0938\u094d\u0925\u093e",
    iast: "sth\u0101",
    gloss: "to stand",
    cluster: "stability",
    action: "stability",
    neighbors: [
      { nodeId: "stability", relationType: "associated_with", edgeId: "edge.semantic.0002" },
      { nodeId: "motion", relationType: "grounds", edgeId: "edge.semantic.0007" },
    ],
    traversalPaths: {
      1: [
        { terminalNodeId: "stability", value: "sth\u0101 -> stability", relationTypes: ["associated_with"], edgeIds: ["edge.semantic.0002"] },
      ],
      2: [
        { terminalNodeId: "stability", value: "sth\u0101 -> stability", relationTypes: ["associated_with"], edgeIds: ["edge.semantic.0002"] },
        { terminalNodeId: "motion", value: "stability -> motion", relationTypes: ["grounds"], edgeIds: ["edge.semantic.0007"] },
      ],
    },
  },
];

const SEMANTIC_DERIVATION_FALLBACK_DATA = {
  schemaVersion: "1.0.0",
  generatedBy: "ui/tabs/sanskrit/controller.js:fallback",
  policy: {
    authoritativePaninianClaims: false,
    exactSutraAssertions: false,
    grammaticalCorrectnessGuarantee: false,
    requiredReviewStatus: "placeholder-local-review-required",
    requiredRelationConfidence: "unreviewed",
  },
  records: [
    {
      schemaVersion: "1.0.0",
      derivationId: "derivation.semantic.01.0005",
      dhatuId: "01.0005",
      rootIast: "gam",
      derivationFamilyId: "family.semantic.motion-transition",
      semanticLineage: ["movement", "traversal", "transition"],
      usageDomains: ["motion", "journey", "transition"],
      conceptualAffixHints: [
        {
          hintId: "hint.semantic.gam.01",
          label: "motion-oriented formation space",
          confidence: "unreviewed",
          source: "placeholder-local-model",
          note: "Conceptual placeholder only; no affix rule is asserted.",
        },
      ],
      protoDerivationRelations: [
        {
          relationId: "relation.semantic.0001",
          sourceDerivationId: "derivation.semantic.01.0005",
          targetDerivationId: "derivation.semantic.01.0008",
          relationType: "motion-guidance-adjacent",
          confidence: "unreviewed",
          source: "placeholder-local-model",
          note: "Semantic adjacency only; no derivational correctness claim is made.",
        },
        {
          relationId: "relation.semantic.0002",
          sourceDerivationId: "derivation.semantic.01.0005",
          targetDerivationId: "derivation.semantic.01.0013",
          relationType: "motion-stability-contrast",
          confidence: "unreviewed",
          source: "placeholder-local-model",
          note: "Semantic contrast only; no derivational correctness claim is made.",
        },
      ],
      semanticTransformationNotes: [
        "Local placeholder for future movement-to-result semantic exploration.",
        "No grammatical correctness guarantee is provided.",
      ],
      placeholderPaniniRelation: {
        status: "not-asserted",
        reviewStatus: "placeholder-local-review-required",
        source: "placeholder-local-review-required",
        note: "No exact Paninian source is asserted.",
      },
      reviewStatus: "placeholder-local-review-required",
    },
    {
      schemaVersion: "1.0.0",
      derivationId: "derivation.semantic.01.0008",
      dhatuId: "01.0008",
      rootIast: "ni",
      derivationFamilyId: "family.semantic.guidance-transfer",
      semanticLineage: ["guidance", "leading", "transfer"],
      usageDomains: ["guidance", "motion", "agency"],
      conceptualAffixHints: [
        {
          hintId: "hint.semantic.ni.01",
          label: "guidance-oriented formation space",
          confidence: "unreviewed",
          source: "placeholder-local-model",
          note: "Conceptual placeholder only; no affix rule is asserted.",
        },
      ],
      protoDerivationRelations: [
        {
          relationId: "relation.semantic.0003",
          sourceDerivationId: "derivation.semantic.01.0008",
          targetDerivationId: "derivation.semantic.01.0005",
          relationType: "guidance-motion-adjacent",
          confidence: "unreviewed",
          source: "placeholder-local-model",
          note: "Semantic adjacency only; no derivational correctness claim is made.",
        },
      ],
      semanticTransformationNotes: [
        "Local placeholder for future guidance-and-transfer semantic exploration.",
        "No grammatical correctness guarantee is provided.",
      ],
      placeholderPaniniRelation: {
        status: "not-asserted",
        reviewStatus: "placeholder-local-review-required",
        source: "placeholder-local-review-required",
        note: "No exact Paninian source is asserted.",
      },
      reviewStatus: "placeholder-local-review-required",
    },
    {
      schemaVersion: "1.0.0",
      derivationId: "derivation.semantic.01.0013",
      dhatuId: "01.0013",
      rootIast: "stha",
      derivationFamilyId: "family.semantic.stability-state",
      semanticLineage: ["stability", "standing", "persistence"],
      usageDomains: ["stability", "posture", "state"],
      conceptualAffixHints: [
        {
          hintId: "hint.semantic.stha.01",
          label: "state-oriented formation space",
          confidence: "unreviewed",
          source: "placeholder-local-model",
          note: "Conceptual placeholder only; no affix rule is asserted.",
        },
      ],
      protoDerivationRelations: [
        {
          relationId: "relation.semantic.0004",
          sourceDerivationId: "derivation.semantic.01.0013",
          targetDerivationId: "derivation.semantic.01.0005",
          relationType: "stability-motion-contrast",
          confidence: "unreviewed",
          source: "placeholder-local-model",
          note: "Semantic contrast only; no derivational correctness claim is made.",
        },
      ],
      semanticTransformationNotes: [
        "Local placeholder for future stability-and-state semantic exploration.",
        "No grammatical correctness guarantee is provided.",
      ],
      placeholderPaniniRelation: {
        status: "not-asserted",
        reviewStatus: "placeholder-local-review-required",
        source: "placeholder-local-review-required",
        note: "No exact Paninian source is asserted.",
      },
      reviewStatus: "placeholder-local-review-required",
    },
  ],
};

const SEMANTIC_DERIVATION_DEFAULTS = {
  family: "",
  domain: "",
  relation: "",
};

const SEMANTIC_DERIVATION_GRAPH_FALLBACK_PANEL = {
  schemaVersion: "1.0.0",
  generatedBy: "ui/tabs/sanskrit/controller.js:fallback",
  panelType: "semanticDerivationGraphPlaceholder",
  title: "Semantic Derivation Graph Bridge",
  safetyNote: SEMANTIC_DERIVATION_GRAPH_PLACEHOLDER_WARNING,
  nodes: [
    { graphNodeId: "motion", label: "motion", nodeType: "semantic_cluster", reviewStatus: "placeholder-local-review-required", x: 10, y: 42 },
    { graphNodeId: "motion_transition_family", label: "motion transition family", nodeType: "derivation_family", derivationFamilyId: "family.semantic.motion-transition", semanticLineage: ["movement", "traversal", "transition"], transformationHints: ["movement-to-result exploration"], reviewStatus: "placeholder-local-review-required", x: 34, y: 42 },
    { graphNodeId: "derivation.semantic.01.0005", label: "gam", nodeType: "derivation_record", dhatuId: "01.0005", derivationFamilyId: "family.semantic.motion-transition", semanticLineage: ["movement", "traversal", "transition"], transformationHints: ["Local placeholder for future movement-to-result semantic exploration."], reviewStatus: "placeholder-local-review-required", x: 58, y: 42 },
    { graphNodeId: "guidance", label: "guidance", nodeType: "semantic_cluster", reviewStatus: "placeholder-local-review-required", x: 10, y: 20 },
    { graphNodeId: "directional_guidance_family", label: "directional guidance family", nodeType: "derivation_family", derivationFamilyId: "family.semantic.guidance-transfer", semanticLineage: ["guidance", "leading", "transfer"], transformationHints: ["guidance-and-transfer exploration"], reviewStatus: "placeholder-local-review-required", x: 34, y: 20 },
    { graphNodeId: "derivation.semantic.01.0008", label: "ni", nodeType: "derivation_record", dhatuId: "01.0008", derivationFamilyId: "family.semantic.guidance-transfer", semanticLineage: ["guidance", "leading", "transfer"], transformationHints: ["Local placeholder for future guidance-and-transfer semantic exploration."], reviewStatus: "placeholder-local-review-required", x: 82, y: 20 },
    { graphNodeId: "stability", label: "stability", nodeType: "semantic_cluster", reviewStatus: "placeholder-local-review-required", x: 10, y: 64 },
    { graphNodeId: "grounding_stability_family", label: "grounding stability family", nodeType: "derivation_family", derivationFamilyId: "family.semantic.stability-state", semanticLineage: ["stability", "standing", "persistence"], transformationHints: ["stability-and-state exploration"], reviewStatus: "placeholder-local-review-required", x: 34, y: 64 },
    { graphNodeId: "derivation.semantic.01.0013", label: "stha", nodeType: "derivation_record", dhatuId: "01.0013", derivationFamilyId: "family.semantic.stability-state", semanticLineage: ["stability", "standing", "persistence"], transformationHints: ["Local placeholder for future stability-and-state semantic exploration."], reviewStatus: "placeholder-local-review-required", x: 82, y: 64 },
  ],
  edges: [
    { edgeId: "edge.derivation.semantic.0001", sourceId: "motion", targetId: "motion_transition_family", relationType: "semantic_family_bridge", relationLabel: "motion -> motion_transition_family", confidence: "unreviewed", reviewStatus: "placeholder-local-review-required" },
    { edgeId: "edge.derivation.semantic.0002", sourceId: "guidance", targetId: "directional_guidance_family", relationType: "semantic_family_bridge", relationLabel: "guidance -> directional_guidance_family", confidence: "unreviewed", reviewStatus: "placeholder-local-review-required" },
    { edgeId: "edge.derivation.semantic.0003", sourceId: "stability", targetId: "grounding_stability_family", relationType: "semantic_family_bridge", relationLabel: "stability -> grounding_stability_family", confidence: "unreviewed", reviewStatus: "placeholder-local-review-required" },
    { edgeId: "edge.derivation.semantic.0004", sourceId: "motion_transition_family", targetId: "derivation.semantic.01.0005", relationType: "family_record_placeholder", relationLabel: "motion_transition_family -> gam placeholder record", confidence: "unreviewed", reviewStatus: "placeholder-local-review-required" },
    { edgeId: "edge.derivation.semantic.0005", sourceId: "directional_guidance_family", targetId: "derivation.semantic.01.0008", relationType: "family_record_placeholder", relationLabel: "directional_guidance_family -> ni placeholder record", confidence: "unreviewed", reviewStatus: "placeholder-local-review-required" },
    { edgeId: "edge.derivation.semantic.0006", sourceId: "grounding_stability_family", targetId: "derivation.semantic.01.0013", relationType: "family_record_placeholder", relationLabel: "grounding_stability_family -> stha placeholder record", confidence: "unreviewed", reviewStatus: "placeholder-local-review-required" },
    { edgeId: "edge.derivation.semantic.0007", sourceId: "derivation.semantic.01.0005", targetId: "derivation.semantic.01.0008", relationType: "motion_guidance_placeholder", relationLabel: "gam placeholder -> ni placeholder", confidence: "unreviewed", reviewStatus: "placeholder-local-review-required" },
    { edgeId: "edge.derivation.semantic.0008", sourceId: "derivation.semantic.01.0005", targetId: "derivation.semantic.01.0013", relationType: "motion_stability_placeholder", relationLabel: "gam placeholder -> stha placeholder", confidence: "unreviewed", reviewStatus: "placeholder-local-review-required" },
  ],
  cards: [
    {
      cardId: "semantic.derivation.graph.fallback.01",
      cardType: "semanticDerivationGraphPath",
      label: "derivation.semantic.01.0005",
      value: "motion -> motion_transition_family -> derivation.semantic.01.0005",
      metadata: {
        depth: 2,
        edgeIds: ["edge.derivation.semantic.0001", "edge.derivation.semantic.0004"],
        relationLabels: ["motion -> motion_transition_family", "motion_transition_family -> gam placeholder record"],
      },
    },
  ],
};

const SEMANTIC_DERIVATION_GRAPH_DEFAULTS = {
  family: "",
  domain: "",
  relation: "",
};

const SEMANTIC_DERIVATION_GRAPH_RELATION_ORDER = [
  "semantic_family_bridge",
  "family_record_placeholder",
  "motion_guidance_placeholder",
  "motion_stability_placeholder",
];

const SEMANTIC_GRAPH_FALLBACK = {
  nodes: [
    { nodeId: "01.0005", label: "gam / \u0917\u092e\u094d", nodeType: "dhatu", cluster: "motion", x: 10, y: 44 },
    { nodeId: "motion", label: "motion", nodeType: "semantic_cluster", cluster: "motion", x: 34, y: 44 },
    { nodeId: "guidance", label: "guidance", nodeType: "semantic_cluster", cluster: "guidance", x: 58, y: 24 },
    { nodeId: "stability", label: "stability", nodeType: "semantic_cluster", cluster: "stability", x: 58, y: 64 },
    { nodeId: "01.0008", label: "n\u012b / \u0928\u0940", nodeType: "dhatu", cluster: "guidance", x: 82, y: 24 },
    { nodeId: "01.0013", label: "sth\u0101 / \u0938\u094d\u0925\u093e", nodeType: "dhatu", cluster: "stability", x: 82, y: 64 },
  ],
  edges: [
    { edgeId: "edge.semantic.0001", sourceId: "01.0005", targetId: "motion", relationType: "associated_with" },
    { edgeId: "edge.semantic.0004", sourceId: "motion", targetId: "guidance", relationType: "associated_with" },
    { edgeId: "edge.semantic.0005", sourceId: "motion", targetId: "stability", relationType: "transitions_to" },
    { edgeId: "edge.semantic.0006", sourceId: "guidance", targetId: "motion", relationType: "guides" },
    { edgeId: "edge.semantic.0007", sourceId: "stability", targetId: "motion", relationType: "grounds" },
    { edgeId: "edge.semantic.0003", sourceId: "01.0008", targetId: "guidance", relationType: "associated_with" },
    { edgeId: "edge.semantic.0002", sourceId: "01.0013", targetId: "stability", relationType: "associated_with" },
  ],
};

const SEMANTIC_GRAPH_RELATION_ORDER = ["associated_with", "guides", "transitions_to", "grounds"];

function byId(id) {
  return mountNode?.querySelector(`#${id}`);
}

function all(selector) {
  return Array.from(mountNode?.querySelectorAll(selector) || []);
}

function setStatus(message, isError = false) {
  const status = byId("sanskrit-status");
  if (!status) return;
  status.textContent = message;
  status.classList.toggle("error", isError);
}

function clearChildren(node) {
  if (!node) return;
  while (node.firstChild) node.removeChild(node.firstChild);
}

function text(value, fallback = "-") {
  if (value === null || value === undefined || value === "") return fallback;
  return String(value);
}

function setText(id, value, fallback = "-") {
  const node = byId(id);
  if (node) node.textContent = text(value, fallback);
}

function fieldValue(id) {
  return byId(id)?.value.trim() || "";
}

function setBusy(button, isBusy) {
  if (button) button.disabled = isBusy;
}

function runShikshaAnalysis(inputText = "") {
  try {
    return analyzeShikshaText(inputText);
  } catch (error) {
    return {
      inputText,
      phonemes: [],
      summary: {
        total: 0,
        vowel: 0,
        consonant: 0,
        modifier: 0,
        unknown: 0,
        byArticulation: {},
        byGroup: {},
      },
      safetyNote: "Śikṣā analysis unavailable due to local classification error.",
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

function renderPratyaharaPanel() {
  const container = byId("pratyahara-analysis-panel");
  if (!container) return;

  clearChildren(container);

  const examples = [
    { label: "अच्", start: "अ", marker: "च्" },
    { label: "हल्", start: "ह", marker: "ल्" },
    { label: "इक्", start: "इ", marker: "क्" },
  ];

  examples.forEach((example) => {
    const result = expandPratyahara(example.start, example.marker);

    appendInspectionRow(
      container,
      example.label,
      result.valid ? result.sounds.join(" ") : "Invalid",
      result.safetyNote,
    );
  });
}

function renderShikshaBreakdown(container, title, values = {}) {
  const entries = Object.entries(values).sort(([left], [right]) =>
    left.localeCompare(right),
  );

  appendInspectionRow(container, title, entries.length ? "" : "None");

  entries.forEach(([label, count]) => {
    appendInspectionRow(container, `• ${label}`, count);
  });
}

function renderShikshaPhonemeRows(container, phonemes = []) {
  appendInspectionRow(container, "Phoneme Details", phonemes.length ? "" : "None");

  phonemes.slice(0, 24).forEach((phoneme, index) => {
    appendInspectionRow(
      container,
      `${index + 1}. ${phoneme.character}`,
      phoneme.type,
      `${phoneme.group}; ${phoneme.articulation}`,
    );
  });

  if (phonemes.length > 24) {
    appendInspectionRow(
      container,
      "Phoneme Details Truncated",
      `${phonemes.length - 24} more characters`,
      "UI preview is capped to keep the panel readable.",
    );
  }
}

function renderShikshaPanel(analysis) {
  const container = byId("shiksha-analysis-panel");
  if (!container) return;

  clearChildren(container);

  const summary = analysis?.summary || {};
  appendInspectionRow(container, "Characters", summary.total || 0);
  appendInspectionRow(container, "Vowels", summary.vowel || 0);
  appendInspectionRow(container, "Consonants", summary.consonant || 0);
  appendInspectionRow(container, "Modifiers", summary.modifier || 0);
  appendInspectionRow(container, "Unknown", summary.unknown || 0);
  renderShikshaBreakdown(container, "Articulation", summary.byArticulation || {});
  renderShikshaBreakdown(container, "Group", summary.byGroup || {});
  renderShikshaPhonemeRows(container, analysis?.phonemes || []);

  const safety = document.createElement("small");
  safety.className = "inspection-note";
  safety.textContent = analysis?.safetyNote || "Śikṣā analysis is deterministic read-only classification.";
  container.appendChild(safety);
}

function renderSandhiExecutionPanel(inputText = "") {
  const container = byId("sandhi-execution-panel") || byId("sandhi-transition-panel");
  if (!container) return;

  const tokens = String(inputText || "")
    .split(/\s+/)
    .filter(Boolean)
    .map((token, index) => ({ token, index }));
  const execution = executeSandhi({
    text: inputText,
    tokens,
    mode: "static-preview",
    enableTrace: true,
    enableReversePreview: true,
  });
  renderSandhiExecution(container, execution);
}

function renderTransliterationPanel(inputText = "") {
  const container = byId("transliteration-analysis-panel");
  if (!container) return;

  clearChildren(container);

  const analysis = inspectTransliteration(inputText);
  appendInspectionRow(container, "Characters", analysis.summary.characterCount || 0);
  appendInspectionRow(container, "IAST", analysis.iast.output || "-");
  appendInspectionRow(container, "IPA", analysis.ipa.output || "-");
  appendInspectionRow(container, "IAST Unknown", analysis.summary.iastUnknownCount || 0);
  appendInspectionRow(container, "IPA Unknown", analysis.summary.ipaUnknownCount || 0);
  appendInspectionRow(container, "Safety", "Read-only", analysis.safetyNote);
}

function renderSymbolicCompressionPanel() {
  const container = byId("symbolic-compression-panel");
  if (!container) return;

  clearChildren(container);

  const analysis = inspectSymbolicCompression();
  const summary = analysis.summary || {};

  appendInspectionRow(container, "Classes", summary.classCount || 0);
  appendInspectionRow(container, "Valid", summary.validCount || 0);
  appendInspectionRow(container, "Invalid", summary.invalidCount || 0);

  analysis.classes.forEach((item) => {
    appendInspectionRow(
      container,
      item.classId,
      item.sounds.join(" "),
      item.label,
    );
  });

  appendInspectionRow(container, "Safety", "Read-only", analysis.safetyNote);
}

function renderPhoneticTopologyPanel(inputText = "") {
  const container = byId("phonetic-topology-panel");
  if (!container) return;

  clearChildren(container);

  const analysis = inspectInputTopology(inputText);
  const activeSet = new Set(analysis.activeNodeIds || []);

  appendInspectionRow(container, "Topology Nodes", analysis.summary.nodeCount || 0);
  appendInspectionRow(container, "Topology Edges", analysis.summary.edgeCount || 0);
  appendInspectionRow(container, "Active Nodes", analysis.summary.activeNodeCount || 0);

  analysis.nodes.forEach((node) => {
    appendInspectionRow(
      container,
      activeSet.has(node.id) ? `● ${node.label}` : `○ ${node.label}`,
      node.sounds.join(" "),
      `${node.type}; ${node.id}`,
    );
  });

  appendInspectionRow(container, "Safety", "Read-only", analysis.safetyNote);
}

function renderDerivationGraphPanel(inputText = "") {
  const container = byId("derivation-graph-panel");
  if (!container) return;

  clearChildren(container);

  const analysis = inspectDerivationGraph(inputText);

  appendInspectionRow(
    container,
    "Graph Nodes",
    analysis.summary.nodeCount || 0,
  );

  appendInspectionRow(
    container,
    "Graph Edges",
    analysis.summary.edgeCount || 0,
  );

  appendInspectionRow(
    container,
    "Symbolic Classes",
    analysis.summary.symbolicClassCount || 0,
  );

  appendInspectionRow(
    container,
    "Topology Nodes",
    analysis.summary.topologyNodeCount || 0,
  );

  appendInspectionRow(
    container,
    "Sandhi Transitions",
    analysis.summary.sandhiTransitionCount || 0,
  );

  renderDerivationOverlayList(container, analysis);

  appendInspectionRow(
    container,
    "Safety",
    "Read-only",
    analysis.safetyNote,
  );
}

function renderDhatuSemanticPanel(inputText = "") {
  const container = byId("dhatu-semantic-panel");
  if (!container) return;

  clearChildren(container);

  const analysis = inspectDhatuSemanticGraph(inputText);
  const summary = analysis.summary || {};

  appendInspectionRow(container, "Semantic Nodes", summary.nodeCount || 0);
  appendInspectionRow(container, "Semantic Edges", summary.edgeCount || 0);
  appendInspectionRow(container, "Semantic Clusters", summary.clusterCount || 0);
  appendInspectionRow(container, "Derivation Nodes", summary.derivationNodeCount || 0);
  appendInspectionRow(container, "Derivation Edges", summary.derivationEdgeCount || 0);

  renderDhatuSemanticList(container, analysis);

  appendInspectionRow(container, "Safety", "Read-only", analysis.safetyNote);
}

function renderSutraReferencePanel(inputText = "") {
  const container = byId("sutra-reference-panel");
  if (!container) return;

  clearChildren(container);

  const analysis = inspectSutraReferenceOverlay(inputText);
  const summary = analysis.summary || {};

  appendInspectionRow(container, "Reference Nodes", summary.referenceNodeCount || 0);
  appendInspectionRow(container, "Reference Edges", summary.referenceEdgeCount || 0);
  appendInspectionRow(container, "Symbolic Classes", summary.symbolicClassCount || 0);
  appendInspectionRow(container, "Semantic Nodes", summary.semanticNodeCount || 0);
  appendInspectionRow(container, "Semantic Edges", summary.semanticEdgeCount || 0);

  renderSutraReferenceList(container, analysis);

  appendInspectionRow(container, "Safety", "Read-only", analysis.safetyNote);
}

function renderRuleTracePanel(inputText = "") {
  const container = byId("rule-trace-panel");
  if (!container) return;

  clearChildren(container);

  const analysis = inspectRuleTrace(inputText);
  const summary = analysis.summary || {};

  appendInspectionRow(container, "Trace Nodes", summary.traceNodeCount || 0);
  appendInspectionRow(container, "Trace Edges", summary.traceEdgeCount || 0);
  appendInspectionRow(container, "Sūtra Reference Nodes", summary.sutraReferenceNodeCount || 0);
  appendInspectionRow(container, "Derivation Nodes", summary.derivationNodeCount || 0);
  appendInspectionRow(container, "Semantic Nodes", summary.semanticNodeCount || 0);
  appendInspectionRow(container, "Sandhi Transitions", summary.sandhiTransitionCount || 0);
  appendInspectionRow(container, "Symbolic Classes", summary.symbolicClassCount || 0);

  renderRuleTraceList(container, analysis);

  appendInspectionRow(container, "Safety", "Read-only", analysis.safetyNote);
}

function renderMorphologyTransitionPanel(inputText = "") {
  const container = byId("morphology-transition-panel");
  if (!container) return;

  clearChildren(container);

  const analysis = inspectMorphologyTransitions(inputText);
  const summary = analysis.summary || {};

  appendInspectionRow(container, "Morphology Nodes", summary.nodeCount || 0);
  appendInspectionRow(container, "Morphology Edges", summary.edgeCount || 0);
  appendInspectionRow(container, "Roots", summary.rootCount || 0);
  appendInspectionRow(container, "Stems", summary.stemCount || 0);
  appendInspectionRow(container, "Suffixes", summary.suffixCount || 0);
  appendInspectionRow(container, "Surface Forms", summary.surfaceFormCount || 0);
  appendInspectionRow(container, "Trace Nodes", summary.traceNodeCount || 0);
  appendInspectionRow(container, "Semantic Nodes", summary.semanticNodeCount || 0);

  renderMorphologyTransitionList(container, analysis);

  appendInspectionRow(container, "Safety", "Read-only", analysis.safetyNote);
}

function renderSubantaGeneratorPanel(inputText = "") {
  const container = byId("subanta-generator-panel");
  if (!container) return;

  const stem = String(inputText || "")
    .split(/\s+/)
    .filter(Boolean)[0] || "";
  const generation = generateSubanta({
    stem,
    vibhakti: "prathama",
    vacana: "eka",
    enableTrace: true,
    enableReversePreview: true,
  });

  renderSubanta(container, generation);
}

function renderTinantaGeneratorPanels(inputText = "") {
  const formContainer = byId("tinanta-generator-panel");
  const paradigmContainer = byId("tinanta-paradigm-panel");
  if (!formContainer && !paradigmContainer) return;

  const dhatu = String(inputText || "")
    .split(/\s+/)
    .filter(Boolean)[0] || "";
  const baseInput = {
    dhatu,
    lakara: "laṭ",
    pada: "parasmaipada",
    purusha: "prathama",
    vacana: "eka",
    enableTrace: true,
    enableReversePreview: true,
  };

  if (formContainer) renderTinanta(formContainer, generateTinanta(baseInput));
  if (paradigmContainer) renderTinantaParadigm(paradigmContainer, generateTinantaParadigm(baseInput));
}

function renderPrakriyaCompositionPanel(inputText = "") {
  const container = byId("prakriya-composition-panel");
  if (!container) return;

  const firstToken = String(inputText || "")
    .split(/\s+/)
    .filter(Boolean)[0] || "";
  const nounInput = firstToken === "फल"
    ? { stem: "फल", stemClass: "a-stem", linga: "neuter", vibhakti: "prathama", vacana: "eka" }
    : firstToken === "सीता"
      ? { stem: "सीता", stemClass: "ā-stem", linga: "feminine", vibhakti: "prathama", vacana: "eka" }
      : { stem: "राम", stemClass: "a-stem", linga: "masculine", vibhakti: "prathama", vacana: "eka" };
  const verbInput = firstToken === "भू" || firstToken === "bhū"
    ? { dhatu: "bhū", lakara: "laṭ", pada: "parasmaipada", purusha: "prathama", vacana: "eka" }
    : firstToken === "नी" || firstToken === "nī"
      ? { dhatu: "nī", lakara: "laṭ", pada: "parasmaipada", purusha: "prathama", vacana: "eka" }
      : { dhatu: "gam", lakara: "laṭ", pada: "parasmaipada", purusha: "prathama", vacana: "eka" };

  renderPrakriya(container, executePrakriya({
    nounInputs: [nounInput],
    verbInput,
    enableSandhi: true,
    enableTrace: true,
    enableReversePreview: true,
  }));
}

function renderKarakaOverlayPanel(inputText = "") {
  const container = byId("karaka-overlay-panel");
  if (!container) return;

  const morphologyTransitions = inspectMorphologyTransitions(inputText);
  const overlay = buildKarakaOverlay({
    morphologyTransitions,
    semanticOverlays: inspectDhatuSemanticGraph(inputText),
    derivationGraph: inspectDerivationGraph(inputText),
    ruleTraceChain: inspectRuleTrace(inputText),
  });

  renderKarakaOverlay(container, overlay);
}

function renderVakyaDependencyPanel(inputText = "") {
  const container = byId("vakya-dependency-panel");
  if (!container) return;

  const morphologyTransitions = inspectMorphologyTransitions(inputText);
  const karakaOverlay = buildKarakaOverlay({
    morphologyTransitions,
    semanticOverlays: inspectDhatuSemanticGraph(inputText),
    derivationGraph: inspectDerivationGraph(inputText),
    ruleTraceChain: inspectRuleTrace(inputText),
  });
  const overlay = buildVakyaDependencyOverlay({
    tokens: String(inputText || "")
      .split(/\s+/)
      .filter(Boolean)
      .map((token, index) => ({ token, index })),
    morphologyTransitions,
    karakaOverlay,
    semanticOverlays: inspectDhatuSemanticGraph(inputText),
    derivationGraph: inspectDerivationGraph(inputText),
    ruleTraceChain: inspectRuleTrace(inputText),
  });

  renderVakyaDependencyOverlay(container, overlay);
}

function renderSandarbhaContextPanel(inputText = "") {
  const container = byId("sandarbha-context-panel");
  if (!container) return;

  const morphologyTransitions = inspectMorphologyTransitions(inputText);
  const semanticOverlay = inspectDhatuSemanticGraph(inputText);
  const derivationOverlay = inspectDerivationGraph(inputText);
  const ruleTrace = inspectRuleTrace(inputText);
  const karakaOverlay = buildKarakaOverlay({
    morphologyTransitions,
    semanticOverlays: semanticOverlay,
    derivationGraph: derivationOverlay,
    ruleTraceChain: ruleTrace,
  });
  const vakyaDependencyOverlay = buildVakyaDependencyOverlay({
    tokens: String(inputText || "")
      .split(/\s+/)
      .filter(Boolean)
      .map((token, index) => ({ token, index })),
    morphologyTransitions,
    karakaOverlay,
    semanticOverlays: semanticOverlay,
    derivationGraph: derivationOverlay,
    ruleTraceChain: ruleTrace,
  });
  const overlay = buildSandarbhaContextOverlay({
    tokens: String(inputText || "")
      .split(/\s+/)
      .filter(Boolean)
      .map((token, index) => ({ token, index })),
    morphologyTransitions,
    karakaOverlay,
    vakyaDependencyOverlay,
    semanticOverlays: semanticOverlay.graph,
    derivationGraph: derivationOverlay.graph,
    ruleTraceChain: ruleTrace,
  });

  renderSandarbhaContextOverlay(container, overlay);
}

function renderChandasProsodyPanel(inputText = "") {
  const container = byId("chandas-prosody-panel");
  if (!container) return;

  const morphologyTransitions = inspectMorphologyTransitions(inputText);
  const derivationGraph = inspectDerivationGraph(inputText);
  const sandarbhaContextOverlay = buildSandarbhaContextOverlay({
    tokens: String(inputText || "")
      .split(/\s+/)
      .filter(Boolean)
      .map((token, index) => ({ token, index })),
    morphologyTransitions,
    karakaOverlay: buildKarakaOverlay({ morphologyTransitions }),
    vakyaDependencyOverlay: buildVakyaDependencyOverlay({
      morphologyTransitions,
      karakaOverlay: buildKarakaOverlay({ morphologyTransitions }),
    }),
    semanticOverlays: inspectDhatuSemanticGraph(inputText).graph,
    derivationGraph: derivationGraph.graph,
    ruleTraceChain: inspectRuleTrace(inputText),
  });
  const overlay = buildChandasProsodyOverlay({
    text: inputText,
    tokens: String(inputText || "")
      .split(/\s+/)
      .filter(Boolean)
      .map((token, index) => ({ token, index })),
    phoneticAnalysis: runShikshaAnalysis(inputText),
    sandhiTransitions: inspectSandhiText(inputText),
    symbolicCompression: inspectSymbolicCompression(),
    phoneticTopology: inspectInputTopology(inputText),
    morphologyTransitions,
    sandarbhaContextOverlay,
    derivationGraph,
  });

  renderChandasProsodyOverlay(container, overlay);
}

function appendEmpty(node, message = "No entries") {
  if (!node) return;
  const empty = document.createElement("div");
  empty.className = "inspection-row";
  empty.textContent = message;
  node.appendChild(empty);
}

function appendInspectionRow(node, label, value, detail) {
  if (!node) return;
  const row = document.createElement("div");
  row.className = "inspection-row";
  const title = document.createElement("strong");
  title.textContent = label;
  const body = document.createElement("span");
  body.textContent = text(value);
  row.append(title, document.createTextNode(": "), body);
  if (detail) {
    const small = document.createElement("small");
    small.textContent = detail;
    row.appendChild(small);
  }
  node.appendChild(row);
}

function metadataSummary(metadata) {
  if (!metadata || typeof metadata !== "object") return "";
  const parts = [];
  if (metadata.dhatuId) parts.push(`dhatu ${metadata.dhatuId}`);
  if (metadata.gloss) parts.push(metadata.gloss);
  if (metadata.relationTypes) parts.push(`relations ${metadata.relationTypes.join(", ")}`);
  if (metadata.traversedEdgeIds) parts.push(`edges ${metadata.traversedEdgeIds.join(", ")}`);
  if (metadata.pathCount !== undefined) parts.push(`${metadata.pathCount} paths`);
  if (metadata.visitedNodeCount !== undefined) parts.push(`${metadata.visitedNodeCount} visited`);
  return parts.join("; ");
}

function renderSemanticPanelCard(card) {
  const row = document.createElement("article");
  row.className = `semantic-dhatu-card ${text(card?.cardType, "semantic-card")}`;

  const label = document.createElement("strong");
  label.textContent = text(card?.label, "Semantic card");

  const value = document.createElement("span");
  value.textContent = text(card?.value);

  const meta = document.createElement("small");
  meta.textContent = metadataSummary(card?.metadata) || text(card?.cardId);

  row.append(label, value, meta);
  return row;
}

function renderSemanticPanelLinks(container, links) {
  const values = Array.isArray(links) ? links : [];
  if (values.length === 0) return;

  const list = document.createElement("div");
  list.className = "semantic-dhatu-links";
  values.forEach((item) => {
    const anchor = document.createElement("a");
    anchor.href = text(item?.href, "#");
    anchor.textContent = text(item?.label, "Semantic link");
    anchor.dataset.linkType = text(item?.linkType, "reference");
    list.appendChild(anchor);
  });
  container.appendChild(list);
}

function readSemanticQueryState() {
  return {
    searchText: semanticSearchInput?.value.trim().toLowerCase() || "",
    cluster: semanticClusterFilter?.value || "",
    action: semanticActionFilter?.value || "",
    gloss: semanticGlossFilter?.value || "",
    traversalDepth: Number(semanticDepthSelect?.value || SEMANTIC_QUERY_DEFAULTS.traversalDepth),
    relationType: semanticRelationFilter?.value || "",
  };
}

function semanticRecordMatches(record, queryState) {
  const searchable = [
    record.dhatuId,
    record.root,
    record.iast,
    record.gloss,
    record.cluster,
    record.action,
  ].join(" ").toLowerCase();
  if (queryState.searchText && !searchable.includes(queryState.searchText)) return false;
  if (queryState.cluster && record.cluster !== queryState.cluster) return false;
  if (queryState.action && record.action !== queryState.action) return false;
  if (queryState.gloss && !record.gloss.toLowerCase().includes(queryState.gloss)) return false;
  return true;
}

function relationMatches(values, relationType) {
  if (!relationType) return true;
  return values.includes(relationType);
}

function selectedSemanticRecord(queryState) {
  return SEMANTIC_DHATU_RECORDS.find((record) => semanticRecordMatches(record, queryState)) || null;
}

function cardFromSemanticRecord(record) {
  return {
    cardId: `interactive.search.${record.dhatuId}`,
    cardType: "searchResult",
    label: "Search Results",
    value: `${record.iast} / ${record.root}`,
    metadata: {
      section: "Search Results",
      dhatuId: record.dhatuId,
      gloss: record.gloss,
      cluster: record.cluster,
      action: record.action,
    },
  };
}

function neighborCardsForRecord(record, queryState) {
  return record.neighbors
    .filter((neighbor) => relationMatches([neighbor.relationType], queryState.relationType))
    .map((neighbor, index) => ({
      cardId: `interactive.neighbor.${record.dhatuId}.${index + 1}`,
      cardType: "semanticNeighbor",
      label: "Semantic Neighbors",
      value: neighbor.nodeId,
      metadata: {
        section: "Semantic Neighbors",
        sourceNodeId: record.dhatuId,
        relationTypes: [neighbor.relationType],
        traversedEdgeIds: [neighbor.edgeId],
      },
    }));
}

function traversalCardsForRecord(record, queryState) {
  const depth = queryState.traversalDepth === 1 ? 1 : 2;
  return (record.traversalPaths[depth] || [])
    .filter((path) => relationMatches(path.relationTypes, queryState.relationType))
    .map((path, index) => ({
      cardId: `interactive.traversal.${record.dhatuId}.${depth}.${index + 1}`,
      cardType: "traversalPath",
      label: "Traversal Paths",
      value: path.value,
      metadata: {
        section: "Traversal Paths",
        sourceNodeId: record.dhatuId,
        terminalNodeId: path.terminalNodeId,
        depth,
        relationTypes: path.relationTypes,
        traversedEdgeIds: path.edgeIds,
      },
    }));
}

function highlightedSemanticEdgeIds(record, queryState) {
  if (!record) return [];
  const depth = queryState.traversalDepth === 1 ? 1 : 2;
  return (record.traversalPaths[depth] || [])
    .filter((path) => relationMatches(path.relationTypes, queryState.relationType))
    .flatMap((path) => path.edgeIds);
}

function sortedSemanticGraphNodes(nodes) {
  return [...(Array.isArray(nodes) ? nodes : [])].sort((left, right) => left.nodeId.localeCompare(right.nodeId));
}
function clampSemanticGraphZoom(value) {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) {
    return 1;
  }

  return Math.min(
    SEMANTIC_GRAPH_MAX_ZOOM,
    Math.max(SEMANTIC_GRAPH_MIN_ZOOM, numericValue),
  );
}

function sortedSemanticGraphEdges(edges) {
  return [...(Array.isArray(edges) ? edges : [])].sort((left, right) => {
    const relationDelta = SEMANTIC_GRAPH_RELATION_ORDER.indexOf(left.relationType) - SEMANTIC_GRAPH_RELATION_ORDER.indexOf(right.relationType);
    return relationDelta || left.edgeId.localeCompare(right.edgeId);
  });
}
function createSemanticGraphStore(seedPayload = SEMANTIC_GRAPH_FALLBACK) {
  const store = {
    nodeMap: new Map(),
    edgeMap: new Map(),
  };

  mergeSemanticGraphPayload(store, seedPayload);
  return store;
}

function semanticGraphNodeKey(node) {
  return text(node?.nodeId || node?.id, "");
}

function semanticGraphEdgeKey(edge) {
  return text(edge?.edgeId || edge?.id || `${edge?.sourceId || edge?.source}->${edge?.targetId || edge?.target}`, "");
}

function mergeSemanticGraphPayload(store, payload = {}) {
  if (!store) return createSemanticGraphStore(payload);

  const nodes = Array.isArray(payload.nodes) ? payload.nodes : [];
  const edges = Array.isArray(payload.edges) ? payload.edges : [];

  nodes.forEach((node) => {
    const nodeId = semanticGraphNodeKey(node);
    if (!nodeId) return;
    store.nodeMap.set(nodeId, {
      ...store.nodeMap.get(nodeId),
      ...node,
      nodeId,
    });
  });

  edges.forEach((edge) => {
    const edgeId = semanticGraphEdgeKey(edge);
    if (!edgeId) return;
    const sourceId = text(edge?.sourceId || edge?.source, "");
    const targetId = text(edge?.targetId || edge?.target, "");
    if (!sourceId || !targetId) return;

    store.edgeMap.set(edgeId, {
      ...store.edgeMap.get(edgeId),
      ...edge,
      edgeId,
      sourceId,
      targetId,
    });
  });

  return store;
}

function getSemanticGraphStore() {
  if (!semanticGraphStore) {
    semanticGraphStore = createSemanticGraphStore(SEMANTIC_GRAPH_FALLBACK);
  }
  return semanticGraphStore;
}

function getSemanticGraphSnapshot() {
  const store = getSemanticGraphStore();
  return {
    nodes: sortedSemanticGraphNodes(Array.from(store.nodeMap.values())),
    edges: sortedSemanticGraphEdges(Array.from(store.edgeMap.values())),
  };
}
function localSemanticNeighborPayloadForNode(nodeId) {
  const record = SEMANTIC_DHATU_RECORDS.find((item) => item.dhatuId === nodeId || item.cluster === nodeId);
  if (!record) return { nodes: [], edges: [] };

  const nodes = [];
  const edges = [];

  nodes.push({
    nodeId: record.dhatuId,
    label: `${record.iast} / ${record.root}`,
    nodeType: "dhatu",
    cluster: record.cluster,
    x: 10,
    y: 44,
  });

  record.neighbors.forEach((neighbor, index) => {
    nodes.push({
      nodeId: neighbor.nodeId,
      label: neighbor.nodeId,
      nodeType: "semantic_cluster",
      cluster: neighbor.nodeId,
      x: 34 + index * 18,
      y: 34 + index * 12,
    });

    edges.push({
      edgeId: neighbor.edgeId,
      sourceId: record.dhatuId,
      targetId: neighbor.nodeId,
      relationType: neighbor.relationType,
    });
  });

  return { nodes, edges };
}

function expandSemanticGraphNeighbors(nodeId) {
  const store = getSemanticGraphStore();
  const payload = localSemanticNeighborPayloadForNode(nodeId);
  mergeSemanticGraphPayload(store, payload);
  recordSemanticGraphExpansion(nodeId, payload);
  return getSemanticGraphSnapshot();
}

function recordSemanticGraphExpansion(nodeId, payload = {}, reason = "local-neighbor-expansion") {
  const nodes = Array.isArray(payload.nodes) ? payload.nodes : [];
  const edges = Array.isArray(payload.edges) ? payload.edges : [];

  semanticGraphExpansionHistory.push({
    step: semanticGraphExpansionHistory.length + 1,
    nodeId: text(nodeId, ""),
    reason,
    nodeCount: nodes.length,
    edgeCount: edges.length,
    nodeIds: nodes.map((node) => text(node?.nodeId || node?.id, "")).filter(Boolean),
    edgeIds: edges.map((edge) => text(edge?.edgeId || edge?.id, "")).filter(Boolean),
    generatedAt: new Date().toISOString(),
  });

  return semanticGraphExpansionHistory;
}

function getSemanticGraphExpansionHistory() {
  return semanticGraphExpansionHistory.map((entry) => ({ ...entry }));
}

function resetSemanticGraphExpansionHistory() {
  semanticGraphExpansionHistory = [];
}

function rebuildSemanticGraphStoreThroughStep(stepNumber) {
  const targetStep = Number(stepNumber);
  semanticGraphStore = createSemanticGraphStore(SEMANTIC_GRAPH_FALLBACK);

  if (!Number.isFinite(targetStep) || targetStep <= 0) {
    return getSemanticGraphSnapshot();
  }

  semanticGraphExpansionHistory
    .filter((entry) => entry.step <= targetStep)
    .forEach((entry) => {
      mergeSemanticGraphPayload(
        semanticGraphStore,
        localSemanticNeighborPayloadForNode(entry.nodeId),
      );
    });

  return getSemanticGraphSnapshot();
}

function replaySemanticGraphExpansionStep(stepNumber) {
  const snapshot = rebuildSemanticGraphStoreThroughStep(stepNumber);
  const queryState = readSemanticQueryState();
  const record = selectedSemanticRecord(queryState);
  renderSemanticGraphView(queryState, record);
  return snapshot;
}

function renderSemanticGraphReplayInspector() {
  const replay = byId("semantic-graph-replay");
  if (!replay) return;

  clearChildren(replay);

  const history = getSemanticGraphExpansionHistory();
  if (history.length === 0) {
    appendEmpty(replay, "No graph expansion history recorded");
    return;
  }

  history.forEach((entry) => {
    const row = document.createElement("button");
    row.type = "button";
    row.className = "semantic-graph-replay-step";
    row.textContent = `Step ${entry.step}: ${entry.nodeId} (${entry.nodeCount} nodes, ${entry.edgeCount} edges)`;
    row.title = `${entry.reason}; ${entry.generatedAt}`;
    row.addEventListener("click", () => replaySemanticGraphExpansionStep(entry.step));
    replay.appendChild(row);
  });
}

function ensureSemanticGraphCanvasSize(canvas) {
  const width = canvas.clientWidth || 600;
  const height = canvas.clientHeight || 320;
  const dpr = window.devicePixelRatio || 1;
  const nextWidth = Math.floor(width * dpr);
  const nextHeight = Math.floor(height * dpr);

  if (canvas.width !== nextWidth || canvas.height !== nextHeight) {
    canvas.width = nextWidth;
    canvas.height = nextHeight;
  }

  const ctx = canvas.getContext("2d");
  if (!ctx) return { width, height, ctx: null };

  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { width, height, ctx };
}

function normalizeSemanticGraphPoint(node, width, height) {
  const rawX = Number(node?.x);
  const rawY = Number(node?.y);
  const xPercent = Number.isFinite(rawX) ? rawX : 50;
  const yPercent = Number.isFinite(rawY) ? rawY : 50;

  return {
    x: (xPercent / 100) * width,
    y: (yPercent / 100) * height,
  };
}

function buildSemanticGraphNodeIndex(nodes = []) {
  const index = new Map();
  nodes.forEach((node) => {
    const nodeId = text(node?.nodeId || node?.id, "");
    if (nodeId) index.set(nodeId, node);
  });
  return index;
}

function shortSemanticGraphLabel(node) {
  const rawLabel = text(node?.label || node?.nodeId || node?.id, "");
  return rawLabel.length > 18 ? `${rawLabel.slice(0, 17)}…` : rawLabel;
}

function drawSemanticGraphCanvas(canvas, payload = {}) {
  const { width, height, ctx } = ensureSemanticGraphCanvasSize(canvas);

  if (!ctx) return;

  ctx.clearRect(0, 0, width, height);

  const nodes = Array.isArray(payload.nodes) ? payload.nodes : [];
  const edges = Array.isArray(payload.edges) ? payload.edges : [];
  const highlightedEdgeIds = payload.highlightedEdgeIds instanceof Set ? payload.highlightedEdgeIds : new Set();
  const highlightedNodeIds = payload.highlightedNodeIds instanceof Set ? payload.highlightedNodeIds : new Set();
  const selectedNodeId = text(payload.selectedNodeId, "");

  if (nodes.length === 0) {
    ctx.fillStyle = "#9fb0c7";
    ctx.font = "14px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("Semantic graph unavailable", width / 2, height / 2);
    return;
  }

  const nodeIndex = buildSemanticGraphNodeIndex(nodes);

  edges.forEach((edge) => {
    const sourceId = text(edge?.sourceId || edge?.source, "");
    const targetId = text(edge?.targetId || edge?.target, "");
    const source = nodeIndex.get(sourceId);
    const target = nodeIndex.get(targetId);
    if (!source || !target) return;

    const edgeId = text(edge?.edgeId || edge?.id, "");
    const edgeType = text(edge?.edgeType || edge?.type || edge?.relationType, "");
    const isHovered = edgeId === semanticGraphHoverEdgeId;
    const isHighlighted = highlightedEdgeIds.has(edgeId) || isHovered;
    const isStrong = edgeType.includes("derivation") || edgeType.includes("root");

    const sourceWorldPoint = semanticGraphNodeWorldPoint(source, width, height);
    const targetWorldPoint = semanticGraphNodeWorldPoint(target, width, height);
    const sourcePoint = semanticGraphWorldToScreen(sourceWorldPoint, width, height);
    const targetPoint = semanticGraphWorldToScreen(targetWorldPoint, width, height);

    ctx.beginPath();
    ctx.moveTo(sourcePoint.x, sourcePoint.y);
    ctx.lineTo(targetPoint.x, targetPoint.y);
    ctx.strokeStyle = isHighlighted
      ? "rgba(212, 175, 55, 0.85)"
      : isStrong
        ? "rgba(104, 190, 255, 0.45)"
        : "rgba(159, 176, 199, 0.25)";
    ctx.lineWidth = isHovered ? 3 : isHighlighted ? 2.25 : isStrong ? 1.5 : 1;
    ctx.stroke();
  });

  nodes.forEach((node) => {
    const nodeId = text(node?.nodeId || node?.id, "");
    const nodeType = text(node?.nodeType || node?.type, "");
    const isSelected = nodeId === selectedNodeId;
    const isHighlighted = highlightedNodeIds.has(nodeId);
    const isHovered = nodeId === semanticGraphHoverNodeId;
    const isRoot = nodeType === "dhatu" || nodeType === "root" || nodeType.includes("dhatu");
    const worldPoint = semanticGraphNodeWorldPoint(node, width, height);
    const point = semanticGraphWorldToScreen(worldPoint, width, height);
    const radius = isHovered ? (isRoot ? 11 : 8) : (isRoot ? 8 : 5);

    ctx.beginPath();
    ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
    ctx.fillStyle = isSelected
      ? "#f0d77a"
      : isHighlighted
        ? "rgba(104, 190, 255, 0.35)"
        : "#100e08";
    ctx.fill();

    ctx.strokeStyle = isHovered
      ? "#f0d77a"
      : isSelected
        ? "#d4af37"
        : isHighlighted
          ? "#68beff"
          : "rgba(159, 176, 199, 0.4)";
    ctx.lineWidth = isHovered ? 2.5 : isSelected ? 2 : 1.5;
    ctx.stroke();
  });

  ctx.textAlign = "center";
  ctx.textBaseline = "top";

  nodes.forEach((node) => {
    const nodeId = text(node?.nodeId || node?.id, "");
    const isSelected = nodeId === selectedNodeId;
    const isHovered = nodeId === semanticGraphHoverNodeId;
    const worldPoint = semanticGraphNodeWorldPoint(node, width, height);
    const point = semanticGraphWorldToScreen(worldPoint, width, height);
    const label = shortSemanticGraphLabel(node);

    ctx.fillStyle = isHovered || isSelected ? "#f0d77a" : "#eef3f8";
    ctx.font = isHovered || isSelected ? "bold 12px sans-serif" : "11px sans-serif";
    ctx.fillText(label, point.x, point.y + 10);
  });
}

function getSemanticGraphCanvasCoordinates(canvas, event) {
  const rect = canvas.getBoundingClientRect();

  return {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top,
  };
}

function handleSemanticGraphWheel(event) {
  event.preventDefault();

  const canvas = event.currentTarget;
  if (!canvas) return;

  const { width, height } = ensureSemanticGraphCanvasSize(canvas);
  const pointer = getSemanticGraphCanvasCoordinates(canvas, event);
  const previousZoom = clampSemanticGraphZoom(semanticGraphCamera.zoom);
  const zoomFactor = Math.exp(-event.deltaY * SEMANTIC_GRAPH_WHEEL_ZOOM_SPEED);
  const nextZoom = clampSemanticGraphZoom(previousZoom * zoomFactor);

  if (nextZoom === previousZoom) return;

  const worldPoint = semanticGraphScreenToWorld(pointer, width, height, {
    ...semanticGraphCamera,
    zoom: previousZoom,
  });

  semanticGraphCamera.zoom = nextZoom;
  semanticGraphCamera.x = worldPoint.x - ((pointer.x - (width / 2)) / nextZoom);
  semanticGraphCamera.y = worldPoint.y - ((pointer.y - (height / 2)) / nextZoom);
  requestSemanticGraphRedraw();
} 

function beginSemanticGraphPan(event) {
  const canvas = event.currentTarget;
  if (!canvas) return;

  semanticGraphPanState = {
    pointerId: event.pointerId,
    startX: event.clientX,
    startY: event.clientY,
    lastX: event.clientX,
    lastY: event.clientY,
    moved: false,
  };

  canvas.setPointerCapture?.(event.pointerId);
}

function moveSemanticGraphPan(event) {
  if (!semanticGraphPanState || semanticGraphPanState.pointerId !== event.pointerId) {
    return;
  }

  const dx = event.clientX - semanticGraphPanState.lastX;
  const dy = event.clientY - semanticGraphPanState.lastY;
  const totalDx = event.clientX - semanticGraphPanState.startX;
  const totalDy = event.clientY - semanticGraphPanState.startY;

  if (
    Math.abs(totalDx) > SEMANTIC_GRAPH_PAN_CLICK_TOLERANCE ||
    Math.abs(totalDy) > SEMANTIC_GRAPH_PAN_CLICK_TOLERANCE
  ) {
    semanticGraphPanState.moved = true;
  }

  semanticGraphCamera.x -= dx / semanticGraphCamera.zoom;
  semanticGraphCamera.y -= dy / semanticGraphCamera.zoom;

  semanticGraphPanState.lastX = event.clientX;
  semanticGraphPanState.lastY = event.clientY;

  requestSemanticGraphRedraw();
}

function endSemanticGraphPan(event) {
  if (!semanticGraphPanState || semanticGraphPanState.pointerId !== event.pointerId) {
    return;
  }

  const canvas = event.currentTarget;
  canvas?.releasePointerCapture?.(event.pointerId);
  semanticGraphPanState = null;
}

function semanticGraphWorldToScreen(point, width, height, camera = semanticGraphCamera) {
  return {
    x: ((point.x - camera.x) * camera.zoom) + (width / 2),
    y: ((point.y - camera.y) * camera.zoom) + (height / 2),
  };
}

function semanticGraphScreenToWorld(point, width, height, camera = semanticGraphCamera) {
  return {
    x: ((point.x - (width / 2)) / camera.zoom) + camera.x,
    y: ((point.y - (height / 2)) / camera.zoom) + camera.y,
  };
}

function semanticGraphNodeWorldPoint(node, width, height) {
  return normalizeSemanticGraphPoint(node, width, height);
}

function semanticGraphPointToSegmentDistance(point, start, end) {
  const dx = end.x - start.x;
  const dy = end.y - start.y;

  if (dx === 0 && dy === 0) {
    const px = point.x - start.x;
    const py = point.y - start.y;
    return Math.sqrt((px * px) + (py * py));
  }

  const projection = (
    (
      ((point.x - start.x) * dx)
      + ((point.y - start.y) * dy)
    )
    / ((dx * dx) + (dy * dy))
  );

  const clampedProjection = Math.max(0, Math.min(1, projection));

  const closestX = start.x + (clampedProjection * dx);
  const closestY = start.y + (clampedProjection * dy);

  const distanceX = point.x - closestX;
  const distanceY = point.y - closestY;

  return Math.sqrt(
    (distanceX * distanceX)
    + (distanceY * distanceY)
  );
}

function findSemanticGraphNodeAtPoint(x, y, nodes = [], width = 600, height = 320, hitRadius = 15) {
  const hitRadiusSquared = hitRadius * hitRadius;

  for (let index = nodes.length - 1; index >= 0; index -= 1) {
    const node = nodes[index];
    const nodeId = text(node?.nodeId || node?.id, "");
    if (!nodeId) continue;

    const worldPoint = semanticGraphNodeWorldPoint(node, width, height);
    const point = semanticGraphWorldToScreen(worldPoint, width, height);
    const dx = x - point.x;
    const dy = y - point.y;
    const distanceSquared = (dx * dx) + (dy * dy);

    if (distanceSquared <= hitRadiusSquared) {
      return nodeId;
    }
  }

  return null;
}

function findSemanticGraphEdgeAtPoint(x, y, nodes = [], edges = [], width = 600, height = 320) {
  const nodeIndex = buildSemanticGraphNodeIndex(nodes);
  const point = { x, y };

  for (let index = edges.length - 1; index >= 0; index -= 1) {
    const edge = edges[index];
    const source = nodeIndex.get(text(edge?.sourceId || edge?.source, ""));
    const target = nodeIndex.get(text(edge?.targetId || edge?.target, ""));

    if (!source || !target) continue;

    const sourcePoint = semanticGraphWorldToScreen(
      semanticGraphNodeWorldPoint(source, width, height),
      width,
      height,
    );

    const targetPoint = semanticGraphWorldToScreen(
      semanticGraphNodeWorldPoint(target, width, height),
      width,
      height,
    );

    const padding = SEMANTIC_GRAPH_EDGE_HOVER_TOLERANCE;
    const minX = Math.min(sourcePoint.x, targetPoint.x) - padding;
    const maxX = Math.max(sourcePoint.x, targetPoint.x) + padding;
    const minY = Math.min(sourcePoint.y, targetPoint.y) - padding;
    const maxY = Math.max(sourcePoint.y, targetPoint.y) + padding;

    if (x < minX || x > maxX || y < minY || y > maxY) {
      continue;
    }

    const distance = semanticGraphPointToSegmentDistance(
      point,
      sourcePoint,
      targetPoint,
    );

    if (distance <= SEMANTIC_GRAPH_EDGE_HOVER_TOLERANCE) {
      return text(edge?.edgeId || edge?.id, "");
    }
  }

  return null;
}

function zoomSemanticGraph(scaleFactor) {
  const factor = Number(scaleFactor);

  if (!Number.isFinite(factor) || factor <= 0) {
    return;
  }

  semanticGraphCamera.zoom = clampSemanticGraphZoom(
    semanticGraphCamera.zoom * factor,
  );

  requestSemanticGraphRedraw();
}

function resetSemanticGraphCamera() {
  semanticGraphCamera.x = 0;
  semanticGraphCamera.y = 0;
  semanticGraphCamera.zoom = 1;

  requestSemanticGraphRedraw();
}

function fitSemanticGraphToView() {
  const canvas = byId("semantic-graph-canvas");
  if (!canvas) return;

  const graph = getSemanticGraphSnapshot();
  const nodes = Array.isArray(graph.nodes) ? graph.nodes : [];

  if (nodes.length === 0) {
    resetSemanticGraphCamera();
    return;
  }

  const { width, height } = ensureSemanticGraphCanvasSize(canvas);

  const points = nodes.map((node) =>
    semanticGraphNodeWorldPoint(node, width, height),
  );

  const minX = Math.min(...points.map((point) => point.x));
  const maxX = Math.max(...points.map((point) => point.x));
  const minY = Math.min(...points.map((point) => point.y));
  const maxY = Math.max(...points.map((point) => point.y));

  const contentWidth = Math.max(1, maxX - minX);
  const contentHeight = Math.max(1, maxY - minY);

  const availableWidth = Math.max(
    1,
    width - (SEMANTIC_GRAPH_FIT_PADDING * 2),
  );

  const availableHeight = Math.max(
    1,
    height - (SEMANTIC_GRAPH_FIT_PADDING * 2),
  );

  const zoomX = availableWidth / contentWidth;
  const zoomY = availableHeight / contentHeight;

  semanticGraphCamera.zoom = clampSemanticGraphZoom(
    Math.min(zoomX, zoomY),
  );

  semanticGraphCamera.x = minX + (contentWidth / 2);
  semanticGraphCamera.y = minY + (contentHeight / 2);

  requestSemanticGraphRedraw();
}

function applySemanticGraphCameraPreset(preset) {
  switch (preset) {
    case "home":
      semanticGraphCamera.x = 0;
      semanticGraphCamera.y = 0;
      semanticGraphCamera.zoom = 1;
      break;

    case "detail":
      semanticGraphCamera.zoom = clampSemanticGraphZoom(2.2);
      break;

    case "overview":
      fitSemanticGraphToView();
      return;

    default:
      return;
  }

  requestSemanticGraphRedraw();
}

function initializeSemanticGraphZoomControls() {
  semanticGraphZoomInButton?.addEventListener("click", () => {
    zoomSemanticGraph(SEMANTIC_GRAPH_BUTTON_ZOOM_FACTOR);
  });

  semanticGraphZoomOutButton?.addEventListener("click", () => {
    zoomSemanticGraph(1 / SEMANTIC_GRAPH_BUTTON_ZOOM_FACTOR);
  });

  semanticGraphResetCameraButton?.addEventListener("click", () => {
    resetSemanticGraphCamera();
  });

  semanticGraphFitViewButton?.addEventListener("click", () => {
    fitSemanticGraphToView();
  });

  semanticGraphPresetHomeButton?.addEventListener("click", () => {
    applySemanticGraphCameraPreset("home");
  });

  semanticGraphPresetDetailButton?.addEventListener("click", () => {
    applySemanticGraphCameraPreset("detail");
  });

  semanticGraphPresetOverviewButton?.addEventListener("click", () => {
    applySemanticGraphCameraPreset("overview");
  });

  semanticGraphMinimapCanvas?.addEventListener("click", handleSemanticGraphMinimapClick);
}

function handleSemanticGraphKeyboard(event) {
  const activeElement = document.activeElement;
  const isTyping =
    activeElement &&
    (
      activeElement.tagName === "INPUT"
      || activeElement.tagName === "TEXTAREA"
      || activeElement.isContentEditable
    );

  if (isTyping) return;

  switch (event.key) {
    case "+":
    case "=":
      event.preventDefault();
      zoomSemanticGraph(SEMANTIC_GRAPH_BUTTON_ZOOM_FACTOR);
      break;

    case "-":
    case "_":
      event.preventDefault();
      zoomSemanticGraph(1 / SEMANTIC_GRAPH_BUTTON_ZOOM_FACTOR);
      break;

    case "0":
      event.preventDefault();
      resetSemanticGraphCamera();
      break;

    case "f":
    case "F":
      event.preventDefault();
      fitSemanticGraphToView();
      break;

    case "ArrowLeft":
      event.preventDefault();
      semanticGraphCamera.x -= (
        SEMANTIC_GRAPH_KEYBOARD_PAN_STEP
        / semanticGraphCamera.zoom
      );
      requestSemanticGraphRedraw();
      break;

    case "ArrowRight":
      event.preventDefault();
      semanticGraphCamera.x += (
        SEMANTIC_GRAPH_KEYBOARD_PAN_STEP
        / semanticGraphCamera.zoom
      );
      requestSemanticGraphRedraw();
      break;

    case "ArrowUp":
      event.preventDefault();
      semanticGraphCamera.y -= (
        SEMANTIC_GRAPH_KEYBOARD_PAN_STEP
        / semanticGraphCamera.zoom
      );
      requestSemanticGraphRedraw();
      break;

    case "ArrowDown":
      event.preventDefault();
      semanticGraphCamera.y += (
        SEMANTIC_GRAPH_KEYBOARD_PAN_STEP
        / semanticGraphCamera.zoom
      );
      requestSemanticGraphRedraw();
      break;

    default:
      break;
  }
}

function renderSemanticGraphCameraStatus() {
  if (!semanticGraphCameraStatus) return;

  semanticGraphCameraStatus.textContent =
    `zoom ${semanticGraphCamera.zoom.toFixed(2)} × `
    + `x ${semanticGraphCamera.x.toFixed(1)} `
    + `y ${semanticGraphCamera.y.toFixed(1)}`;
}

function semanticGraphMinimapProjection(nodes = []) {
  const canvas = semanticGraphMinimapCanvas;

  if (!canvas || canvas.tagName?.toLowerCase() !== "canvas") {
    return null;
  }

  const width = canvas.width || 180;
  const height = canvas.height || 120;

  if (!Array.isArray(nodes) || nodes.length === 0) {
    return null;
  }

  const points = nodes.map((node) =>
    semanticGraphNodeWorldPoint(node, width, height),
  );

  const minX = Math.min(...points.map((point) => point.x));
  const maxX = Math.max(...points.map((point) => point.x));
  const minY = Math.min(...points.map((point) => point.y));
  const maxY = Math.max(...points.map((point) => point.y));

  const graphWidth = Math.max(1, maxX - minX);
  const graphHeight = Math.max(1, maxY - minY);

  return {
    width,
    height,
    minX,
    minY,
    graphWidth,
    graphHeight,
    scale: Math.min(
      (width - 16) / graphWidth,
      (height - 16) / graphHeight,
    ),
  };
}

function renderSemanticGraphMinimap(nodes = []) {
  const canvas = semanticGraphMinimapCanvas;

  if (!canvas || canvas.tagName?.toLowerCase() !== "canvas") {
    return;
  }

  const context = canvas.getContext("2d");
  if (!context) return;

  const width = canvas.width || 180;
  const height = canvas.height || 120;

  context.clearRect(0, 0, width, height);

  if (!Array.isArray(nodes) || nodes.length === 0) {
    return;
  }

  const projection = semanticGraphMinimapProjection(nodes);

  if (!projection) {
  return;
  }

  const {
  minX,
  minY,
  scale,
  } = projection;

  const points = nodes.map((node) =>
  semanticGraphNodeWorldPoint(node, width, height),
  );

  context.fillStyle = "#081018";
  context.fillRect(0, 0, width, height);

  points.forEach((point) => {
    const x = ((point.x - minX) * scale) + 8;
    const y = ((point.y - minY) * scale) + 8;

    context.beginPath();
    context.arc(x, y, 2, 0, Math.PI * 2);
    context.fillStyle = "#7dd3fc";
    context.fill();
  });

  const viewportWidth = width / semanticGraphCamera.zoom;
  const viewportHeight = height / semanticGraphCamera.zoom;

  const viewportX = (
    ((semanticGraphCamera.x - minX) * scale)
    + 8
    - (viewportWidth / 2)
  );

  const viewportY = (
    ((semanticGraphCamera.y - minY) * scale)
    + 8
    - (viewportHeight / 2)
  );

  context.strokeStyle = "#f59e0b";
  context.lineWidth = 1.5;

  context.strokeRect(
    viewportX,
    viewportY,
    viewportWidth,
    viewportHeight,
  );
}

function handleSemanticGraphMinimapClick(event) {
  const canvas = event.currentTarget;
  if (!canvas || canvas.tagName?.toLowerCase() !== "canvas") {
    return;
  }

  const graph = getSemanticGraphSnapshot();
  const projection = semanticGraphMinimapProjection(graph.nodes);

  if (!projection) {
    return;
  }

  const rect = canvas.getBoundingClientRect();
  const clickX = event.clientX - rect.left;
  const clickY = event.clientY - rect.top;

  semanticGraphCamera.x = projection.minX + ((clickX - 8) / projection.scale);
  semanticGraphCamera.y = projection.minY + ((clickY - 8) / projection.scale);

  requestSemanticGraphRedraw();
}

function requestSemanticGraphRedraw() {
  if (semanticGraphRenderPending) return;

  semanticGraphRenderPending = true;
  requestAnimationFrame(() => {
    const queryState = readSemanticQueryState();
    const record = selectedSemanticRecord(queryState);
    renderSemanticGraphView(queryState, record);
    semanticGraphRenderPending = false;
  });
}

function renderSemanticGraphView(queryState = readSemanticQueryState(), record = selectedSemanticRecord(queryState)) {
  const graph = getSemanticGraphSnapshot();
  const nodes = graph.nodes;
  const edges = graph.edges;

  const highlightedEdgeIds = new Set(highlightedSemanticEdgeIds(record, queryState));
  const highlightedNodeIds = new Set();

  edges.forEach((edge) => {
    if (highlightedEdgeIds.has(edge.edgeId)) {
      highlightedNodeIds.add(edge.sourceId);
      highlightedNodeIds.add(edge.targetId);
    }
  });

  const selectedNodeId = selectedSemanticGraphNodeId || record?.dhatuId || "01.0005";
  const selectedNode = nodes.find((node) => node.nodeId === selectedNodeId) || nodes[0];

  const canvas = byId("semantic-graph-canvas");
  if (canvas && canvas.tagName?.toLowerCase() === "canvas") {
  drawSemanticGraphCanvas(canvas, {
    nodes,
    edges,
    highlightedEdgeIds,
    highlightedNodeIds,
    selectedNodeId,
  });
  attachSemanticGraphCanvasInteraction(canvas);
}

renderSemanticGraphCameraStatus();
renderSemanticGraphMinimap(nodes);

  const summary = byId("semantic-graph-summary");
  clearChildren(summary);

  if (summary) {
    appendInspectionRow(
      summary,
      "Node",
      selectedSemanticNodeSummary(selectedNode),
    );
  }

  const edgeList = byId("semantic-graph-edges");
  clearChildren(edgeList);

  if (edgeList) {
    if (edges.length === 0) {
      appendEmpty(edgeList, "No semantic relation edges available");
    }

    edges.forEach((edge) => {
      edgeList.appendChild(
        renderSemanticGraphEdge(edge, highlightedEdgeIds),
      );
    });
  }

  renderSemanticGraphLegend(edges, highlightedEdgeIds);
  renderSemanticGraphEdgeHoverInspector(edges);
  renderSemanticGraphReplayInspector();

  const safety = byId("semantic-graph-safety");
  clearChildren(safety);

  if (safety) {
    const note = document.createElement("div");
    note.className = "semantic-graph-safety-note";
    note.textContent = SEMANTIC_DHATU_FALLBACK_PANEL.safetyNote;
    safety.appendChild(note);
  }
}

function attachSemanticGraphCanvasInteraction(canvas) {
  if (!canvas || semanticGraphInteractionAttached) return;

  semanticGraphInteractionAttached = true;

  canvas.addEventListener("pointerdown", beginSemanticGraphPan);
  canvas.addEventListener("pointermove", moveSemanticGraphPan);
  canvas.addEventListener("pointerup", endSemanticGraphPan);
  canvas.addEventListener("pointercancel", endSemanticGraphPan);

  canvas.addEventListener("mousemove", (event) => {
    semanticGraphMousePosition = getSemanticGraphCanvasCoordinates(canvas, event);

    const graph = getSemanticGraphSnapshot();
    const width = canvas.clientWidth || 600;
    const height = canvas.clientHeight || 320;

    const hoveredNodeId = findSemanticGraphNodeAtPoint(
  semanticGraphMousePosition.x,
  semanticGraphMousePosition.y,
  graph.nodes,
  width,
  height,
);

const hoveredEdgeId = hoveredNodeId
  ? null
  : findSemanticGraphEdgeAtPoint(
      semanticGraphMousePosition.x,
      semanticGraphMousePosition.y,
      graph.nodes,
      graph.edges,
      width,
      height,
    );

if (
  semanticGraphHoverNodeId !== hoveredNodeId
  || semanticGraphHoverEdgeId !== hoveredEdgeId
) {
  semanticGraphHoverNodeId = hoveredNodeId;
  semanticGraphHoverEdgeId = hoveredEdgeId;
  canvas.style.cursor = hoveredNodeId ? "pointer" : hoveredEdgeId ? "crosshair" : "grab";
  requestSemanticGraphRedraw();
}
  });

  canvas.addEventListener("mouseleave", () => {
  if (semanticGraphHoverNodeId !== null || semanticGraphHoverEdgeId !== null) {
    semanticGraphHoverNodeId = null;
    semanticGraphHoverEdgeId = null;
    canvas.style.cursor = "grab";
    requestSemanticGraphRedraw();
  }
});

  canvas.addEventListener("click", () => {
    if (semanticGraphPanState?.moved) return;
    if (!semanticGraphHoverNodeId) return;

    focusSemanticGraphNode(semanticGraphHoverNodeId);
  });

  canvas.addEventListener(
    "wheel",
    handleSemanticGraphWheel,
    { passive: false },
  );

  canvas.style.cursor = "grab";
}

function renderSemanticGraphNode(node, selectedNodeId, highlightedNodeIds) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "semantic-graph-node";
  button.style.left = `${node.x}%`;
  button.style.top = `${node.y}%`;
  button.dataset.nodeId = node.nodeId;
  button.textContent = node.label;
  button.title = `${node.nodeType}: ${node.nodeId}`;
  button.setAttribute("aria-label", `${node.label}, ${node.nodeType}`);
  button.setAttribute("aria-pressed", node.nodeId === selectedNodeId ? "true" : "false");
  button.classList.toggle("selected", node.nodeId === selectedNodeId);
  button.classList.toggle("traversal-highlight", highlightedNodeIds.has(node.nodeId));
  button.addEventListener("click", () => focusSemanticGraphNode(node.nodeId));
  button.addEventListener("keydown", (event) => handleSemanticGraphNodeKeydown(event, node.nodeId));
  return button;
}

function renderSemanticGraphEdge(edge, highlightedEdgeIds) {
  const row = document.createElement("div");
  row.className = "semantic-graph-edge";
  row.classList.toggle("traversal-highlight", highlightedEdgeIds.has(edge.edgeId));

  const relation = document.createElement("strong");
  relation.textContent = edge.relationType;
  const path = document.createElement("span");
  path.textContent = `${edge.sourceId} -> ${edge.targetId}`;

  row.append(relation, path);
  return row;
}

function renderSemanticGraphEdgeHoverInspector(edges = []) {
  const container = byId("semantic-graph-highlight-note");

  if (!container) return;

  const hoveredEdge = edges.find((edge) => edge.edgeId === semanticGraphHoverEdgeId);

  if (!hoveredEdge) {
    container.textContent = "Highlighted nodes and edges follow the active traversal filters.";
    return;
  }

  container.textContent = [
    `Hovered edge: ${hoveredEdge.edgeId}`,
    `Relation: ${hoveredEdge.relationType}`,
    `Path: ${hoveredEdge.sourceId} → ${hoveredEdge.targetId}`,
  ].join(" | ");
}

function semanticGraphClusterCounts(nodes = []) {
  return nodes.reduce((counts, node) => {
    const cluster = text(node?.cluster || node?.nodeType || "unknown", "unknown");
    counts[cluster] = (counts[cluster] || 0) + 1;
    return counts;
  }, {});
}

function renderSemanticGraphLegend(edges, highlightedEdgeIds) {
  const legend = byId("semantic-graph-legend");
  clearChildren(legend);
  if (!legend) return;
  const graph = getSemanticGraphSnapshot();
const clusterCounts = semanticGraphClusterCounts(graph.nodes);
const separator = document.createElement("div");
separator.className = "semantic-graph-legend-separator";
separator.textContent = "Relations";
legend.appendChild(separator);

Object.entries(clusterCounts).forEach(([cluster, count]) => {
  const item = document.createElement("div");
  item.className = "semantic-graph-legend-item";
  item.setAttribute("role", "listitem");

  const marker = document.createElement("span");
  marker.className = "semantic-graph-legend-marker";
  marker.setAttribute("aria-hidden", "true");

  const label = document.createElement("span");
  label.textContent = `${cluster}: ${count}`;

  item.append(marker, label);
  legend.appendChild(item);
});
  const relations = SEMANTIC_GRAPH_RELATION_ORDER.filter((relation) => edges.some((edge) => edge.relationType === relation));
  if (relations.length === 0) {
    appendEmpty(legend, "No relation legend available");
    return;
  }
  relations.forEach((relation) => {
    const item = document.createElement("div");
    item.className = "semantic-graph-legend-item";
    item.setAttribute("role", "listitem");
    item.classList.toggle("traversal-highlight", edges.some((edge) => edge.relationType === relation && highlightedEdgeIds.has(edge.edgeId)));
    const marker = document.createElement("span");
    marker.className = "semantic-graph-legend-marker";
    marker.setAttribute("aria-hidden", "true");
    const label = document.createElement("span");
    label.textContent = relation;
    item.append(marker, label);
    legend.appendChild(item);
  });
}

function selectedSemanticNodeSummary(node) {
  if (!node) return "No semantic node selected";
  return `${node.label} (${node.nodeType}; ${node.nodeId})`;
}



function focusSemanticGraphNode(nodeId) {
  selectedSemanticGraphNodeId = nodeId;
  const record = SEMANTIC_DHATU_RECORDS.find((item) => item.dhatuId === nodeId || item.cluster === nodeId);
  if (record) {
    if (semanticSearchInput) semanticSearchInput.value = record.iast;
    if (semanticClusterFilter) semanticClusterFilter.value = record.cluster;
  }
  expandSemanticGraphNeighbors(nodeId);
  renderSemanticQueryState();
}

function buildSemanticPanelFromQueryState(queryState = readSemanticQueryState()) {
  const record = selectedSemanticRecord(queryState);
  if (!record) {
    return {
      ...(semanticPanelData || SEMANTIC_DHATU_FALLBACK_PANEL),
      panelType: "semanticInteractive",
      title: "Semantic Query Panel",
      cards: [],
    };
  }
  return {
    ...(semanticPanelData || SEMANTIC_DHATU_FALLBACK_PANEL),
    panelType: "semanticInteractive",
    title: "Semantic Query Panel",
    primaryDhatu: {
      dhatuId: record.dhatuId,
      root: record.root,
      iast: record.iast,
      gloss: record.gloss,
    },
    cards: [
      cardFromSemanticRecord(record),
      ...neighborCardsForRecord(record, queryState),
      ...traversalCardsForRecord(record, queryState),
    ],
  };
}

function renderSemanticQueryState() {
  const queryState = readSemanticQueryState();
  const record = selectedSemanticRecord(queryState);
  selectedSemanticGraphNodeId = record?.dhatuId || selectedSemanticGraphNodeId;
  renderSemanticDhatuPanel(buildSemanticPanelFromQueryState(queryState));
  renderSemanticDerivationPanel(record?.dhatuId || selectedSemanticGraphNodeId);
  renderSemanticGraphView(queryState, record);
}

function resetSemanticQueryControls() {
  if (semanticSearchInput) semanticSearchInput.value = SEMANTIC_QUERY_DEFAULTS.searchText;
  if (semanticClusterFilter) semanticClusterFilter.value = SEMANTIC_QUERY_DEFAULTS.cluster;
  if (semanticActionFilter) semanticActionFilter.value = SEMANTIC_QUERY_DEFAULTS.action;
  if (semanticGlossFilter) semanticGlossFilter.value = SEMANTIC_QUERY_DEFAULTS.gloss;
  if (semanticDepthSelect) semanticDepthSelect.value = String(SEMANTIC_QUERY_DEFAULTS.traversalDepth);
  if (semanticRelationFilter) semanticRelationFilter.value = SEMANTIC_QUERY_DEFAULTS.relationType;
  renderSemanticQueryState();
}

function readSemanticDerivationFilterState() {
  return {
    family: semanticDerivationFamilyFilter?.value || "",
    domain: semanticDerivationDomainFilter?.value || "",
    relation: semanticDerivationRelationFilter?.value || "",
  };
}

function resetSemanticDerivationFilters() {
  if (semanticDerivationFamilyFilter) semanticDerivationFamilyFilter.value = SEMANTIC_DERIVATION_DEFAULTS.family;
  if (semanticDerivationDomainFilter) semanticDerivationDomainFilter.value = SEMANTIC_DERIVATION_DEFAULTS.domain;
  if (semanticDerivationRelationFilter) semanticDerivationRelationFilter.value = SEMANTIC_DERIVATION_DEFAULTS.relation;
  renderSemanticQueryState();
}

function dhatuDisplayRecord(dhatuId) {
  return SEMANTIC_DHATU_RECORDS.find((record) => record.dhatuId === dhatuId) || null;
}

function semanticDerivationRecords() {
  const payload = semanticDerivationData && typeof semanticDerivationData === "object"
    ? semanticDerivationData
    : SEMANTIC_DERIVATION_FALLBACK_DATA;
  return Array.isArray(payload.records) ? payload.records : [];
}

function selectedSemanticDerivationRecord(dhatuId) {
  return semanticDerivationRecords().find((record) => record.dhatuId === dhatuId) || null;
}

function semanticDerivationMatchesFilters(record, filters = readSemanticDerivationFilterState()) {
  if (!record) return false;
  if (filters.family && record.derivationFamilyId !== filters.family) return false;
  if (filters.domain && !record.usageDomains?.includes(filters.domain)) return false;
  if (filters.relation && !record.protoDerivationRelations?.some((relation) => relation.relationType === filters.relation)) return false;
  return true;
}

function renderSemanticDerivationCard(label, value, detail) {
  const row = document.createElement("article");
  row.className = "semantic-derivation-card";
  const title = document.createElement("strong");
  title.textContent = text(label, "Derivation field");
  const body = document.createElement("span");
  body.textContent = text(value);
  row.append(title, body);
  if (detail) {
    const small = document.createElement("small");
    small.textContent = detail;
    row.appendChild(small);
  }
  return row;
}

function renderSemanticDerivationList(container, items, formatter, emptyMessage) {
  clearChildren(container);
  if (!container) return;
  const values = Array.isArray(items) ? items : [];
  if (values.length === 0) {
    appendEmpty(container, emptyMessage);
    return;
  }
  values.forEach((item, index) => {
    container.appendChild(formatter(item, index));
  });
}

function renderSemanticDerivationSummary(record, displayRecord) {
  const summary = byId("semantic-derivation-summary-output");
  clearChildren(summary);
  if (!summary) return;
  if (!record) {
    appendEmpty(summary, "No derivation data exists for this dhatu selection");
    return;
  }
  [
    ["Selected dhatu id", record.dhatuId],
    ["Root", displayRecord?.root],
    ["IAST", displayRecord?.iast || record.rootIast],
    ["Derivation family id", record.derivationFamilyId],
    ["Usage domains", record.usageDomains?.join(", ")],
    ["Review status", record.reviewStatus],
  ].forEach(([label, value]) => summary.appendChild(renderSemanticDerivationCard(label, value)));
}

function renderSemanticDerivationPanel(dhatuId = selectedSemanticGraphNodeId) {
  const candidate = selectedSemanticDerivationRecord(dhatuId);
  const record = semanticDerivationMatchesFilters(candidate) ? candidate : null;
  const displayRecord = dhatuDisplayRecord(dhatuId);

  renderSemanticDerivationSummary(record, displayRecord);
  renderSemanticDerivationList(
    byId("semantic-derivation-lineage-output"),
    record?.semanticLineage,
    (item, index) => renderSemanticDerivationCard(`Lineage ${index + 1}`, item),
    "No semantic lineage available for this selection",
  );
  renderSemanticDerivationList(
    byId("semantic-derivation-hints-output"),
    record?.conceptualAffixHints,
    (hint) => renderSemanticDerivationCard(
      hint.label,
      hint.hintId,
      `${text(hint.confidence)}; ${text(hint.source)}; ${text(hint.note)}`,
    ),
    "No conceptual affix hints available",
  );
  renderSemanticDerivationList(
    byId("semantic-derivation-relations-output"),
    record?.protoDerivationRelations,
    (relation) => renderSemanticDerivationCard(
      relation.relationType,
      `${relation.sourceDerivationId} -> ${relation.targetDerivationId}`,
      `${text(relation.confidence)}; ${text(relation.source)}; ${text(relation.note)}`,
    ),
    "No proto derivation relations match the selected filters",
  );
  renderSemanticDerivationList(
    byId("semantic-derivation-notes-output"),
    record?.semanticTransformationNotes,
    (note, index) => renderSemanticDerivationCard(`Note ${index + 1}`, note),
    "No semantic transformation notes available",
  );

  const paniniContainer = byId("semantic-derivation-panini-output");
  clearChildren(paniniContainer);
  if (paniniContainer) {
    if (!record?.placeholderPaniniRelation) {
      appendEmpty(paniniContainer, "No placeholder Panini relation available");
    } else {
      const relation = record.placeholderPaniniRelation;
      paniniContainer.appendChild(renderSemanticDerivationCard("Status", relation.status));
      paniniContainer.appendChild(renderSemanticDerivationCard("Review status", relation.reviewStatus));
      paniniContainer.appendChild(renderSemanticDerivationCard("Source", relation.source, relation.note));
    }
  }

  const safety = byId("semantic-derivation-safety");
  if (safety) safety.textContent = SEMANTIC_DERIVATION_PLACEHOLDER_WARNING;
}

function readSemanticDerivationGraphFilterState() {
  return {
    family: semanticDerivationGraphFamilyFilter?.value || "",
    domain: semanticDerivationGraphDomainFilter?.value || "",
    relation: semanticDerivationGraphRelationFilter?.value || "",
  };
}

function resetSemanticDerivationGraphFilters() {
  if (semanticDerivationGraphFamilyFilter) semanticDerivationGraphFamilyFilter.value = SEMANTIC_DERIVATION_GRAPH_DEFAULTS.family;
  if (semanticDerivationGraphDomainFilter) semanticDerivationGraphDomainFilter.value = SEMANTIC_DERIVATION_GRAPH_DEFAULTS.domain;
  if (semanticDerivationGraphRelationFilter) semanticDerivationGraphRelationFilter.value = SEMANTIC_DERIVATION_GRAPH_DEFAULTS.relation;
  renderSemanticDerivationGraphPanel();
}

function semanticDerivationGraphPayload() {
  return semanticDerivationGraphData && typeof semanticDerivationGraphData === "object"
    ? semanticDerivationGraphData
    : SEMANTIC_DERIVATION_GRAPH_FALLBACK_PANEL;
}

function positionedDerivationGraphNodes(nodes) {
  const values = Array.isArray(nodes) ? nodes : [];
  const lanes = {
    semantic_cluster: 12,
    derivation_family: 42,
    derivation_record: 74,
  };
  const grouped = values.reduce((acc, node) => {
    const key = node.nodeType || "derivation_record";
    acc[key] = acc[key] || [];
    acc[key].push(node);
    return acc;
  }, {});
  Object.values(grouped).forEach((group) => group.sort((left, right) => text(left.graphNodeId).localeCompare(text(right.graphNodeId))));
  return values.map((node) => {
    if (Number.isFinite(node.x) && Number.isFinite(node.y)) return node;
    const group = grouped[node.nodeType || "derivation_record"] || [node];
    const index = group.findIndex((item) => item.graphNodeId === node.graphNodeId);
    const y = group.length <= 1 ? 44 : 20 + (index * (60 / Math.max(1, group.length - 1)));
    return {
      ...node,
      x: lanes[node.nodeType] || 74,
      y,
    };
  });
}

function derivationGraphNodeMatchesFilters(node, filters) {
  if (!node) return false;
  if (filters.family && node.derivationFamilyId !== filters.family) return false;
  if (filters.domain) {
    const values = [
      node.graphNodeId,
      node.label,
      node.nodeType,
      ...(Array.isArray(node.semanticLineage) ? node.semanticLineage : []),
      ...(Array.isArray(node.transformationHints) ? node.transformationHints : []),
    ].map((item) => text(item).toLowerCase());
    if (!values.some((item) => item.includes(filters.domain.toLowerCase()))) return false;
  }
  return true;
}

function filteredDerivationGraph(payload = semanticDerivationGraphPayload(), filters = readSemanticDerivationGraphFilterState()) {
  const nodes = positionedDerivationGraphNodes(payload.nodes || []);
  const edges = Array.isArray(payload.edges) ? payload.edges : [];
  const relationFilteredEdges = edges.filter((edge) => !filters.relation || edge.relationType === filters.relation);
  const nodeMatches = new Set(nodes.filter((node) => derivationGraphNodeMatchesFilters(node, filters)).map((node) => node.graphNodeId));
  const hasNodeFilters = Boolean(filters.family || filters.domain);
  const visibleEdges = relationFilteredEdges.filter((edge) => {
    if (!hasNodeFilters) return true;
    return nodeMatches.has(edge.sourceId) || nodeMatches.has(edge.targetId);
  });
  const connectedIds = new Set(visibleEdges.flatMap((edge) => [edge.sourceId, edge.targetId]));
  nodeMatches.forEach((nodeId) => connectedIds.add(nodeId));
  const visibleNodes = nodes.filter((node) => connectedIds.has(node.graphNodeId));
  return {
    ...payload,
    nodes: visibleNodes.sort((left, right) => text(left.graphNodeId).localeCompare(text(right.graphNodeId))),
    edges: visibleEdges.sort((left, right) => {
      const relationDelta = SEMANTIC_DERIVATION_GRAPH_RELATION_ORDER.indexOf(left.relationType) - SEMANTIC_DERIVATION_GRAPH_RELATION_ORDER.indexOf(right.relationType);
      return relationDelta || text(left.edgeId).localeCompare(text(right.edgeId));
    }),
  };
}

function highlightedDerivationGraphEdgeIds(payload) {
  const cards = Array.isArray(payload.cards) ? payload.cards : [];
  return new Set(cards.flatMap((card) => card?.metadata?.edgeIds || []));
}

function handleDerivationGraphNodeKeydown(event, nodeId) {
  if (event.key !== "Enter" && event.key !== " ") return;
  event.preventDefault();
  focusDerivationGraphNode(nodeId);
}

function renderDerivationGraphNode(node, selectedNodeId, highlightedNodeIds) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "semantic-derivation-graph-node";
  button.style.left = `${node.x}%`;
  button.style.top = `${node.y}%`;
  button.dataset.nodeId = node.graphNodeId;
  button.textContent = text(node.label, node.graphNodeId);
  button.title = `${text(node.nodeType)}: ${text(node.graphNodeId)}`;
  button.setAttribute("aria-label", `${text(node.label, node.graphNodeId)}, ${text(node.nodeType)}`);
  button.setAttribute("aria-pressed", node.graphNodeId === selectedNodeId ? "true" : "false");
  button.classList.toggle("selected", node.graphNodeId === selectedNodeId);
  button.classList.toggle("traversal-highlight", highlightedNodeIds.has(node.graphNodeId));
  button.addEventListener("click", () => focusDerivationGraphNode(node.graphNodeId));
  button.addEventListener("keydown", (event) => handleDerivationGraphNodeKeydown(event, node.graphNodeId));
  return button;
}

function renderDerivationGraphEdgeRow(edge, highlightedEdgeIds) {
  const row = document.createElement("div");
  row.className = "semantic-derivation-graph-edge";
  row.classList.toggle("traversal-highlight", highlightedEdgeIds.has(edge.edgeId));
  const title = document.createElement("strong");
  title.textContent = text(edge.relationType);
  const body = document.createElement("span");
  body.textContent = text(edge.relationLabel, `${edge.sourceId} -> ${edge.targetId}`);
  const meta = document.createElement("small");
  meta.textContent = `${text(edge.confidence, "unreviewed")}; ${text(edge.reviewStatus, "placeholder-local-review-required")}`;
  row.append(title, body, meta);
  return row;
}

function renderDerivationGraphLegend(edges, highlightedEdgeIds) {
  const legend = byId("semantic-derivation-graph-legend");
  clearChildren(legend);
  if (!legend) return;
  const relations = SEMANTIC_DERIVATION_GRAPH_RELATION_ORDER.filter((relation) => edges.some((edge) => edge.relationType === relation));
  if (relations.length === 0) {
    appendEmpty(legend, "No derivation relation legend available");
    return;
  }
  relations.forEach((relation) => {
    const item = document.createElement("div");
    item.className = "semantic-derivation-graph-legend-item";
    item.setAttribute("role", "listitem");
    item.classList.toggle("traversal-highlight", edges.some((edge) => edge.relationType === relation && highlightedEdgeIds.has(edge.edgeId)));
    const marker = document.createElement("span");
    marker.className = "semantic-derivation-graph-legend-marker";
    marker.setAttribute("aria-hidden", "true");
    const label = document.createElement("span");
    label.textContent = relation;
    item.append(marker, label);
    legend.appendChild(item);
  });
}

function focusDerivationGraphNode(nodeId) {
  selectedDerivationGraphNodeId = nodeId;
  renderSemanticDerivationGraphPanel();
}

function renderDerivationGraphSelectedSummary(node) {
  const summary = byId("semantic-derivation-graph-summary");
  clearChildren(summary);
  if (!summary) return;
  if (!node) {
    appendEmpty(summary, "No derivation graph node selected");
    return;
  }
  summary.appendChild(renderSemanticDerivationCard("Node", text(node.label, node.graphNodeId), `${text(node.nodeType)}; ${text(node.graphNodeId)}`));
  if (node.derivationFamilyId) summary.appendChild(renderSemanticDerivationCard("Family", node.derivationFamilyId));
  if (node.dhatuId) summary.appendChild(renderSemanticDerivationCard("Dhatu id", node.dhatuId));
  if (node.semanticLineage?.length) summary.appendChild(renderSemanticDerivationCard("Semantic lineage", node.semanticLineage.join(", ")));
  if (node.transformationHints?.length) summary.appendChild(renderSemanticDerivationCard("Transformation hints", node.transformationHints.join("; ")));
  summary.appendChild(renderSemanticDerivationCard("Review status", text(node.reviewStatus, "placeholder-local-review-required")));
}

function renderSemanticDerivationGraphPanel() {
  const payload = filteredDerivationGraph();
  const nodes = payload.nodes || [];
  const edges = payload.edges || [];
  const highlightedEdgeIds = highlightedDerivationGraphEdgeIds(payload);
  const highlightedNodeIds = new Set();
  edges.forEach((edge) => {
    if (highlightedEdgeIds.has(edge.edgeId)) {
      highlightedNodeIds.add(edge.sourceId);
      highlightedNodeIds.add(edge.targetId);
    }
  });
  if (!nodes.some((node) => node.graphNodeId === selectedDerivationGraphNodeId)) {
    selectedDerivationGraphNodeId = nodes[0]?.graphNodeId || "";
  }
  const selectedNode = nodes.find((node) => node.graphNodeId === selectedDerivationGraphNodeId);

  const canvas = byId("semantic-derivation-graph-canvas");
  clearChildren(canvas);
  if (canvas) {
    if (nodes.length === 0) {
      appendEmpty(canvas, "Derivation graph unavailable for the selected filters");
    } else {
      edges.forEach((edge) => {
        const source = nodes.find((node) => node.graphNodeId === edge.sourceId);
        const target = nodes.find((node) => node.graphNodeId === edge.targetId);
        if (!source || !target) return;
        const connector = document.createElement("div");
        connector.className = "semantic-derivation-graph-connector";
        connector.classList.toggle("traversal-highlight", highlightedEdgeIds.has(edge.edgeId));
        connector.style.left = `${Math.min(source.x, target.x) + 5}%`;
        connector.style.top = `${(source.y + target.y) / 2}%`;
        connector.style.width = `${Math.max(10, Math.abs(target.x - source.x) - 10)}%`;
        connector.textContent = text(edge.relationLabel, edge.relationType);
        canvas.appendChild(connector);
      });
      nodes.forEach((node) => canvas.appendChild(renderDerivationGraphNode(node, selectedDerivationGraphNodeId, highlightedNodeIds)));
    }
  }

  renderDerivationGraphSelectedSummary(selectedNode);
  renderDerivationGraphLegend(edges, highlightedEdgeIds);

  const edgeList = byId("semantic-derivation-graph-edges");
  clearChildren(edgeList);
  if (edgeList) {
    if (edges.length === 0) appendEmpty(edgeList, "No derivation graph edges match the selected filters");
    edges.forEach((edge) => edgeList.appendChild(renderDerivationGraphEdgeRow(edge, highlightedEdgeIds)));
  }

  const traversal = byId("semantic-derivation-graph-traversal");
  clearChildren(traversal);
  if (traversal) {
    const cardCount = Array.isArray(payload.cards) ? payload.cards.length : 0;
    traversal.appendChild(renderSemanticDerivationCard(
      "Traversal explanation",
      cardCount ? `${cardCount} fixture-compatible traversal cards available` : "No traversal cards available for this filter set",
      SEMANTIC_DERIVATION_GRAPH_PLACEHOLDER_WARNING,
    ));
  }
}

function renderSemanticPlatformStatusCard(label, value, detail, badgeType = "") {
  const card = document.createElement("div");
  card.className = "semantic-platform-status-card";
  card.tabIndex = 0;
  const title = document.createElement("strong");
  title.textContent = label;
  const body = document.createElement("span");
  body.textContent = text(value);
  card.append(title, body);
  if (detail) {
    const small = document.createElement("small");
    small.textContent = detail;
    card.appendChild(small);
  }
  if (badgeType) card.classList.add(`semantic-platform-status-${badgeType.toLowerCase()}`);
  return card;
}

function renderSemanticPlatformStatusList(container, items, formatter, emptyMessage) {
  clearChildren(container);
  if (!container) return;
  const values = Array.isArray(items) ? items : [];
  if (!values.length) {
    appendEmpty(container, emptyMessage);
    return;
  }
  values.forEach((item, index) => container.appendChild(formatter(item, index)));
}

function renderSemanticPlatformStatusPanel(panel = semanticPlatformStatusData) {
  const payload = panel && typeof panel === "object" ? panel : SEMANTIC_PLATFORM_STATUS_FALLBACK_PANEL;
  const overview = byId("semantic-platform-overview-output");
  clearChildren(overview);
  if (overview) {
    overview.appendChild(renderSemanticPlatformStatusCard("Platform status", text(payload.platformStatus, "UNKNOWN"), text(payload.milestoneSpan, "v53-v72"), payload.platformStatus));
    overview.appendChild(renderSemanticPlatformStatusCard("Canonical registry", payload.canonicalRegistryRecordCount, "records remain read-only"));
    overview.appendChild(renderSemanticPlatformStatusCard("Semantic records", payload.semanticRecordCount, "covered semantic sidecar records"));
    overview.appendChild(renderSemanticPlatformStatusCard("UI readiness", text(payload.uiReadiness?.status, "READY"), text(payload.uiReadiness?.mode, "client-side-read-only"), payload.uiReadiness?.status));
  }

  renderSemanticPlatformStatusList(
    byId("semantic-platform-validators-output"),
    payload.validators,
    (validator) => renderSemanticPlatformStatusCard(
      text(validator.name, "validator"),
      text(validator.status, "UNKNOWN"),
      text(validator.command, "validator command unavailable"),
      validator.status,
    ),
    "No validators listed",
  );

  renderSemanticPlatformStatusList(
    byId("semantic-platform-endpoints-output"),
    payload.endpoints,
    (endpoint) => renderSemanticPlatformStatusCard(
      text(endpoint.label, endpoint.path),
      text(endpoint.path),
      `${text(endpoint.method, "GET")} - read-only ${endpoint.readOnly === false ? "no" : "yes"}`,
    ),
    "No endpoints listed",
  );

  const docsAndExamples = [...(Array.isArray(payload.docs) ? payload.docs : []), ...(Array.isArray(payload.examples) ? payload.examples : [])];
  renderSemanticPlatformStatusList(
    byId("semantic-platform-docs-output"),
    docsAndExamples,
    (entry, index) => renderSemanticPlatformStatusCard(index < (payload.docs?.length || 0) ? "Doc" : "Example", entry),
    "No docs or examples listed",
  );

  const checkpoint = byId("semantic-platform-checkpoint-output");
  clearChildren(checkpoint);
  if (checkpoint) {
    checkpoint.appendChild(renderSemanticPlatformStatusCard("Release tag", text(payload.checkpoint?.releaseTag, "checkpoint tag unavailable")));
    checkpoint.appendChild(renderSemanticPlatformStatusCard("JSON", text(payload.checkpoint?.jsonPath, "checkpoint JSON unavailable")));
    checkpoint.appendChild(renderSemanticPlatformStatusCard("Markdown", text(payload.checkpoint?.markdownPath, "checkpoint Markdown unavailable")));
  }

  const safety = payload.safetyPolicy || {};
  const safetyRows = [
    ["Read-only", safety.readOnlySemanticArchitecture],
    ["Exact sutra assertions", safety.exactSutraAssertionsAllowed],
    ["Exact Paninian derivation claims", safety.exactPaninianDerivationClaimsAllowed],
    ["Grammatical guarantee", safety.grammaticalCorrectnessGuarantee],
    ["Canonical mutation", safety.canonicalRegistryMutation],
    ["Write flags required", safety.canonicalWriteEnvironmentFlagsRequired],
  ];
  renderSemanticPlatformStatusList(
    byId("semantic-platform-safety-output"),
    safetyRows,
    ([label, value]) => renderSemanticPlatformStatusCard(label, value === true ? "yes" : "no", payload.safetyNote),
    "No safety policy listed",
  );
}

function renderSemanticDhatuPanel(panel) {
  const payload = panel && typeof panel === "object" ? panel : SEMANTIC_DHATU_FALLBACK_PANEL;
  const cards = Array.isArray(payload.cards) ? payload.cards : [];
  const sections = {
    "Search Results": byId("semantic-dhatu-search-output"),
    "Semantic Neighbors": byId("semantic-dhatu-neighbor-output"),
    "Traversal Paths": byId("semantic-dhatu-traversal-output"),
  };

  Object.values(sections).forEach((container) => clearChildren(container));
  cards.forEach((card) => {
    const sectionName = text(card?.metadata?.section, "Search Results");
    const container = sections[sectionName] || sections["Search Results"];
    container?.appendChild(renderSemanticPanelCard(card));
  });
  Object.entries(sections).forEach(([sectionName, container]) => {
    if (!container) return;
    if (!container.childElementCount) appendEmpty(container, `No ${sectionName.toLowerCase()} cards`);
    if (sectionName === "Search Results") renderSemanticPanelLinks(container, payload.links);
  });

  const safety = byId("semantic-dhatu-safety-output");
  clearChildren(safety);
  if (safety) {
    const note = document.createElement("div");
    note.className = "semantic-dhatu-safety-note";
    note.textContent = text(payload.safetyNote, SEMANTIC_DHATU_FALLBACK_PANEL.safetyNote);
    safety.appendChild(note);
  }
}

async function loadSemanticDhatuPanel() {
  try {
    const response = await fetch(SEMANTIC_DHATU_PANEL_FIXTURE);
    if (!response.ok) throw new Error(`fixture unavailable: ${response.status}`);
    semanticPanelData = await response.json();
    renderSemanticQueryState();
    renderStaticSemanticFixtureBrowser();
  } catch (error) {
    console.warn("[Sanskrit] Semantic Dhatu Intelligence fallback:", error);
    semanticPanelData = SEMANTIC_DHATU_FALLBACK_PANEL;
    renderSemanticQueryState();
    renderStaticSemanticFixtureBrowser();
  }
}

async function loadSemanticPlatformStatusPanel() {
  renderSemanticPlatformStatusPanel(SEMANTIC_PLATFORM_STATUS_FALLBACK_PANEL);
  try {
    const response = await fetch(SEMANTIC_PLATFORM_STATUS_PANEL_FIXTURE);
    if (!response.ok) throw new Error(`fixture unavailable: ${response.status}`);
    semanticPlatformStatusData = await response.json();
    renderSemanticPlatformStatusPanel(semanticPlatformStatusData);
    renderStaticSemanticFixtureBrowser();
  } catch (error) {
    console.warn("[Sanskrit] Semantic Platform Status fallback:", error);
    semanticPlatformStatusData = SEMANTIC_PLATFORM_STATUS_FALLBACK_PANEL;
    renderSemanticPlatformStatusPanel(semanticPlatformStatusData);
    renderStaticSemanticFixtureBrowser();
  }
}

async function loadSemanticDerivationData() {
  try {
    const response = await fetch(SEMANTIC_DERIVATION_DATA_FIXTURE);
    if (!response.ok) throw new Error(`fixture unavailable: ${response.status}`);
    semanticDerivationData = await response.json();
    renderSemanticQueryState();
    renderStaticSemanticFixtureBrowser();
  } catch (error) {
    console.warn("[Sanskrit] Derivation Intelligence fallback:", error);
    semanticDerivationData = SEMANTIC_DERIVATION_FALLBACK_DATA;
    renderSemanticQueryState();
    renderStaticSemanticFixtureBrowser();
  }
}

async function loadSemanticDerivationGraphPanel() {
  try {
    const response = await fetch(SEMANTIC_DERIVATION_GRAPH_PANEL_FIXTURE);
    if (!response.ok) throw new Error(`fixture unavailable: ${response.status}`);
    semanticDerivationGraphData = await response.json();
    renderSemanticDerivationGraphPanel();
    renderStaticSemanticFixtureBrowser();
  } catch (error) {
    console.warn("[Sanskrit] Derivation Graph Intelligence fallback:", error);
    semanticDerivationGraphData = SEMANTIC_DERIVATION_GRAPH_FALLBACK_PANEL;
    renderSemanticDerivationGraphPanel();
    renderStaticSemanticFixtureBrowser();
  }
}

function appendDebugErrorRow(node, label, value) {
  appendInspectionRow(node, label, value);
}

function appendListItems(node, items, formatter) {
  clearChildren(node);
  if (!node) return;

  const values = Array.isArray(items) ? items : [];
  if (values.length === 0) {
    const empty = document.createElement("li");
    empty.textContent = "No entries";
    node.appendChild(empty);
    return;
  }

  values.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = formatter ? formatter(item) : text(item);
    node.appendChild(li);
  });
}

function renderPadas(padas) {
  const container = byId("padas-output");
  clearChildren(container);
  if (!container) return;

  const values = Array.isArray(padas) ? padas : [];
  values.forEach((pada) => {
    const row = document.createElement("article");
    row.className = "pada-row";
    const label = document.createElement("strong");
    const content = document.createElement("span");
    const meta = document.createElement("small");
    label.textContent = text(pada?.label);
    content.textContent = text(pada?.text);
    meta.textContent = `${text(pada?.meter)} · ${text(pada?.matra_count, 0)} matra · ${text(pada?.guru_laghu_pattern)}`;
    row.append(label, content, meta);
    container.appendChild(row);
  });
}

function renderSyllables(syllables) {
  const container = byId("phonological-syllables-output");
  clearChildren(container);
  if (!container) return;

  const values = Array.isArray(syllables) ? syllables : [];
  values.forEach((syllable) => {
    const chip = document.createElement("span");
    const weightClass = text(syllable?.weight).toLowerCase();
    const weightSymbol = weightClass === "guru" ? "G" : "L";
    chip.className = `syllable-chip ${weightClass}`;
    chip.textContent = `${text(syllable?.text)}(${weightSymbol}:${text(syllable?.matra_count, 0)})`;
    chip.title = `${text(syllable?.weight)} syllable, cluster ${text(syllable?.cluster_start)}-${text(syllable?.cluster_end)}`;
    container.appendChild(chip);
  });
}

function renderGraph(graph) {
  const container = byId("prakriya-graph-output");
  clearChildren(container);
  if (!container) return;

  const nodes = Array.isArray(graph?.nodes) ? graph.nodes : [];
  const edges = Array.isArray(graph?.edges) ? graph.edges : [];

  nodes.forEach((node) => {
    const row = document.createElement("div");
    row.className = "graph-node";
    const outgoing = edges.filter((edge) => edge?.from === node?.id).map((edge) => edge?.to).join(", ");
    row.textContent = `${text(node?.label)}${outgoing ? ` -> ${outgoing}` : ""}`;
    container.appendChild(row);
  });
}

function renderLexical(entries) {
  const container = byId("lexical-output");
  clearChildren(container);
  if (!container) return;

  const values = Array.isArray(entries) ? entries : [];
  values.forEach((entry) => {
    const row = document.createElement("div");
    row.className = "lexical-row";
    const token = document.createElement("strong");
    const gloss = document.createElement("span");
    const lemma = document.createElement("small");
    token.textContent = text(entry?.token);
    gloss.textContent = text(entry?.gloss);
    lemma.textContent = text(entry?.lemma);
    row.append(token, gloss, lemma);
    container.appendChild(row);
  });
}

function renderExperimental(payload) {
  const container = byId("experimental-payload-output");
  clearChildren(container);
  if (!container) return;

  const cells = Array.isArray(payload?.field_map) ? payload.field_map : [];
  cells.forEach((cell) => {
    const square = document.createElement("span");
    square.className = "symbolic-cell";
    square.textContent = text(cell?.symbol);
    square.title = `structural index ${text(cell?.index)}; weight ${text(cell?.weight)}`;
    container.appendChild(square);
  });
}

function renderSandhiResult(data) {
  const container = byId("sandhi-result-output");
  clearChildren(container);
  if (!container) return;
  if (!data) {
    appendEmpty(container, "No sandhi result");
    return;
  }

  appendInspectionRow(container, "Merged", data.merged);
  appendInspectionRow(container, "Sutra", data.sutra, data.sutra_name);
  appendInspectionRow(container, "Type", data.type);

  const trace = Array.isArray(data.trace) ? data.trace : [];
  trace.forEach((step, index) => {
    const detail = Object.entries(step || {})
      .filter(([key]) => key !== "layer")
      .map(([key, value]) => `${key}: ${text(value)}`)
      .join("; ");
    appendInspectionRow(container, `Trace ${index + 1}`, step?.layer, detail);
  });
}

function renderMorphologyResult(data) {
  const container = byId("morphology-result-output");
  clearChildren(container);
  if (!container) return;
  if (!data) {
    appendEmpty(container, "No morphology result");
    return;
  }

  appendInspectionRow(container, "Form", data.form);
  appendInspectionRow(container, "Type", data.type);
  appendInspectionRow(container, "Rule Engine", data.rule?.engine);

  Object.entries(data.input || {}).forEach(([key, value]) => {
    appendInspectionRow(container, `Input ${key}`, value);
  });

  Object.entries(data.metadata || {}).forEach(([key, value]) => {
    const renderedValue = typeof value === "object" ? JSON.stringify(value) : value;
    appendInspectionRow(container, `Metadata ${key}`, renderedValue);
  });
}

function renderDerivationTimeline(path) {
  const container = byId("derivation-timeline-output");
  clearChildren(container);
  if (!container) return;

  const steps = Array.isArray(path) ? path : [];
  if (steps.length === 0) {
    const empty = document.createElement("li");
    empty.textContent = "No derivation path";
    container.appendChild(empty);
    return;
  }

  steps.forEach((step) => {
    const item = document.createElement("li");
    const title = document.createElement("strong");
    const body = document.createElement("span");
    const meta = document.createElement("small");
    title.textContent = text(step?.operation);
    body.textContent = ` ${text(step?.input_state)} -> ${text(step?.output_state)}`;
    meta.textContent = `${text(step?.sutra)} · ${text(step?.sutra_name)} · ${text(step?.engine_node)}`;
    item.append(title, body, meta);
    container.appendChild(item);
  });
}

function renderGovernancePanel(gov) {
  const container = byId("governance-output");
  clearChildren(container);
  if (!container) return;
  if (!gov) {
    appendEmpty(container, "No governance metadata");
    return;
  }

  appendInspectionRow(container, "Normalization", gov.normalization);
  appendInspectionRow(container, "Script Policy", gov.script_policy);
  appendInspectionRow(container, "Source", gov.source);
}

function renderAmbiguityPanel(ambiguity) {
  const container = byId("ambiguity-output");
  clearChildren(container);
  if (!container) return;
  if (!ambiguity) {
    appendEmpty(container, "No ambiguity payload");
    return;
  }

  appendInspectionRow(container, "Ambiguous", ambiguity.is_ambiguous ? "true" : "false");
  appendInspectionRow(container, "Strategy", ambiguity.strategy);
  appendInspectionRow(container, "Selected Candidate", ambiguity.selected_candidate_id || "none");

  const candidates = Array.isArray(ambiguity.candidates) ? ambiguity.candidates : [];
  if (candidates.length === 0) {
    appendEmpty(container, "No ambiguity candidates");
    return;
  }

  candidates.forEach((candidate) => {
    const row = document.createElement("div");
    row.className = "candidate-row";
    const title = document.createElement("strong");
    const output = document.createElement("span");
    const meta = document.createElement("small");
    title.textContent = text(candidate?.candidate_id);
    output.textContent = `: ${text(candidate?.final_output)}`;
    meta.textContent = `${text(candidate?.source_engine)} · ${text(candidate?.reason)} · confidence: ${text(candidate?.confidence, "null")}`;
    row.append(title, output, meta);
    container.appendChild(row);
  });
}

function renderApiError(detail) {
  const container = byId("api-error-output");
  clearChildren(container);
  if (!container) return;
  if (!detail) {
    appendEmpty(container, "No API error");
    return;
  }

  const errorDetail = detail.detail || detail;
  appendInspectionRow(container, "Code", errorDetail.code || "api_error");
  appendInspectionRow(container, "Message", errorDetail.message || errorDetail);

  const invalidCharacters = Array.isArray(errorDetail.invalid_characters) ? errorDetail.invalid_characters : [];
  if (invalidCharacters.length > 0) {
    appendInspectionRow(container, "Invalid Characters", invalidCharacters.join(", "));
  }
}

function renderFallbackAnalysisPanel(payload) {
  const panel = byId("fallback-analysis-panel");
  const badge = byId("fallback-analysis-badge");
  const explanation = byId("fallback-analysis-explanation");
  const stages = byId("fallback-analysis-stages");
  const tokens = byId("fallback-analysis-tokens");
  const safety = byId("fallback-analysis-safety");
  const isFallback = payload?.pipelineStatus?.mode === "local-fallback";

  if (panel) panel.classList.toggle("hidden", !isFallback);
  if (!isFallback) return;

  if (badge) badge.textContent = "Local fallback";
  if (explanation) {
    explanation.textContent = text(
      payload?.pipelineStatus?.backendUnavailableExplanation,
      "The backend analysis route was unavailable, so a deterministic local fallback was rendered.",
    );
  }

  clearChildren(stages);
  const stageValues = Array.isArray(payload?.pipelineStatus?.stages) ? payload.pipelineStatus.stages : [];
  stageValues.forEach((stage) => {
    const card = document.createElement("div");
    card.className = "fallback-stage-card";
    const title = document.createElement("strong");
    const body = document.createElement("span");
    title.textContent = text(stage?.label || stage?.stage);
    body.textContent = text(stage?.status);
    card.append(title, body);
    stages?.appendChild(card);
  });

  clearChildren(tokens);
  const tokenValues = Array.isArray(payload?.tokenization?.tokens) ? payload.tokenization.tokens : [];
  tokenValues.forEach((tokenValue) => {
    const item = document.createElement("span");
    item.className = "fallback-token";
    item.textContent = text(tokenValue);
    tokens?.appendChild(item);
  });

  if (safety) safety.textContent = text(payload?.safety_note);
}

function isExpectedStaticPreviewApiMiss(errorOrResponse) {
  const status = Number(errorOrResponse?.status || errorOrResponse?.response?.status || 0);
  const message = text(errorOrResponse?.message, "");
  return (
    status === 404
    || status === 405
    || status === 501
    || /\bHTTP (404|405|501)\b/.test(message)
  );
}

async function detectBackendRuntime() {
  try {
    const response = await fetch("/api/health", {
      method: "GET",
    });

    backendRuntimeAvailable = Boolean(response?.ok);
  } catch (error) {
    backendRuntimeAvailable = false;
  }

  return backendRuntimeAvailable;
}

function renderBackendRuntimeStatus() {
  const node = byId("semantic-runtime-status");

  if (!node) return;

  if (backendRuntimeAvailable) {
    node.textContent = "Backend Runtime Connected";
    node.dataset.runtimeMode = "backend";
  } else {
    node.textContent = "Static Preview Mode";
    node.dataset.runtimeMode = "static";
  }
}

function renderStaticPreviewFallbackNotice(reason) {
  const panel = byId("static-preview-fallback-notice");
  const reasonNode = byId("static-preview-fallback-reason");
  const detailsNode = byId("static-preview-fallback-details");

  renderStaticSemanticFixtureBrowser(Boolean(reason));

  if (!panel) return;

  const hasReason = Boolean(reason);

  panel.classList.toggle("hidden", !hasReason);

  if (!hasReason) return;

  if (reasonNode) {
    reasonNode.textContent = text(reason);
  }

  clearChildren(detailsNode);

 [
  "Backend API unavailable",
  "Local fallback rendered",
  "Static preview remains usable",
  "API endpoints require backend runtime",
  "Canonical registry not mutated",
].forEach((item) => {
  const row = document.createElement("li");
  row.textContent = item;
  detailsNode?.appendChild(row);
});
}

function readStaticFixtureBrowserFilters() {
  return {
    cluster: staticFixtureClusterFilter?.value || "",
    dhatuId: staticFixtureDhatuFilter?.value.trim().toLowerCase() || "",
    nodeId: staticFixtureNodeFilter?.value.trim().toLowerCase() || "",
    section: staticFixtureSectionFilter?.value || "records",
  };
}

function validStaticFixtureClusters() {
  return new Set(SEMANTIC_DHATU_RECORDS.map((record) => record.cluster));
}

function validStaticFixtureDhatuIds() {
  return new Set(SEMANTIC_DHATU_RECORDS.map((record) => record.dhatuId.toLowerCase()));
}

function validStaticFixtureNodeIds() {
  return new Set(SEMANTIC_GRAPH_FALLBACK.nodes.map((node) => node.nodeId.toLowerCase()));
}

function validStaticFixtureSections() {
  return new Set(["records", "clusters", "graph", "neighbors", "json"]);
}

function safeDecodeStaticFixtureHashValue(value) {
  try {
    return decodeURIComponent(text(value, "").replace(/\+/g, " ")).trim();
  } catch (error) {
    console.warn("[Sanskrit] Ignoring malformed static fixture hash value:", error);
    return "";
  }
}

function parseStaticFixtureBrowserHash(hashValue = window.location.hash) {
  try {
    const rawHash = text(hashValue, "");
    if (!rawHash.startsWith("#sanskrit-static-fixtures")) return {};
    const queryStart = rawHash.indexOf("?");
    if (queryStart < 0) return {};
    const params = new URLSearchParams(rawHash.slice(queryStart + 1));
    const cluster = safeDecodeStaticFixtureHashValue(params.get("cluster"));
    const dhatuId = safeDecodeStaticFixtureHashValue(params.get("dhatuId")).toLowerCase();
    const nodeId = safeDecodeStaticFixtureHashValue(params.get("nodeId")).toLowerCase();
    const section = safeDecodeStaticFixtureHashValue(params.get("section")).toLowerCase();
    return {
      cluster: validStaticFixtureClusters().has(cluster) ? cluster : "",
      dhatuId: validStaticFixtureDhatuIds().has(dhatuId) ? dhatuId : "",
      nodeId: validStaticFixtureNodeIds().has(nodeId) ? nodeId : "",
      section: validStaticFixtureSections().has(section) ? section : "",
    };
  } catch (error) {
    console.warn("[Sanskrit] Ignoring malformed static fixture hash:", error);
    return {};
  }
}

function applyStaticFixtureBrowserHashState(state) {
  if (!state || typeof state !== "object") return;
  if (staticFixtureClusterFilter && state.cluster) staticFixtureClusterFilter.value = state.cluster;
  if (staticFixtureDhatuFilter && state.dhatuId) staticFixtureDhatuFilter.value = state.dhatuId;
  if (staticFixtureNodeFilter && state.nodeId) staticFixtureNodeFilter.value = state.nodeId;
  if (staticFixtureSectionFilter && state.section) staticFixtureSectionFilter.value = state.section;
}

function restoreStaticFixtureBrowserHashState() {
  if (staticFixtureHashRestored) return;
  staticFixtureHashRestored = true;
  applyStaticFixtureBrowserHashState(parseStaticFixtureBrowserHash());
}

function buildStaticFixtureBrowserHash(filters = readStaticFixtureBrowserFilters()) {
  const params = new URLSearchParams();
  if (filters.cluster) params.set("cluster", filters.cluster);
  if (filters.dhatuId) params.set("dhatuId", filters.dhatuId);
  if (filters.nodeId) params.set("nodeId", filters.nodeId);
  if (filters.section) params.set("section", filters.section);
  const query = params.toString();
  return query ? `#sanskrit-static-fixtures?${query}` : "#sanskrit-static-fixtures";
}

function updateStaticFixtureBrowserHash(filters = readStaticFixtureBrowserFilters()) {
  const hash = buildStaticFixtureBrowserHash(filters);
  if (window.location.hash === hash) return;
  window.history.replaceState(null, "", hash);
}

function filteredStaticSemanticRecords(filters = readStaticFixtureBrowserFilters()) {
  return SEMANTIC_DHATU_RECORDS.filter((record) => {
    if (filters.cluster && record.cluster !== filters.cluster) return false;
    if (filters.dhatuId && !record.dhatuId.toLowerCase().includes(filters.dhatuId)) return false;
    return true;
  });
}

function filteredStaticGraphNodes(filters = readStaticFixtureBrowserFilters()) {
  return SEMANTIC_GRAPH_FALLBACK.nodes.filter((node) => {
    if (filters.cluster && node.cluster !== filters.cluster) return false;
    if (filters.nodeId && !node.nodeId.toLowerCase().includes(filters.nodeId)) return false;
    return true;
  });
}

function filteredStaticGraphEdges(nodes) {
  const nodeIds = new Set(nodes.map((node) => node.nodeId));
  return SEMANTIC_GRAPH_FALLBACK.edges.filter((edge) => nodeIds.has(edge.sourceId) || nodeIds.has(edge.targetId));
}

function staticFixtureStatusLabel(available) {
  return available ? "Available from read-only fixture/fallback data" : "Unavailable in static preview";
}

function setStaticFixtureStatus(id, label, available, detail) {
  const node = byId(id);
  clearChildren(node);
  if (!node) return;
  const row = document.createElement("div");
  row.className = `static-fixture-browser-status-row ${available ? "available" : "unavailable"}`;
  const title = document.createElement("strong");
  const body = document.createElement("span");
  title.textContent = label;
  body.textContent = staticFixtureStatusLabel(available);
  row.append(title, body);
  if (detail) {
    const small = document.createElement("small");
    small.textContent = detail;
    row.appendChild(small);
  }
  node.appendChild(row);
}

function renderStaticFixtureList(containerId, items, formatter, emptyMessage = "Unavailable in static preview") {
  const container = byId(containerId);
  clearChildren(container);
  if (!container) return;
  const values = Array.isArray(items) ? items : [];
  if (values.length === 0) {
    appendEmpty(container, emptyMessage);
    return;
  }
  values.forEach((item) => {
    const row = document.createElement("div");
    row.className = "static-fixture-browser-row";
    row.textContent = formatter(item);
    container.appendChild(row);
  });
}

function buildStaticSemanticFixtureBrowserPayload(filters = readStaticFixtureBrowserFilters()) {
  const records = filteredStaticSemanticRecords(filters);
  const graphNodes = filteredStaticGraphNodes(filters);
  const graphEdges = filteredStaticGraphEdges(graphNodes);
  const clusters = [...new Set(SEMANTIC_DHATU_RECORDS.map((record) => record.cluster))].sort();
  const derivationRecords = Array.isArray(semanticDerivationData?.records)
    ? semanticDerivationData.records
    : SEMANTIC_DERIVATION_FALLBACK_DATA.records;
  const derivationGraphNodes = Array.isArray(semanticDerivationGraphData?.nodes)
    ? semanticDerivationGraphData.nodes
    : SEMANTIC_DERIVATION_GRAPH_FALLBACK_PANEL.nodes;
  const derivationGraphEdges = Array.isArray(semanticDerivationGraphData?.edges)
    ? semanticDerivationGraphData.edges
    : SEMANTIC_DERIVATION_GRAPH_FALLBACK_PANEL.edges;

  return {
    schemaVersion: "1.0.0",
    generatedBy: "ui/tabs/sanskrit/controller.js:staticSemanticFixtureBrowser",
    readOnly: true,
    safeJsonPreview: "textContent-only; no eval; no mutation",
    hashFormat: "#sanskrit-static-fixtures?cluster=motion&dhatuId=01.0005&nodeId=motion&section=neighbors",
    filters,
    fixtureAvailability: {
      semanticUi: Boolean(semanticPanelData || SEMANTIC_DHATU_FALLBACK_PANEL),
      semanticGraph: Boolean(SEMANTIC_GRAPH_FALLBACK.nodes?.length),
      derivation: Boolean(derivationRecords.length),
      derivationGraph: Boolean(derivationGraphNodes.length),
      platformStatus: Boolean(semanticPlatformStatusData || SEMANTIC_PLATFORM_STATUS_FALLBACK_PANEL),
    },
    semanticRecordCount: records.length,
    availableClusters: clusters,
    semanticRecords: records,
    graphNodes,
    graphEdges,
    derivationRecordCount: derivationRecords.length,
    derivationGraphFixtureAvailable: Boolean(derivationGraphNodes.length),
    derivationGraphNodeCount: derivationGraphNodes.length,
    derivationGraphEdgeCount: derivationGraphEdges.length,
    sourceFixtures: [
      SEMANTIC_DHATU_PANEL_FIXTURE,
      SEMANTIC_GRAPH_PANEL_FIXTURE,
      SEMANTIC_DERIVATION_DATA_FIXTURE,
      SEMANTIC_DERIVATION_GRAPH_PANEL_FIXTURE,
      SEMANTIC_PLATFORM_STATUS_PANEL_FIXTURE,
    ],
    safetyNote: "Static Semantic Fixture Browser is read-only: escaped text rendering, no eval, no backend requirement, and no canonical registry mutation.",
  };
}

function renderStaticSemanticFixtureBrowser(active = staticSemanticFixtureBrowserActive) {
  staticSemanticFixtureBrowserActive = Boolean(active);
  const panel = byId("static-semantic-fixture-browser");
  if (panel) panel.classList.toggle("hidden", !staticSemanticFixtureBrowserActive);
  if (!staticSemanticFixtureBrowserActive) return;

  restoreStaticFixtureBrowserHashState();
  const payload = buildStaticSemanticFixtureBrowserPayload();
  setStaticFixtureStatus(
    "static-fixture-browser-availability",
    "Semantic fixtures",
    payload.fixtureAvailability.semanticUi,
    `${payload.semanticRecordCount} semantic records loaded`,
  );
  setStaticFixtureStatus(
    "static-fixture-browser-derivation-graph-status",
    "Derivation graph fixture",
    payload.derivationGraphFixtureAvailable,
    `${payload.derivationGraphNodeCount} nodes; ${payload.derivationGraphEdgeCount} edges`,
  );

  renderStaticFixtureList(
    "static-fixture-browser-clusters",
    payload.availableClusters,
    (cluster) => cluster,
  );
  renderStaticFixtureList(
    "static-fixture-browser-records",
    payload.semanticRecords,
    (record) => `${record.dhatuId} ${record.iast} (${record.cluster}) - ${record.gloss}`,
  );
  renderStaticFixtureList(
    "static-fixture-browser-graph",
    payload.graphNodes,
    (node) => `${node.nodeId} ${node.label} (${node.nodeType})`,
  );
  renderStaticFixtureList(
    "static-fixture-browser-neighbors",
    payload.graphEdges,
    (edge) => `${edge.sourceId} -> ${edge.targetId} (${edge.relationType})`,
  );

  const preview = byId("static-fixture-browser-json-preview");
  if (preview) preview.textContent = JSON.stringify(payload, null, 2);
  updateStaticFixtureBrowserSection(payload.filters.section);
  if (importedStaticFixtureSnapshot) {
    renderImportedStaticFixtureComparison(importedStaticFixtureSnapshot);
  }
}
function handleStaticFixtureBrowserFilterChange() {
  updateStaticFixtureBrowserHash();
  renderStaticSemanticFixtureBrowser();
}
function renderStaticFixtureImportStatus(message, state = "neutral") {
  if (!staticFixtureImportStatus) return;

  staticFixtureImportStatus.textContent = text(message, "");
  staticFixtureImportStatus.dataset.state = state;
}

function clearImportedStaticFixtureSnapshot() {
  importedStaticFixtureSnapshot = null;

  if (staticFixtureComparisonSummary) {
    staticFixtureComparisonSummary.classList.add("hidden");
  }

  if (staticFixtureImportedMetadata) {
    staticFixtureImportedMetadata.textContent = "No imported snapshot";
  }

  if (staticFixtureComparisonResults) {
    staticFixtureComparisonResults.textContent = "No comparison available";
  }

  if (staticFixtureResetImportButton) {
    staticFixtureResetImportButton.disabled = true;
  }

  renderStaticFixtureImportStatus("", "neutral");
}

function stableStringify(value) {
  if (Array.isArray(value)) {
    return `[${value.map(stableStringify).join(",")}]`;
  }

  if (value && typeof value === "object") {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`)
      .join(",")}}`;
  }

  return JSON.stringify(value);
}
function validateImportedStaticFixtureSnapshot(snapshot) {
  if (!snapshot || typeof snapshot !== "object") {
    return {
      valid: false,
      error: "Imported snapshot must be an object.",
    };
  }

  const supportedSchemas = new Set([
    "aigaane.staticSemanticFixtureSnapshot.v1",
    "aigaane.staticSemanticFixtureExportSnapshot.v1",
  ]);

  if (!supportedSchemas.has(snapshot.schema)) {
    return {
      valid: false,
      error: "Unsupported snapshot schema.",
    };
  }

  if (snapshot.mode !== "static-preview") {
    return {
      valid: false,
      error: "Snapshot mode must be static-preview.",
    };
  }

  return {
    valid: true,
    error: null,
  };
}
function renderImportedStaticFixtureComparison(snapshot) {
  if (
    !snapshot ||
    !staticFixtureComparisonSummary ||
    !staticFixtureImportedMetadata ||
    !staticFixtureComparisonResults
  ) {
    return;
  }

  const currentPayload = buildStaticSemanticFixtureBrowserPayload();
  const currentSelected = currentPayload.filters || {};
  const importedSelected = snapshot.selected || snapshot.filters || {};

  const selectedDifferences = [];

  ["cluster", "dhatuId", "nodeId", "section"].forEach((field) => {
    if ((currentSelected[field] || "") !== (importedSelected[field] || "")) {
      selectedDifferences.push(field);
    }
  });

  const importedPreview = snapshot.preview || snapshot.payload || {};
  const currentPreview = currentPayload || {};

  const previewMatches =
    stableStringify(importedPreview) === stableStringify(currentPreview);

  staticFixtureImportedMetadata.textContent = [
    `generatedAt: ${text(snapshot.generatedAt, "unknown")}`,
    `cluster: ${text(importedSelected.cluster, "(none)")}`,
    `dhatuId: ${text(importedSelected.dhatuId, "(none)")}`,
    `nodeId: ${text(importedSelected.nodeId, "(none)")}`,
    `section: ${text(importedSelected.section, "(none)")}`,
  ].join("\n");

  staticFixtureComparisonResults.textContent = [
    selectedDifferences.length === 0
      ? "Selected state matches current browser state."
      : `Changed selected fields: ${selectedDifferences.join(", ")}`,
    previewMatches
      ? "Preview JSON matches current payload."
      : "Preview JSON differs from current payload.",
  ].join("\n");

  staticFixtureComparisonSummary.classList.remove("hidden");

  if (staticFixtureResetImportButton) {
    staticFixtureResetImportButton.disabled = false;
  }
}
function handleStaticFixtureImportFileChange(event) {
  const file = event?.target?.files?.[0];

  if (!file) {
    return;
  }

  if (!file.name.toLowerCase().endsWith(".json")) {
    renderStaticFixtureImportStatus("Only .json snapshot files are supported.", "error");
    return;
  }

  const reader = new FileReader();

  reader.onload = () => {
    try {
      const parsed = JSON.parse(String(reader.result || "{}"));
      const validation = validateImportedStaticFixtureSnapshot(parsed);

      if (!validation.valid) {
        clearImportedStaticFixtureSnapshot();
        renderStaticFixtureImportStatus(validation.error, "error");
        return;
      }

      importedStaticFixtureSnapshot = parsed;
      renderImportedStaticFixtureComparison(importedStaticFixtureSnapshot);
      renderStaticFixtureImportStatus("Snapshot imported and compared.", "success");
    } catch (error) {
      clearImportedStaticFixtureSnapshot();
      renderStaticFixtureImportStatus("Invalid JSON snapshot file.", "error");
    }
  };

  reader.onerror = () => {
    clearImportedStaticFixtureSnapshot();
    renderStaticFixtureImportStatus("Unable to read snapshot file.", "error");
  };

  reader.readAsText(file);
}

function handleStaticFixtureImportClick() {
  if (staticFixtureImportFileInput) {
    staticFixtureImportFileInput.click();
  }
}

function handleStaticFixtureResetImport() {
  clearImportedStaticFixtureSnapshot();

  if (staticFixtureImportFileInput) {
    staticFixtureImportFileInput.value = "";
  }
}
function updateStaticFixtureBrowserSection(section) {
  const cards = all("[data-static-fixture-section]");
  cards.forEach((card) => {
    const cardSection = card.getAttribute("data-static-fixture-section");
    card.classList.toggle("static-fixture-browser-card-selected", cardSection === section);
  });
}

function currentStaticFixtureBrowserUrl() {
  const hash = buildStaticFixtureBrowserHash();
  return `${window.location.origin}${window.location.pathname}${hash}`;
}

function renderStaticFixtureCopyStatus(message, mode = "neutral") {
  const status = byId("static-fixture-copy-status");
  if (!status) return;
  status.textContent = text(message, "");
  status.classList.toggle("success", mode === "success");
  status.classList.toggle("fallback", mode === "fallback");
}

async function handleStaticFixtureCopyLink() {
  const url = currentStaticFixtureBrowserUrl();
  const fallback = byId("static-fixture-copy-fallback");
  if (fallback) {
    fallback.value = url;
    fallback.classList.add("hidden");
  }
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(url);
      renderStaticFixtureCopyStatus("Inspection link copied", "success");
      return;
    } catch (error) {
      console.warn("[Sanskrit] Clipboard unavailable for static fixture link:", error);
    }
  }
  if (fallback) {
    fallback.classList.remove("hidden");
    fallback.focus();
    fallback.select();
  }
  renderStaticFixtureCopyStatus("Copy unavailable; link selected below", "fallback");
}
function bindStaticFixtureImportControls() {
  if (staticFixtureImportSnapshotButton) {
    staticFixtureImportSnapshotButton.addEventListener(
      "click",
      handleStaticFixtureImportClick,
    );
  }

  if (staticFixtureImportFileInput) {
    staticFixtureImportFileInput.addEventListener(
      "change",
      handleStaticFixtureImportFileChange,
    );
  }

  if (staticFixtureResetImportButton) {
    staticFixtureResetImportButton.addEventListener(
      "click",
      handleStaticFixtureResetImport,
    );
  }
}
function buildStaticFixtureExportSnapshot() {
  const selected = readStaticFixtureBrowserFilters();
  const preview = buildStaticSemanticFixtureBrowserPayload();
  return {
    schemaVersion: "1.0.0",
    schema: "aigaane.staticSemanticFixtureExportSnapshot.v1",
    generatedBy: "ui/tabs/sanskrit/controller.js:static-fixture-export",
    generatedAt: new Date().toISOString(),
    mode: "static-preview",
    readOnly: true,
    backendRequired: false,
    canonicalMutationAllowed: false,
    url: currentStaticFixtureBrowserUrl(),
    hash: buildStaticFixtureBrowserHash(),
    selected,
    preview,
    filters: selected,
    payload: preview,
  };
}
function downloadStaticFixtureExport(filename, mimeType, content) {
  const blob = new Blob([content], { type: mimeType });
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = filename;
  anchor.rel = "noopener";
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(objectUrl);
}

function renderStaticFixtureExportStatus(message, mode = "success") {
  const status = byId("static-fixture-export-status");
  if (!status) return;
  status.textContent = text(message, "");
  status.classList.toggle("success", mode === "success");
  status.classList.toggle("warn", mode === "warn");
}

function staticFixtureExportTimestamp() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

function handleStaticFixtureExportJson() {
  try {
    const snapshot = buildStaticFixtureExportSnapshot();
    downloadStaticFixtureExport(
      `sanskrit-static-fixture-snapshot-${staticFixtureExportTimestamp()}.json`,
      "application/json;charset=utf-8",
      JSON.stringify(snapshot, null, 2),
    );
    renderStaticFixtureExportStatus("JSON snapshot exported", "success");
  } catch (error) {
    console.warn("[Sanskrit] Static fixture JSON export failed:", error);
    renderStaticFixtureExportStatus("JSON export unavailable", "warn");
  }
}

function buildStaticFixtureMarkdownReport(snapshot = buildStaticFixtureExportSnapshot()) {
  return [
    "# Sanskrit Static Semantic Fixture Snapshot",
    "",
    `Generated: ${snapshot.generatedAt}`,
    `Mode: ${snapshot.mode}`,
    `Read-only: ${snapshot.readOnly ? "yes" : "no"}`,
    `Backend required: ${snapshot.backendRequired ? "yes" : "no"}`,
    `Canonical mutation allowed: ${snapshot.canonicalMutationAllowed ? "yes" : "no"}`,
    `Inspection URL: ${snapshot.url}`,
    "",
    "## Selected State",
    "",
    `- Cluster: ${snapshot.filters.cluster || "any"}`,
    `- Dhatu ID: ${snapshot.filters.dhatuId || "any"}`,
    `- Node ID: ${snapshot.filters.nodeId || "any"}`,
    `- Section: ${snapshot.filters.section || "records"}`,
    "",
    "## Fixture Summary",
    "",
    `- Semantic records: ${snapshot.payload.semanticRecordCount}`,
    `- Available clusters: ${snapshot.payload.availableClusters.join(", ") || "none"}`,
    `- Graph nodes in view: ${snapshot.payload.graphNodes.length}`,
    `- Graph edges in view: ${snapshot.payload.graphEdges.length}`,
    `- Derivation graph available: ${snapshot.payload.derivationGraphFixtureAvailable ? "yes" : "no"}`,
    "",
    "## Safe JSON Preview",
    "",
    "```json",
    JSON.stringify(snapshot.payload, null, 2),
    "```",
    "",
  ].join("\n");
}

function handleStaticFixtureExportMarkdown() {
  try {
    const snapshot = buildStaticFixtureExportSnapshot();
    downloadStaticFixtureExport(
      `sanskrit-static-fixture-report-${staticFixtureExportTimestamp()}.md`,
      "text/markdown;charset=utf-8",
      buildStaticFixtureMarkdownReport(snapshot),
    );
    renderStaticFixtureExportStatus("Markdown report exported", "success");
  } catch (error) {
    console.warn("[Sanskrit] Static fixture Markdown export failed:", error);
    renderStaticFixtureExportStatus("Markdown export unavailable", "warn");
  }
}

function buildStaticFixtureTextSummary(snapshot = buildStaticFixtureExportSnapshot()) {
  return [
    "Sanskrit Static Semantic Fixture Snapshot",
    `Generated: ${snapshot.generatedAt}`,
    `Mode: ${snapshot.mode}`,
    `Read-only: ${snapshot.readOnly ? "yes" : "no"}`,
    `Backend required: ${snapshot.backendRequired ? "yes" : "no"}`,
    `Canonical mutation allowed: ${snapshot.canonicalMutationAllowed ? "yes" : "no"}`,
    `Inspection URL: ${snapshot.url}`,
    "",
    "Selected State",
    `Cluster: ${snapshot.filters.cluster || "any"}`,
    `Dhatu ID: ${snapshot.filters.dhatuId || "any"}`,
    `Node ID: ${snapshot.filters.nodeId || "any"}`,
    `Section: ${snapshot.filters.section || "records"}`,
    "",
    "Fixture Summary",
    `Semantic records: ${snapshot.payload.semanticRecordCount}`,
    `Available clusters: ${snapshot.payload.availableClusters.join(", ") || "none"}`,
    `Graph nodes in view: ${snapshot.payload.graphNodes.length}`,
    `Graph edges in view: ${snapshot.payload.graphEdges.length}`,
    `Derivation graph available: ${snapshot.payload.derivationGraphFixtureAvailable ? "yes" : "no"}`,
    "",
  ].join("\n");
}

function handleStaticFixtureExportText() {
  try {
    const snapshot = buildStaticFixtureExportSnapshot();
    downloadStaticFixtureExport(
      `sanskrit-static-fixture-summary-${staticFixtureExportTimestamp()}.txt`,
      "text/plain;charset=utf-8",
      buildStaticFixtureTextSummary(snapshot),
    );
    renderStaticFixtureExportStatus("Text summary exported", "success");
  } catch (error) {
    console.warn("[Sanskrit] Static fixture text export failed:", error);
    renderStaticFixtureExportStatus("Text export unavailable", "warn");
  }
}

function renderDiagnosticsStatusClass(status) {
  if (status === "READY_STATIC_PREVIEW") return "ready";
  if (status === "DEGRADED_STATIC_PREVIEW") return "degraded";
  return "blocked";
}

function appendDiagnosticsRow(container, label, status, note) {
  if (!container) return;
  const row = document.createElement("div");
  row.className = `local-diagnostics-row ${status ? "ok" : "warn"}`;
  const title = document.createElement("strong");
  const value = document.createElement("span");
  title.textContent = text(label);
  value.textContent = status ? "Available" : "Unavailable";
  row.append(title, value);
  if (note) {
    const detail = document.createElement("small");
    detail.textContent = text(note);
    row.appendChild(detail);
  }
  container.appendChild(row);
}

function renderLocalStaticDiagnostics(report) {
  const badge = byId("local-diagnostics-status-badge");
  const backend = byId("local-diagnostics-backend-output");
  const fallback = byId("local-diagnostics-fallback-output");
  const fixtures = byId("local-diagnostics-fixtures-output");
  const safety = byId("local-diagnostics-safety-output");
  const warnings = byId("local-diagnostics-warnings-output");

  if (badge) {
    badge.textContent = text(report?.diagnosticsStatus, "CHECKING");
    badge.className = `local-diagnostics-status-badge ${renderDiagnosticsStatusClass(report?.diagnosticsStatus)}`;
  }
  renderStaticSemanticFixtureBrowser(Boolean(
    report
      && report.diagnosticsStatus !== "CHECKING"
      && !report.backendAnalyzeAvailable
      && report.fallbackAnalysisAvailable,
  ));

  clearChildren(backend);
  appendDiagnosticsRow(
    backend,
    "Backend /api/v3/analyze",
    Boolean(report?.backendAnalyzeAvailable),
    report?.backendAnalyzeAvailable
      ? "Backend analysis route responded with JSON."
      : "Unavailable in static preview. Unavailable is allowed in local static preview mode.",
  );
  appendDiagnosticsRow(backend, "Backend required for green static mode", !report?.backendRequired, "Expected: not required");

  clearChildren(fallback);
  appendDiagnosticsRow(
    fallback,
    "Fallback analysis",
    Boolean(report?.fallbackAnalysisAvailable),
    report?.fallbackAnalysisAvailable
      ? "Local fallback renderer is ready."
      : "Fallback renderer is missing; static preview is blocked.",
  );
  appendDiagnosticsRow(fallback, "Controller module health", true, "Sanskrit controller initialized and rendered diagnostics.");

  clearChildren(fixtures);
  const fixtureChecks = Array.isArray(report?.fixtureChecks) ? report.fixtureChecks : [];
  fixtureChecks.forEach((check) => appendDiagnosticsRow(fixtures, check?.label, Boolean(check?.available), check?.path));
  if (fixtureChecks.length === 0) appendEmpty(fixtures, "No fixture checks returned");

  clearChildren(safety);
  const safetyChecks = Array.isArray(report?.safetyChecks) ? report.safetyChecks : [];
  safetyChecks.forEach((check) => appendDiagnosticsRow(safety, check?.label, Boolean(check?.passed), check?.note));
  if (safetyChecks.length === 0) appendEmpty(safety, "No safety checks returned");

  clearChildren(warnings);
  const warningValues = Array.isArray(report?.warnings) ? report.warnings : [];
  if (warningValues.length === 0) {
    appendEmpty(warnings, "No warnings");
  } else {
    warningValues.forEach((warning) => {
      const row = document.createElement("div");
      row.className = "local-diagnostics-warning";
      row.textContent = text(warning);
      warnings?.appendChild(row);
    });
  }
}

function renderDebugError(targetId, error) {
  const container = byId(targetId);
  clearChildren(container);
  if (!container) return;
  if (!error) {
    appendEmpty(container, "No debug error");
    return;
  }

  const detail = error.detail || error;
  appendDebugErrorRow(container, "Code", detail.code || "debug_error");
  appendDebugErrorRow(container, "Message", detail.message || text(detail));
}

function renderDebugSession(session) {
  const container = byId("debug-session-output");
  clearChildren(container);
  if (!container) return;
  if (!session) {
    appendEmpty(container, "No debug session");
    return;
  }

  appendInspectionRow(container, "Session ID", session.session_id);
  appendInspectionRow(container, "Created At", session.created_at);
  appendInspectionRow(container, "Input Text", session.input_text);
  appendInspectionRow(container, "Total Steps", session.total_steps, `ambiguity branches: ${text(session.total_ambiguity_branches, 0)}`);
}

function renderDebugSessionSteps(steps) {
  const container = byId("debug-session-steps-output");
  clearChildren(container);
  if (!container) return;

  const values = Array.isArray(steps) ? steps : [];
  if (values.length === 0) {
    const empty = document.createElement("li");
    empty.textContent = "No debug session steps";
    container.appendChild(empty);
    return;
  }

  values.forEach((step) => {
    const item = document.createElement("li");
    const title = document.createElement("strong");
    const body = document.createElement("span");
    const meta = document.createElement("small");
    const input = step?.input_state || {};
    const output = step?.output_state || {};
    const inputText = input.text || input.word1 || input.request?.stem || JSON.stringify(input);
    const outputText = output.text || output.merged || output.form || JSON.stringify(output);
    title.textContent = `${text(step?.step_id)} ${text(step?.operation)}`;
    body.textContent = ` ${text(inputText)} -> ${text(outputText)}`;
    meta.textContent = `engine: ${text(step?.engine)}; parent: ${text(step?.parent_step_id, "none")}`;
    item.append(title, body, meta);
    container.appendChild(item);
  });
}

function appendDebugDerivationPath(node, path) {
  const steps = Array.isArray(path) ? path : [];
  steps.forEach((step, index) => {
    const meta = document.createElement("small");
    meta.textContent = `path ${index + 1}: ${text(step?.sutra)} ${text(step?.operation)} ${text(step?.input_state)} -> ${text(step?.output_state)}`;
    node.appendChild(meta);
  });
}

function renderDebugAmbiguity(ambiguity) {
  const container = byId("debug-ambiguity-output");
  clearChildren(container);
  if (!container) return;
  if (!ambiguity) {
    appendEmpty(container, "No ambiguity demo loaded");
    return;
  }

  const candidates = Array.isArray(ambiguity.candidates) ? ambiguity.candidates : [];
  appendInspectionRow(container, "Ambiguous", ambiguity.is_ambiguous ? "true" : "false");
  appendInspectionRow(container, "Candidate Count", candidates.length);

  candidates.forEach((candidate) => {
    const row = document.createElement("div");
    row.className = "candidate-row";
    const title = document.createElement("strong");
    const output = document.createElement("span");
    const reason = document.createElement("small");
    title.textContent = text(candidate?.candidate_id);
    output.textContent = `: ${text(candidate?.final_output)}`;
    reason.textContent = text(candidate?.reason);
    row.append(title, output, reason);
    appendDebugDerivationPath(row, candidate?.derivation_path);
    container.appendChild(row);
  });
}

function renderDebugPipelineResult(data) {
  const container = byId("debug-pipeline-output");
  clearChildren(container);
  if (!container) return;
  if (!data) {
    appendEmpty(container, "No pipeline run");
    return;
  }

  appendInspectionRow(container, "Final Output", data.final_output || "No final output");

  const pipelineSteps = Array.isArray(data.pipeline_steps) ? data.pipeline_steps : [];
  if (pipelineSteps.length === 0) {
    appendEmpty(container, "No pipeline steps returned");
    return;
  }

  pipelineSteps.forEach((step, index) => {
    const output = step?.output_state || {};
    const renderedOutput = output.merged || output.form || JSON.stringify(output);
    appendInspectionRow(
      container,
      `Step ${index + 1}`,
      renderedOutput,
      `${text(step?.engine)} · ${text(step?.operation)}`,
    );
  });
}

function pipelineDataFromSession(session) {
  const steps = Array.isArray(session?.steps) ? session.steps : [];
  const pipelineSteps = steps.filter((step) => step?.metadata?.source === "debug_session_pipeline");
  if (pipelineSteps.length === 0) return null;
  const lastStep = pipelineSteps[pipelineSteps.length - 1];
  const output = lastStep?.output_state || {};
  return {
    final_output: output.merged || output.form || "",
    pipeline_steps: pipelineSteps,
  };
}

function renderDebugStorageStatus(message, type = "neutral") {
  const node = byId("debug-storage-status");
  if (!node) return;
  node.textContent = text(message, "Storage idle");
  node.classList.toggle("success", type === "success");
  node.classList.toggle("error", type === "error");
}

function renderDebugSessionStorageList(data) {
  const container = byId("debug-storage-list");
  clearChildren(container);
  if (!container) return;

  const sessions = Array.isArray(data?.sessions) ? [...data.sessions] : [];
  if (sessions.length === 0) {
    appendEmpty(container, "No saved sessions");
    return;
  }

  sessions.sort((left, right) => text(right?.created_at, "").localeCompare(text(left?.created_at, "")));

  sessions.forEach((session) => {
    const row = document.createElement("div");
    row.className = "debug-storage-row";

    const meta = document.createElement("div");
    meta.className = "debug-storage-meta";
    const sessionId = document.createElement("strong");
    const details = document.createElement("small");
    sessionId.textContent = text(session?.session_id, "unknown-session");
    details.textContent = `${text(session?.created_at, "created_at unavailable")} - steps: ${text(session?.step_count, "unknown")}`;
    meta.append(sessionId, details);

    const actions = document.createElement("div");
    actions.className = "debug-storage-actions";
    const loadButton = document.createElement("button");
    loadButton.type = "button";
    loadButton.textContent = "Load";
    loadButton.addEventListener("click", () => handleDebugSessionLoad(session?.session_id));

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "delete";
    deleteButton.textContent = "Delete";
    deleteButton.addEventListener("click", () => handleDebugSessionDelete(session?.session_id));
    actions.append(loadButton, deleteButton);

    row.append(meta, actions);
    container.appendChild(row);
  });
}

function renderPayload(payload) {
  renderFallbackAnalysisPanel(payload);
  setText("overall-stanza-meter", payload?.overall_stanza_meter);
  setText("total-matra-count", payload?.total_matra_count, 0);
  setText("diagnostic-count", Array.isArray(payload?.parser_diagnostics) ? payload.parser_diagnostics.length : 0, 0);
  setText("transliteration-output", payload?.transliteration);

  appendListItems(byId("sandhi-output"), payload?.sandhi, (item) => `${text(item?.rule)}: ${text(item?.before)} -> ${text(item?.after)}`);
  renderPadas(payload?.padas);
  renderSyllables(payload?.phonological_syllables);
  appendListItems(byId("derivation-history-output"), payload?.derivation_history, (step) => `${text(step?.stage)}: ${text(step?.input)} -> ${text(step?.output)} (${text(step?.rule)})`);
  renderGraph(payload?.prakriya_graph);
  renderLexical(payload?.lexical_lookup);
  appendListItems(byId("parser-diagnostics-output"), payload?.parser_diagnostics, (item) => `${text(item?.level)}: ${text(item?.message)}`);
  renderExperimental(payload?.experimental_payload);
}

async function readJsonResponse(response) {
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload || { detail: { code: "api_error", message: `HTTP ${response.status}` } };
    renderApiError(detail);
    throw new Error(detail.detail?.message || `HTTP ${response.status}`);
  }
  renderApiError(null);
  return payload;
}

async function postJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return readJsonResponse(response);
}

function normalizeSanskritFallbackInput(inputText) {
  return text(inputText, "")
    .trim()
    .replace(/\s+/g, " ")
    .toLowerCase();
}

function buildLocalSanskritAnalysisFallback(inputText) {
  const normalizedInput = normalizeSanskritFallbackInput(inputText);
  const tokens = normalizedInput ? normalizedInput.split(" ") : [];
  const sampleRigvedaOpening = "agnim ile purohitam yajnasya devam rtvijam hotaram ratnadhatamam";
  const isLikelyRigvedaOpening = normalizedInput === sampleRigvedaOpening;
  const safetyNote = "Local fallback only: backend analysis is required for authoritative vyakarana, exact chandas, exact sandhi, or canonical grammatical claims. No canonical registry or backend mutation is performed.";

  return {
    input_text: inputText,
    normalized_input: normalizedInput,
    pipelineStatus: {
      mode: "local-fallback",
      backendRoute: "/api/v3/analyze",
      backendUnavailable: true,
      backendUnavailableExplanation: "The backend /api/v3/analyze route was unavailable or returned an unreadable payload. This panel uses deterministic client-side fallback data and makes no authoritative grammatical claim.",
      likelySourceMarker: isLikelyRigvedaOpening
        ? "Likely Rigveda 1.1.1 opening mantra transliteration-style input."
        : "Local transliteration-style input fallback; source not identified.",
      stages: [
        { stage: "transliteration", label: "Transliteration", status: "latin/IAST-like fallback mode" },
        { stage: "tokenization", label: "Tokenization", status: `${tokens.length} whitespace tokens` },
        { stage: "sandhi", label: "Sandhi", status: "not resolved locally; backend required" },
        { stage: "chandas", label: "Chandas", status: "not authoritatively determined in fallback mode" },
        { stage: "vyakarana", label: "Vyakarana", status: "backend required for full parse" },
        { stage: "prakriya_graph", label: "Prakriya graph", status: "local placeholder only" },
      ],
    },
    transliteration: "latin/IAST-like fallback",
    tokenization: {
      method: "whitespace",
      tokens,
      token_count: tokens.length,
      likelyRigvedaOpening: isLikelyRigvedaOpening,
      source_note: isLikelyRigvedaOpening
        ? "Likely Rigveda 1.1.1 opening mantra transliteration-style input."
        : "No source identification is asserted in fallback mode.",
    },
    sandhi: [
      {
        rule: "fallback_no_sandhi_resolution",
        before: normalizedInput,
        after: normalizedInput,
        note: "No exact sandhi claim is made without backend analysis.",
      },
    ],
    chandas: {
      status: "not_authoritatively_determined",
      note: "Chandas is not authoritatively determined in fallback mode.",
      exact_meter_claim: false,
    },
    vyakarana: {
      status: "backend_required",
      note: "Backend required for full parse; no authoritative grammatical claim is made.",
    },
    prakriya_graph: {
      graph_status: "local_placeholder_only",
      nodes: [
        { id: "input", label: "Input text", type: "input" },
        { id: "tokens", label: "Fallback tokens", type: "tokenization" },
        { id: "backend-required", label: "Backend parse required", type: "safety" },
      ],
      edges: [
        { from: "input", to: "tokens", label: "whitespace fallback" },
        { from: "tokens", to: "backend-required", label: "no authoritative parse" },
      ],
    },
    safety_note: safetyNote,
    overall_stanza_meter: "not authoritatively determined in fallback mode",
    total_matra_count: 0,
    parser_diagnostics: [
      { level: "info", message: "Analysis rendered with local fallback because /api/v3/analyze was unavailable or unreadable." },
      { level: "warning", message: "Backend required for full Sanskrit grammatical parsing and exact chandas." },
      ...(isLikelyRigvedaOpening
        ? [{ level: "info", message: "Likely Rigveda 1.1.1 opening mantra transliteration-style input." }]
        : []),
    ],
    padas: [],
    phonological_syllables: [],
    derivation_history: [
      {
        stage: "tokenization",
        input: normalizedInput,
        output: tokens.join(" | "),
        rule: "local whitespace fallback",
      },
      {
        stage: "vyakarana",
        input: tokens.join(" | "),
        output: "backend required for full parse",
        rule: "no authoritative grammatical claim",
      },
    ],
    lexical_lookup: tokens.map((tokenValue, index) => ({
      token: tokenValue,
      index,
      status: "fallback-token-only",
      note: "Lexical identity is not asserted without backend analysis.",
    })),
    experimental_payload: {
      field_map: tokens.map((tokenValue, index) => ({
        symbol: tokenValue.slice(0, 1) || "-",
        token: tokenValue,
        index,
      })),
    },
  };
}

async function checkLocalStaticFixture(label, path) {
  try {
    const response = await fetch(path, { cache: "no-store" });
    const payload = await response.json().catch(() => null);
    return {
      label,
      path,
      available: Boolean(response.ok && payload && typeof payload === "object"),
      status: response.status,
      note: response.ok ? "Read-only fixture loaded." : `Fixture fetch returned HTTP ${response.status}.`,
    };
  } catch (error) {
    return {
      label,
      path,
      available: false,
      status: "fetch-error",
      note: text(error?.message, "Fixture fetch failed."),
    };
  }
}

async function checkBackendAnalyzeAvailability() {
  try {
    const response = await fetch("/api/v3/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input_text: DEFAULT_PAYLOAD.input_text }),
      cache: "no-store",
    });
    if (isExpectedStaticPreviewApiMiss(response)) {
      console.info("[Sanskrit] Static diagnostics expected backend miss:", response.status);
      return { available: false, expectedStaticPreviewMiss: true, status: response.status };
    }
    const payload = await response.json().catch(() => null);
    return {
      available: Boolean(response.ok && payload && typeof payload === "object"),
      expectedStaticPreviewMiss: false,
      status: response.status,
    };
  } catch (error) {
    if (isExpectedStaticPreviewApiMiss(error)) {
      console.info("[Sanskrit] Static diagnostics expected backend miss:", error);
      return { available: false, expectedStaticPreviewMiss: true, status: error?.status || "expected-miss" };
    }
    console.warn("[Sanskrit] Static diagnostics backend probe:", error);
    return { available: false, expectedStaticPreviewMiss: false, status: "fetch-error" };
  }
}

async function buildLocalStaticDiagnosticsReport() {
  const fixtureChecks = await Promise.all([
    checkLocalStaticFixture("Semantic UI fixture", SEMANTIC_DHATU_PANEL_FIXTURE),
    checkLocalStaticFixture("Semantic graph fixture", SEMANTIC_GRAPH_PANEL_FIXTURE),
    checkLocalStaticFixture("Derivation fixture", SEMANTIC_DERIVATION_DATA_FIXTURE),
    checkLocalStaticFixture("Derivation graph fixture", SEMANTIC_DERIVATION_GRAPH_PANEL_FIXTURE),
    checkLocalStaticFixture("Platform status fixture", SEMANTIC_PLATFORM_STATUS_PANEL_FIXTURE),
  ]);
  const backendAnalyze = await checkBackendAnalyzeAvailability();
  const backendAnalyzeAvailable = Boolean(backendAnalyze.available);
  const fallbackAnalysisAvailable = typeof buildLocalSanskritAnalysisFallback === "function";
  const fixtureFailures = fixtureChecks.filter((check) => !check.available);
  const diagnosticsStatus = !fallbackAnalysisAvailable
    ? "BLOCKED"
    : fixtureFailures.length > 0
      ? "DEGRADED_STATIC_PREVIEW"
      : "READY_STATIC_PREVIEW";
  const warnings = [];

  if (!backendAnalyzeAvailable) {
    warnings.push("Backend /api/v3/analyze unavailable; allowed for local static preview because fallback analysis is ready.");
  }
  fixtureFailures.forEach((check) => warnings.push(`${check.label} unavailable; built-in UI fallback remains read-only.`));

  return {
    schemaVersion: "1.0.0",
    generatedBy: "ui/tabs/sanskrit/controller.js:buildLocalStaticDiagnosticsReport",
    diagnosticsStatus,
    staticModeSupported: true,
    backendRequired: false,
    backendAnalyzeAvailable,
    backendAnalyzeUnavailableExpected: Boolean(backendAnalyze.expectedStaticPreviewMiss || !backendAnalyzeAvailable),
    backendAnalyzeStatus: backendAnalyze.status,
    fallbackAnalysisAvailable,
    fixtureChecks,
    safetyChecks: [
      {
        label: "Canonical registry mutation",
        passed: true,
        note: "Diagnostics only fetch static JSON fixtures and do not write canonical records.",
      },
      {
        label: "Canonical writer",
        passed: true,
        note: "No canonical writer is called by local static diagnostics.",
      },
      {
        label: "Canonical write environment flags",
        passed: true,
        note: "No canonical write environment flags are set by browser diagnostics.",
      },
      {
        label: "Backend optional in static mode",
        passed: true,
        note: "Backend unavailable is allowed when fallback analysis is available.",
      },
    ],
    warnings,
    checkedAt: new Date().toISOString(),
  };
}

async function runLocalStaticDiagnostics() {
  renderLocalStaticDiagnostics({
    schemaVersion: "1.0.0",
    generatedBy: "ui/tabs/sanskrit/controller.js:runLocalStaticDiagnostics",
    diagnosticsStatus: "CHECKING",
    staticModeSupported: true,
    backendRequired: false,
    backendAnalyzeAvailable: false,
    fallbackAnalysisAvailable: typeof buildLocalSanskritAnalysisFallback === "function",
    fixtureChecks: [],
    safetyChecks: [],
    warnings: ["Running local static diagnostics..."],
    checkedAt: new Date().toISOString(),
  });

  try {
    const report = await buildLocalStaticDiagnosticsReport();
    renderLocalStaticDiagnostics(report);
  } catch (error) {
    console.warn("[Sanskrit] Local static diagnostics failed:", error);
    renderLocalStaticDiagnostics({
      schemaVersion: "1.0.0",
      generatedBy: "ui/tabs/sanskrit/controller.js:runLocalStaticDiagnostics",
      diagnosticsStatus: "BLOCKED",
      staticModeSupported: true,
      backendRequired: false,
      backendAnalyzeAvailable: false,
      fallbackAnalysisAvailable: false,
      fixtureChecks: [],
      safetyChecks: [],
      warnings: [text(error?.message, "Diagnostics failed.")],
      checkedAt: new Date().toISOString(),
    });
  }
}

async function readDebugJsonResponse(response, targetId) {
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload || { detail: { code: "debug_api_error", message: `HTTP ${response.status}` } };
    renderDebugError(targetId, detail);
    throw new Error(detail.detail?.message || `HTTP ${response.status}`);
  }
  renderDebugError(targetId, null);
  return payload;
}

async function postDebugJson(url, body, targetId) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return readDebugJsonResponse(response, targetId);
}

async function getDebugJson(url, targetId) {
  let response = await fetch(url);
  const isLocalFrontend = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
  if (!response.ok && response.status === 404 && isLocalFrontend && url.startsWith("/api/")) {
    response = await fetch(`http://127.0.0.1:8000${url}`);
  }
  return readDebugJsonResponse(response, targetId);
}

async function readLexiconJsonResponse(response) {
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload?.detail || payload || {};
    throw new Error(detail.message || `HTTP ${response.status}`);
  }
  return payload;
}

async function getLexiconJson(url) {
  let response = await fetch(url);
  const isLocalFrontend = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
  if (!response.ok && response.status === 404 && isLocalFrontend && url.startsWith("/api/")) {
    response = await fetch(`http://127.0.0.1:8000${url}`);
  }
  return readLexiconJsonResponse(response);
}

async function getSutraJson(url) {
  let response = await fetch(url);
  const isLocalFrontend = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
  if (!response.ok && response.status === 404 && isLocalFrontend && url.startsWith("/api/")) {
    response = await fetch(`http://127.0.0.1:8000${url}`);
  }
  return readLexiconJsonResponse(response);
}

async function postSemanticTraceJson(url, body) {
  let response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const isLocalFrontend = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
  if (!response.ok && response.status === 404 && isLocalFrontend && url.startsWith("/api/")) {
    response = await fetch(`http://127.0.0.1:8000${url}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  }
  return readLexiconJsonResponse(response);
}

async function getSemanticTraceJson(url) {
  let response = await fetch(url);
  const isLocalFrontend = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
  if (!response.ok && response.status === 404 && isLocalFrontend && url.startsWith("/api/")) {
    response = await fetch(`http://127.0.0.1:8000${url}`);
  }
  return readLexiconJsonResponse(response);
}

async function postGraphJson(url, body) {
  let response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const isLocalFrontend = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
  if (!response.ok && response.status === 404 && isLocalFrontend && url.startsWith("/api/")) {
    response = await fetch(`http://127.0.0.1:8000${url}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  }
  return readLexiconJsonResponse(response);
}

async function getGraphJson(url) {
  let response = await fetch(url);
  const isLocalFrontend = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
  if (!response.ok && response.status === 404 && isLocalFrontend && url.startsWith("/api/")) {
    response = await fetch(`http://127.0.0.1:8000${url}`);
  }
  return readLexiconJsonResponse(response);
}

async function postReplayJson(url, body) {
  let response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const isLocalFrontend = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
  if (!response.ok && response.status === 404 && isLocalFrontend && url.startsWith("/api/")) {
    response = await fetch(`http://127.0.0.1:8000${url}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  }
  return readLexiconJsonResponse(response);
}

async function getReplayJson(url) {
  let response = await fetch(url);
  const isLocalFrontend = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
  if (!response.ok && response.status === 404 && isLocalFrontend && url.startsWith("/api/")) {
    response = await fetch(`http://127.0.0.1:8000${url}`);
  }
  return readLexiconJsonResponse(response);
}

function renderLexiconStatus(message, type = "neutral") {
  const node = byId("lexicon-status");
  if (!node) return;
  node.textContent = text(message, "Lexicon idle");
  node.classList.toggle("success", type === "success");
  node.classList.toggle("error", type === "error");
}

function renderLexiconError(message) {
  renderLexiconStatus(message || "Lexicon request failed", "error");
}

function renderLexiconSamples(data) {
  const container = byId("lexicon-samples-output");
  clearChildren(container);
  if (!container) return;

  const entries = Array.isArray(data?.entries) ? data.entries : [];
  if (entries.length === 0) {
    appendEmpty(container, "No sample entries");
    return;
  }

  entries.forEach((entry) => {
    const row = document.createElement("div");
    row.className = "lexicon-row";
    const title = document.createElement("strong");
    const body = document.createElement("span");
    const meta = document.createElement("small");
    title.textContent = text(entry?.lemma_devanagari);
    body.textContent = ` ${text(entry?.lemma_iast)} · ${text(entry?.category)}`;
    meta.textContent = `${text(entry?.lexical_id)} · status: ${text(entry?.status)}`;
    row.append(title, body, meta);
    container.appendChild(row);
  });
}

function renderLexiconSources(data) {
  const container = byId("lexicon-sources-output");
  clearChildren(container);
  if (!container) return;

  const sources = Array.isArray(data?.sources) ? data.sources : [];
  if (sources.length === 0) {
    appendEmpty(container, "No registry sources");
    return;
  }

  sources.forEach((source) => {
    const row = document.createElement("div");
    row.className = "lexicon-row";
    const title = document.createElement("strong");
    const body = document.createElement("span");
    const badge = document.createElement("span");
    const citation = document.createElement("small");
    title.textContent = text(source?.name);
    body.textContent = ` ${text(source?.type)}`;
    badge.className = `lexicon-badge ${source?.verified ? "verified" : "draft"}`;
    badge.textContent = source?.verified ? "verified" : "unverified";
    citation.textContent = text(source?.citation, "No citation");
    row.append(title, body, badge, citation);
    container.appendChild(row);
  });
}

function renderLexiconValidation(data) {
  const container = byId("lexicon-validation-output");
  clearChildren(container);
  if (!container) return;
  if (!data) {
    appendEmpty(container, "No validation run");
    return;
  }

  const summary = document.createElement("div");
  summary.className = `lexicon-validation-summary ${data.valid ? "success" : "error"}`;
  summary.textContent = `valid: ${data.valid === true ? "true" : "false"} · entries: ${text(data.entry_count, 0)}`;
  container.appendChild(summary);

  const ids = Array.isArray(data.validated_ids) ? data.validated_ids : [];
  appendInspectionRow(container, "Validated IDs", ids.length > 0 ? ids.join(", ") : "none");

  const errors = Array.isArray(data.errors) ? data.errors : [];
  if (errors.length === 0) {
    appendInspectionRow(container, "Errors", "none");
    renderLexiconStatus("Registry validation passed", "success");
    return;
  }

  errors.forEach((error, index) => {
    appendInspectionRow(container, `Error ${index + 1}`, typeof error === "object" ? JSON.stringify(error) : error);
  });
}

function renderSutraStatus(message, type = "neutral") {
  const node = byId("sutra-status");
  if (!node) return;
  node.textContent = text(message, "Sutra registry idle");
  node.classList.toggle("success", type === "success");
  node.classList.toggle("error", type === "error");
}

function renderSutraError(message) {
  renderSutraStatus(message || "Sutra registry request failed", "error");
}

function renderSutraSamples(data) {
  const container = byId("sutra-samples-output");
  clearChildren(container);
  if (!container) return;

  const sutras = Array.isArray(data?.sutras) ? data.sutras : [];
  if (sutras.length === 0) {
    appendEmpty(container, "No operational sutras");
    return;
  }

  sutras.forEach((sutra) => {
    const row = document.createElement("div");
    row.className = "sutra-row";
    const title = document.createElement("strong");
    const body = document.createElement("span");
    const domain = document.createElement("span");
    const status = document.createElement("span");
    const meta = document.createElement("small");
    title.textContent = text(sutra?.sutra_id);
    body.textContent = ` ${text(sutra?.sutra_text_devanagari)} · ${text(sutra?.sutra_text_iast)}`;
    domain.className = "sutra-badge domain";
    domain.textContent = text(sutra?.domain, "unknown");
    status.className = `sutra-badge ${sutra?.status === "canonical" ? "canonical" : "provisional"}`;
    status.textContent = text(sutra?.status, "unknown");
    meta.textContent = `${text(sutra?.source)} · ${text(sutra?.source_type)}`;
    row.append(title, body, domain, status, meta);
    container.appendChild(row);
  });
}

function renderSutraSources(data) {
  const container = byId("sutra-sources-output");
  clearChildren(container);
  if (!container) return;

  const sources = Array.isArray(data?.sources) ? data.sources : [];
  if (sources.length === 0) {
    appendEmpty(container, "No sutra sources");
    return;
  }

  sources.forEach((source) => {
    const row = document.createElement("div");
    row.className = "sutra-row";
    const title = document.createElement("strong");
    const body = document.createElement("span");
    const badge = document.createElement("span");
    const provenance = document.createElement("small");
    title.textContent = text(source?.name);
    body.textContent = ` ${text(source?.source_type || source?.type, "unknown")}`;
    badge.className = "sutra-badge canonical";
    badge.textContent = text(source?.verified === false ? "unverified" : "governed");
    provenance.textContent = text(source?.provenance || source?.description || source?.citation, "No provenance");
    row.append(title, body, badge, provenance);
    container.appendChild(row);
  });
}

function renderSutraValidation(data) {
  const container = byId("sutra-validation-output");
  clearChildren(container);
  if (!container) return;
  if (!data) {
    appendEmpty(container, "No validation run");
    return;
  }

  const summary = document.createElement("div");
  summary.className = `sutra-validation-summary ${data.valid ? "success" : "error"}`;
  summary.textContent = `valid: ${data.valid === true ? "true" : "false"} · sutras: ${text(data.sutra_count, 0)}`;
  container.appendChild(summary);

  const ids = Array.isArray(data.validated_ids) ? data.validated_ids : [];
  appendInspectionRow(container, "Validated IDs", ids.length > 0 ? ids.join(", ") : "none");

  const errors = Array.isArray(data.errors) ? data.errors : [];
  if (errors.length === 0) {
    appendInspectionRow(container, "Errors", "none");
    renderSutraStatus("Sutra registry validation passed", "success");
    return;
  }

  errors.forEach((error, index) => {
    appendInspectionRow(container, `Error ${index + 1}`, typeof error === "object" ? JSON.stringify(error) : error);
  });
}

function renderSemanticTraceStatus(message, type = "neutral") {
  const node = byId("semantic-trace-status");
  if (!node) return;
  node.textContent = text(message, "Semantic trace idle");
  node.classList.toggle("success", type === "success");
  node.classList.toggle("error", type === "error");
}

function renderSemanticTraceError(message) {
  renderSemanticTraceStatus(message || "Semantic trace request failed", "error");
}

function renderSemanticTraceStep(step) {
  const row = document.createElement("div");
  row.className = "semantic-trace-row";

  const title = document.createElement("strong");
  const sutra = document.createElement("span");
  title.textContent = text(step?.operation, "unknown_operation");
  sutra.textContent = ` sutra: ${text(step?.sutra, "unresolved")}`;
  row.append(title, sutra);

  const ref = step?.sutra_ref || null;
  if (!ref) {
    const unresolved = document.createElement("small");
    unresolved.className = "semantic-trace-unresolved";
    unresolved.textContent = "unresolved canonical sutra reference";
    row.appendChild(unresolved);
    return row;
  }

  const metadata = document.createElement("div");
  metadata.className = "semantic-sutra-metadata";

  const devanagari = document.createElement("span");
  const iast = document.createElement("small");
  const domain = document.createElement("span");
  const status = document.createElement("span");
  devanagari.textContent = text(ref.sutra_text_devanagari);
  iast.textContent = text(ref.sutra_text_iast);
  domain.className = "semantic-trace-badge domain";
  domain.textContent = text(ref.domain, "unknown");
  status.className = `semantic-trace-badge ${ref.status === "canonical" ? "canonical" : "provisional"}`;
  status.textContent = text(ref.status, "unknown");
  metadata.append(devanagari, iast, domain, status);
  row.appendChild(metadata);
  return row;
}

function renderSemanticTrace(trace, targetId = "semantic-trace-linked-output") {
  const container = byId(targetId);
  clearChildren(container);
  if (!container) return;

  const steps = Array.isArray(trace) ? trace : [];
  if (steps.length === 0) {
    appendEmpty(container, "No semantic trace steps");
    return;
  }

  steps.forEach((step) => {
    container.appendChild(renderSemanticTraceStep(step));
  });
}

function renderGraphStatus(message, type = "neutral") {
  const node = byId("graph-status");
  if (!node) return;
  node.textContent = text(message, "Graph inspector idle");
  node.classList.toggle("success", type === "success");
  node.classList.toggle("error", type === "error");
}

function renderGraphError(message) {
  renderGraphStatus(message || "Graph request failed", "error");
}

function renderGraphNode(node) {
  const row = document.createElement("div");
  row.className = "graph-node-card";

  const title = document.createElement("strong");
  const meta = document.createElement("span");
  const detail = document.createElement("small");
  title.textContent = text(node?.title, text(node?.node_id, "graph node"));
  meta.textContent = `${text(node?.engine)} · ${text(node?.operation)}`;
  detail.textContent = `${text(node?.node_id)} · step ${text(node?.step_id)} · ${text(node?.timestamp)}`;
  row.append(title, meta, detail);

  const branchIds = Array.isArray(node?.ambiguity_branch_ids) ? node.ambiguity_branch_ids : [];
  if (branchIds.length > 0) {
    const badge = document.createElement("span");
    badge.className = "graph-badge ambiguity";
    badge.textContent = `ambiguity: ${branchIds.join(", ")}`;
    row.appendChild(badge);
  }

  return row;
}

function renderGraphEdge(edge) {
  const row = document.createElement("div");
  row.className = "graph-edge-row";

  const title = document.createElement("strong");
  const detail = document.createElement("span");
  title.textContent = text(edge?.relation, "derives_to");
  detail.textContent = `${text(edge?.source)} -> ${text(edge?.target)}`;
  row.append(title, detail);
  return row;
}

function renderDerivationGraph(graph, targetId = "graph-session-output") {
  const container = byId(targetId);
  clearChildren(container);
  if (!container) return;
  if (!graph || typeof graph !== "object") {
    appendEmpty(container, "No graph exported");
    return;
  }

  const metadata = graph.metadata || {};
  const nodes = Array.isArray(graph.nodes) ? graph.nodes : [];
  const edges = Array.isArray(graph.edges) ? graph.edges : [];

  const summary = document.createElement("div");
  summary.className = "graph-metadata-panel";
  appendInspectionRow(summary, "Session", metadata.session_id);
  appendInspectionRow(summary, "Input", metadata.input_text);
  appendInspectionRow(summary, "Nodes", text(metadata.total_nodes, nodes.length));
  appendInspectionRow(summary, "Edges", text(metadata.total_edges, edges.length));
  container.appendChild(summary);

  const nodeSection = document.createElement("div");
  nodeSection.className = "graph-section-block";
  const nodeTitle = document.createElement("strong");
  nodeTitle.textContent = "Nodes";
  nodeSection.appendChild(nodeTitle);
  if (nodes.length === 0) {
    appendEmpty(nodeSection, "No graph nodes");
  } else {
    nodes.forEach((node) => nodeSection.appendChild(renderGraphNode(node)));
  }
  container.appendChild(nodeSection);

  const edgeSection = document.createElement("div");
  edgeSection.className = "graph-section-block";
  const edgeTitle = document.createElement("strong");
  edgeTitle.textContent = "Edges";
  edgeSection.appendChild(edgeTitle);
  if (edges.length === 0) {
    appendEmpty(edgeSection, "No graph edges");
  } else {
    edges.forEach((edge) => edgeSection.appendChild(renderGraphEdge(edge)));
  }
  container.appendChild(edgeSection);
}

function renderReplayStatus(message, type = "neutral") {
  const node = byId("replay-status");
  if (!node) return;
  node.textContent = text(message, "Replay inspector idle");
  node.classList.toggle("success", type === "success");
  node.classList.toggle("error", type === "error");
}

function renderReplayError(message) {
  renderReplayStatus(message || "Replay request failed", "error");
}

function renderReplayFrame(frame) {
  const row = document.createElement("div");
  row.className = "replay-frame-card";

  const title = document.createElement("strong");
  const meta = document.createElement("span");
  const detail = document.createElement("small");
  title.textContent = text(frame?.title, text(frame?.frame_id, "replay frame"));
  meta.textContent = `${text(frame?.engine)} · ${text(frame?.operation)}`;
  detail.textContent = `${text(frame?.frame_id)} · step ${text(frame?.step_id)} · ${text(frame?.timestamp)}`;
  row.append(title, meta, detail);

  const branchIds = Array.isArray(frame?.ambiguity_branch_ids) ? frame.ambiguity_branch_ids : [];
  if (branchIds.length > 0) {
    const badge = document.createElement("span");
    badge.className = "replay-badge ambiguity";
    badge.textContent = `ambiguity replay: ${branchIds.join(", ")}`;
    row.appendChild(badge);
  }

  return row;
}

function renderReplayTimeline(replay, targetId = "replay-session-output") {
  const container = byId(targetId);
  clearChildren(container);
  if (!container) return;
  if (!replay || typeof replay !== "object") {
    appendEmpty(container, "No replay exported");
    return;
  }

  const metadata = replay.metadata || {};
  const frames = Array.isArray(replay.timeline) ? replay.timeline : [];

  const summary = document.createElement("div");
  summary.className = "replay-metadata-panel";
  appendInspectionRow(summary, "Replay", replay.replay_id);
  appendInspectionRow(summary, "Session", metadata.session_id);
  appendInspectionRow(summary, "Input", metadata.input_text);
  appendInspectionRow(summary, "Frames", text(metadata.total_frames, frames.length));
  container.appendChild(summary);

  const frameSection = document.createElement("div");
  frameSection.className = "replay-section-block";
  const frameTitle = document.createElement("strong");
  frameTitle.textContent = "Frames";
  frameSection.appendChild(frameTitle);
  if (frames.length === 0) {
    appendEmpty(frameSection, "No replay frames");
  } else {
    frames.forEach((frame) => frameSection.appendChild(renderReplayFrame(frame)));
  }
  container.appendChild(frameSection);
}

async function analyzeCurrentInput() {
  if (!inputNode) return;

  const inputText = inputNode.value.trim();

  if (!inputText) {
    renderTransliterationPanel(inputText);
    renderPhoneticTopologyPanel(inputText);
    renderSandhiExecutionPanel(inputText);
    renderSubantaGeneratorPanel(inputText);
    renderTinantaGeneratorPanels(inputText);
    renderPrakriyaCompositionPanel(inputText);
    renderDerivationGraphPanel(inputText);
    renderSutraReferencePanel(inputText);
    renderRuleTracePanel(inputText);
    renderMorphologyTransitionPanel(inputText);
    renderKarakaOverlayPanel(inputText);
    renderVakyaDependencyPanel(inputText);
    renderSandarbhaContextPanel(inputText);
    renderChandasProsodyPanel(inputText);
    renderDhatuSemanticPanel(inputText);
    setStatus("Enter Sanskrit text to analyze.", true);
    return;
  }

  renderTransliterationPanel(inputText);
  renderPhoneticTopologyPanel(inputText);
  renderSandhiExecutionPanel(inputText);
  renderSubantaGeneratorPanel(inputText);
  renderTinantaGeneratorPanels(inputText);
  renderPrakriyaCompositionPanel(inputText);
  renderDerivationGraphPanel(inputText);
  renderSutraReferencePanel(inputText);
  renderRuleTracePanel(inputText);
  renderMorphologyTransitionPanel(inputText);
  renderKarakaOverlayPanel(inputText);
  renderVakyaDependencyPanel(inputText);
  renderSandarbhaContextPanel(inputText);
  renderChandasProsodyPanel(inputText);
  renderDhatuSemanticPanel(inputText);
  setStatus("Analyzing...");
  setBusy(analyzeButton, true);

  try {
    const response = await fetch("/api/v3/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input_text: inputText }),
    });

    if (isExpectedStaticPreviewApiMiss(response)) {
      console.info("[Sanskrit] Expected static preview API miss; local fallback active.", response.status);

      const fallbackPayload = buildLocalSanskritAnalysisFallback(inputText);

      renderStaticPreviewFallbackNotice(
        "Static Preview Mode active. Backend API routes are unavailable from Live Server; deterministic local fallback rendered.",
      );

      renderApiError({
        detail: {
          code: "static_preview_backend_unavailable",
          message: "Backend unavailable in static preview; local fallback active.",
        },
      });

      renderPayload(fallbackPayload);
      setStatus("Backend unavailable; local fallback active");
      return;
    }

    const payload = await response.json().catch(() => null);

    if (!response.ok || !payload || typeof payload !== "object") {
      throw new Error(response.ok ? "Unreadable analysis payload" : `HTTP ${response.status}`);
    }

    renderStaticPreviewFallbackNotice(null);
    renderApiError(null);
    renderPayload(payload);
    setStatus("Analysis complete");
  } catch (error) {
    const expectedMiss = isExpectedStaticPreviewApiMiss(error);

    if (expectedMiss) {
      console.info("[Sanskrit] Expected static preview API miss; local fallback active.", error);
    } else {
      console.warn("[Sanskrit] Analysis fallback after backend issue:", error);
    }

    const payload = buildLocalSanskritAnalysisFallback(inputText);

    renderStaticPreviewFallbackNotice(
  expectedMiss
    ? "Static Preview Mode active. Backend API routes are unavailable from Live Server; Local fallback rendered."
    : "Backend runtime unavailable or unreadable; Local fallback rendered.",
);

renderApiError({
  detail: {
    code: expectedMiss ? "static_preview_backend_unavailable" : "local_fallback",
    message: expectedMiss
      ? "Backend unavailable in static preview; Local fallback rendered."
      : "Backend analysis unavailable; Local fallback rendered.",
  },
});

renderPayload(payload);
setStatus(
  expectedMiss
    ? "Backend unavailable; local fallback active"
    : "Analysis rendered with local fallback",
);
  } finally {
    setBusy(analyzeButton, false);
  }
}
async function runSandhi() {
  setStatus("Running sandhi...");
  setBusy(sandhiButton, true);

  try {
    const data = await postJson("/api/v3/sandhi", {
      word1: fieldValue("sandhi-word1"),
      word2: fieldValue("sandhi-word2"),
    });
    renderSandhiResult(data);
    renderDerivationTimeline(data?.derivation_path);
    renderGovernancePanel(data?.governance);
    renderAmbiguityPanel(data?.ambiguity);
    setStatus("Sandhi complete");
  } catch (error) {
    console.error("[Sanskrit] Sandhi error:", error);
    setStatus("Sandhi unavailable", true);
  } finally {
    setBusy(sandhiButton, false);
  }
}

function morphologyMode() {
  return all('input[name="morphology-mode"]').find((input) => input.checked)?.value || "noun";
}

function updateMorphologyFields() {
  const mode = morphologyMode();
  all("[data-morphology-fields]").forEach((node) => {
    node.classList.toggle("hidden", node.dataset.morphologyFields !== mode);
  });
}

function morphologyRequest() {
  if (morphologyMode() === "verb") {
    return {
      url: "/api/v3/morphology/verb/conjugate",
      body: {
        dhatu: fieldValue("morphology-dhatu"),
        lakara: fieldValue("morphology-lakara"),
        person: fieldValue("morphology-person"),
        number: fieldValue("morphology-verb-number"),
      },
    };
  }

  return {
    url: "/api/v3/morphology/noun/inflect",
    body: {
      stem: fieldValue("morphology-stem"),
      case: fieldValue("morphology-case"),
      number: fieldValue("morphology-number"),
    },
  };
}

async function runMorphology() {
  setStatus("Running morphology...");
  setBusy(morphologyButton, true);

  try {
    const request = morphologyRequest();
    const data = await postJson(request.url, request.body);
    renderMorphologyResult(data);
    renderDerivationTimeline(data?.derivation_path);
    renderGovernancePanel(data?.governance);
    renderAmbiguityPanel(data?.ambiguity);
    setStatus("Morphology complete");
  } catch (error) {
    console.error("[Sanskrit] Morphology error:", error);
    setStatus("Morphology unavailable", true);
  } finally {
    setBusy(morphologyButton, false);
  }
}

async function handleDebugSessionCreate() {
  setStatus("Creating debug session...");
  setBusy(debugCreateButton, true);

  try {
    currentDebugSession = await postDebugJson(
      "/api/v3/debug/session/create",
      {
        input_text: fieldValue("debug-session-input"),
        metadata: { source: "sanskrit_tab_debug_ui" },
      },
      "debug-session-error-output",
    );
    renderDebugSession(currentDebugSession);
    renderDebugSessionSteps(currentDebugSession?.steps);
    setStatus("Debug session created");
  } catch (error) {
    console.error("[Sanskrit] Debug session create error:", error);
    setStatus("Debug session unavailable", true);
  } finally {
    setBusy(debugCreateButton, false);
  }
}

async function handleDebugSessionAppend() {
  if (!currentDebugSession) {
    renderDebugError("debug-session-error-output", {
      detail: {
        code: "debug_session_missing",
        message: "Create a debug session before appending a step.",
      },
    });
    setStatus("Create a debug session first.", true);
    return;
  }

  setStatus("Appending debug step...");
  setBusy(debugAppendButton, true);

  try {
    const steps = Array.isArray(currentDebugSession.steps) ? currentDebugSession.steps : [];
    const lastStep = steps.length > 0 ? steps[steps.length - 1] : null;
    currentDebugSession = await postDebugJson(
      "/api/v3/debug/session/append",
      {
        session: currentDebugSession,
        step: {
          engine: "debug.ui",
          operation: "manual_debug_step",
          input_state: { text: "debug-input" },
          output_state: { text: "debug-output" },
          parent_step_id: lastStep?.step_id || null,
          derivation_path: [],
          metadata: { source: "sanskrit_tab_debug_ui" },
        },
      },
      "debug-session-error-output",
    );
    renderDebugSession(currentDebugSession);
    renderDebugSessionSteps(currentDebugSession?.steps);
    setStatus("Debug step appended");
  } catch (error) {
    console.error("[Sanskrit] Debug session append error:", error);
    setStatus("Debug append unavailable", true);
  } finally {
    setBusy(debugAppendButton, false);
  }
}

async function handleDebugAmbiguityDemo() {
  setStatus("Loading ambiguity demo...");
  setBusy(debugAmbiguityButton, true);

  try {
    const ambiguity = await getDebugJson("/api/v3/debug/ambiguity-demo", "debug-session-error-output");
    renderDebugAmbiguity(ambiguity);
    setStatus("Ambiguity demo loaded");
  } catch (error) {
    console.error("[Sanskrit] Debug ambiguity error:", error);
    setStatus("Ambiguity demo unavailable", true);
  } finally {
    setBusy(debugAmbiguityButton, false);
  }
}

async function handleDebugPipelineDemo() {
  if (!currentDebugSession) {
    renderDebugError("debug-session-error-output", {
      detail: {
        code: "debug_session_missing",
        message: "Create a debug session first.",
      },
    });
    setStatus("Create a debug session first.", true);
    return;
  }

  setStatus("Running debug pipeline...");
  setBusy(debugPipelineButton, true);

  try {
    const data = await postDebugJson(
      "/api/v3/debug/session/run-pipeline",
      {
        session: currentDebugSession,
        pipeline: [
          {
            engine: "morphology",
            request: {
              mode: "noun",
              stem: "राम",
              case: "nominative",
              number: "singular",
            },
          },
          {
            engine: "sandhi",
            request: {
              word2: "अस्ति",
            },
          },
        ],
      },
      "debug-session-error-output",
    );
    currentDebugSession = data?.session || currentDebugSession;
    renderDebugSession(currentDebugSession);
    renderDebugSessionSteps(currentDebugSession?.steps);
    renderDebugPipelineResult(data);
    setStatus("Debug pipeline complete");
  } catch (error) {
    console.error("[Sanskrit] Debug pipeline error:", error);
    setStatus("Debug pipeline unavailable", true);
  } finally {
    setBusy(debugPipelineButton, false);
  }
}

async function handleDebugSessionSave() {
  if (!currentDebugSession) {
    renderDebugError("debug-session-error-output", {
      detail: {
        code: "debug_session_missing",
        message: "Create a debug session first.",
      },
    });
    renderDebugStorageStatus("Create a debug session first.", "error");
    setStatus("Create a debug session first.", true);
    return;
  }

  setStatus("Saving debug session...");
  renderDebugStorageStatus("Saving session...");
  setBusy(debugSaveButton, true);

  try {
    const data = await postDebugJson(
      "/api/v3/debug/session/save",
      { session: currentDebugSession },
      "debug-session-error-output",
    );
    renderDebugStorageStatus(`Saved ${text(data?.session_id, "session")}`, "success");
    await handleDebugSessionList();
    setStatus("Debug session saved");
  } catch (error) {
    console.error("[Sanskrit] Debug session save error:", error);
    renderDebugStorageStatus("Save unavailable", "error");
    setStatus("Debug save unavailable", true);
  } finally {
    setBusy(debugSaveButton, false);
  }
}

async function handleDebugSessionList() {
  setStatus("Refreshing saved sessions...");
  renderDebugStorageStatus("Refreshing saved sessions...");
  setBusy(debugRefreshSessionsButton, true);

  try {
    const data = await getDebugJson("/api/v3/debug/session/list", "debug-session-error-output");
    renderDebugSessionStorageList(data);
    const count = Array.isArray(data?.sessions) ? data.sessions.length : 0;
    renderDebugStorageStatus(`${count} saved session${count === 1 ? "" : "s"}`, "success");
    setStatus("Saved sessions refreshed");
  } catch (error) {
    console.error("[Sanskrit] Debug session list error:", error);
    renderDebugStorageStatus("Saved sessions unavailable", "error");
    setStatus("Saved sessions unavailable", true);
  } finally {
    setBusy(debugRefreshSessionsButton, false);
  }
}

async function handleDebugSessionLoad(sessionId) {
  if (!sessionId) {
    renderDebugStorageStatus("Cannot load session without an id.", "error");
    return;
  }

  setStatus("Loading saved session...");
  renderDebugStorageStatus("Loading saved session...");

  try {
    const data = await postDebugJson(
      "/api/v3/debug/session/load",
      { session_id: sessionId },
      "debug-session-error-output",
    );
    currentDebugSession = data?.session || null;
    const branches = Array.isArray(currentDebugSession?.ambiguity_branches) ? currentDebugSession.ambiguity_branches : [];
    renderDebugSession(currentDebugSession);
    renderDebugSessionSteps(currentDebugSession?.steps);
    renderDebugAmbiguity(branches.length > 0 ? { is_ambiguous: branches.length > 1, candidates: branches } : null);
    renderDebugPipelineResult(pipelineDataFromSession(currentDebugSession));
    renderDebugStorageStatus(`Loaded ${text(currentDebugSession?.session_id, "session")}`, "success");
    setStatus("Saved session loaded");
  } catch (error) {
    console.error("[Sanskrit] Debug session load error:", error);
    renderDebugStorageStatus("Load unavailable", "error");
    setStatus("Debug load unavailable", true);
  }
}

async function handleDebugSessionDelete(sessionId) {
  if (!sessionId) {
    renderDebugStorageStatus("Cannot delete session without an id.", "error");
    return;
  }

  setStatus("Deleting saved session...");
  renderDebugStorageStatus("Deleting saved session...");

  try {
    await postDebugJson(
      "/api/v3/debug/session/delete",
      { session_id: sessionId },
      "debug-session-error-output",
    );
    renderDebugStorageStatus("Deleted saved session", "success");
    await handleDebugSessionList();
    setStatus("Saved session deleted");
  } catch (error) {
    console.error("[Sanskrit] Debug session delete error:", error);
    renderDebugStorageStatus("Delete unavailable", "error");
    setStatus("Debug delete unavailable", true);
  }
}

async function handleLoadLexiconSamples() {
  setStatus("Loading lexical samples...");
  renderLexiconStatus("Loading sample entries...");
  setBusy(lexiconSamplesButton, true);

  try {
    const data = await getLexiconJson("/api/v3/debug/lexicon/samples");
    renderLexiconSamples(data);
    renderLexiconStatus(`${text(data?.count, 0)} sample entries loaded`, "success");
    setStatus("Lexical samples loaded");
  } catch (error) {
    console.error("[Sanskrit] Lexicon samples error:", error);
    renderLexiconError(error.message);
    setStatus("Lexicon samples unavailable", true);
  } finally {
    setBusy(lexiconSamplesButton, false);
  }
}

async function handleLoadLexiconSources() {
  setStatus("Loading lexical sources...");
  renderLexiconStatus("Loading registry sources...");
  setBusy(lexiconSourcesButton, true);

  try {
    const data = await getLexiconJson("/api/v3/debug/lexicon/sources");
    renderLexiconSources(data);
    renderLexiconStatus(`${text(data?.count, 0)} registry sources loaded`, "success");
    setStatus("Lexical sources loaded");
  } catch (error) {
    console.error("[Sanskrit] Lexicon sources error:", error);
    renderLexiconError(error.message);
    setStatus("Lexicon sources unavailable", true);
  } finally {
    setBusy(lexiconSourcesButton, false);
  }
}

async function handleValidateLexiconRegistry() {
  setStatus("Validating lexical registry...");
  renderLexiconStatus("Validating registry...");
  setBusy(lexiconValidateButton, true);

  try {
    const data = await getLexiconJson("/api/v3/debug/lexicon/validate");
    renderLexiconValidation(data);
    if (data?.valid === true) {
      renderLexiconStatus("Registry validation passed", "success");
      setStatus("Lexical registry valid");
    } else {
      renderLexiconStatus("Registry validation found issues", "error");
      setStatus("Lexical registry validation issues", true);
    }
  } catch (error) {
    console.error("[Sanskrit] Lexicon validation error:", error);
    renderLexiconError(error.message);
    setStatus("Lexicon validation unavailable", true);
  } finally {
    setBusy(lexiconValidateButton, false);
  }
}

async function handleLoadSutraSamples() {
  setStatus("Loading sutra registry...");
  renderSutraStatus("Loading operational sutras...");
  setBusy(sutraSamplesButton, true);

  try {
    const data = await getSutraJson("/api/v3/debug/sutras/samples");
    renderSutraSamples(data);
    renderSutraStatus(`${text(data?.count, 0)} sutras loaded`, "success");
    setStatus("Sutra registry loaded");
  } catch (error) {
    console.error("[Sanskrit] Sutra samples error:", error);
    renderSutraError(error.message);
    setStatus("Sutra registry unavailable", true);
  } finally {
    setBusy(sutraSamplesButton, false);
  }
}

async function handleLoadSutraSources() {
  setStatus("Loading sutra sources...");
  renderSutraStatus("Loading sutra sources...");
  setBusy(sutraSourcesButton, true);

  try {
    const data = await getSutraJson("/api/v3/debug/sutras/sources");
    renderSutraSources(data);
    renderSutraStatus(`${text(data?.count, 0)} sutra sources loaded`, "success");
    setStatus("Sutra sources loaded");
  } catch (error) {
    console.error("[Sanskrit] Sutra sources error:", error);
    renderSutraError(error.message);
    setStatus("Sutra sources unavailable", true);
  } finally {
    setBusy(sutraSourcesButton, false);
  }
}

async function handleValidateSutraRegistry() {
  setStatus("Validating sutra registry...");
  renderSutraStatus("Validating sutra registry...");
  setBusy(sutraValidateButton, true);

  try {
    const data = await getSutraJson("/api/v3/debug/sutras/validate");
    renderSutraValidation(data);
    if (data?.valid === true) {
      renderSutraStatus("Sutra registry validation passed", "success");
      setStatus("Sutra registry valid");
    } else {
      renderSutraStatus("Sutra registry validation found issues", "error");
      setStatus("Sutra registry validation issues", true);
    }
  } catch (error) {
    console.error("[Sanskrit] Sutra validation error:", error);
    renderSutraError(error.message);
    setStatus("Sutra validation unavailable", true);
  } finally {
    setBusy(sutraValidateButton, false);
  }
}

async function handleLoadSemanticTraceDemo() {
  setStatus("Loading semantic trace demo...");
  renderSemanticTraceStatus("Loading semantic trace demo...");
  setBusy(semanticTraceDemoButton, true);

  try {
    const data = await getSemanticTraceJson("/api/v3/debug/trace/demo");
    renderSemanticTrace(data?.linked_trace, "semantic-trace-demo-output");
    renderSemanticTraceStatus("Demo semantic trace loaded", "success");
    setStatus("Semantic trace demo loaded");
  } catch (error) {
    console.error("[Sanskrit] Semantic trace demo error:", error);
    renderSemanticTraceError(error.message);
    setStatus("Semantic trace demo unavailable", true);
  } finally {
    setBusy(semanticTraceDemoButton, false);
  }
}

async function handleLinkSemanticTrace() {
  setStatus("Linking semantic trace...");
  renderSemanticTraceStatus("Linking custom trace...");
  setBusy(semanticTraceCustomButton, true);

  try {
    const data = await postSemanticTraceJson(
      "/api/v3/debug/trace/link",
      {
        trace: [
          {
            operation: "savarna_dirgha",
            sutra: "6.1.101",
          },
          {
            operation: "scutva",
            sutra: "8.4.40",
          },
        ],
      },
    );
    renderSemanticTrace(data?.linked_trace, "semantic-trace-linked-output");
    renderSemanticTraceStatus("Custom trace linked", "success");
    setStatus("Semantic trace linked");
  } catch (error) {
    console.error("[Sanskrit] Semantic trace link error:", error);
    renderSemanticTraceError(error.message);
    setStatus("Semantic trace link unavailable", true);
  } finally {
    setBusy(semanticTraceCustomButton, false);
  }
}

async function handleLoadGraphDemo() {
  setStatus("Loading graph demo...");
  renderGraphStatus("Loading demo graph...");
  setBusy(graphDemoButton, true);

  try {
    const data = await getGraphJson("/api/v3/debug/graph/demo");
    renderDerivationGraph(data?.graph, "graph-demo-output");
    renderGraphStatus("Demo graph loaded", "success");
    setStatus("Graph demo loaded");
  } catch (error) {
    console.error("[Sanskrit] Graph demo error:", error);
    renderGraphError(error.message);
    setStatus("Graph demo unavailable", true);
  } finally {
    setBusy(graphDemoButton, false);
  }
}

async function handleExportSessionGraph() {
  if (!currentDebugSession) {
    renderGraphError("Create or load a debug session first.");
    setStatus("Create or load a debug session first.", true);
    return;
  }

  setStatus("Exporting session graph...");
  renderGraphStatus("Exporting current session graph...");
  setBusy(graphExportButton, true);

  try {
    const data = await postGraphJson(
      "/api/v3/debug/graph/export",
      { session: currentDebugSession },
    );
    renderDerivationGraph(data?.graph, "graph-session-output");
    renderGraphStatus("Session graph exported", "success");
    setStatus("Session graph exported");
  } catch (error) {
    console.error("[Sanskrit] Session graph export error:", error);
    renderGraphError(error.message);
    setStatus("Session graph export unavailable", true);
  } finally {
    setBusy(graphExportButton, false);
  }
}

async function handleLoadReplayDemo() {
  setStatus("Loading replay demo...");
  renderReplayStatus("Loading demo replay...");
  setBusy(replayDemoButton, true);

  try {
    const data = await getReplayJson("/api/v3/debug/replay/demo");
    renderReplayTimeline(data?.replay, "replay-demo-output");
    renderReplayStatus("Demo replay loaded", "success");
    setStatus("Replay demo loaded");
  } catch (error) {
    console.error("[Sanskrit] Replay demo error:", error);
    renderReplayError(error.message);
    setStatus("Replay demo unavailable", true);
  } finally {
    setBusy(replayDemoButton, false);
  }
}

async function handleExportSessionReplay() {
  if (!currentDebugSession) {
    renderReplayError("Create or load a debug session first.");
    setStatus("Create or load a debug session first.", true);
    return;
  }

  setStatus("Exporting session replay...");
  renderReplayStatus("Exporting current session replay...");
  setBusy(replayExportButton, true);

  try {
    const data = await postReplayJson(
      "/api/v3/debug/replay/export",
      { session: currentDebugSession },
    );
    renderReplayTimeline(data?.replay, "replay-session-output");
    renderReplayStatus("Session replay exported", "success");
    setStatus("Session replay exported");
  } catch (error) {
    console.error("[Sanskrit] Session replay export error:", error);
    renderReplayError(error.message);
    setStatus("Session replay export unavailable", true);
  } finally {
    setBusy(replayExportButton, false);
  }
}

function renderInitialState() {
  renderPayload({
    overall_stanza_meter: "-",
    total_matra_count: 0,
    parser_diagnostics: [],
    transliteration: "-",
    sandhi: [],
    padas: [],
    phonological_syllables: [],
    derivation_history: [],
    prakriya_graph: { nodes: [], edges: [] },
    lexical_lookup: [],
    experimental_payload: { field_map: [] },
  });
  renderSandhiResult(null);
  renderMorphologyResult(null);
  renderDerivationTimeline(null);
  renderGovernancePanel(null);
  renderAmbiguityPanel(null);
  renderApiError(null);
  renderDebugSession(null);
  renderDebugSessionSteps(null);
  renderDebugAmbiguity(null);
  renderDebugPipelineResult(null);
  renderDebugSessionStorageList(null);
  renderDebugStorageStatus("Storage idle");
  renderDebugError("debug-session-error-output", null);
  renderLexiconSamples(null);
  renderLexiconSources(null);
  renderLexiconValidation(null);
  renderLexiconStatus("Lexicon idle");
  renderSutraSamples(null);
  renderSutraSources(null);
  renderSutraValidation(null);
  renderSutraStatus("Sutra registry idle");
  renderSemanticTrace(null, "semantic-trace-demo-output");
  renderSemanticTrace(null, "semantic-trace-linked-output");
  renderSemanticTraceStatus("Semantic trace idle");
  renderSemanticDhatuPanel(SEMANTIC_DHATU_FALLBACK_PANEL);
  renderSemanticPlatformStatusPanel(SEMANTIC_PLATFORM_STATUS_FALLBACK_PANEL);
  renderSemanticDerivationPanel("01.0005");
  renderSemanticDerivationGraphPanel();
  detectBackendRuntime().then(renderBackendRuntimeStatus);
  renderSemanticGraphView();
  initializeSemanticGraphZoomControls();
  document.addEventListener("keydown", handleSemanticGraphKeyboard);
  renderDerivationGraph(null, "graph-demo-output");
  renderDerivationGraph(null, "graph-session-output");
  renderGraphStatus("Graph inspector idle");
  renderReplayTimeline(null, "replay-demo-output");
  renderReplayTimeline(null, "replay-session-output");
  renderReplayStatus("Replay inspector idle");
  renderLocalStaticDiagnostics({
    schemaVersion: "1.0.0",
    generatedBy: "ui/tabs/sanskrit/controller.js:initial",
    diagnosticsStatus: "CHECKING",
    staticModeSupported: true,
    backendRequired: false,
    backendAnalyzeAvailable: false,
    fallbackAnalysisAvailable: true,
    fixtureChecks: [],
    safetyChecks: [],
    warnings: ["Diagnostics pending."],
    checkedAt: new Date().toISOString(),
  });
}

export function init(node) {
  mountNode = node;
  analyzeButton = byId("analyze-sanskrit");
  sandhiButton = byId("run-sandhi");
  morphologyButton = byId("run-morphology");
  debugCreateButton = byId("debug-create-session");
  debugAppendButton = byId("debug-append-step");
  debugAmbiguityButton = byId("debug-load-ambiguity");
  debugPipelineButton = byId("debug-run-pipeline");
  debugSaveButton = byId("debug-save-session");
  debugRefreshSessionsButton = byId("debug-refresh-sessions");
  lexiconSamplesButton = byId("lexicon-load-samples");
  lexiconSourcesButton = byId("lexicon-load-sources");
  lexiconValidateButton = byId("lexicon-validate-registry");
  sutraSamplesButton = byId("sutra-load-samples");
  sutraSourcesButton = byId("sutra-load-sources");
  sutraValidateButton = byId("sutra-validate-registry");
  semanticTraceDemoButton = byId("semantic-trace-load-demo");
  semanticTraceCustomButton = byId("semantic-trace-link-custom");
  graphDemoButton = byId("graph-load-demo");
  graphExportButton = byId("graph-export-session");

  semanticGraphZoomInButton = byId("semantic-graph-zoom-in");
  semanticGraphZoomOutButton = byId("semantic-graph-zoom-out");
  semanticGraphResetCameraButton = byId("semantic-graph-reset-camera");
  semanticGraphFitViewButton = byId("semantic-graph-fit-view");
  semanticGraphCameraStatus = byId("semantic-graph-camera-status");
  semanticGraphMinimapCanvas = byId("semantic-graph-minimap");

  semanticGraphPresetHomeButton = byId("semantic-graph-preset-home");
  semanticGraphPresetDetailButton = byId("semantic-graph-preset-detail");
  semanticGraphPresetOverviewButton = byId("semantic-graph-preset-overview");

  replayDemoButton = byId("replay-load-demo");
  replayExportButton = byId("replay-export-session");
  semanticSearchInput = byId("semantic-dhatu-search-input");
  semanticClusterFilter = byId("semantic-dhatu-cluster-filter");
  semanticActionFilter = byId("semantic-dhatu-action-filter");
  semanticGlossFilter = byId("semantic-dhatu-gloss-filter");
  semanticDepthSelect = byId("semantic-dhatu-depth-select");
  semanticRelationFilter = byId("semantic-dhatu-relation-filter");
  semanticResetButton = byId("semantic-dhatu-reset");
  semanticDerivationFamilyFilter = byId("semantic-derivation-family-filter");
  semanticDerivationDomainFilter = byId("semantic-derivation-domain-filter");
  semanticDerivationRelationFilter = byId("semantic-derivation-relation-filter");
  semanticDerivationResetButton = byId("semantic-derivation-reset");
  semanticDerivationGraphFamilyFilter = byId("semantic-derivation-graph-family-filter");
  semanticDerivationGraphDomainFilter = byId("semantic-derivation-graph-domain-filter");
  semanticDerivationGraphRelationFilter = byId("semantic-derivation-graph-relation-filter");
  semanticDerivationGraphResetButton = byId("semantic-derivation-graph-reset");
  staticFixtureClusterFilter = byId("static-fixture-cluster-filter");
  staticFixtureDhatuFilter = byId("static-fixture-dhatu-filter");
  staticFixtureNodeFilter = byId("static-fixture-node-filter");
  staticFixtureSectionFilter = byId("static-fixture-section-filter");
  staticFixtureCopyLinkButton = byId("static-fixture-copy-link");
  staticFixtureExportJsonButton = byId("static-fixture-export-json");
  staticFixtureExportMarkdownButton = byId("static-fixture-export-markdown");
  staticFixtureExportTextButton = byId("static-fixture-export-text");
  staticFixtureImportSnapshotButton = byId("static-fixture-import-snapshot");
  staticFixtureImportFileInput = byId("static-fixture-import-file");
  staticFixtureResetImportButton = byId("static-fixture-reset-import");
  staticFixtureImportStatus = byId("static-fixture-import-status");
  staticFixtureComparisonSummary = byId("static-fixture-comparison-summary");
  staticFixtureImportedMetadata = byId("static-fixture-imported-metadata");
  staticFixtureComparisonResults = byId("static-fixture-comparison-results");
  inputNode = byId("sanskrit-input");

  analyzeButton?.addEventListener("click", analyzeCurrentInput);
  sandhiButton?.addEventListener("click", runSandhi);
  morphologyButton?.addEventListener("click", runMorphology);
  debugCreateButton?.addEventListener("click", handleDebugSessionCreate);
  debugAppendButton?.addEventListener("click", handleDebugSessionAppend);
  debugAmbiguityButton?.addEventListener("click", handleDebugAmbiguityDemo);
  debugPipelineButton?.addEventListener("click", handleDebugPipelineDemo);
  debugSaveButton?.addEventListener("click", handleDebugSessionSave);
  debugRefreshSessionsButton?.addEventListener("click", handleDebugSessionList);
  lexiconSamplesButton?.addEventListener("click", handleLoadLexiconSamples);
  lexiconSourcesButton?.addEventListener("click", handleLoadLexiconSources);
  lexiconValidateButton?.addEventListener("click", handleValidateLexiconRegistry);
  sutraSamplesButton?.addEventListener("click", handleLoadSutraSamples);
  sutraSourcesButton?.addEventListener("click", handleLoadSutraSources);
  sutraValidateButton?.addEventListener("click", handleValidateSutraRegistry);
  semanticTraceDemoButton?.addEventListener("click", handleLoadSemanticTraceDemo);
  semanticTraceCustomButton?.addEventListener("click", handleLinkSemanticTrace);
  graphDemoButton?.addEventListener("click", handleLoadGraphDemo);
  graphExportButton?.addEventListener("click", handleExportSessionGraph);
  replayDemoButton?.addEventListener("click", handleLoadReplayDemo);
  replayExportButton?.addEventListener("click", handleExportSessionReplay);
  semanticSearchInput?.addEventListener("input", renderSemanticQueryState);
  semanticClusterFilter?.addEventListener("change", renderSemanticQueryState);
  semanticActionFilter?.addEventListener("change", renderSemanticQueryState);
  semanticGlossFilter?.addEventListener("change", renderSemanticQueryState);
  semanticDepthSelect?.addEventListener("change", renderSemanticQueryState);
  semanticRelationFilter?.addEventListener("change", renderSemanticQueryState);
  semanticResetButton?.addEventListener("click", resetSemanticQueryControls);
  semanticDerivationFamilyFilter?.addEventListener("change", renderSemanticQueryState);
  semanticDerivationDomainFilter?.addEventListener("change", renderSemanticQueryState);
  semanticDerivationRelationFilter?.addEventListener("change", renderSemanticQueryState);
  semanticDerivationResetButton?.addEventListener("click", resetSemanticDerivationFilters);
  semanticDerivationGraphFamilyFilter?.addEventListener("change", renderSemanticDerivationGraphPanel);
  semanticDerivationGraphDomainFilter?.addEventListener("change", renderSemanticDerivationGraphPanel);
  semanticDerivationGraphRelationFilter?.addEventListener("change", renderSemanticDerivationGraphPanel);
  semanticDerivationGraphResetButton?.addEventListener("click", resetSemanticDerivationGraphFilters);
  staticFixtureClusterFilter?.addEventListener("change", handleStaticFixtureBrowserFilterChange);
  staticFixtureDhatuFilter?.addEventListener("input", handleStaticFixtureBrowserFilterChange);
  staticFixtureNodeFilter?.addEventListener("input", handleStaticFixtureBrowserFilterChange);
  staticFixtureSectionFilter?.addEventListener("change", handleStaticFixtureBrowserFilterChange);
  staticFixtureCopyLinkButton?.addEventListener("click", handleStaticFixtureCopyLink);
  staticFixtureExportJsonButton?.addEventListener("click", handleStaticFixtureExportJson);
  staticFixtureExportMarkdownButton?.addEventListener("click", handleStaticFixtureExportMarkdown);
  staticFixtureExportTextButton?.addEventListener("click", handleStaticFixtureExportText);
  bindStaticFixtureImportControls();
  all('input[name="morphology-mode"]').forEach((input) => input.addEventListener("change", updateMorphologyFields));
  inputNode?.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      analyzeCurrentInput();
    }
  });

  renderInitialState();
  renderTransliterationPanel(inputNode?.value || "");
  renderSandhiExecutionPanel(inputNode?.value || "");
  renderSubantaGeneratorPanel(inputNode?.value || "");
  renderTinantaGeneratorPanels(inputNode?.value || "");
  renderPrakriyaCompositionPanel(inputNode?.value || "");
  renderSymbolicCompressionPanel();
  renderPhoneticTopologyPanel(inputNode?.value || "");
  renderDerivationGraphPanel(inputNode?.value || "");
  renderSutraReferencePanel(inputNode?.value || "");
  renderRuleTracePanel(inputNode?.value || "");
  renderMorphologyTransitionPanel(inputNode?.value || "");
  renderKarakaOverlayPanel(inputNode?.value || "");
  renderVakyaDependencyPanel(inputNode?.value || "");
  renderSandarbhaContextPanel(inputNode?.value || "");
  renderChandasProsodyPanel(inputNode?.value || "");
  renderDhatuSemanticPanel(inputNode?.value || "");
  updateMorphologyFields();
  loadSemanticDhatuPanel();
  loadSemanticPlatformStatusPanel();
  loadSemanticDerivationData();
  loadSemanticDerivationGraphPanel();
  runLocalStaticDiagnostics();

  if (inputNode && !inputNode.value.trim()) inputNode.value = DEFAULT_PAYLOAD.input_text;
  analyzeCurrentInput();
}

export function render() {
  // The Sanskrit tab is driven by its own linguistic API payload, not shared scalar controls.
}

export function destroy() {
  analyzeButton?.removeEventListener("click", analyzeCurrentInput);
  sandhiButton?.removeEventListener("click", runSandhi);
  morphologyButton?.removeEventListener("click", runMorphology);
  debugCreateButton?.removeEventListener("click", handleDebugSessionCreate);
  debugAppendButton?.removeEventListener("click", handleDebugSessionAppend);
  debugAmbiguityButton?.removeEventListener("click", handleDebugAmbiguityDemo);
  debugPipelineButton?.removeEventListener("click", handleDebugPipelineDemo);
  debugSaveButton?.removeEventListener("click", handleDebugSessionSave);
  debugRefreshSessionsButton?.removeEventListener("click", handleDebugSessionList);
  lexiconSamplesButton?.removeEventListener("click", handleLoadLexiconSamples);
  lexiconSourcesButton?.removeEventListener("click", handleLoadLexiconSources);
  lexiconValidateButton?.removeEventListener("click", handleValidateLexiconRegistry);
  sutraSamplesButton?.removeEventListener("click", handleLoadSutraSamples);
  sutraSourcesButton?.removeEventListener("click", handleLoadSutraSources);
  sutraValidateButton?.removeEventListener("click", handleValidateSutraRegistry);
  semanticTraceDemoButton?.removeEventListener("click", handleLoadSemanticTraceDemo);
  semanticTraceCustomButton?.removeEventListener("click", handleLinkSemanticTrace);
  graphDemoButton?.removeEventListener("click", handleLoadGraphDemo);
  graphExportButton?.removeEventListener("click", handleExportSessionGraph);
  replayDemoButton?.removeEventListener("click", handleLoadReplayDemo);
  replayExportButton?.removeEventListener("click", handleExportSessionReplay);
  semanticSearchInput?.removeEventListener("input", renderSemanticQueryState);
  semanticClusterFilter?.removeEventListener("change", renderSemanticQueryState);
  semanticActionFilter?.removeEventListener("change", renderSemanticQueryState);
  semanticGlossFilter?.removeEventListener("change", renderSemanticQueryState);
  semanticDepthSelect?.removeEventListener("change", renderSemanticQueryState);
  semanticRelationFilter?.removeEventListener("change", renderSemanticQueryState);
  semanticResetButton?.removeEventListener("click", resetSemanticQueryControls);
  semanticDerivationFamilyFilter?.removeEventListener("change", renderSemanticQueryState);
  semanticDerivationDomainFilter?.removeEventListener("change", renderSemanticQueryState);
  semanticDerivationRelationFilter?.removeEventListener("change", renderSemanticQueryState);
  semanticDerivationResetButton?.removeEventListener("click", resetSemanticDerivationFilters);
  semanticDerivationGraphFamilyFilter?.removeEventListener("change", renderSemanticDerivationGraphPanel);
  semanticDerivationGraphDomainFilter?.removeEventListener("change", renderSemanticDerivationGraphPanel);
  semanticDerivationGraphRelationFilter?.removeEventListener("change", renderSemanticDerivationGraphPanel);
  semanticDerivationGraphResetButton?.removeEventListener("click", resetSemanticDerivationGraphFilters);
  staticFixtureClusterFilter?.removeEventListener("change", handleStaticFixtureBrowserFilterChange);
  staticFixtureDhatuFilter?.removeEventListener("input", handleStaticFixtureBrowserFilterChange);
  staticFixtureNodeFilter?.removeEventListener("input", handleStaticFixtureBrowserFilterChange);
  staticFixtureSectionFilter?.removeEventListener("change", handleStaticFixtureBrowserFilterChange);
  staticFixtureCopyLinkButton?.removeEventListener("click", handleStaticFixtureCopyLink);
  staticFixtureExportJsonButton?.removeEventListener("click", handleStaticFixtureExportJson);
  staticFixtureExportMarkdownButton?.removeEventListener("click", handleStaticFixtureExportMarkdown);
  staticFixtureExportTextButton?.removeEventListener("click", handleStaticFixtureExportText);
  staticFixtureImportSnapshotButton?.removeEventListener("click", handleStaticFixtureImportClick);
  staticFixtureImportFileInput?.removeEventListener("change", handleStaticFixtureImportFileChange);
  staticFixtureResetImportButton?.removeEventListener("click", handleStaticFixtureResetImport);
  all('input[name="morphology-mode"]').forEach((input) => input.removeEventListener("change", updateMorphologyFields));
  mountNode = null;
  analyzeButton = null;
  sandhiButton = null;
  morphologyButton = null;
  debugCreateButton = null;
  debugAppendButton = null;
  debugAmbiguityButton = null;
  debugPipelineButton = null;
  debugSaveButton = null;
  debugRefreshSessionsButton = null;
  lexiconSamplesButton = null;
  lexiconSourcesButton = null;
  lexiconValidateButton = null;
  sutraSamplesButton = null;
  sutraSourcesButton = null;
  sutraValidateButton = null;
  semanticTraceDemoButton = null;
  semanticTraceCustomButton = null;
  graphDemoButton = null;
  graphExportButton = null;
  replayDemoButton = null;
  replayExportButton = null;
  semanticSearchInput = null;
  semanticClusterFilter = null;
  semanticActionFilter = null;
  semanticGlossFilter = null;
  semanticDepthSelect = null;
  semanticRelationFilter = null;
  semanticResetButton = null;
  semanticDerivationFamilyFilter = null;
  semanticDerivationDomainFilter = null;
  semanticDerivationRelationFilter = null;
  semanticDerivationResetButton = null;
  semanticDerivationGraphFamilyFilter = null;
  semanticDerivationGraphDomainFilter = null;
  semanticDerivationGraphRelationFilter = null;
  semanticDerivationGraphResetButton = null;
  staticFixtureClusterFilter = null;
  staticFixtureDhatuFilter = null;
  staticFixtureNodeFilter = null;
  staticFixtureSectionFilter = null;
  staticFixtureCopyLinkButton = null;
  staticFixtureExportJsonButton = null;
  staticFixtureExportMarkdownButton = null;
  staticFixtureExportTextButton = null;
  staticFixtureImportSnapshotButton = null;
  staticFixtureImportFileInput = null;
  staticFixtureResetImportButton = null;
  staticFixtureImportStatus = null;
  staticFixtureComparisonSummary = null;
  staticFixtureImportedMetadata = null;
  staticFixtureComparisonResults = null;
  importedStaticFixtureSnapshot = null;
  currentDebugSession = null;
  semanticPanelData = null;
  semanticDerivationData = null;
  semanticDerivationGraphData = null;
  semanticPlatformStatusData = null;
  staticSemanticFixtureBrowserActive = false;
  staticFixtureHashRestored = false;
  inputNode = null;
}
