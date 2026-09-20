"use strict";

const {
createRuntimeTagIndex
}=require(
"./execution-kernel-runtime-tag-index.js"
);

const SUMMARY_SCHEMA=
"sanskrit-runtime-tag-summary.v1";

function freeze(v){
return Object.freeze(v);
}

function createRuntimeTagSummary(
input={}
){

const index=
input.index||
createRuntimeTagIndex({});

const entries=
Array.isArray(index.entries)
?
index.entries
:
[];

return freeze({

schemaVersion:
SUMMARY_SCHEMA,

kind:
"CONTROLLED_RUNTIME_TAG_SUMMARY",

summary:
freeze({

entryCount:
entries.length,

published:
Boolean(
index.publication?.published
),

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

summaryOnly:true

}),

diagnostics:
freeze({

ready:true,

summaryOnly:true,

executionBlocked:true,

mutationFree:true,

canonicalWriteBlocked:true

})

});

}

function getRuntimeTagSummaryDiagnostics(
summary={}
){

return freeze({

schemaVersion:
summary.schemaVersion,

ready:
Boolean(
summary.diagnostics?.ready
),

summaryOnly:true,

executionBlocked:true,

canonicalWriteBlocked:true

});

}

module.exports={

SUMMARY_SCHEMA,

createRuntimeTagSummary,

getRuntimeTagSummaryDiagnostics

};