"use strict";

const {
  buildCorpusReadinessRecord,
  MAX_BULK_CORPUS_RECORDS
} = require("./corpus-readiness-map.js");

const {
  inspectCorpusStagingManifest
} = require("./corpus-staging-engine.js");

const {
  validateBulkCorpusManifest
} = require("./corpus-validator-engine.js");

const {
  auditCorpusProvenanceManifest
} = require("./corpus-provenance-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function prefixErrors(prefix, values) {
  return (Array.isArray(values) ? values : []).map((value) => {
    return prefix + ":" + String(value);
  });
}

function computeCorpusReadiness(input = {}) {
  const staging = inspectCorpusStagingManifest(input);
  const validator = validateBulkCorpusManifest(input);
  const provenance = auditCorpusProvenanceManifest(input);

  const errors = [
    ...prefixErrors("staging", staging.errors),
    ...prefixErrors("validator", validator.errors),
    ...prefixErrors("provenance", provenance.errors)
  ];

  const warnings = [
    ...prefixErrors("provenance", provenance.warnings)
  ];

  const recordCount = Math.max(
    Number(staging.recordCount || 0),
    Number(validator.recordCount || 0),
    Number(provenance.recordCount || 0)
  );

  const batchCount = Math.max(
    Number(staging.batchCount || 0),
    Number(provenance.batchCount || 0)
  );

  const readinessScore = errors.length
    ? Math.max(
      0,
      Math.min(
        Number(validator.readinessScore || 0),
        Number(provenance.confidenceScore || 0)
      ) - errors.length * 2
    )
    : Math.min(
      Number(validator.readinessScore || 100),
      Number(provenance.confidenceScore || 100)
    );

  const promotionEligible = Boolean(
    errors.length === 0 &&
    recordCount <= MAX_BULK_CORPUS_RECORDS &&
    staging.previewOnly === true &&
    validator.previewOnly === true &&
    provenance.previewOnly === true
  );

  return buildCorpusReadinessRecord({
    recordCount,
    batchCount,
    errors,
    warnings,
    staging,
    validator,
    provenance,
    metadata: {
      readinessScore,
      promotionEligible
    }
  });
}

function summarizeCorpusReadiness(input = {}) {
  const readiness = computeCorpusReadiness(input);

  return freeze({
    state: readiness.state,
    valid: readiness.errors.length === 0,
    promotionEligible: readiness.metadata.promotionEligible === true,
    readinessScore: readiness.metadata.readinessScore,
    recordCount: readiness.recordCount,
    batchCount: readiness.batchCount,
    errors: readiness.errors,
    warnings: readiness.warnings,
    previewOnly: true,
    readOnly: true,
    canonicalWriteAllowed: false,
    promotionAllowed: false
  });
}

module.exports = {
  computeCorpusReadiness,
  summarizeCorpusReadiness
};