"use strict";

const {
createRuntimeUiBridge
}=require(
"./execution-kernel-runtime-ui-bridge.js"
);

const PANEL_ADAPTER_SCHEMA =
"sanskrit-runtime-panel-adapter.v1";

function freeze(v){
return Object.freeze(v);
}

function createRuntimePanelAdapter(
input={}
){

const bridge=
input.bridge||
createRuntimeUiBridge({});

return freeze({

schemaVersion:
PANEL_ADAPTER_SCHEMA,

panel:freeze({

id:
"execution-runtime-panel",

visible:true,

mode:
"READ_ONLY",

title:
"Execution Runtime",

status:
bridge.ui.status,

tag:
bridge.ui.tag
}),

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

adapterReady:true,

readOnly:true,

executionBlocked:true,

canonicalWriteBlocked:true
})
});

}

function inspectRuntimePanelAdapter(
adapter={}
){

return freeze({

ready:
Boolean(
adapter.diagnostics?.adapterReady
),

render:
Boolean(
adapter.capabilities?.render
),

readOnly:
Boolean(
adapter.diagnostics?.readOnly
)
});

}

module.exports={
PANEL_ADAPTER_SCHEMA,
createRuntimePanelAdapter,
inspectRuntimePanelAdapter
};