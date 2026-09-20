"use strict";

function asObject(value) {
  return value && typeof value === "object" && !Array.isArray(value) ? value : null;
}

function asString(value, fallback) {
  return typeof value === "string" ? value : fallback;
}

function asNumber(value, fallback) {
  var number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

var EMPTY_CANONICAL_ENVELOPE = {
  input_text: "",
  unicode_clusters: [],
  transliteration: "",
  sandhi: [],
  overall_stanza_meter: "Fragment / partial pada - meter not determined",
  total_matra_count: 0,
  pada_segments: [],
  padas: [],
  phonological_syllables: [],
  derivation_history: [],
  prakriya_graph: { nodes: [], edges: [] },
  rulefire: {},
  sutra_dependency: {},
  nirukta: {},
  lexical_lookup: [],
  parser_diagnostics: [],
  lexical_source_governance: {},
  experimental_payload: { field_map: [] }
};

function extractClientFallback(raw) {
  var explicit = asObject(raw.client_fallback);
  if (explicit) {
    return explicit;
  }
  var experimental = asObject(raw.experimental_payload);
  var nested = experimental && asObject(experimental.client_fallback);
  if (nested) {
    return nested;
  }
  if (raw.pipelineStatus || raw.safety_note || raw.tokenization || raw.normalized_input) {
    return {
      pipelineStatus: asObject(raw.pipelineStatus),
      safety_note: asString(raw.safety_note, ""),
      tokenization: asObject(raw.tokenization),
      normalized_input: asString(raw.normalized_input, "")
    };
  }
  return null;
}

function normalizeAnalysisEnvelope(rawPayload) {
  var raw = asObject(rawPayload) || {};
  var envelope = {
    input_text: asString(raw.input_text, EMPTY_CANONICAL_ENVELOPE.input_text),
    unicode_clusters: asArray(raw.unicode_clusters),
    transliteration: asString(raw.transliteration, EMPTY_CANONICAL_ENVELOPE.transliteration),
    sandhi: asArray(raw.sandhi),
    overall_stanza_meter: asString(
      raw.overall_stanza_meter,
      EMPTY_CANONICAL_ENVELOPE.overall_stanza_meter
    ),
    total_matra_count: asNumber(raw.total_matra_count, 0),
    pada_segments: asArray(raw.pada_segments),
    padas: asArray(raw.padas),
    phonological_syllables: asArray(raw.phonological_syllables),
    derivation_history: asArray(raw.derivation_history),
    prakriya_graph: asObject(raw.prakriya_graph) || { nodes: [], edges: [] },
    rulefire: asObject(raw.rulefire) || {},
    sutra_dependency: asObject(raw.sutra_dependency) || {},
    nirukta: asObject(raw.nirukta) || {},
    lexical_lookup: asArray(raw.lexical_lookup),
    parser_diagnostics: asArray(raw.parser_diagnostics),
    lexical_source_governance: asObject(raw.lexical_source_governance) || {},
    experimental_payload: asObject(raw.experimental_payload) || { field_map: [] }
  };

  if (asObject(raw.governance)) {
    envelope.governance = raw.governance;
  }

  var clientFallback = extractClientFallback(raw);
  if (clientFallback) {
    envelope.client_fallback = clientFallback;
    if (!asObject(envelope.experimental_payload.client_fallback)) {
      envelope.experimental_payload = Object.assign({}, envelope.experimental_payload, {
        client_fallback: clientFallback
      });
    }
  }

  return envelope;
}

module.exports = {
  EMPTY_CANONICAL_ENVELOPE: EMPTY_CANONICAL_ENVELOPE,
  normalizeAnalysisEnvelope: normalizeAnalysisEnvelope
};
