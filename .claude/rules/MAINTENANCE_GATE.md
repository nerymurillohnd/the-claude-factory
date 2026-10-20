# Maintenance Gate

## After Changing a Plugin

- Read its README. Add what the change made missing and remove what it made obsolete.
- Summarize the change in its `CHANGELOG.md`. Each plugin changelog tells the full story of that plugin.
- The Version badge in a plugin README must stay dynamic, reading `version` from `plugin.json`. Never hardcode a version in it.

## Root Changelog

- The root `CHANGELOG.md` is a summary, never a copy of a plugin changelog.
