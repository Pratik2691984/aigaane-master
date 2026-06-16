"use strict";

const {
createExecutionKernelCloseoutRenderer
}=require(
"./execution-kernel-closeout-renderer.js"
);

const EXECUTION_KERNEL_STABLE_TAG =
"sanskrit-v1254-execution-kernel-closeout-stable";

function freeze(v){
return Object.freeze(v);
}

function createExecutionKernelStableTag(
input={}
){

const renderer=
input.renderer||
createExecutionKernelCloseoutRenderer({});

return freeze({

tag:
EXECUTION_KERNEL_STABLE_TAG,

kind:
"EXECUTION_KERNEL_STABLE_TAG",

renderer:
freeze({

schemaVersion:
renderer.schemaVersion,

renderCount:
Number(
renderer.render?.renderCount||
0
)

}),

closeout:
freeze({

sealed:true,

executionEnabled:false,

surfaceFormsEnabled:false,

mutationEnabled:false

}),

diagnostics:
freeze({

ready:true,

deterministic:true,

immutable:true,

inspectionOnly:true,

executionBlocked:true,

surfaceBlocked:true,

mutationFree:true,

replaySafe:true

})

});

}

function getExecutionKernelStableTagDiagnostics(
tag={}
){

const d=
tag.diagnostics||{};

return freeze({

ready:
Boolean(
d.ready
),

executionBlocked:
Boolean(
d.executionBlocked
),

surfaceBlocked:
Boolean(
d.surfaceBlocked
),

mutationFree:
Boolean(
d.mutationFree
),

replaySafe:
Boolean(
d.replaySafe
)

});

}

module.exports={

EXECUTION_KERNEL_STABLE_TAG,

createExecutionKernelStableTag,

getExecutionKernelStableTagDiagnostics

};