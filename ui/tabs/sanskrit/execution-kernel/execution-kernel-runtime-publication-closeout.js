"use strict";

const {
createRuntimeTagSummary
}=require("./execution-kernel-runtime-tag-summary.js");

const PUBLICATION_CLOSEOUT_SCHEMA =
"sanskrit-runtime-publication-closeout.v1";

function freeze(v){
return Object.freeze(v);
}

function createRuntimePublicationCloseout(input={}){

const summary=
input.summary||
createRuntimeTagSummary({});

return freeze({

schemaVersion:
PUBLICATION_CLOSEOUT_SCHEMA,

kind:
"CONTROLLED_RUNTIME_PUBLICATION_CLOSEOUT",

publication:
freeze({
closed:true,
published:Boolean(summary.summary?.published),
entryCount:Number(summary.summary?.entryCount||0),
deterministic:true,
immutable:true
}),

capabilities:
freeze({
execute:false,
rollback:false,
replay:false,
mutate:false,
canonicalWrite:false,
closeoutOnly:true
}),

diagnostics:
freeze({
ready:true,
closeoutOnly:true,
executionBlocked:true,
rollbackBlocked:true,
replayBlocked:true,
mutationFree:true,
canonicalWriteBlocked:true
})

});

}

function getRuntimePublicationCloseoutDiagnostics(closeout={}){

return freeze({
schemaVersion:closeout.schemaVersion,
ready:Boolean(closeout.diagnostics?.ready),
closeoutOnly:true,
executionBlocked:true,
rollbackBlocked:true,
replayBlocked:true,
mutationFree:true,
canonicalWriteBlocked:true
});

}

module.exports={
PUBLICATION_CLOSEOUT_SCHEMA,
createRuntimePublicationCloseout,
getRuntimePublicationCloseoutDiagnostics
};