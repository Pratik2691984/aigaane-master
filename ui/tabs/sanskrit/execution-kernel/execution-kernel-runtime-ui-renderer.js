"use strict";

const {
createRuntimePanelAdapter
}=require("./execution-kernel-runtime-panel-adapter.js");

const UI_RENDERER_SCHEMA =
"sanskrit-runtime-ui-renderer.v1";

function freeze(v){
return Object.freeze(v);
}

function renderRuntimeUi(input={}){

const adapter=
input.adapter||
createRuntimePanelAdapter({});

return freeze({
schemaVersion:UI_RENDERER_SCHEMA,

view:freeze({
id:"execution-runtime-view",
title:String(adapter.panel?.title||"Execution Runtime"),
status:String(adapter.panel?.status||"READY"),
tag:String(adapter.panel?.tag||"sanskrit-runtime-publication-stable"),
visible:Boolean(adapter.panel?.visible),
readOnly:true
}),

sections:freeze([
freeze({
id:"runtime-status",
label:"Runtime Status",
value:String(adapter.panel?.status||"READY"),
readOnly:true
}),
freeze({
id:"runtime-tag",
label:"Runtime Tag",
value:String(adapter.panel?.tag||"sanskrit-runtime-publication-stable"),
readOnly:true
})
]),

capabilities:freeze({
render:true,
inspect:true,
execute:false,
publish:false,
rollback:false,
mutate:false,
canonicalWrite:false
}),

diagnostics:freeze({
rendererReady:true,
readOnly:true,
executionBlocked:true,
publicationBlocked:true,
canonicalWriteBlocked:true
})
});

}

function inspectRuntimeUiRenderer(view={}){
return freeze({
ready:Boolean(view.diagnostics?.rendererReady),
sectionCount:(view.sections||[]).length,
readOnly:Boolean(view.diagnostics?.readOnly),
executionBlocked:true,
canonicalWriteBlocked:true
});
}

module.exports={
UI_RENDERER_SCHEMA,
renderRuntimeUi,
inspectRuntimeUiRenderer
};