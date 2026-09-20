"use strict";

const {
renderRuntimePublicationFinal
}=require("./execution-kernel-runtime-publication-final-renderer.js");

const FINAL_CLOSEOUT_SCHEMA =
"sanskrit-runtime-publication-final-closeout.v1";

function freeze(v){
return Object.freeze(v);
}

function createRuntimePublicationFinalCloseout(input={}){

const rendered =
input.rendered ||
renderRuntimePublicationFinal({});

return freeze({

schemaVersion:FINAL_CLOSEOUT_SCHEMA,

closeout:freeze({
status:String(rendered.view?.status||"READY"),
sealed:true,
closed:true,
published:false
}),

source:freeze({
schemaVersion:rendered.schemaVersion
}),

capabilities:freeze({
execute:false,
publish:false,
rollback:false,
mutate:false,
canonicalWrite:false
}),

diagnostics:freeze({
closeoutReady:true,
sealed:true,
closed:true,
executionBlocked:true,
publicationBlocked:true,
canonicalWriteBlocked:true
})
});

}

function inspectRuntimePublicationFinalCloseout(
closeout={}
){

return freeze({
ready:Boolean(closeout.diagnostics?.closeoutReady),
sealed:Boolean(closeout.diagnostics?.sealed),
closed:Boolean(closeout.diagnostics?.closed),
executionBlocked:true,
publicationBlocked:true,
canonicalWriteBlocked:true
});

}

module.exports={
FINAL_CLOSEOUT_SCHEMA,
createRuntimePublicationFinalCloseout,
inspectRuntimePublicationFinalCloseout
};