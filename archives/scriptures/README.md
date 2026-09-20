# Aigaane Scripture Archive Vault

Purpose:
- Non-runtime archival scripture references
- Wikipedia-style encyclopedic nodes
- Canonical textual fallback material
- Historical reference registry

Important:
- These files are NOT active runtime tabs
- These files are NOT loaded into the Sanskrit semantic engine
- Runtime Sanskrit systems remain isolated under:
  /ui/tabs/sanskrit/
  /data/sanskrit/
  /api/

Architecture Policy:
- Runtime engine must remain lightweight
- Scripture archives remain static and independent
- Future scripture engines may selectively query archive content
- Archive content must never directly mutate canonical runtime state