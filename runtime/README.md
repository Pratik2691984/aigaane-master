# Aigaane Runtime Layer

Purpose:
- Defines which modules are active in the live website runtime.
- Keeps the production web page lightweight.
- Prevents experimental/future modules from loading accidentally.
- Supports future manifest-driven scaling.

Current Active Runtime:
- Sanskrit engine only

Registry:
- `runtime/registry/active-tabs.json`

Active Runtime Rules:
- Only entries listed in `active-tabs.json` may be loaded by the live website.
- `ui/tabs/sanskrit/` is the only active runtime tab.
- `future-labs/ui-tabs/` is local-only reference storage.
- `archives/scriptures/` is archival/static reference storage.

Future-Labs Policy:
- Future labs are preserved for later development.
- Future labs are not loaded by `index.html`.
- Future labs are not part of active production runtime.
- A future module must be explicitly promoted into `active-tabs.json` before becoming active.

Safety Policy:
- Runtime must remain lightweight.
- Archive and lab modules must not mutate Sanskrit canonical data.
- Sanskrit canonical write paths remain guarded by backend validation and environment flags.