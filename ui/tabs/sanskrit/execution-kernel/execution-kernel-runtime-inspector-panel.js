"use strict";

const {
createRuntimeDiagnosticsView
}=require("./execution-kernel-runtime-diagnostics-view.js");

const INSPECTOR_PANEL_SCHEMA =
"sanskrit-runtime-inspector-panel.v1";

function freeze(v){
return Object.freeze(v);
}

function createRuntimeInspectorPanel(input={}){

const diagnostics =
input.diagnosticsView ||
createRuntimeDiagnosticsView({});

return freeze({
schemaVersion:INSPECTOR_PANEL_SCHEMA,

panel:freeze({
id:"execution-runtime-inspector-panel",
title:"Runtime Inspector",
visible:true,
readOnly:true,
status:String(diagnostics.view?.status||"READY"),
sectionCount:Number(diagnostics.view?.sectionCount||0)
}),

inspection:freeze({
ready:Boolean(diagnostics.diagnostics?.ready),
executionBlocked:Boolean(diagnostics.diagnostics?.executionBlocked),
publicationBlocked:Boolean(diagnostics.diagnostics?.publicationBlocked),
canonicalWriteBlocked:Boolean(diagnostics.diagnostics?.canonicalWriteBlocked),
readOnly:Boolean(diagnostics.diagnostics?.readOnly)
}),

capabilities:freeze({
inspect:true,
render:true,
execute:false,
publish:false,
rollback:false,
mutate:false,
canonicalWrite:false
}),

diagnostics:freeze({
panelReady:true,
readOnly:true,
executionBlocked:true,
publicationBlocked:true,
canonicalWriteBlocked:true
})
});

}

function inspectRuntimeInspectorPanel(panel={}){
return freeze({
ready:Boolean(panel.diagnostics?.panelReady),
visible:Boolean(panel.panel?.visible),
readOnly:Boolean(panel.panel?.readOnly),
executionBlocked:true,
canonicalWriteBlocked:true
});
}

module.exports={
INSPECTOR_PANEL_SCHEMA,
createRuntimeInspectorPanel,
inspectRuntimeInspectorPanel
};