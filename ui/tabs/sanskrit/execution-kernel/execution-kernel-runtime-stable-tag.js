"use strict";

const {
createRuntimeCloseout
}=require(
"./execution-kernel-runtime-closeout.js"
);

const RUNTIME_STABLE_TAG_VERSION =
"sanskrit-runtime-stable.v1";

function freeze(v){
return Object.freeze(v);
}

function createRuntimeStableTag(
input={}
){

const closeout=
input.closeout||
createRuntimeCloseout({});

return freeze({

schemaVersion:
RUNTIME_STABLE_TAG_VERSION,

kind:
"CONTROLLED_RUNTIME_STABLE_TAG",

tag:
freeze({

name:
"sanskrit-runtime-stable",

ready:
Boolean(
closeout.summary?.ready
),

deterministic:true,

immutable:true

}),

capabilities:
freeze({

execute:false,

rollback:false,

mutate:false,

commit:false,

replay:false

}),

diagnostics:
freeze({

ready:true,

stable:true,

executionBlocked:true,

mutationFree:true

})

});

}

function getRuntimeStableDiagnostics(
tag={}
){

return freeze({

schemaVersion:
tag.schemaVersion,

ready:
Boolean(
tag.diagnostics?.ready
),

stable:true,

executionBlocked:true

});

}

module.exports={

RUNTIME_STABLE_TAG_VERSION,

createRuntimeStableTag,

getRuntimeStableDiagnostics

};