"use strict";

const {
  createExecutionKernelSnapshot,
} = require("./execution-kernel-engine.js");

const INTEGRITY_BRIDGE_SCHEMA_VERSION =
"sanskrit-execution-kernel-integrity-bridge.v1";

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

function normalizeExecutionIntegrityReference(
integrity
){

const obj=
integrity&&
typeof integrity==="object";

const str=
typeof integrity==="string";

return freeze({

id:
str
? integrity
: obj
? String(
integrity.id||
integrity.referenceId||
"integrity.unresolved"
)
:
"integrity.unresolved",

kind:
str
?
"EXECUTION_INTEGRITY_REFERENCE"
:
obj
?
String(
integrity.kind||
"EXECUTION_INTEGRITY_REFERENCE"
)
:
"EXECUTION_INTEGRITY_REFERENCE",

schemaVersion:
str
?
"unknown"
:
obj
?
String(
integrity.schemaVersion||
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
integrity.status||
"REFERENCED"
)
:
"UNRESOLVED",

verified:
Boolean(
obj&&
integrity.verified===true
),

repairAllowed:
Boolean(
obj&&
integrity.repairAllowed===true
),

executionAllowed:
Boolean(
obj&&
integrity.executionAllowed===true
),

diagnostics:
freeze({

normalized:true,

integrityLinked:true,

sourceVerifiedObserved:
Boolean(
obj&&
integrity.verified===true
),

sourceRepairObserved:
Boolean(
obj&&
integrity.repairAllowed===true
),

sourceExecutionObserved:
Boolean(
obj&&
integrity.executionAllowed===true
),

bridgeIntegrityGranted:false,

bridgeRepairGranted:false,

bridgeExecutionGranted:false

})

});

}

function createExecutionKernelIntegrityBridge(
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
INTEGRITY_BRIDGE_SCHEMA_VERSION,

kind:
"EXECUTION_KERNEL_INTEGRITY_BRIDGE",

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

integrity:
normalizeExecutionIntegrityReference(
input.integrity
),

assurance:
freeze({
id:
ref(
input.assurance,
"assurance.unresolved"
),
linked:true
}),

compliance:
freeze({
id:
ref(
input.compliance,
"compliance.unresolved"
),
linked:true
}),

policy:
freeze({
id:
ref(
input.policy,
"policy.unresolved"
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

integrityLinked:true,

assuranceLinked:true,

complianceLinked:true,

policyLinked:true,

runtimeLinked:true,

integrityInspectionOnly:true,

repairBlocked:true,

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

integrityOnly:true,

repairBlocked:true,

executionBlocked:true,

mutationFree:true,

rollbackBlocked:true,

replayBlocked:true,

surfaceFormBlocked:true,

assuranceCompatible:true,

complianceCompatible:true,

policyCompatible:true,

runtimeCompatible:true,

stageCount:
stages.length

})

});

}

function buildExecutionKernelIntegrityBridgeSnapshot(
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

return createExecutionKernelIntegrityBridge({

kernelSnapshot:
kernel,

integrity:
input.integrity,

assurance:
input.assurance,

compliance:
input.compliance,

policy:
input.policy,

runtimeEnvironment:
input.runtimeEnvironment

});

}

function getExecutionKernelIntegrityBridgeDiagnostics(
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

integrityLinked:
Boolean(
l.integrityLinked
),

assuranceLinked:
Boolean(
l.assuranceLinked
),

complianceLinked:
Boolean(
l.complianceLinked
),

policyLinked:
Boolean(
l.policyLinked
),

runtimeLinked:
Boolean(
l.runtimeLinked
),

repairBlocked:
Boolean(
l.repairBlocked
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
INTEGRITY_BRIDGE_SCHEMA_VERSION,
normalizeExecutionIntegrityReference,
createExecutionKernelIntegrityBridge,
buildExecutionKernelIntegrityBridgeSnapshot,
getExecutionKernelIntegrityBridgeDiagnostics
};