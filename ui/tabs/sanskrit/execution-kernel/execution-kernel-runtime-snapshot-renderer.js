"use strict";

function freeze(v){
return Object.freeze(v);
}

function escapeHtml(
v
){

return String(v)
.replace(/&/g,"&amp;")
.replace(/</g,"&lt;")
.replace(/>/g,"&gt;");
}

function renderExecutionRuntimeSnapshotPanel(
snapshot={}
){

return freeze({
title:
"Runtime Snapshot",

status:
String(
snapshot.state||
"READY"
),

readOnly:true,

body:
[
escapeHtml(
snapshot.executionMode
),

escapeHtml(
snapshot.pipelineStage
),

escapeHtml(
snapshot.inspectionHash
)

].join(
"\n"
)
});

}

module.exports={
renderExecutionRuntimeSnapshotPanel
};