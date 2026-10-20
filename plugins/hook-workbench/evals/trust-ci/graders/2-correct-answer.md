---
type: llm
weight: 3
---

PASS if the reply says that yes, those hooks run, because a `claude -p` (or SDK) session never shows the workspace trust dialog and treats the folder as trusted; AND it gives at least one documented way to stop it: `--bare`, `--settings '{"disableAllHooks": true}'`, or `--setting-sources user`.
FAIL if it says the hooks don't run under -p, relies only on the trust dialog, or recommends setting disableAllHooks only in the user's own settings file as sufficient.
