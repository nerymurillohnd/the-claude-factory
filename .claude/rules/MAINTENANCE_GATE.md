# Maintenance Gate

- Keep the documentation current, consistent and in sync with the code.
- Every plugin carries a `README.md`, a `CHANGELOG.md` and a `LICENSE`.
- Read the templates in `.claude/templates/` before writing any of them.
- Never hand-edit the generated blocks of the root `README.md` (`<!-- catalog:* -->`, `<!-- plugin-count:* -->`). Run `node .github/scripts/catalog.mjs`.

## After Changing a Plugin

- Read its README. Add what the change made missing and remove what it made obsolete.
- Summarize the change in its `CHANGELOG.md`. Each plugin changelog tells the full story of that plugin.
- The Version badge in a plugin README must stay dynamic, reading `version` from `plugin.json`. Never hardcode a version in it.

## Root Changelog

- The root `CHANGELOG.md` is a summary, never a copy of a plugin changelog.
- Add a line when a plugin launches, when its version is bumped or when a substantial change lands.
- Write each line as `- **plugin** x.y.z — what changed, in a few words`, under the day's heading.
