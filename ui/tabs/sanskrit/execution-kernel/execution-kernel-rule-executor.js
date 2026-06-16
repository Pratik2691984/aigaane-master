"use strict";

const {
createExecutionKernelSnapshot
}=require(
"./execution-kernel-engine.js"
);

const RULE_EXECUTOR_SCHEMA_VERSION=
"sanskrit-rule-executor.v1";

function freeze(v){
return Object.freeze(v);
}

function normalizeRule(
rule,
index
){

return freeze({

index,

id:
String(
rule?.id||
`rule-${index}`
),

type:
String(
rule?.type||
"INSPECTION_RULE"
),

scheduled:true,

authorized:false,

executed:false,

mutated:false,

diagnostics:
freeze({

inspectionOnly:true,

executionBlocked:true,

mutationBlocked:true

})

});

}

function createRuleExecutionEnvelope(
input={}
){

const rules=
Array.isArray(
input.rules
)
?
input.rules
:
[];

return freeze({

schemaVersion:
RULE_EXECUTOR_SCHEMA_VERSION,

kind:
"RULE_EXECUTION_ENVELOPE",

kernel:
createExecutionKernelSnapshot({

mode:
"CONTROLLED_EXECUTION",

guard:
input.guard,

runtimeEnvironment:
input.runtime,

prakriyaPlan:
input.plan,

derivationGraph:
input.graph,

stages:[]
}),

rules:
freeze(
rules
.map(
normalizeRule
)
),

capabilities:
freeze({

execute:false,

mutate:false,

surfaceForms:false,

rollback:true,

inspectOnly:true

}),

diagnostics:
freeze({

ready:true,

deterministic:true,

executionBlocked:true,

mutationFree:true,

replaySafe:true

})

});

}

function getRuleExecutorDiagnostics(
envelope={}
){

return freeze({

ready:true,

ruleCount:
(
envelope.rules||
[]
).length,

executionBlocked:true,

mutationFree:true,

replaySafe:true

});

}

module.exports={

RULE_EXECUTOR_SCHEMA_VERSION,

normalizeRule,

createRuleExecutionEnvelope,

getRuleExecutorDiagnostics

};