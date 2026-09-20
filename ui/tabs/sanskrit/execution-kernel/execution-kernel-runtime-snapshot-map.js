"use strict";

const SNAPSHOT_SCHEMA =
"sanskrit-runtime-snapshot.v1";

const SNAPSHOT_STATES =
Object.freeze({
EMPTY:"EMPTY",
READY:"READY",
CONTROLLED:"CONTROLLED"
});

function freeze(v){
return Object.freeze(v);
}

function normalizeRuntimeSnapshot(input={}){

return freeze({
snapshotId:
String(
input.snapshotId||
"runtime-snapshot"
),

createdAt:
String(
input.createdAt||
"static"
),

executionMode:
String(
input.executionMode||
"controlled"
),

pipelineStage:
String(
input.pipelineStage||
"unresolved"
),

ruleQueueLength:
Math.max(
0,
Number(
input.ruleQueueLength||0
)
),

transformCount:
Math.max(
0,
Number(
input.transformCount||0
)
),

inspectionHash:
String(
input.inspectionHash||
"pending"
),

diagnostics:
freeze({
...(input.diagnostics||{})
}),

warnings:
freeze([
...(input.warnings||[])
]),

metadata:
freeze({
...(input.metadata||{})
})
});

}

function buildExecutionRuntimeSnapshot(
input={}
){

return freeze({
schemaVersion:
SNAPSHOT_SCHEMA,

state:
SNAPSHOT_STATES.CONTROLLED,

...normalizeRuntimeSnapshot(
input
)
});

}

function validateRuntimeSnapshot(
snapshot={}
){

const errors=[];

if(
typeof snapshot!=="object"
){
errors.push(
"snapshot"
);
}

if(
typeof snapshot.executionMode!=="string"
){
errors.push(
"executionMode"
);
}

if(
typeof snapshot.pipelineStage!=="string"
){
errors.push(
"pipelineStage"
);
}

return freeze({
valid:
errors.length===0,
errors
});

}

module.exports={
SNAPSHOT_SCHEMA,
SNAPSHOT_STATES,
normalizeRuntimeSnapshot,
buildExecutionRuntimeSnapshot,
validateRuntimeSnapshot
};