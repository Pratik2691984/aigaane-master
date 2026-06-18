"use strict";

const {
  buildCorpusAdmissionRecord
} = require("./corpus-admission-map.js");

const {
  summarizeCorpusForecast,
  buildCorpusForecast
} = require("./corpus-forecast-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveAdmissionStatus(forecast = {}) {
  if (forecast.valid === false) {
    return "admission-blocked";
  }

  if (
    forecast.importReadinessForecast === true &&
    forecast.forecastExecutionAllowed === false &&
    forecast.canonicalWriteAllowed === false
  ) {
    return "admission-ready";
  }

  return "admission-review";
}

function buildAdmissionReasons(status) {
  if (status === "admission-ready") {
    return freeze([
      "forecastReady",
      "importReadinessForecast",
      "previewOnly",
      "canonicalWriteLocked"
    ]);
  }

  return freeze([]);
}

function buildRejectionReasons(status) {
  if (status === "admission-blocked") {
    return freeze(["forecastBlocked"]);
  }

  if (status === "admission-review") {
    return freeze(["requiresReview"]);
  }

  return freeze([]);
}

function buildCorpusAdmission(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const forecastSummary = summarizeCorpusForecast(
    input,
    windowSize,
    secondsPerWindow
  );

  const forecast = buildCorpusForecast(input, windowSize, secondsPerWindow);
  const admissionStatus = deriveAdmissionStatus(forecastSummary);
  const accepted = admissionStatus === "admission-ready";

  return buildCorpusAdmissionRecord({
    admissionStatus,
    acceptedRecordCount: accepted ? forecastSummary.totalRecords : 0,
    rejectedRecordCount: accepted ? 0 : forecastSummary.totalRecords,
    admissionReasons: buildAdmissionReasons(admissionStatus),
    rejectionReasons: buildRejectionReasons(admissionStatus),
    forecast
  });
}

function summarizeCorpusAdmission(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const admission = buildCorpusAdmission(input, windowSize, secondsPerWindow);

  return freeze({
    state: admission.state,
    valid: admission.state !== "ADMISSION_BLOCKED",
    admissionStatus: admission.admissionStatus,
    acceptedRecordCount: admission.acceptedRecordCount,
    rejectedRecordCount: admission.rejectedRecordCount,
    admissionReasons: admission.admissionReasons,
    rejectionReasons: admission.rejectionReasons,
    previewOnly: true,
    readOnly: true,
    admissionExecutionAllowed: false,
    forecastExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

module.exports = {
  deriveAdmissionStatus,
  buildAdmissionReasons,
  buildRejectionReasons,
  buildCorpusAdmission,
  summarizeCorpusAdmission
};