"use strict";

const {
createRuntimePublicationFinalSummary
}=require("./execution-kernel-runtime-publication-final-summary.js");

const FINAL_RENDERER_SCHEMA =
"sanskrit-runtime-publication-final-renderer.v1";

function freeze(v){
return Object.freeze(v);
}

function renderRuntimePublicationFinal(
input={}
){

const summary =
input.summary ||
createRuntimePublicationFinalSummary({});

return freeze({

schemaVersion:
FINAL_RENDERER_SCHEMA,

view:freeze({
title:
"Runtime Publication Final",

status:
summary.summary?.status ||
"READY",

sealed:true,

published:false
}),

source:freeze({
schemaVersion:
summary.schemaVersion
}),

capabilities:freeze({
execute:false,
publish:false,
rollback:false,
mutate:false,
canonicalWrite:false
}),

diagnostics:freeze({
rendered:true,
executionBlocked:true,
publicationBlocked:true,
canonicalWriteBlocked:true
})
});

}

function inspectRuntimePublicationRenderer(
view={}
){

return freeze({
rendered:
Boolean(
view.diagnostics?.rendered
),

executionBlocked:true,

canonicalWriteBlocked:true
});

}

module.exports={
FINAL_RENDERER_SCHEMA,
renderRuntimePublicationFinal,
inspectRuntimePublicationRenderer
};