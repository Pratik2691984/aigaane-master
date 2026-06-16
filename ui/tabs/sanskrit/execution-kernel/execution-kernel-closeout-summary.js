"use strict";

const {
createExecutionKernelCloseoutManifest
}=require(
"./execution-kernel-closeout-manifest.js"
);

const CLOSEOUT_SUMMARY_SCHEMA_VERSION =
"sanskrit-execution-kernel-closeout-summary.v1";

function freeze(v){
return Object.freeze(v);
}

function normalizeSummaryEntry(
entry,
index
){

const obj=
entry&&
typeof entry==="object";

return freeze({

index,

id:
obj
?
String(
entry.id||
`summary-${index}`
)
:
`summary-${index}`,

kind:
obj
?
String(
entry.kind||
"CLOSEOUT_SUMMARY_ENTRY"
)
:
"CLOSEOUT_SUMMARY_ENTRY",

included:true,

executed:false,

released:false,

surfaceProduced:false,

diagnostics:
freeze({

inspectionOnly:true,

summaryOnly:true,

executionBlocked:true,

releaseBlocked:true,

surfaceBlocked:true

})

});

}

function createExecutionKernelCloseoutSummary(
input={}
){

const manifest=
input.manifest||

createExecutionKernelCloseoutManifest(
{}
);

const entries=
(
input.entries||
[]
)
.map(
normalizeSummaryEntry
);

return freeze({

schemaVersion:
CLOSEOUT_SUMMARY_SCHEMA_VERSION,

kind:
"EXECUTION_KERNEL_CLOSEOUT_SUMMARY",

manifest:
freeze({

schemaVersion:
manifest.schemaVersion,

manifestCount:
Number(
manifest.summary?.manifestCount||
0
)

}),

entries:
freeze(entries),

summary:
freeze({

summaryCount:
entries.length,

closeoutComplete:false,

releaseComplete:false,

surfaceFormsProduced:false

}),

diagnostics:
freeze({

ready:true,

deterministic:true,

immutable:true,

inspectionOnly:true,

summaryOnly:true,

executionBlocked:true,

releaseBlocked:true,

surfaceBlocked:true,

replaySafe:true,

mutationFree:true

})

});

}

function buildExecutionKernelCloseoutSummary(
input={}
){

return createExecutionKernelCloseoutSummary({

manifest:
input.manifest,

entries:
input.entries

});

}

function getExecutionKernelCloseoutSummaryDiagnostics(
summary={}
){

const d=
summary.diagnostics||{};

const s=
summary.summary||{};

return freeze({

schemaVersion:
summary.schemaVersion,

ready:
Boolean(
d.ready
),

summaryCount:
Number(
s.summaryCount||
0
),

executionBlocked:
Boolean(
d.executionBlocked
),

releaseBlocked:
Boolean(
d.releaseBlocked
),

surfaceBlocked:
Boolean(
d.surfaceBlocked
),

replaySafe:
Boolean(
d.replaySafe
),

mutationFree:
Boolean(
d.mutationFree
)

});

}

module.exports={

CLOSEOUT_SUMMARY_SCHEMA_VERSION,

normalizeSummaryEntry,

createExecutionKernelCloseoutSummary,

buildExecutionKernelCloseoutSummary,

getExecutionKernelCloseoutSummaryDiagnostics

};