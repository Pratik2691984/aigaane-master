"use strict";

const EXPORT_SCHEMA = "sanskrit-runtime-export.v1";

const EXPORT_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  EXPORT_READY: "EXPORT_READY",
  BLOCKED: "BLOCKED"
});

function freeze(v){
  return Object.freeze(v);
}

function isObject(v){
  return Boolean(v) &&
    typeof v === "object" &&
    !Array.isArray(v);
}

function asCount(v){
  const n = Number(v || 0);
  if (!Number.isFinite(n)) {
    return 0;
  }
  return Math.max(
    0,
    Math.floor(n)
  );
}

function normalizeRuntimeExportRecord(
  input={}
){

  return freeze({

    exportId:
      String(
        input.exportId ||
        "runtime-export"
      ),

    createdAt:
      String(
        input.createdAt ||
        "static"
      ),

    certificationId:
      String(
        input.certificationId ||
        "runtime-certification"
      ),

    certificationStatus:
      String(
        input.certificationStatus ||
        "certified-for-inspection"
      ),

    certificate:
      String(
        input.certificate ||
        "controlled-runtime-inspection-only"
      ),

    exportStatus:
      String(
        input.exportStatus ||
        "export-ready"
      ),

    exportMode:
      String(
        input.exportMode ||
        "inspection-export"
      ),

    replayAllowed:
      false,

    executionAllowed:
      false,

    mutationAllowed:
      false,

    publicationAllowed:
      false,

    rollbackAllowed:
      false,

    canonicalWriteAllowed:
      false,

    controlCount:
      asCount(
        input.controlCount
      ),

    findingCount:
      asCount(
        input.findingCount
      ),

    warningCount:
      asCount(
        input.warningCount
      ),

    attestations:
      freeze([
        ...(
          Array.isArray(
            input.attestations
          )
            ? input.attestations
            : []
        )
      ]),

    warnings:
      freeze([
        ...(
          Array.isArray(
            input.warnings
          )
            ? input.warnings
            : []
        )
      ]),

    diagnostics:
      freeze({
        ...(
          isObject(
            input.diagnostics
          )
            ? input.diagnostics
            : {}
        )
      }),

    metadata:
      freeze({
        ...(
          isObject(
            input.metadata
          )
            ? input.metadata
            : {}
        )
      })

  });

}

function buildRuntimeExportRecord(
  input={}
){

  const normalized =
    normalizeRuntimeExportRecord(
      input
    );

  return freeze({
    schemaVersion:
      EXPORT_SCHEMA,

    state:
      normalized.attestations.length
        ? EXPORT_STATES.EXPORT_READY
        : EXPORT_STATES.EMPTY,

    ...normalized
  });

}

function validateRuntimeExportRecord(
  record={}
){

  const errors=[];

  if(
    !isObject(record)
  ){
    errors.push(
      "record"
    );
  }

  [
    "attestations",
    "warnings"
  ].forEach(
    (field)=>{
      if(
        !Array.isArray(
          record[field]
        )
      ){
        errors.push(
          field
        );
      }
    }
  );

  return freeze({
    valid:
      errors.length===0,

    errors
  });

}

module.exports={
  EXPORT_SCHEMA,
  EXPORT_STATES,

  normalizeRuntimeExportRecord,
  buildRuntimeExportRecord,
  validateRuntimeExportRecord
};