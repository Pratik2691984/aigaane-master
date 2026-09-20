"use strict";

const {
createRuntimePublicationCloseout
}=require(
"./execution-kernel-runtime-publication-closeout.js"
);

const STABLE_TAG_SCHEMA =
"sanskrit-runtime-publication-stable-tag.v1";

function freeze(v){
return Object.freeze(v);
}

function createRuntimePublicationStableTag(
input={}
){

const closeout=
input.closeout||
createRuntimePublicationCloseout({});

return freeze({

schemaVersion:
STABLE_TAG_SCHEMA,

kind:
"CONTROLLED_RUNTIME_PUBLICATION_STABLE_TAG",

tag:
freeze({

name:
input.name||
"sanskrit-runtime-stable",

published:
Boolean(
closeout.publication?.published
),

closed:
Boolean(
closeout.publication?.closed
),

immutable:true,

deterministic:true

}),

capabilities:
freeze({

execute:false,
rollback:false,
replay:false,
mutate:false,
canonicalWrite:false,
publishOnly:true

}),

diagnostics:
freeze({

ready:true,
publishOnly:true,
executionBlocked:true,
rollbackBlocked:true,
replayBlocked:true,
mutationFree:true,
canonicalWriteBlocked:true

})

});

}

function getRuntimePublicationStableTagDiagnostics(
tag={}
){

return freeze({

schemaVersion:
tag.schemaVersion,

ready:
Boolean(
tag.diagnostics?.ready
),

publishOnly:true,

executionBlocked:true,

canonicalWriteBlocked:true

});

}

module.exports={
STABLE_TAG_SCHEMA,
createRuntimePublicationStableTag,
getRuntimePublicationStableTagDiagnostics
};