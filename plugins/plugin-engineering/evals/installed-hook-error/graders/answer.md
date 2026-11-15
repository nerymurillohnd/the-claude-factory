---
type: llm
focus: last_message
---

PASS if the reply explains that a marketplace install copies only the plugin directory into the plugin cache, so the hook's `../../../shared/style-config.js` outside the plugin is missing in the installed copy, and tells the user to move that file inside the plugin and reference it from the plugin root (for example through `${CLAUDE_PLUGIN_ROOT}`).
FAIL if the reply blames a missing `npm install`, Node's module resolution or a hook timeout, or suggests keeping the parent-folder path.
Formatting, headings and wording do not decide the verdict.
