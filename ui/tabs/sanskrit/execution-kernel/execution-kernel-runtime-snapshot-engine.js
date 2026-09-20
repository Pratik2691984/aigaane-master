"use strict";

const {
buildExecutionRuntimeSnapshot
}=require(
"./execution-kernel-runtime-snapshot-map.js"
);

function freeze(v){
return Object.freeze(v);
}

function stableSerialize(
obj
){

if(
Array.isArray(obj)
){
return "["+
obj.map(
stableSerialize
).join(",")
+"]";
}

if(
obj&&
typeof obj==="object"
){

return "{"+
Object.keys(obj)
.sort()
.map(
k=>
JSON.stringify(k)+
":"+
stableSerialize(obj[k])
)
.join(",")
+"}";
}

return JSON.stringify(
obj
);

}

function hash(v){

const s=
stableSerialize(v);

let h=0;

for(
let i=0;
i<s.length;
i++
){
h=
(
(h<<5)-h
)+
s.charCodeAt(i);

h|=0;
}

return String(
Math.abs(h)
);

}

function captureExecutionRuntimeSnapshot(
runtime={}
){

const snapshot=
buildExecutionRuntimeSnapshot(
runtime
);

return freeze({
...snapshot,
inspectionHash:
hash(snapshot)
});

}

function compareExecutionRuntimeSnapshots(
a,
b
){

return freeze({
stable:
stableSerialize(a)===
stableSerialize(b)
});

}

function summarizeExecutionRuntimeSnapshot(
snapshot
){

return freeze({
snapshotId:
snapshot.snapshotId,

stable:true,

executionMode:
snapshot.executionMode,

pipelineStage:
snapshot.pipelineStage,

ruleQueueLength:
snapshot.ruleQueueLength,

transformCount:
snapshot.transformCount,

inspectionHash:
snapshot.inspectionHash
});

}

module.exports={
stableSerializeExecutionRuntimeSnapshot:
stableSerialize,

hashExecutionRuntimeSnapshot:
hash,

captureExecutionRuntimeSnapshot,

compareExecutionRuntimeSnapshots,

summarizeExecutionRuntimeSnapshot
};