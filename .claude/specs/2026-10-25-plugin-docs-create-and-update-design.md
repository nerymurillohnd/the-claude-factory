# Plugin documentation: create and update

Status: proposal, awaiting Nery's approval. Nothing below is implemented except what "Already written" lists.

## 1. Goal

A plugin's user documentation (`README.md`, `CHANGELOG.md`, `LICENSE`, `NOTICE.txt`, and the plugin's line in the root `CHANGELOG.md`) is created complete when the plugin is born and stays true every time the plugin changes. Each file has one owner per moment, one template, written rules and its own single-purpose checks.

## 2. Who owns what

| Moment | Skill | Owns | Does not own |
| :-- | :-- | :-- | :-- |
| A plugin is created | `building-plugins` | The templates (`assets/`), the scaffold, the creation rules for README, LICENSE and NOTICE, the README checks | Version numbers, changelog notes, the root changelog line |
| An existing plugin changes | `plugin-docs-updates` (new) | Deciding which parts of README, LICENSE and NOTICE the change touches, rewriting them with `building-plugins`' template and rules, the docs-impact report, running the README, LICENSE and NOTICE checks | Version numbers, changelog notes, the root changelog line; the template itself |
| Any version, bump or release, the first one included | `release-and-versioning` | The `0.1.0` launch notes, every later `[Unreleased]` → `[X.Y.Z]` section, the root changelog line, the changelog checks | README, LICENSE, NOTICE |
| A rename, merge or removal | `plugin-renames-and-removals` | The `renames` entry, its own changelog lines | README edits of `<new>` or `<target>`: it runs `plugin-docs-updates` for them |
| A plugin that is or contains a mod | `building-mods` § 5 | What the README says about the mod (where it runs, what turns it off, organizations, what it reaches, permission prompt, diagnosis, options, "Tested with") | Every other README section |
| Marketplace docs | `maintaining-user-docs` | Root README outside generated blocks, `docs/`, SECURITY, SUPPORT, CONTRIBUTING, CODE_OF_CONDUCT, root LICENSE; `docs/compatibility.md`, the source the plugin Compatibility tables copy | Every file inside `plugins/<name>/`, the root CHANGELOG |

Order when one change needs several: `plugin-docs-updates` (README, LICENSE, NOTICE) → `building-mods` § 5 when a mod is involved → `release-and-versioning` (notes, bump, root line, release). A `README.md`-only change stops after `plugin-docs-updates`: no bump, no changelog entry, still a pull request.

## 3. Already written (uncommitted, in the working tree)

### 3.1 `building-plugins/assets/README-template.md`

The union of the frozen `.claude/templates/plugin/README.md` and the previous skill template. Sections, in this order, each a `##` heading with its emoji:

| # | Heading | Required | Content rule |
| --: | :-- | :-- | :-- |
| — | Hero (centered `<div>`) | Yes | `# <emoji> <displayName>`, `<p><strong><description></strong></p>`, the five badges, the nav line |
| — | Surfaces note + TL;DR | Yes | Claude Code-only note with its reason (only that profile); one-sentence TL;DR tip |
| 1 | ✨ Why use it | Yes | 3–5 bold-benefit bullets |
| 2 | 🧩 What's inside | Yes | One row per component: type, name, what it does, how it runs |
| 3 | ✅ Requirements | Yes | Claude Code minimum, surfaces, external tools with version constraints, accounts and keys, network; then "Install the tools" with per-OS commands, or deleted when there are none |
| 4 | 📥 Installation | Yes | Terminal (open), in-session, Claude app, desktop Code tab; HTTPS note; mod warning only for a mod |
| 5 | 🚀 Usage | Yes | 2–4 examples: what the user types, what they get |
| 6 | ⚙️ Configuration | When it has options | Option table; how to set them in session (**Configure options**, `/plugin configure`) and from the shell (`--config`); which are stored in the credential store |
| 7 | 🔍 What this plugin runs and sends | Yes | Five lines, never deleted, "None" when empty: Hooks, MCP servers, Monitors, Network, Files written |
| 8 | 🔄 Updating | Yes | Auto-update off by default for third-party marketplaces; update command and **Update now**; `/reload-plugins`; the `@synced` paragraph unless Claude Code-only; auto-update tip |
| 9 | 🗑️ Uninstalling | Yes | Command, `--scope project`, `--keep-data`, in-session and app paths, what stays behind |
| 10 | 🧭 Compatibility | Yes | "Works in" line; one row per shipped component type, each cell copied from `docs/compatibility.md`; legend |
| 11 | ❓ FAQ & Troubleshooting | Yes | Reload question, then plugin-specific ones |
| 12 | 🔗 Related | Yes | Catalog, plugin docs, sibling plugins, docs per component type |
| 13 | 🐞 Found a problem? | Yes | Bug, feature and question issue links with `plugin=<name>` |
| 14 | 📝 Changelog | Yes | Link to `CHANGELOG.md` |
| 15 | 📄 License | Yes | `[MIT](./LICENSE) © Nery Murillo`, NOTICE sentence when third-party material, trademark sentence when a third-party product is named |

These contain every name `REQUIRED_PLUGIN_SECTIONS` in `scripts/lib.mjs` lists, so the old repository check accepts the new shape (DEBT-011, section 9).

Verified against the live docs on 2026-10-25 (Claude Code v2.1.310): `/en/plugins/install` (`--marketplace` 2.1.292+ shell and 2.1.275+ session, `--scope project`, **Update now**, **Configure options**, auto-update defaults and the **Marketplaces** → **Enable auto-update** path, `@synced`), `/en/plugins/cli-reference` (`--keep-data`), `/en/desktop` (Code tab **+** → **Add plugins** / **Plugins** → **Browse plugins**), claude.com `/docs/plugins/overview` (**Customize** → **Plugins**, **Add** → **Add marketplace**, **Discover**, **Remove**), claude.com `/docs/plugins/platform-support` (matrix).

Removed from the old template because no current doc states them: the desktop path **Settings** → **Plugins** → **Discover**, and "v2.1.273+" for synced plugins. Changed: the HTTPS note now says only what `/en/plugins/install` says (`CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` skips the SSH check and always clones over HTTPS); the old claim that in-session installs and updates have no HTTPS fallback is not in the docs.

### 3.2 `building-plugins/assets/NOTICE-template.txt`

Placeholders `{{name}}`, `{{source}}`, `{{sourceUrl}}`, `{{sourceVersion}}`, `{{sourceLicense}}`, `{{derivedFile}}`, `{{sourceLicenseText}}`. Line 1 the plugin name, line 2 `Copyright (c) 2026 Nery Murillo. Licensed under the MIT License (see LICENSE).`, then one block per source (repository, version or commit, license, the derived files one per line), then the source's license text when its license requires it to travel with the copy. Matches the two published NOTICE files (`hook-engineering`, `svelte-development`). The scaffold does not write it.

### 3.3 `building-plugins/scripts/scaffold-plugin.py`

New required arguments `--emoji` and `--min-claude-code X.Y.Z`; `--description` must not be empty. It fills in the README: `{{name}}`, `{{displayName}}`, `{{description}}` (HTML-escaped), `{{emoji}}`, `{{surfacesBadge}}`, `{{surfacesText}}`, `{{surfacesNote}}` (Claude Code-only: the note with its TODO reason), `{{categoryBadge}}` (the category's title from `scripts/categories.json`, shields-escaped), `{{minClaudeCode}}`. Every TODO stays for the author. Surface values copy `SURFACE_PROFILES` of `scripts/lib.mjs`. Verified: ruff, ruff format, basedpyright clean; in a scratchpad copy two valid runs created both profiles and three invalid runs (unknown category, version `2.1`) wrote nothing.

## 4. `building-plugins` changes

### 4.1 New `references/plugin-docs.md`: how each file is created

It absorbs `references/readme-style.md` (deleted), the README part of `references/public-readiness.md` (that file keeps secrets, hygiene, users' machines, directory and its checklist, and points here), and the creation rules of `.claude/CLAUDE.md` → Plugin Documentation and Changelogs and of `.claude/rules/readme-md.md` → Plugin README. Contents:

1. **Files every plugin ships**: `.claude-plugin/plugin.json`, `README.md`, `CHANGELOG.md`, `LICENSE`; `NOTICE.txt` when the plugin bundles or derives from third-party material. `plugin.json` is the only source of name, version, description and category.
2. **README, section by section**: the table of 3.1 with, per section, what goes in, what never goes in, and the source to check each claim against.
3. **Badges**: the exact URL of each of the five, which file each value comes from (`plugin.json` version via the dynamic badge, `metadata.surfaces`, `scripts/categories.json` title, the Requirements minimum, `LICENSE`), and that none is typed by hand.
4. **Version numbers in a README**: never the plugin's own version. Claude Code versions are allowed in exactly three places: the minimum (badge and Requirements, the same value), the minimum of a version-gated feature (`v2.1.292+`), and a mod's "Tested with Claude Code X.Y.Z" in Compatibility. See decision D4.
5. **Compatibility**: one row per component type shipped; how to classify an MCP server (fixed `http`/`sse` URL → Remote row; `command` or `.mcpb` → Local row; any `${user_config.*}` → the `${user_config.*}` row, in addition); cells copied verbatim from `docs/compatibility.md`; Output styles and Themes as separate rows; Monitors and Workflows rows until `docs/compatibility.md` has them (decision D5).
6. **Style**: the current `readme-style.md` list, unchanged.
7. **CHANGELOG.md at creation**: created by the scaffold from the asset with today's `0.1.0` section; its launch notes are written by `release-and-versioning` step 1, never by this skill.
8. **LICENSE**: the MIT asset, copied as is; `plugin.json` `license` is `MIT`; the README License section and the License badge say the same.
9. **NOTICE.txt**: when it is needed (code, text or data copied, adapted or derived from a third party; a doc read is not derivation unless its text is reproduced), how to fill the asset, the README License sentence that points to it.

### 4.2 `SKILL.md`

- Scripts table: `scaffold-plugin.py` gets its new arguments; four new check scripts (section 6.1).
- Step 3: the scaffold call with `--emoji` and `--min-claude-code`.
- Step 4 "Make it public-ready": fill the README from the template by `references/plugin-docs.md`; create `NOTICE.txt` from its asset when 4.1 item 9 applies; run the four checks of 6.1 and show their raw output; hand the `0.1.0` notes and the root launch line to `release-and-versioning`.
- "What to hand back": adds the four checks' output.

### 4.3 `references/templates.md`

Asset table: the README row lists the new `{{…}}` placeholders and that the scaffold fills them all; new NOTICE row ("not scaffolded; copied by hand when needed"). "Create from them" step 2 points to `plugin-docs.md`.

### 4.4 `references/mcp-servers.md` fix

Step 7: the in-session path for `userConfig` is `/plugin` → **Installed** → **Configure options**; **Configure** is the `.mcpb` server's own settings (`/en/plugins/install`, plugin details menu).

## 5. `plugin-docs-updates` (new skill)

### 5.1 Frontmatter

`name: plugin-docs-updates`; `description: Use when an existing plugin of this marketplace changes in any way that its README, LICENSE or NOTICE must follow, such as a component added, removed or renamed, a changed manifest, option, hook, MCP server, surface, category, prerequisite or third-party source, and for a README-only edit. Not for creating a plugin, changelog notes or version bumps.` (plain values, no colon inside, per memory `skill-frontmatter-plain-values`).

### 5.2 Rules

1. The template and the creation rules are `building-plugins`' (`assets/README-template.md`, `references/plugin-docs.md`); this skill never keeps its own copy of either and never edits them. A template change is `building-plugins` work.
2. Change only what the plugin change touches, but leave every touched section in the template's current shape. A README still in an older shape is brought to the template as a whole the first time it is touched (decision D2).
3. Every claim written or rewritten is checked against the live docs and the release notes; the release notes win.
4. Changelogs, versions and the root line are never written here: step 7 hands them to `release-and-versioning`.
5. Every change inside `plugins/<name>/` goes through a pull request (`.claude/CLAUDE.md` → Change Control). A README-only change needs no bump and no changelog entry, and users who already installed keep the old README until the next version.

### 5.3 What each change touches (the core of the skill)

| The change | README sections to rewrite | Other files |
| :-- | :-- | :-- |
| Skill or command added, removed or renamed | What's inside rows; Usage examples; FAQ entries naming it; Compatibility row when the type appears or disappears | — |
| Agent added, removed or renamed | What's inside; Usage; Compatibility Agents row on appearance or disappearance | — |
| Hook added, removed or its matcher, event or script changed | What this plugin runs and sends → Hooks; Requirements → External tools when the script calls a new tool; Compatibility Hooks row | — |
| Hooks module (mod) added or changed | Everything `building-mods` § 5 lists; Compatibility Mods row and "Tested with"; Installation mod warning | — |
| MCP server added, removed, URL, command or transport changed | Runs and sends → MCP servers and Network; Requirements → Accounts and Network; Compatibility MCP rows by kind (4.1 item 5); Configuration when it uses options; `references/mcp-servers.md` step 7 items | — |
| `userConfig` option added, removed or changed | Configuration table and how to set it; Requirements → Accounts when it is a credential | — |
| LSP server | Requirements → External tools (the language server binary); Compatibility LSP row | — |
| Monitor | Runs and sends → Monitors; Compatibility Monitors row | — |
| Output style, theme, workflow | What's inside; Compatibility row | — |
| Top-level `bin/` | Surfaces must become Claude Code-only: the surface items of the next row | — |
| `metadata.surfaces` | Works in badge; surfaces note and reason; Installation app and Code-tab blocks; Updating `@synced` paragraph; Uninstalling app sentence; Compatibility "Works in" | Root README catalog (`node scripts/generators/catalog.mjs`, run alone) |
| `metadata.category` | Category badge | Catalog |
| `description` | Hero `<p>` | Catalog |
| `displayName` | H1; every bold UI label that names it (Installation, Updating, Uninstalling, Configuration) | Catalog |
| Feature that needs a newer Claude Code | Claude Code badge and Requirements minimum, same value; the feature's own `vX.Y.Z+` | — |
| New external tool, account, key or network call | Requirements; Install the tools; Runs and sends → Network | — |
| Files the plugin writes | Runs and sends → Files written; Uninstalling → what stays | — |
| Third-party material added, removed or updated | License section sentence | `NOTICE.txt` (create, update or delete) |
| License change | License section, License badge | `LICENSE`, `plugin.json` `license` (needs Nery) |
| README-only edit | The edited sections | — |

What a diff cannot show and is always asked: new tools a script calls, new network destinations, new files written, a newer Claude Code minimum, new third-party material.

### 5.4 Procedure

1. **Fix the change**: `git diff --name-status origin/main...HEAD -- plugins/<name>` and `git diff origin/main...HEAD -- plugins/<name>/.claude-plugin/plugin.json`.
2. **Run `docs-impact.py <name> origin/main`** and read every line; add the always-asked items of 5.3.
3. **Read the sources** for each section to rewrite: the official page of the component type, `docs/compatibility.md` for Compatibility cells, the release notes for minimum versions.
4. **Rewrite** each section by 5.3, in the template's shape and `plugin-docs.md`'s rules; for a mod, also `building-mods` § 5.
5. **LICENSE and NOTICE** when 5.3 says so.
6. **Run the checks** of 6.2 and show their raw output; fix and rerun until they pass.
7. **Hand off**: when anything other than `README.md` changed in the plugin, `release-and-versioning` writes the notes, bumps and adds the root line. A README-only change ends here.
8. **Report**: sections rewritten and why, checks output, what was not verified live.

## 6. Scripts: one script per check, each in the skill that runs it

Every script: Python with `#!/usr/bin/env python3`, executable, run by path from the repository root, standard library only, reads files only (no writes, no network; `docs-impact.py` runs `git diff`), `TCF_ROOT` for another copy, exit 0 pass, 1 findings, 2 wrong arguments, every finding printed with file and line. None calls `check-repo.mjs`, `gates.mjs`, `scripts/validators/` or an `npm run` script. Proven with by-path runs on real plugins and scratchpad fixtures, never committed tests (memory `no-tests-inside-skills`).

### 6.1 `building-plugins/scripts/` (new)

| Script | Fails when |
| :-- | :-- |
| `check-readme-sections.py <plugin>` | A required heading of 3.1 is missing or out of order; Configuration is missing while `plugin.json` has `userConfig`; a `{{…}}` placeholder or a `<!-- TODO`/`<!-- TEMPLATE` comment remains; a nav link's `#anchor` matches no heading (GitHub's anchor rule); Runs and sends lacks one of its five lines |
| `check-readme-badges.py <plugin>` | A badge is missing; Version is not the dynamic badge for this plugin's `plugin.json`; Works in differs from `metadata.surfaces`; Category is not the title of `metadata.category`; the Claude Code badge differs from the Requirements minimum; License does not link `./LICENSE` or names another SPDX id than `plugin.json`; a version string appears outside the places 4.1 item 4 allows |
| `check-readme-compatibility.py <plugin>` | A shipped component type has no row, or a row names a type not shipped (detection: `skills/**/SKILL.md` or root `SKILL.md`, `commands/*.md`, `agents/*.md`, `hooks/hooks.json` `hooks` or manifest `hooks`, `modules`, `.mcp.json`/`mcpServers` split by kind, `.lsp.json`/`lspServers`, `output-styles/*.md`, `themes/*.json`, `monitors/monitors.json`/`experimental.monitors`, `workflows/*.js`, top-level `bin/`); a cell differs from `docs/compatibility.md`; the Works in line differs from the surfaces profile; a Claude Code-only plugin lacks the note or its reason |
| `check-license-notice.py <plugin>` | `LICENSE` is missing or not MIT while `plugin.json` says MIT; its copyright holder differs from `plugin.json` `author.name`; `NOTICE.txt` exists and its first two lines are not the plugin name and its copyright and license; a derived file it lists does not exist; the README License section mentions NOTICE without the file, or the file exists without the sentence |

### 6.2 `plugin-docs-updates/scripts/`

| Script | What it does |
| :-- | :-- |
| `docs-impact.py <plugin> <base>` | Reads the diff of `plugins/<plugin>` against `<base>` and the two `plugin.json` versions, and prints one line per row of 5.3 that applies: the change, the README sections and files to rewrite. Exit 0 with the list; 1 only when the plugin or base cannot be read |
| The four checks of 6.1 | Run against the changed plugin (decision D1: copies or by path) |

### 6.3 `release-and-versioning/scripts/` (new) and copies in `plugin-renames-and-removals/scripts/`

| Script | Fails when |
| :-- | :-- |
| `check-changelog-order.py <plugin>` | `## [Unreleased]` is missing; the newest `## [X.Y.Z] - YYYY-MM-DD` is not the `plugin.json` version; sections are not strictly newest first; a section lacks its `[X.Y.Z]: …/releases/tag/<plugin>--vX.Y.Z` link; a link names a version with no section; `[Unreleased]` does not compare from the current tag |
| `check-root-changelog-line.py <plugin>` | A `- **<plugin>** X.Y.Z` line names a version the plugin changelog lacks, or appears twice; a version of the plugin changelog has no root line |

Release step 6 and renames step 10 gain both checks; `release-and-versioning` step 1 gains "write the `0.1.0` launch notes for a new plugin" explicitly.

## 7. Rules and pointers outside the skills

- `.claude/CLAUDE.md` → Plugin Documentation and Changelogs: replaced by five lines: required files and their checks live in `building-plugins`; creating a plugin's docs, `building-plugins`; changing them, `plugin-docs-updates`; changelogs and versions, `release-and-versioning`; a mod's README, `building-mods` § 5. Third-party material goes in `NOTICE.txt` stays as a rule line.
- `.claude/rules/readme-md.md` → Plugin README: the row and section become "create: `building-plugins`; change: `plugin-docs-updates`; a mod: also `building-mods`"; the rules move to `plugin-docs.md`.
- `.claude/rules/workflow.md` → Plugin creation: add "To change an existing plugin's README, LICENSE or NOTICE, load and use the `plugin-docs-updates` skill."
- `release-and-versioning`: step 6 item 9 (read README, CHANGELOG and plugin.json side by side) becomes "the README, LICENSE and NOTICE agree with the change: `plugin-docs-updates` ran on it".
- `plugin-renames-and-removals`: step 3 rename and merge, and step 10 item 10, run `plugin-docs-updates` on `<new>` or `<target>`.
- `maintaining-user-docs`: Scope "Out" row names `building-plugins` and `plugin-docs-updates` as owners of the plugin files; a change to `docs/compatibility.md` reports that every plugin Compatibility table must follow (run `check-readme-compatibility.py` on each).
- `building-mods` § 5: first line "the README is created by `building-plugins` and changed by `plugin-docs-updates`; this section adds the mod's items".

## 8. Decisions for Nery

- **D1. The four README, LICENSE and NOTICE checks, shared by two skills.** (a) One copy in `building-plugins/scripts/`, and `plugin-docs-updates` runs them by that path: no drift, one cross-skill path. (b) A copy in each skill, as `release-and-versioning` and `plugin-renames-and-removals` already do: each skill self-contained, two copies to keep identical. Recommendation: (a), because these checks enforce the template `building-plugins` owns.
- **D2. Published READMEs in the old shape.** (a) Bring each one to the new template the first time `plugin-docs-updates` touches it. (b) Move all 17 in one pull request now. (c) Touch only the edited sections. Recommendation: (a); (c) leaves the checks of 6.1 failing on old READMEs forever.
- **D3. The scaffold's new required `--emoji` and `--min-claude-code`.** Keep them required, or give `--min-claude-code` no default and make the README carry a TODO instead. Recommendation: required; a badge URL cannot hold a TODO comment.
- **D4. Version numbers in a README.** `.claude/CLAUDE.md` says "never write a version number, except a mod's Tested with", but the template, `readme-style.md` and every published README state Claude Code minimums (`v2.1.292+`, the badge). Proposed rule: never the plugin's own version; Claude Code versions only as the minimum, a feature's minimum and a mod's Tested with.
- **D5. Monitors and Workflows Compatibility rows.** `docs/compatibility.md` and claude.com platform-support list neither. (a) `maintaining-user-docs` adds them after verifying the Claude app behavior, and until then the check reports them as unverified without failing. (b) The template drops them and the check refuses them. Recommendation: (a).
- **D6. Where the changelog checks live.** In `release-and-versioning` (and a copy for renames), as section 6.3, or with the other docs checks. Recommendation: release, since you placed every version facet there.

## 9. Records

- ADR: the README section set (3.1), the create/update/version split (section 2), and D1–D6 as decided.
- DEBT-011: its open question on the section set is answered by 3.1; the template's headings satisfy `REQUIRED_PLUGIN_SECTIONS`, so the remaining work is D2 and deleting the frozen templates once nothing reads them.

## 10. Verification

- Each script: ruff, ruff format, basedpyright; by-path runs on at least three published plugins (one Claude Code-only, one with MCP, one with a mod) and on scratchpad fixtures that break each rule once; raw output shown.
- Templates: scaffold into a scratchpad copy for both surface profiles and read every file it wrote.
- No `check-repo.mjs`, gates, `scripts/validators/` or `npm run` script, unless Nery orders it.

## 11. Commits, in order

1. Templates and scaffold (3.1–3.3).
2. `building-plugins`: `plugin-docs.md`, SKILL.md, templates.md, public-readiness.md, the `mcp-servers.md` fix, the four checks.
3. `plugin-docs-updates`: SKILL.md and `docs-impact.py` (and the check copies if D1 is b).
4. `release-and-versioning` and `plugin-renames-and-removals`: the two changelog checks and their steps.
5. CLAUDE.md, `readme-md.md`, `workflow.md`, `maintaining-user-docs`, `building-mods` pointers.
6. ADR and DEBT-011.
