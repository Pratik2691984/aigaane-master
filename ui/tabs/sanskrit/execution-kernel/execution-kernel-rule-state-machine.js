"use strict";

const {
createRuleExecutionEnvelope
}=require("./execution-kernel-rule-executor.js");

const RULE_STATE_MACHINE_SCHEMA_VERSION =
"sanskrit-rule-state-machine.v1";

function freeze(v){ return Object.freeze(v); }

const RULE_STATES = freeze({
PLANNED:"PLANNED",
QUEUED:"QUEUED",
INSPECTED:"INSPECTED",
BLOCKED:"BLOCKED"
});

function normalizeRuleState(rule,index){
return freeze({
index,
id:String(rule?.id||`rule-state-${index}`),
state:String(rule?.state||RULE_STATES.PLANNED),
authorized:false,
executed:false,
mutated:false,
transitionAllowed:false,
diagnostics:freeze({
inspectionOnly:true,
transitionBlocked:true,
executionBlocked:true,
mutationBlocked:true
})
});
}

function createRuleStateMachine(input={}){
const envelope=input.envelope||createRuleExecutionEnvelope({rules:input.rules||[]});
const rules=Array.isArray(envelope.rules)?envelope.rules:[];

return freeze({
schemaVersion:RULE_STATE_MACHINE_SCHEMA_VERSION,
kind:"RULE_STATE_MACHINE",
envelope:freeze({
schemaVersion:envelope.schemaVersion,
ruleCount:rules.length
}),
states:freeze(rules.map(normalizeRuleState)),
capabilities:freeze({
transition:false,
authorize:false,
execute:false,
mutate:false,
inspectOnly:true
}),
diagnostics:freeze({
ready:true,
deterministic:true,
immutable:true,
stateMachineOnly:true,
transitionBlocked:true,
executionBlocked:true,
mutationFree:true,
replaySafe:true
})
});
}

function getRuleStateMachineDiagnostics(machine={}){
const states=machine.states||[];
return freeze({
schemaVersion:machine.schemaVersion,
ready:Boolean(machine.diagnostics?.ready),
stateCount:states.length,
transitionBlocked:Boolean(machine.diagnostics?.transitionBlocked),
executionBlocked:Boolean(machine.diagnostics?.executionBlocked),
mutationFree:Boolean(machine.diagnostics?.mutationFree),
replaySafe:Boolean(machine.diagnostics?.replaySafe)
});
}

module.exports={
RULE_STATE_MACHINE_SCHEMA_VERSION,
RULE_STATES,
normalizeRuleState,
createRuleStateMachine,
getRuleStateMachineDiagnostics
};