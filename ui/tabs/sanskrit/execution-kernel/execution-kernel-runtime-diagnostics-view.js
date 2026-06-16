"use strict";

const {
renderRuntimeUi
}=require("./execution-kernel-runtime-ui-renderer.js");

const DIAGNOSTICS_VIEW_SCHEMA =
"sanskrit-runtime-diagnostics-view.v1";

function freeze(v){
return Object.freeze(v);
}

function createRuntimeDiagnosticsView(input={}){

const rendered=
input.rendered||
renderRuntimeUi({});

return freeze({
schemaVersion:DIAGNOSTICS_VIEW_SCHEMA,

diagnostics:freeze({
ready:Boolean(rendered.diagnostics?.rendererReady),
readOnly:Boolean(rendered.diagnostics?.readOnly),
executionBlocked:Boolean(rendered.diagnostics?.executionBlocked),
publicationBlocked:Boolean(rendered.diagnostics?.publicationBlocked),
canonicalWriteBlocked:Boolean(rendered.diagnostics?.canonicalWriteBlocked)
}),

view:freeze({
id:"execution-runtime-diagnostics",
title:"Runtime Diagnostics",
visible:true,
sectionCount:(rendered.sections||[]).length,
status:String(rendered.view?.status||"READY")
}),

capabilities:freeze({
inspect:true,
render:true,
execute:false,
publish:false,
rollback:false,
mutate:false,
canonicalWrite:false
})
});

}

function inspectRuntimeDiagnosticsView(view={}){

return freeze({
ready:Boolean(view.diagnostics?.ready),
visible:Boolean(view.view?.visible),
sectionCount:Number(view.view?.sectionCount||0),
executionBlocked:true,
canonicalWriteBlocked:true
});

}

module.exports={
DIAGNOSTICS_VIEW_SCHEMA,
createRuntimeDiagnosticsView,
inspectRuntimeDiagnosticsView
};