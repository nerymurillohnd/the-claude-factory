---
paths:
  - "plugins/*/README.md"
---

# Plugin README

`plugins/<plugin>/README.md` is the plugin's user guide, and the description Anthropic's plugin directory shows for it. Its template is `.claude/templates/plugin-readme-template.md`.

## Write it from the template

1. Never start from another plugin's README. A new plugin's README comes from `.claude/skills/building-plugins/scripts/scaffold-plugin.py`, which fills `<Display Name>` and every lowercase placeholder: `<plugin>`, `<owner>/<repo>` and its URL-encoded `<owner>%2F<repo>`, `<marketplace-name>`, `<description>`, `<category-badge>`, `<surfaces-badge>`, `<surfaces-text>`, and the `<app>` / `<code-only>` blocks it keeps or drops by surface.
2. Replace every other `<…>` (each starts with a capital letter) with the plugin's facts. Delete a section or row only when it cannot apply, and give the reason in your report.
3. Run `python3 .claude/skills/building-plugins/scripts/check-readme-placeholders.py <plugin>`: it fails while any template placeholder is left, in any case.
4. Run `node scripts/check-repo.mjs` for the sections, leftover `TODO` and `TEMPLATE` comments, the Works in badge and one Compatibility row per component type; `scripts/validators/plugin-versions-consistency.py` covers the Version badge. Neither reads the prose or the cells: compare those yourself.

## What it states

- What the plugin does for the user, and where it works: one Compatibility row per component type the plugin ships, each cell copied from `docs/compatibility.md`.
- Prerequisites: every tool, runtime, account or service, how to install each, and for every program its hooks or scripts invoke, a command that verifies it is present. Python is stated as 3.12 or later. A dependency a hook installs into `${CLAUDE_PLUGIN_DATA}` is listed here and under What this plugin runs and sends: what it downloads, from where, and where it writes.
- How to add and remove the marketplace, and install, update and uninstall the plugin, with `nerymurillohnd/the-claude-factory` and `@the-claude-factory`. Install includes `export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` for users without a GitHub SSH key, because installs from `/plugin` and plugin updates don't fall back to HTTPS. Update says that auto-update is off for this marketplace until the user turns it on. Uninstall says what `${CLAUDE_PLUGIN_DATA}` holds and that the last uninstall deletes it unless `--keep-data` is passed.
- Configuration: each `userConfig` option and how to set it (`--config KEY=VALUE` or `/plugin configure`).
- What this plugin runs and sends: every hook (event, matcher, what it does), MCP server, monitor and network destination, and the data each one receives. Hooks run with the user's full permissions outside the sandbox.
- Usage: the skill commands (`/<plugin>:<skill>`) and prompts that trigger the plugin's skills.
- Platform support: Linux and macOS; Windows only through Git Bash.
- For a plugin that is a mod or contains one, also what `building-mods` section 5 lists.
- At least 40 words outside code blocks: Anthropic's directory blocks a shorter README.

## Badges and version numbers

`plugin.json` is the only source of the plugin's name, version, description and category; the README follows it.

- The badges sit only in the hero, from shields.io in the flat style, in this order:
  - **Version** (`D97757`): a dynamic badge reading `$.version` from this plugin's `plugin.json` on `main`, linked to `./CHANGELOG.md`.
  - **Works in** (`2563EB`): `Claude Code · Claude app` or `Claude Code only`, matching `metadata.surfaces`; links to `#-compatibility`.
  - **Category** (`6B7280`): the title in `scripts/categories.json` of `metadata.category`; links to `../../README.md#-catalog`.
  - **Claude Code** (`D97757`, `logo=claude&logoColor=white`): the minimum Claude Code version, the same one Prerequisites states; links to `https://code.claude.com/docs/en/plugins/install`.
  - **License** (`22C55E`): links to the plugin's `LICENSE`.
- Write no plugin version in the README; the Version badge shows it. The only version numbers written by hand are the minimum Claude Code version (badge, Prerequisites, each version-gated feature as "v2.1.292+") and the minimum version of an external tool in Prerequisites.
- Set the minimum Claude Code version to the highest of the releases that added each feature the plugin uses or fixed each bug it would hit, from the release notes, and say in Prerequisites which feature sets it. Raise it only when a later release breaks the plugin.
- When the surfaces, the category or the minimum version change, change the badge and the text that states it together, then run `npm run generate`.

## Style

- Lead with the outcome and why to install, in an outcome-first TL;DR, then teach.
- `##` headings with one emoji each: 📋 prerequisites, 📥 install, 🔧 manage, 🧭 compatibility, 🩺 troubleshooting, ❓ FAQ, 🔄 update, 🗑️ uninstall, 📝 changelog, 📄 license.
- Tables for comparisons, the Prerequisites summary and options.
- Every command the user runs in a fenced code block, never inside a sentence, so GitHub gives it a copy button.
- `<details>` for each install method of a prerequisite (its `<summary>` names the method and platforms, its body holds only the command) and for FAQ entries; never to hide prose.

## Change the template

- Change `.claude/templates/plugin-readme-template.md` only to change what every plugin README gets, and bring every plugin README in line in the same change.
- Keep its placeholders. A new lowercase one needs `scaffold-plugin.py` to fill it; a new capitalized one needs at least two words, because `check-repo.mjs` refuses one-word placeholders such as `<Type>`, which code can hold.
- Scaffold a throwaway plugin in a scratch copy of the repository (`TCF_ROOT=<copy> scaffold-plugin.py …`) and read what it wrote.
