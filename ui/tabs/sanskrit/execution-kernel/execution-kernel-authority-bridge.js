"use strict";

const {
createExecutionKernelSnapshot
}=require("./execution-kernel-engine.js");

const AUTHORITY_BRIDGE_SCHEMA_VERSION =
"sanskrit-execution-kernel-authority-bridge.v1";

function freeze(v){
return Object.freeze(v);
}

function ref(v,f){
if(typeof v==="string"){
return v;
}

if(v&&typeof v==="object"){
return String(
v.id||
v.referenceId||
f
);
}

return f;
}

function normalizeExecutionAuthorityReference(
authority
){

const obj=
authority&&
typeof authority==="object";

const str=
typeof authority==="string";

return freeze({

id:
str
? authority
:
obj
?
String(
authority.id||
authority.referenceId||
"authority.unresolved"
)
:
"authority.unresolved",

kind:
str
?
"EXECUTION_AUTHORITY_REFERENCE"
:
obj
?
String(
authority.kind||
"EXECUTION_AUTHORITY_REFERENCE"
)
:
"EXECUTION_AUTHORITY_REFERENCE",

schemaVersion:
str
?
"unknown"
:
obj
?
String(
authority.schemaVersion||
"unknown"
)
:
"unknown",

status:
str
?
"REFERENCED"
:
obj
?
String(
authority.status||
"REFERENCED"
)
:
"UNRESOLVED",

authorized:
Boolean(
obj&&
authority.authorized===true
),

delegationAllowed:
Boolean(
obj&&
authority.delegationAllowed===true
),

executionAllowed:
Boolean(
obj&&
authority.executionAllowed===true
),

diagnostics:
freeze({

normalized:true,

authorityLinked:true,

sourceAuthorizedObserved:
Boolean(
obj&&
authority.authorized===true
),

sourceDelegationObserved:
Boolean(
obj&&
authority.delegationAllowed===true
),

sourceExecutionObserved:
Boolean(
obj&&
authority.executionAllowed===true
),

bridgeAuthorityGranted:false,

bridgeDelegationGranted:false,

bridgeExecutionGranted:false

})

});

}

function createExecutionKernelAuthorityBridge(
input={}
){

const kernel=
input.kernelSnapshot||{};

const stages=
Array.isArray(
kernel.stages
)
?
kernel.stages
:
[];

return freeze({

schemaVersion:
AUTHORITY_BRIDGE_SCHEMA_VERSION,

kind:
"EXECUTION_KERNEL_AUTHORITY_BRIDGE",

kernel:
freeze({

schemaVersion:
String(
kernel.schemaVersion||
"unknown"
),

kind:
String(
kernel.kind||
"EXECUTION_KERNEL_SNAPSHOT"
),

mode:
String(
kernel.mode||
"INSPECTION"
),

stageCount:
stages.length

}),

authority:
normalizeExecutionAuthorityReference(
input.authority
),

governance:
freeze({
id:
ref(
input.governance,
"governance.unresolved"
),
linked:true
}),

certification:
freeze({
id:
ref(
input.certification,
"certification.unresolved"
),
linked:true
}),

integrity:
freeze({
id:
ref(
input.integrity,
"integrity.unresolved"
),
linked:true
}),

runtimeEnvironment:
freeze({
id:
ref(
input.runtimeEnvironment,
"runtime.unresolved"
),
linked:true
}),

linkage:
freeze({

kernelLinked:true,

authorityLinked:true,

governanceLinked:true,

certificationLinked:true,

integrityLinked:true,

runtimeLinked:true,

authorityInspectionOnly:true,

delegationBlocked:true,

executionBlocked:true,

mutationBlocked:true,

rollbackBlocked:true,

replayBlocked:true,

surfaceFormBlocked:true

}),

diagnostics:
freeze({

ready:true,

deterministic:true,

immutable:true,

inspectionOnly:true,

authorityOnly:true,

delegationBlocked:true,

executionBlocked:true,

mutationFree:true,

rollbackBlocked:true,

replayBlocked:true,

surfaceFormBlocked:true,

governanceCompatible:true,

certificationCompatible:true,

integrityCompatible:true,

runtimeCompatible:true,

stageCount:
stages.length

})

});

}

function buildExecutionKernelAuthorityBridgeSnapshot(
input={}
){

const kernel=
input.kernelSnapshot||

createExecutionKernelSnapshot({

mode:
input.mode||
"INSPECTION",

guard:
input.guardReference||
"guard.unresolved",

runtimeEnvironment:
input.runtimeEnvironment||
"runtime.unresolved",

prakriyaPlan:
input.prakriyaPlan||
"prakriya.unresolved",

derivationGraph:
input.derivationGraph||
"graph.unresolved",

stages:
input.stages||
[]

});

return createExecutionKernelAuthorityBridge({

kernelSnapshot:
kernel,

authority:
input.authority,

governance:
input.governance,

certification:
input.certification,

integrity:
input.integrity,

runtimeEnvironment:
input.runtimeEnvironment

});

}

function getExecutionKernelAuthorityBridgeDiagnostics(
bridge={}
){

const l=
bridge.linkage||{};

const d=
bridge.diagnostics||{};

return freeze({

schemaVersion:
bridge.schemaVersion,

ready:
Boolean(
d.ready
),

authorityLinked:
Boolean(
l.authorityLinked
),

governanceLinked:
Boolean(
l.governanceLinked
),

certificationLinked:
Boolean(
l.certificationLinked
),

integrityLinked:
Boolean(
l.integrityLinked
),

runtimeLinked:
Boolean(
l.runtimeLinked
),

delegationBlocked:
Boolean(
l.delegationBlocked
),

executionBlocked:
Boolean(
l.executionBlocked
),

mutationFree:
Boolean(
d.mutationFree
),

rollbackBlocked:
Boolean(
l.rollbackBlocked
),

replayBlocked:
Boolean(
l.replayBlocked
),

surfaceFormBlocked:
Boolean(
l.surfaceFormBlocked
),

stageCount:
Number(
d.stageCount||0
)

});

}

module.exports={
AUTHORITY_BRIDGE_SCHEMA_VERSION,
normalizeExecutionAuthorityReference,
createExecutionKernelAuthorityBridge,
buildExecutionKernelAuthorityBridgeSnapshot,
getExecutionKernelAuthorityBridgeDiagnostics
};