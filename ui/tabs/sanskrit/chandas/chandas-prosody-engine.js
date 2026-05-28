import { CHANDAS_GANA_MAP, matchMetreBySyllableCount } from "./chandas-prosody-map.js";

const SHORT_VOWELS = new Set(["अ", "इ", "उ", "ऋ", "ऌ"]);
const LONG_VOWELS = new Set(["आ", "ई", "ऊ", "ॠ", "ए", "ऐ", "ओ", "औ"]);
const SHORT_SIGNS = new Set(["ि", "ु", "ृ", "ॢ"]);
const LONG_SIGNS = new Set(["ा", "ी", "ू", "ॄ", "े", "ै", "ो", "ौ"]);
const VOWEL_SIGNS = new Set([...SHORT_SIGNS, ...LONG_SIGNS]);
const CONSONANT_PATTERN = /^[क-ह]$/u;
const ANUSVARA = "ं";
const VISARGA = "ः";
const VIRAMA = "्";

function stablePart(value) {
  return String(value ?? "unknown")
    .trim()
    .toLowerCase()
    .replace(/[^\p{Letter}\p{Number}]+/gu, "_")
    .replace(/^_+|_+$/g, "") || "unknown";
}

function explicitText(input) {
  if (typeof input.text === "string") return input.text;
  if (Array.isArray(input.tokens)) {
    return input.tokens
      .map((token) => typeof token === "string" ? token : token?.token || token?.text || token?.label || "")
      .filter(Boolean)
      .join(" ");
  }
  return "";
}

function isConsonant(character) {
  return CONSONANT_PATTERN.test(character);
}

function vowelInfo(chars, index) {
  const character = chars[index];
  if (SHORT_VOWELS.has(character)) return { found: true, long: false, start: index, end: index, text: character };
  if (LONG_VOWELS.has(character)) return { found: true, long: true, start: index, end: index, text: character };
  if (VOWEL_SIGNS.has(character)) {
    const previous = chars[index - 1] || "";
    return {
      found: true,
      long: LONG_SIGNS.has(character),
      start: isConsonant(previous) ? index - 1 : index,
      end: index,
      text: isConsonant(previous) ? `${previous}${character}` : character,
    };
  }
  return { found: false };
}

function followingContext(chars, index) {
  let cursor = index + 1;
  let hasAnusvara = false;
  let hasVisarga = false;
  let consonants = 0;
  let hasViramaCluster = false;

  while (cursor < chars.length) {
    const character = chars[cursor];
    if (/\s/u.test(character)) break;
    if (character === ANUSVARA) {
      hasAnusvara = true;
      cursor += 1;
      continue;
    }
    if (character === VISARGA) {
      hasVisarga = true;
      cursor += 1;
      continue;
    }
    if (isConsonant(character)) {
      consonants += 1;
      if (chars[cursor + 1] === VIRAMA) {
        hasViramaCluster = true;
        cursor += 2;
        continue;
      }
      cursor += 1;
      continue;
    }
    if (SHORT_VOWELS.has(character) || LONG_VOWELS.has(character) || VOWEL_SIGNS.has(character)) break;
    cursor += 1;
  }

  return {
    hasAnusvara,
    hasVisarga,
    hasCluster: hasViramaCluster || consonants >= 2,
  };
}

function classifySyllable(info, context) {
  if (info.long) return { weight: "guru", matra: 2, reason: "longVowelGuru" };
  if (context.hasAnusvara) return { weight: "guru", matra: 2, reason: "anusvaraGuru" };
  if (context.hasVisarga) return { weight: "guru", matra: 2, reason: "visargaGuru" };
  if (context.hasCluster) return { weight: "guru", matra: 2, reason: "closedSyllableGuru" };
  return { weight: "laghu", matra: 1, reason: "laghuSyllable" };
}

function buildSyllables(text) {
  const chars = Array.from(text);
  const syllables = [];
  const seenSignIndexes = new Set();

  chars.forEach((character, index) => {
    if (seenSignIndexes.has(index)) return;
    const info = vowelInfo(chars, index);
    if (!info.found) return;
    if (VOWEL_SIGNS.has(character) && isConsonant(chars[index - 1])) {
      seenSignIndexes.add(index - 1);
    }
    const context = followingContext(chars, index);
    const classification = classifySyllable(info, context);
    syllables.push({
      id: `chandas.syllable.${syllables.length}.${stablePart(info.text)}`,
      text: info.text,
      index: syllables.length,
      weight: classification.weight,
      matra: classification.matra,
      reason: classification.reason,
      source: "phonetic-analysis",
      confidence: "deterministic",
    });
  });

  return syllables;
}

function buildGanas(syllables) {
  const ganas = [];
  for (let index = 0; index + 2 < syllables.length; index += 3) {
    const group = syllables.slice(index, index + 3);
    const pattern = group.map((syllable) => syllable.weight).join("-");
    ganas.push({
      id: `chandas.gana.${ganas.length}.${stablePart(pattern)}`,
      index: ganas.length,
      pattern,
      gana: CHANDAS_GANA_MAP[pattern] || "unknown",
      syllableIds: group.map((syllable) => syllable.id),
      confidence: "deterministic",
    });
  }
  return ganas;
}

function buildPadaCandidates(syllables) {
  const candidates = [];
  for (let start = 0; start + 7 < syllables.length; start += 8) {
    const group = syllables.slice(start, start + 8);
    candidates.push({
      id: `chandas.pada.${candidates.length}.${start}.${start + 7}`,
      startIndex: start,
      endIndex: start + 7,
      syllableIds: group.map((syllable) => syllable.id),
      matraCount: group.reduce((total, syllable) => total + syllable.matra, 0),
      confidence: "deterministic",
    });
  }
  return candidates;
}

function buildMetreCandidates(syllables) {
  const totalSyllables = syllables.length;

  return matchMetreBySyllableCount(totalSyllables).map((metre, index) => ({
    id: `chandas.metre.${index}.${stablePart(metre.id)}`,
    metreId: metre.id,
    label: metre.label,
    totalSyllables: metre.totalSyllables,
    padaCount: metre.padaCount,
    syllablesPerPada: metre.syllablesPerPada,
    confidence: "deterministic-candidate",
    source: "chandas-metre-registry",
  }));
}

function buildPadaRhythmCandidates(syllables, padaCandidates) {
  return padaCandidates.map((pada, index) => {
    const group = syllables.slice(pada.startIndex, pada.endIndex + 1);
    const rhythm = group.map((syllable) => syllable.weight).join("-");
    const matraPattern = group.map((syllable) => syllable.matra).join("-");

    return {
      id: `chandas.rhythm.${index}.${pada.startIndex}.${pada.endIndex}`,
      padaId: pada.id,
      startIndex: pada.startIndex,
      endIndex: pada.endIndex,
      rhythm,
      matraPattern,
      syllableIds: group.map((syllable) => syllable.id),
      confidence: "deterministic-candidate",
      source: "chandas-pada-rhythm",
    };
  });
}

function buildCaesuraCandidates(padaCandidates) {
  return padaCandidates.map((pada, index) => {
    const midpoint = Math.floor((pada.startIndex + pada.endIndex) / 2);

    return {
      id: `chandas.caesura.${index}.${pada.startIndex}.${pada.endIndex}`,
      padaId: pada.id,
      afterSyllableIndex: midpoint,
      beforeSyllableIndex: midpoint + 1,
      confidence: "deterministic-candidate",
      source: "chandas-deterministic-midpoint",
      notes: "Candidate pause only; no authoritative caesura or poetic intent is claimed.",
    };
  });
}

function buildStructuralGraphNodes(syllables, ganas, padaCandidates, metreCandidates, padaRhythmCandidates, caesuraCandidates) {
  return [
    ...syllables.map((syllable) => ({
      id: `chandas.struct.node.${stablePart(syllable.id)}`,
      sourceId: syllable.id,
      nodeType: "syllable",
      label: syllable.text,
      confidence: "deterministic",
      source: "chandas-structural-graph",
    })),
    ...ganas.map((gana) => ({
      id: `chandas.struct.node.${stablePart(gana.id)}`,
      sourceId: gana.id,
      nodeType: "gana",
      label: gana.gana,
      confidence: "deterministic",
      source: "chandas-structural-graph",
    })),
    ...padaCandidates.map((pada) => ({
      id: `chandas.struct.node.${stablePart(pada.id)}`,
      sourceId: pada.id,
      nodeType: "pada",
      label: `pāda ${pada.startIndex}-${pada.endIndex}`,
      confidence: "deterministic",
      source: "chandas-structural-graph",
    })),
    ...metreCandidates.map((metre) => ({
      id: `chandas.struct.node.${stablePart(metre.id)}`,
      sourceId: metre.id,
      nodeType: "metre",
      label: metre.label,
      confidence: "deterministic-candidate",
      source: "chandas-structural-graph",
    })),
    ...padaRhythmCandidates.map((rhythm) => ({
      id: `chandas.struct.node.${stablePart(rhythm.id)}`,
      sourceId: rhythm.id,
      nodeType: "pada-rhythm",
      label: rhythm.rhythm,
      confidence: "deterministic-candidate",
      source: "chandas-structural-graph",
    })),
    ...caesuraCandidates.map((caesura) => ({
      id: `chandas.struct.node.${stablePart(caesura.id)}`,
      sourceId: caesura.id,
      nodeType: "caesura",
      label: `after ${caesura.afterSyllableIndex}`,
      confidence: "deterministic-candidate",
      source: "chandas-structural-graph",
    })),
  ];
}

function buildStructuralGraphEdges(syllables, ganas, padaCandidates, metreCandidates, padaRhythmCandidates, caesuraCandidates) {
  const edges = [];

  ganas.forEach((gana) => {
    gana.syllableIds.forEach((syllableId) => {
      edges.push({
        id: `chandas.struct.edge.${stablePart(syllableId)}.${stablePart(gana.id)}`,
        source: syllableId,
        target: gana.id,
        relation: "syllable-to-gana",
        confidence: "deterministic",
        sourceLayer: "chandas-structural-graph",
      });
    });
  });

  padaCandidates.forEach((pada) => {
    pada.syllableIds.forEach((syllableId) => {
      edges.push({
        id: `chandas.struct.edge.${stablePart(syllableId)}.${stablePart(pada.id)}`,
        source: syllableId,
        target: pada.id,
        relation: "syllable-to-pada",
        confidence: "deterministic",
        sourceLayer: "chandas-structural-graph",
      });
    });
  });

  padaRhythmCandidates.forEach((rhythm) => {
    edges.push({
      id: `chandas.struct.edge.${stablePart(rhythm.padaId)}.${stablePart(rhythm.id)}`,
      source: rhythm.padaId,
      target: rhythm.id,
      relation: "pada-to-rhythm",
      confidence: "deterministic-candidate",
      sourceLayer: "chandas-structural-graph",
    });
  });

  caesuraCandidates.forEach((caesura) => {
    edges.push({
      id: `chandas.struct.edge.${stablePart(caesura.padaId)}.${stablePart(caesura.id)}`,
      source: caesura.padaId,
      target: caesura.id,
      relation: "pada-to-caesura",
      confidence: "deterministic-candidate",
      sourceLayer: "chandas-structural-graph",
    });
  });

  metreCandidates.forEach((metre) => {
    padaCandidates.forEach((pada) => {
      edges.push({
        id: `chandas.struct.edge.${stablePart(pada.id)}.${stablePart(metre.id)}`,
        source: pada.id,
        target: metre.id,
        relation: "pada-to-metre-candidate",
        confidence: "deterministic-candidate",
        sourceLayer: "chandas-structural-graph",
      });
    });
  });

  return edges;
}

function buildEdges(syllables, ganas, padaCandidates, padaRhythmCandidates = [], caesuraCandidates = []) {
  const edges = [];
  ganas.forEach((gana) => {
    gana.syllableIds.forEach((syllableId) => {
      edges.push({
        id: `chandas.edge.${stablePart(syllableId)}.${stablePart(gana.id)}`,
        source: syllableId,
        target: gana.id,
        relation: "ganaGrouping",
        label: gana.gana,
        confidence: "deterministic",
        sourceLayer: "chandas-prosody",
      });
    });
  });
  padaCandidates.forEach((pada) => {
    pada.syllableIds.forEach((syllableId) => {
      edges.push({
        id: `chandas.edge.${stablePart(syllableId)}.${stablePart(pada.id)}`,
        source: syllableId,
        target: pada.id,
        relation: "padaBoundaryCandidate",
        label: "pāda candidate",
        confidence: "deterministic",
        sourceLayer: "chandas-prosody",
      });
    });
  });
    padaRhythmCandidates.forEach((rhythm) => {
    rhythm.syllableIds.forEach((syllableId) => {
      edges.push({
        id: `chandas.edge.${stablePart(syllableId)}.${stablePart(rhythm.id)}`,
        source: syllableId,
        target: rhythm.id,
        relation: "padaRhythmCandidate",
        label: "pāda rhythm",
        confidence: "deterministic-candidate",
        sourceLayer: "chandas-prosody",
      });
    });
  });

  caesuraCandidates.forEach((caesura) => {
    edges.push({
      id: `chandas.edge.${stablePart(caesura.padaId)}.${stablePart(caesura.id)}`,
      source: caesura.padaId,
      target: caesura.id,
      relation: "caesuraCandidate",
      label: "caesura candidate",
      confidence: "deterministic-candidate",
      sourceLayer: "chandas-prosody",
    });
  });
  return edges;
}

export function buildChandasProsodyOverlay(input = {}) {
  const source = input && typeof input === "object" ? input : {};
  const text = explicitText(source);
  const warnings = [];
  const syllables = buildSyllables(text);
  const ganas = buildGanas(syllables);
  const padaCandidates = buildPadaCandidates(syllables);
  const metreCandidates = buildMetreCandidates(syllables);
  const padaRhythmCandidates = buildPadaRhythmCandidates(syllables, padaCandidates);
  const caesuraCandidates = buildCaesuraCandidates(padaCandidates);
  const structuralGraphNodes = buildStructuralGraphNodes(
  syllables,
  ganas,
  padaCandidates,
  metreCandidates,
  padaRhythmCandidates,
  caesuraCandidates,
);
const structuralGraphEdges = buildStructuralGraphEdges(
  syllables,
  ganas,
  padaCandidates,
  metreCandidates,
  padaRhythmCandidates,
  caesuraCandidates,
);
  const trailing = syllables.length % 3;
  const unresolvedCount = trailing === 0 ? 0 : trailing;

  if (!text) warnings.push("No text supplied for deterministic chandas inspection.");
  if (unresolvedCount > 0) warnings.push("Trailing syllables do not complete a gaṇa group; retained as unresolved prosody candidates.");

  const laghuCount = syllables.filter((syllable) => syllable.weight === "laghu").length;
  const guruCount = syllables.filter((syllable) => syllable.weight === "guru").length;

  return {
    schemaVersion: "chandas-prosody-overlay.v1",
    status: "ready",
    overlayType: "chandas-prosody",
    syllables,
    ganas,
    padaCandidates,
    metreCandidates,
    padaRhythmCandidates,
    caesuraCandidates,
    structuralGraphNodes,
    structuralGraphEdges,
    edges: buildEdges(syllables, ganas, padaCandidates, padaRhythmCandidates, caesuraCandidates),
    diagnostics: {
      syllableCount: syllables.length,
      laghuCount,
      guruCount,
      matraTotal: syllables.reduce((total, syllable) => total + syllable.matra, 0),
      ganaCount: ganas.length,
      padaCandidateCount: padaCandidates.length,
      metreCandidateCount: metreCandidates.length,
      padaRhythmCandidateCount: padaRhythmCandidates.length,
      caesuraCandidateCount: caesuraCandidates.length,
      matchedMetres: metreCandidates.map((metre) => metre.label),
      structuralGraphNodeCount: structuralGraphNodes.length,
      structuralGraphEdgeCount: structuralGraphEdges.length,
      unresolvedCount,
      warnings,
    },
  };
}

export function attachChandasOverlay(graph, overlayData = {}, bridge = {}) {
  if (typeof bridge.attachOverlayItems !== "function") return graph;
  return bridge.attachOverlayItems(
    graph,
    "chandas",
    overlayData,
    [
  "syllables",
  "ganas",
  "padaCandidates",
  "metreCandidates",
  "padaRhythmCandidates",
  "caesuraCandidates",
  "structuralGraphNodes",
  "structuralGraphEdges",
],
    ["edges"],
  );
}
