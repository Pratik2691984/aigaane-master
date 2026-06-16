"use strict";

const {
createExecutionKernelSnapshot
}=require("./execution-kernel-engine.js");

const GOVERNANCE_BRIDGE_SCHEMA_VERSION=
"sanskrit-execution-kernel-governance-bridge.v1";

function freeze(v){
return Object.freeze(v);
}

function ref(v,f){
if(typeof v==="string") return v;

if(v&&typeof v==="object"){
return String(
v.id||
v.referenceId||
f
);
}

return f;
}

function normalizeExecutionGovernanceReference(
governance
){

const obj=
governance&&
typeof governance==="object";

const str=
typeof governance==="string";

return freeze({

id:
str
? governance
:
obj
?
String(
governance.id||
governance.referenceId||
"governance.unresolved"
)
:
"governance.unresolved",

kind:
str
?
"EXECUTION_GOVERNANCE_REFERENCE"
:
obj
?
String(
governance.kind||
"EXECUTION_GOVERNANCE_REFERENCE"
)
:
"EXECUTION_GOVERNANCE_REFERENCE",

schemaVersion:
str
?
"unknown"
:
obj
?
String(
governance.schemaVersion||
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
governance.status||
"REFERENCED"
)
:
"UNRESOLVED",

governed:
Boolean(
obj&&
governance.governed===true
),

authorizationAllowed:
Boolean(
obj&&
governance.authorizationAllowed===true
),

executionAllowed:
Boolean(
obj&&
governance.executionAllowed===true
),

diagnostics:
freeze({

normalized:true,

governanceLinked:true,

sourceGovernedObserved:
Boolean(
obj&&
governance.governed===true
),

sourceAuthorizationObserved:
Boolean(
obj&&
governance.authorizationAllowed===true
),

sourceExecutionObserved:
Boolean(
obj&&
governance.executionAllowed===true
),

bridgeGovernanceGranted:false,

bridgeAuthorizationGranted:false,

bridgeExecutionGranted:false

})

});

}

function createExecutionKernelGovernanceBridge(
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
GOVERNANCE_BRIDGE_SCHEMA_VERSION,

kind:
"EXECUTION_KERNEL_GOVERNANCE_BRIDGE",

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

governance:
normalizeExecutionGovernanceReference(
input.governance
),

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

assurance:
freeze({
id:
ref(
input.assurance,
"assurance.unresolved"
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

governanceLinked:true,

certificationLinked:true,

integrityLinked:true,

assuranceLinked:true,

runtimeLinked:true,

governanceInspectionOnly:true,

authorizationBlocked:true,

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

governanceOnly:true,

authorizationBlocked:true,

executionBlocked:true,

mutationFree:true,

rollbackBlocked:true,

replayBlocked:true,

surfaceFormBlocked:true,

certificationCompatible:true,

integrityCompatible:true,

assuranceCompatible:true,

runtimeCompatible:true,

stageCount:
stages.length

})

});

}

function buildExecutionKernelGovernanceBridgeSnapshot(
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

return createExecutionKernelGovernanceBridge({

kernelSnapshot:
kernel,

governance:
input.governance,

certification:
input.certification,

integrity:
input.integrity,

assurance:
input.assurance,

runtimeEnvironment:
input.runtimeEnvironment

});

}

function getExecutionKernelGovernanceBridgeDiagnostics(
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

assuranceLinked:
Boolean(
l.assuranceLinked
),

runtimeLinked:
Boolean(
l.runtimeLinked
),

authorizationBlocked:
Boolean(
l.authorizationBlocked
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
GOVERNANCE_BRIDGE_SCHEMA_VERSION,
normalizeExecutionGovernanceReference,
createExecutionKernelGovernanceBridge,
buildExecutionKernelGovernanceBridgeSnapshot,
getExecutionKernelGovernanceBridgeDiagnostics
};