"use strict";

const {
createRuntimePublicationFinalTagIndex
}=require("./execution-kernel-runtime-publication-final-tag-index.js");

const FINAL_SUMMARY_SCHEMA =
"sanskrit-runtime-publication-final-summary.v1";

function freeze(v){
return Object.freeze(v);
}

function createRuntimePublicationFinalSummary(input={}){

const index =
input.index ||
createRuntimePublicationFinalTagIndex({});

return freeze({

schemaVersion:FINAL_SUMMARY_SCHEMA,

summary:freeze({
status:"READY",
tagCount:(index.tags||[]).length,
published:false,
sealed:true
}),

source:freeze({
schemaVersion:index.schemaVersion
}),

capabilities:freeze({
execute:false,
publish:false,
rollback:false,
mutate:false,
canonicalWrite:false
}),

diagnostics:freeze({
summaryReady:true,
executionBlocked:true,
publicationBlocked:true,
canonicalWriteBlocked:true
})
});

}

function inspectRuntimePublicationFinalSummary(
summary={}
){

return freeze({
ready:Boolean(
summary.diagnostics?.summaryReady
),
executionBlocked:true,
publicationBlocked:true,
canonicalWriteBlocked:true
});

}

module.exports={
FINAL_SUMMARY_SCHEMA,
createRuntimePublicationFinalSummary,
inspectRuntimePublicationFinalSummary
};