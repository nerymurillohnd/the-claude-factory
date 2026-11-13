# Plugin README

How to create and keep `plugins/<plugin>/README.md` from `assets/plugin-readme-template.md`. This procedure replaces the former path-scoped rule `.claude/rules/plugins/plugin-readme.md`.

## Contents

- [Produces](#produces)
- [When](#when)
- [Sources](#sources)
- [Placeholders](#placeholders)
- [Procedure](#procedure)
- [What it states](#what-it-states)
- [Badges and version numbers](#badges-and-version-numbers)
- [Rules](#rules)
- [Checks](#checks)
- [Change the template](#change-the-template)
- [Never](#never)

## Produces

`plugins/<plugin>/README.md`: the plugin's user guide, and the description Anthropic's plugin directory shows for it. GitHub renders it on the plugin's folder page.

## When

- When a plugin is created.
- In the same change as any change to the plugin's components, prerequisites, surfaces, configuration or minimum Claude Code version.
- When `docs/compatibility.md` changes: every plugin README's Compatibility cells follow it.

## Sources

Read 2026-11-10:

- GitHub Docs, "About the repository README file" and "Basic writing and formatting syntax" (`github/docs` at `f309096`): relative links resolve inside the repository; alerts (`> [!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`); content past 500 KiB is truncated.
- Claude Code docs `plugins/manifest-reference` (`description`, the directory listing fields) and `plugins/install`.
- claude.com `/docs/plugins/pre-submission-checklist` (checked 2026-10-25 by `building-plugins/references/public-readiness.md`): the directory blocks a README under 40 words, code blocks excluded.
- claude.com `/docs/plugins/platform-support`, through `docs/compatibility.md`.

## Placeholders

The template's values are `{{camelCase}}`; its instructions are HTML comments.

| Value | Meaning | True value from |
| :-- | :-- | :-- |
| `{{name}}` | Plugin name | `plugin.json` `name` |
| `{{displayName}}`, `{{description}}` | Display name and one-line description | `plugin.json` |
| `{{pluginEmoji}}` | Heading emoji | Chosen for the plugin |
| `{{owner}}`, `{{repo}}` | GitHub owner and repository of the marketplace (URL-encoded in the Version badge as `{{owner}}%2F{{repo}}`) | The marketplace repository |
| `{{marketplaceName}}`, `{{marketplaceDisplayName}}` | The marketplace's `name` (the `@` suffix) and its display name | `.claude-plugin/marketplace.json` |
| `{{marketplaceCatalogUrl}}` | Link to the catalog | This repository: `../../README.md#-catalog` |
| `{{surfacesBadge}}`, `{{surfacesText}}` | `Claude%20Code%20%C2%B7%20Claude` or `Claude%20Code%20only`, and the same in words | `plugin.json` `metadata.surfaces` |
| `{{categoryBadge}}` | The category title, URL-encoded | The category's heading in the root `README.md` catalog, for `metadata.category` (no categories file exists on this branch) |
| `{{minClaudeCodeVersion}}` | Minimum Claude Code version | Release notes (see Rules) |
| `{{license}}`, `{{copyrightHolders}}` | License and copyright holders | `plugin.json` `license` and the plugin's `LICENSE` (this repository: `MIT`, `Nery Murillo`) |
| `{{privacyPolicyUrl}}` | Privacy policy link | `plugin.json` `privacyPolicyUrl` |
| `{{troubleshootingUrl}}` | Troubleshooting guide | This repository: `../../docs/troubleshooting.md` |
| Every other value | The plugin's facts | The plugin's files, and the official docs of each tool |

Surface blocks: the content between `<!-- app:start -->` and `<!-- app:end -->` stays only when the plugin works in Claude; the content between `<!-- code-only:start -->` and `<!-- code-only:end -->` stays only when it works in Claude Code alone. The markers are deleted in both cases.

## Procedure

1. Start from the template, never from another plugin's README.
2. Replace every `{{value}}` with the plugin's facts. The template holds a slot for every case: delete a section, row or bullet only when it cannot apply to this plugin, and give the reason in your report.
3. Follow each instruction comment, then delete it. The finished README has no `{{` and no instruction comment.
4. Write each section to "What it states" below; then check the badges and version numbers against "Badges and version numbers".
5. Run the checks.

## What it states

- **Hero:** the plugin's purpose as a fuller overview for readers. `plugin.json`'s `description` is the compact line `/plugin` shows before install; the hero says the same thing at more length, with the benefits, and never contradicts it.
- **Compatibility:** one row per component type the plugin ships, each cell copied character for character from `docs/compatibility.md`. A plugin-specific caveat goes in the note under the table, never into a cell.
- **Platforms**, under Compatibility: "macOS and Linux", plus "Windows through Git Bash" only when every script and tool the plugin runs works there and Prerequisites gives a Windows install method for each. When only one part of the plugin needs something else on Windows, such as WSL2 for sandboxed eval runs, keep "macOS and Linux." and say it in the Compatibility note.
- **Prerequisites**, before Installation: every tool, runtime, account or service, with step-by-step install methods for each, and for every program its hooks or scripts invoke, a command that verifies it is present. Name the POSIX base tools macOS and Linux ship (`sh`, `sed`, `awk`, `grep`, `tr`, `find` and the like) once, without a check each. Copy each install command and package name from the tool's official docs or a package index such as repology.org, never from memory. Python is stated as 3.12 or later. A dependency a hook installs into the plugin's data directory (the `CLAUDE_PLUGIN_DATA` variable) is listed here and under What this plugin runs and sends: what it downloads, from where, and where it writes.
- **Installation, Updating and Uninstalling:** how to add and remove the marketplace, and install, update and uninstall the plugin, with `nerymurillohnd/the-claude-factory` and `@the-claude-factory`. Install includes `export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` for users without a GitHub SSH key, because installs from `/plugin` and plugin updates don't fall back to HTTPS. Update says that auto-update is off for this marketplace until the user turns it on. Uninstall says what the plugin's data directory (`CLAUDE_PLUGIN_DATA`) holds, or that the plugin keeps nothing there (search the plugin's hooks, scripts and modules for it before you write either), and that the last uninstall deletes it unless `--keep-data` is passed.
- **Configuration:** each `userConfig` option and how to set it, with `--config KEY=VALUE` and `/plugin configure` in fenced blocks. A plugin without options but with behavior the user's project decides uses the template's project-settings variant; otherwise the section and its link in the header go.
- **What this plugin runs and sends:** one line per hook, with its event and matcher copied from `hooks/hooks.json`, what it runs and what it does, and that it runs on its own with your access, without a permission prompt; then every MCP server, monitor and network destination, and the data each one receives. Keep it to the facts of this plugin, with no general explanation of hooks.
- **Usage:** the skill commands (`/<plugin>:<skill>`) and prompts that trigger the plugin's skills.
- **Mods:** for a plugin that is a mod or contains one, also what `building-mods` section 5 lists, in the template's slots. Build its Mod line from the module's code: every `$.fs`, `$.env`, `$.process` and `$.http` call, including an environment read such as `HOME`, so the README never claims the mod reads nothing it does read.
- **License line:** the license and `© {{copyrightHolders}}`, then the template's NOTICE sentence when the plugin has `NOTICE.txt`, and a non-affiliation and trademark sentence for each third-party product it names, always including Anthropic for _Claude_ and _Claude Code_.
- **Only the current state:** no "yet", "for now" or "until a newer release", no testing or checking dates, and no "we tested" or "built and tested on". Say what works today and what doesn't. Old names, merges, removed features and migration steps go in the CHANGELOG and the release notes.
- **Length:** at least 40 words outside code blocks, because Anthropic's directory blocks a shorter README.

## Badges and version numbers

`plugin.json` is the only source of the plugin's name, version and category; the README follows it.

- The badges sit only in the hero, from shields.io in the flat style, in this order:
  - **Version** (`D97757`): a dynamic badge reading `$.version` from this plugin's `plugin.json` on `main`, linked to `./CHANGELOG.md`. Exactly one, on line 7 of the finished README (the line after the hero's description).
  - **Works in** (`2563EB`): `Claude Code · Claude` or `Claude Code only`, matching `metadata.surfaces`; links to `#-compatibility`.
  - **Category** (`6B7280`): the category's title as the root `README.md` catalog heads it, for `metadata.category`; links to `../../README.md#-catalog`.
  - **Claude Code** (`D97757`, `logo=claude&logoColor=white`): the minimum Claude Code version, the same one Prerequisites states; links to `https://code.claude.com/docs/en/plugins/install`.
  - **License** (`22C55E`): links to the plugin's `LICENSE`.
- Write no plugin version in the README; the Version badge shows it. The only version numbers written by hand are the minimum Claude Code version (badge, Prerequisites, each version-gated feature as "v2.1.292+") and the minimum version of an external tool in Prerequisites.
- Set the minimum Claude Code version to the highest of the releases that added each feature the plugin uses or fixed each bug it would hit, from the release notes, and record that feature in the CHANGELOG entry that sets the minimum. The README states the minimum, never why: Prerequisites says what the user needs, not the reasoning. When the component behind the minimum is removed, recompute it from the release notes. Raise it only when a later release breaks the plugin.
- When the surfaces, the category or the minimum version change, change the badge and the text that states it together, then regenerate the catalog.

## Rules

Official (GitHub, Anthropic):

- Relative links for files inside the repository; absolute `https://` links outside it.
- GitHub alerts only "when they are crucial for user success", "one or two per article", never consecutive and never nested in other elements (GitHub Docs, Basic writing and formatting syntax → Alerts, `github/docs` `main` read 2026-11-10).
- At least 40 words outside code blocks (Anthropic's directory).

This repository:

- English, for users: second person, active voice, present tense, short sentences. Never mention this repository's maintenance, `.claude/`, scripts, CI internals or release mechanics; a user's own `.claude/settings.json` may be mentioned.
- Name the two surfaces **Claude Code** (the terminal, the IDE extensions, the desktop app's **Code** tab and cloud sessions) and **Claude** (web, desktop and mobile), never "the Claude app", "chat conversation" or "Cowork" as a surface name. Where a component loads in only some Claude conversations, say "where Claude can run tasks".
- Check every command, flag, UI path and minimum version against the installed binary, then the release notes, then the docs, before you write it.
- Lead with the outcome and why to install, in an outcome-first TL;DR, then teach.
- `##` headings with one emoji each: 📋 prerequisites, 📥 install, ⚙️ configuration, 🔍 what it runs and sends, 🔄 update, 🗑️ uninstall, 🧭 compatibility, 🚧 limitations, ❓ FAQ, 🔗 related, 🙏 credits, 📝 changelog, 📄 license.
- Tables for comparisons, the Prerequisites summary and options.
- Name only this plugin on an install or command line; to point at another plugin, give its README link or a `/plugin` → **Installed** path. A table of example commands the plugin acts on, such as the commands a hook blocks, describes behavior and stays a table.
- Every command the user runs in a fenced code block, never inside a sentence or a table cell, so GitHub gives it a copy button. The Check column of the Prerequisites table is the one exception.
- `<details>` for each install method of a prerequisite (its `<summary>` names the method and platforms, its body holds only the command) and for FAQ entries, all closed; never to hide prose.
- **Bold** for UI labels exactly as the app shows them; _italics_ for emphasis or terms.

## Checks

- `claude plugin validate --strict plugins/<plugin>` and `claude plugin details plugins/<plugin>`: the plugin loads with the README beside it.
- By hand, since no script checks them yet (DEBT-001): the sections, leftover `TODO` and `TEMPLATE` comments, the Works in badge, one Compatibility row per component type with its cells copied from `docs/compatibility.md`, the Platforms line, the Version badge, and no other plugin's name on a command line.
- `grep -n '{{\|<!--' plugins/<plugin>/README.md` returns nothing.
- No script reads the prose: compare it with the plugin's files yourself, and open every relative link and `#anchor` you wrote.

## Change the template

- Change `assets/plugin-readme-template.md` only to change what every plugin README gets, and bring every plugin README in line in the same change.
- Keep its Compatibility table identical to `docs/compatibility.md`.
- A new value is `{{camelCase}}` and gets a row in Placeholders above.
- Render the template for a throwaway plugin in a scratch copy of the repository and read the result.

## Never

- Never copy another plugin's README as a start.
- Never invent a command, a flag, a minimum version, a contact or a URL.
- Never leave a `{{value}}`, an instruction comment or a surface marker in the finished README.
