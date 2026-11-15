---
type: llm
focus: last_message
---

PASS if the reply says a cloud session does not load plugins that the repository turns on under `enabledPlugins` (or marketplaces under `extraKnownMarketplaces`) in `.claude/settings.json`, and gives as the fix turning lint-kit on for the user's claude.ai account, so it loads as a synced plugin in a new cloud session.
FAIL if the reply blames a broken install, the plugin's files or a missing `/plugin install`, tells the user to run `/plugin` in the cloud session, or gives no way to get lint-kit into cloud sessions.
Formatting, headings and wording do not decide the verdict.
