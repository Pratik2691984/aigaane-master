"use strict";

const {
createRuntimePublicationStableGitTag
}=require("./execution-kernel-runtime-publication-stable-git-tag.js");

const RUNTIME_UI_BRIDGE_SCHEMA =
"sanskrit-runtime-ui-bridge.v1";

function freeze(v){
return Object.freeze(v);
}

function createRuntimeUiBridge(input={}){

const tag=
input.tag||
createRuntimePublicationStableGitTag({});

return freeze({
schemaVersion:RUNTIME_UI_BRIDGE_SCHEMA,

kind:"CONTROLLED_RUNTIME_UI_BRIDGE",

ui:freeze({
panel:"execution-runtime",
visible:true,
readOnly:true,
status:"READY",
tag:String(tag.tag?.name||"sanskrit-runtime-publication-stable")
}),

capabilities:freeze({
execute:false,
publish:false,
rollback:false,
mutate:false,
canonicalWrite:false,
uiOnly:true
}),

diagnostics:freeze({
ready:true,
uiBridge:true,
readOnly:true,
executionBlocked:true,
publicationBlocked:true,
canonicalWriteBlocked:true
})
});
}

function inspectRuntimeUiBridge(bridge={}){
return freeze({
ready:Boolean(bridge.diagnostics?.ready),
readOnly:Boolean(bridge.diagnostics?.readOnly),
executionBlocked:true,
canonicalWriteBlocked:true
});
}

module.exports={
RUNTIME_UI_BRIDGE_SCHEMA,
createRuntimeUiBridge,
inspectRuntimeUiBridge
};