"use strict";

const {
  buildCorpusAllocationRecord,
  DEFAULT_CORPUS_ALLOCATION,
  MAX_BULK_CORPUS_RECORDS
} = require("./corpus-allocation-map.js");

const {
  summarizeCorpusCapacity
} = require("./corpus-capacity-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function collectAllocationRecords(input = {}) {
  const records = [];

  for (const batch of Array.isArray(input.batches) ? input.batches : []) {
    for (const record of Array.isArray(batch.records) ? batch.records : []) {
      if (record && typeof record === "object" && !Array.isArray(record)) {
        records.push(record);
      }
    }
  }

  return freeze(records);
}

function countCorpusTypes(records = []) {
  const counts = {
    dhatu: 0,
    sutra: 0,
    stotra: 0
  };

  records.forEach((record) => {
    const type = String(record.type || "").trim();
    if (Object.prototype.hasOwnProperty.call(counts, type)) {
      counts[type] += 1;
    }
  });

  return freeze(counts);
}

function buildAllocationByType(typeCounts = {}, quotas = DEFAULT_CORPUS_ALLOCATION) {
  const allocation = {};

  Object.keys(quotas).forEach((type) => {
    const quota = Number(quotas[type] || 0);
    const used = Number(typeCounts[type] || 0);

    allocation[type] = {
      quota,
      used,
      remaining: Math.max(0, quota - used),
      exceeded: used > quota
    };
  });

  return freeze(allocation);
}

function planCorpusAllocation(input = {}, quotas = DEFAULT_CORPUS_ALLOCATION) {
  const capacity = summarizeCorpusCapacity(input);
  const records = collectAllocationRecords(input);
  const typeCounts = countCorpusTypes(records);
  const allocation = buildAllocationByType(typeCounts, quotas);

  const warnings = [];
  const errors = [];

  Object.keys(allocation).forEach((type) => {
    if (allocation[type].exceeded) {
      warnings.push(type + ":quotaExceeded");
    }
  });

  const totalReserved = Object.values(quotas).reduce((sum, value) => {
    return sum + Number(value || 0);
  }, 0);

  const totalUsed = Object.values(typeCounts).reduce((sum, value) => {
    return sum + Number(value || 0);
  }, 0);

  if (totalReserved > MAX_BULK_CORPUS_RECORDS) {
    errors.push("allocationExceedsCapacity");
  }

  return buildCorpusAllocationRecord({
    allocation,
    typeCounts,
    totalReserved,
    totalUsed,
    maxRecords: MAX_BULK_CORPUS_RECORDS,
    freeCapacity: Math.max(0, MAX_BULK_CORPUS_RECORDS - totalUsed),
    warnings,
    errors,
    capacity
  });
}

function summarizeCorpusAllocation(input = {}, quotas = DEFAULT_CORPUS_ALLOCATION) {
  const allocation = planCorpusAllocation(input, quotas);

  return freeze({
    state: allocation.state,
    valid: allocation.state !== "ALLOCATION_BLOCKED",
    allocation: allocation.allocation,
    typeCounts: allocation.typeCounts,
    totalReserved: allocation.totalReserved,
    totalUsed: allocation.totalUsed,
    maxRecords: allocation.maxRecords,
    freeCapacity: allocation.freeCapacity,
    warnings: allocation.warnings,
    errors: allocation.errors,
    previewOnly: true,
    readOnly: true,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false,
    allocationWriteAllowed: false
  });
}

module.exports = {
  collectAllocationRecords,
  countCorpusTypes,
  buildAllocationByType,
  planCorpusAllocation,
  summarizeCorpusAllocation
};