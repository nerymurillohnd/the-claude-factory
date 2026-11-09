---
paths:
  - "plugins/*/README.md"
---

# Plugin README

`plugins/<plugin>/README.md` is the plugin's user guide, and the description Anthropic's plugin directory shows for it. Its template is `.claude/templates/plugin-readme-template.md`.

## Write it from the template

1. Never start from another plugin's README. A new plugin's README comes from `.claude/skills/building-plugins/scripts/scaffold-plugin.py`, which fills `<Display Name>` and every lowercase placeholder: `<plugin>`, `<owner>/<repo>` and its URL-encoded `<owner>%2F<repo>`, `<marketplace-name>`, `<description>`, `<category-badge>`, `<surfaces-badge>`, `<surfaces-text>`, and the `<app>` / `<code-only>` blocks it keeps or drops by surface.
2. Replace every other `<…>` (each starts with a capital letter) with the plugin's facts. The template holds a slot for every case; delete a section, row or bullet only when it cannot apply to this plugin, and give the reason in your report.
3. Run `python3 .claude/skills/building-plugins/scripts/check-readme-placeholders.py <plugin>`: it fails while any template placeholder is left, in any case.
4. Run `node scripts/check-repo.mjs` for the sections, leftover `TODO` and `TEMPLATE` comments, the Works in badge, one Compatibility row per component type with its cells copied from `docs/compatibility.md`, and the Platforms line; `scripts/validators/plugin-versions-consistency.py` covers the Version badge. Neither reads the rest of the prose: compare it yourself.

## What it states

- The hero: the plugin's purpose as a fuller overview for readers. `plugin.json`'s `description` is the compact line `/plugin` shows before install; the hero says the same thing at more length, with the benefits, and never contradicts it.
- Where it works: one Compatibility row per component type the plugin ships, each cell copied character for character from `docs/compatibility.md`. A plugin-specific caveat goes in a note under the table, never into a cell.
- Platforms, under Compatibility: "macOS and Linux", plus "Windows through Git Bash" only when every script and tool the plugin runs works there and Prerequisites gives a Windows install method for each. When only one part of the plugin needs something else on Windows, such as WSL2 for sandboxed eval runs, keep "macOS and Linux." and say it in the Compatibility note.
- Prerequisites, before Installation: every tool, runtime, account or service, with step-by-step install methods for each, and for every program its hooks or scripts invoke, a command that verifies it is present. Name the POSIX base tools macOS and Linux ship (`sh`, `sed`, `awk`, `grep`, `tr`, `find` and the like) once, without a check each. Copy each install command and package name from the tool's official docs or a package index such as repology.org, never from memory. Python is stated as 3.12 or later. A dependency a hook installs into `${CLAUDE_PLUGIN_DATA}` is listed here and under What this plugin runs and sends: what it downloads, from where, and where it writes.
- How to add and remove the marketplace, and install, update and uninstall the plugin, with `nerymurillohnd/the-claude-factory` and `@the-claude-factory`. Install includes `export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` for users without a GitHub SSH key, because installs from `/plugin` and plugin updates don't fall back to HTTPS. Update says that auto-update is off for this marketplace until the user turns it on. Uninstall says what `${CLAUDE_PLUGIN_DATA}` holds, or that the plugin keeps nothing there (search the plugin's hooks, scripts and modules for it before you write either), and that the last uninstall deletes it unless `--keep-data` is passed.
- Configuration: each `userConfig` option and how to set it, with `--config KEY=VALUE` and `/plugin configure` in fenced blocks. A plugin without options but with behavior the user's project decides uses the template's project-settings variant; otherwise the section and its link go.
- What this plugin runs and sends: one line per hook, with its event and matcher copied from `hooks/hooks.json`, what it runs and what it does, and that it runs on its own with your access, without a permission prompt; then every MCP server, monitor and network destination, and the data each one receives. Keep it to the facts of this plugin, with no general explanation of hooks.
- Usage: the skill commands (`/<plugin>:<skill>`) and prompts that trigger the plugin's skills.
- For a plugin that is a mod or contains one, also what `building-mods` section 5 lists, in the template's slots. Build its Mod line from the module's code: every `$.fs`, `$.env`, `$.process` and `$.http` call, including an environment read such as `HOME`, so the README never claims the mod reads nothing it does read.
- The License line: `© Nery Murillo.`, then the template's NOTICE sentence when the plugin has `NOTICE.txt`, and a non-affiliation and trademark sentence for each third-party product it names, always including Anthropic for _Claude_ and _Claude Code_.
- Only the current state: no "yet", "for now" or "until a newer release", no testing or checking dates, and no "we tested" or "built and tested on". Say what works today and what doesn't.
- At least 40 words outside code blocks: Anthropic's directory blocks a shorter README.

## Badges and version numbers

`plugin.json` is the only source of the plugin's name, version and category; the README follows it.

- The badges sit only in the hero, from shields.io in the flat style, in this order:
  - **Version** (`D97757`): a dynamic badge reading `$.version` from this plugin's `plugin.json` on `main`, linked to `./CHANGELOG.md`.
  - **Works in** (`2563EB`): `Claude Code · Claude` or `Claude Code only`, matching `metadata.surfaces`; links to `#-compatibility`.
  - **Category** (`6B7280`): the title in `scripts/categories.json` of `metadata.category`; links to `../../README.md#-catalog`.
  - **Claude Code** (`D97757`, `logo=claude&logoColor=white`): the minimum Claude Code version, the same one Prerequisites states; links to `https://code.claude.com/docs/en/plugins/install`.
  - **License** (`22C55E`): links to the plugin's `LICENSE`.
- Write no plugin version in the README; the Version badge shows it. The only version numbers written by hand are the minimum Claude Code version (badge, Prerequisites, each version-gated feature as "v2.1.292+") and the minimum version of an external tool in Prerequisites.
- Set the minimum Claude Code version to the highest of the releases that added each feature the plugin uses or fixed each bug it would hit, from the release notes, and record that feature in the CHANGELOG entry that sets the minimum. The README states the minimum, never why: Prerequisites says what the user needs, not the reasoning. When the component behind the minimum is removed, recompute it from the release notes. Raise it only when a later release breaks the plugin.
- When the surfaces, the category or the minimum version change, change the badge and the text that states it together, then run `npm run generate`.

## Style

- Lead with the outcome and why to install, in an outcome-first TL;DR, then teach.
- `##` headings with one emoji each: 📋 prerequisites, 📥 install, ⚙️ configuration, 🔍 what it runs and sends, 🔄 update, 🗑️ uninstall, 🧭 compatibility, 🚧 limitations, ❓ FAQ, 🔗 related, 🙏 credits, 📝 changelog, 📄 license.
- Tables for comparisons, the Prerequisites summary and options.
- Name only this plugin on an install or command line (`plugin-names-consistency.py` refuses another plugin's name or a `<name>@<marketplace>` stand-in); to point at another plugin, give its README link or a `/plugin` → **Installed** path. A table of example commands the plugin acts on, such as the commands a hook blocks, describes behavior and stays a table.
- Every command the user runs in a fenced code block, never inside a sentence or a table cell, so GitHub gives it a copy button. The Check column of the Prerequisites table is the one exception.
- `<details>` for each install method of a prerequisite (its `<summary>` names the method and platforms, its body holds only the command) and for FAQ entries, all closed; never to hide prose.

## Change the template

- Change `.claude/templates/plugin-readme-template.md` only to change what every plugin README gets, and bring every plugin README in line in the same change.
- Keep its Compatibility table identical to `docs/compatibility.md`; `check-repo.mjs` compares them.
- Keep its placeholders. A new lowercase one needs `scaffold-plugin.py` to fill it; a new capitalized one needs at least two words, because `check-repo.mjs` refuses one-word placeholders such as `<Type>`, which code can hold.
- Scaffold a throwaway plugin in a scratch copy of the repository (`TCF_ROOT=<copy> scaffold-plugin.py …`) and read what it wrote.
