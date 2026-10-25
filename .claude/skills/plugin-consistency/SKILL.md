---
name: plugin-consistency
description: Use after any edit to a plugin, its README, a CHANGELOG or a manifest, to make them agree before it is done.
---

# Plugin consistency

A change to one file of a plugin is only done when every file that must agree with it agrees. Nobody reviews this repo between a push and the users who install from it, so an unrecorded change, a README that describes the old plugin or a Compatibility cell that differs from `docs/compatibility.md` reaches them as is. This skill runs on every such change, during plugin development and on any later edit, and finishes with everything consistent and the proof.

## Role

Act as a release engineer who owns the integrity of the marketplace: the plugin as built, its README, its changelogs, its manifests and the docs are one system. You trace what a change touches, you assume nothing agrees until you compared both sides, and you fix the cause in the same change.

## Rules

- Scope is the change: the files touched since `origin/main` plus the working tree, and every counterpart they must agree with. Widen to the whole repo only when Nery asks for a freshness check or before a release.
- Read the rules, do not restate them: `.claude/rules/user-docs.md` is the style source for plugin READMEs, and the `release-and-versioning` skill the source for versions and changelogs. This skill checks that they were followed.
- Fix the inconsistencies the change created, in the same change, at their root. Ask Nery before changing anything the change did not touch or cause.
- Never push or bump by hand, and leave commits to `github-workflow` and `release-and-versioning`. Bump with `bump-version.mjs`, as the `release-and-versioning` skill says.
- A passing script is not consistency: the scripts check that things exist, not that they are true. Read both sides of every pair.
- Check changed claims against live official sources, never against memory: commands, flags, UI paths and versions go stale.
- Mark what you could not verify as **unverified** and say what it affects.

## Gotchas

- `check-repo.mjs` verifies that the Compatibility table has a row for each component type the plugin ships. It does not read the cell text, so compare the cells with `docs/compatibility.md` yourself.
- A marketplace entry never carries `version`; `plugin.json` is the only source, and the README version badge reads it. A hardcoded version anywhere else is an inconsistency.
- No linter reads Markdown here, so a broken link or `#anchor` in a touched doc is found only by opening its target.
- User docs may mention the user's own `.claude/settings.json`; they must not mention this repo's `.claude/` or its internal process.

## Hand-offs

| When | Invoke with the Skill tool |
| :-- | :-- |
| The bump level, a CHANGELOG entry or the root CHANGELOG line is wrong or missing | `release-and-versioning`, during step 6 |
| A hook file or the README text about it changed, and `plugin-hooks-guidance` has not run on that hook since its last edit | `plugin-hooks-guidance`, to check the hook against its rules (step 4) |
| An `.mcp.json`, a manifest `mcpServers` or `userConfig` entry, or an agent's `tools` changed, and `plugin-mcp-guidance` has not run on it since its last edit | `plugin-mcp-guidance`, to check names, secrets and the README setup text (step 4) |
| A component was added or rewritten and `plugin-development` has not run on it | `plugin-development` |
| You were loaded alone (no skill invoked you) and the change goes to a PR | `github-workflow`, after step 8 |

A skill you invoke hands back to you when it ends: continue at your next step. When a row names the skill that invoked you, hand back to it instead of invoking it, and never re-invoke it.

## Workflow

Tick each step as you finish it. Step 4 needs the pairs from step 2, and step 7 only passes when step 6 leaves nothing open.

Progress:
- [ ] 1. **Change**: what was touched.
- [ ] 2. **Pairs**: which files must agree with it.
- [ ] 3. **Scripts**: the mechanical checks.
- [ ] 4. **Agreement**: both sides of every pair.
- [ ] 5. **Sources**: changed claims against live docs.
- [ ] 6. **Fix**: make the pairs agree.
- [ ] 7. **Prove**: rerun until clean.
- [ ] 8. **Report**: what was inconsistent, what changed, what is open.

## Step details

### 1. Change

Run `git status --short` and `git diff --name-only origin/main`, and for a file without a diff read the file itself. Classify each touched file as one of: plugin component, `plugin.json`, plugin README, plugin CHANGELOG, root CHANGELOG, `marketplace.json`, template or workflow. For a component or manifest change, read the diff, not only the file names: the pairs depend on what changed.

### 2. Pairs

For each touched file, list the files it must agree with, from this map:

| When you change | It must agree with |
| :-- | :-- |
| A component (skill, agent, hook, MCP or LSP server, `bin/`, output style) | The plugin README (feature list, usage examples named `/<plugin>:<skill>`, one Compatibility row per component type, prerequisites, every network call), `metadata.surfaces` and the "works in" badge, the plugin CHANGELOG `[Unreleased]`, the bump level, the minimum Claude Code version the README states, the evals and their entry in `evals-config.json` |
| `plugin.json` (name, displayName, description, keywords, `metadata.category`, version) | The `marketplace.json` entry (regenerated by `generators/marketplace.mjs`), the root README catalog, the README title and badges, the CHANGELOG version headings |
| A plugin README | The components as they now are, `docs/compatibility.md`, the root README catalog line, the required sections of the template |
| A plugin CHANGELOG | The diff (every user-visible change recorded in user language, breaking ones marked), the bump level, the root CHANGELOG line |
| The root CHANGELOG | The plugin CHANGELOG version and summary, in one line under the right date |
| A rename or removal in `marketplace.json` | The `renames` map, the root CHANGELOG line and the steps of the `plugin-renames-and-removals` skill |
| A template | The plugin READMEs built from it and the sections `check-repo.mjs` requires |

### 3. Scripts

Run these from the repository root, read the output, and fix what they report before going further:

- `node scripts/check-repo.mjs`
- `node scripts/generators/marketplace.mjs --check`
- `node scripts/generators/catalog.mjs --check`
- `node scripts/check-version-bump.mjs origin/main` (skip if `origin/main` does not exist; it reads committed changes only and fails while a bump is pending or uncommitted, so expect that failure until step 6 delivers and commits the bump)

### 4. Agreement

Open both sides of every pair from step 2 and compare them. Goal: one fact has one value everywhere, because when two files disagree one is wrong and the user cannot tell which. Check at least:

- Every component the diff adds, removes or renames appears, or disappears, in the README, with the right name and usage example.
- The README matches the plugin's behavior: prerequisites, network calls, options and defaults as the code has them.
- The CHANGELOG `[Unreleased]` covers each user-visible change in the diff and nothing that did not happen; the bump level matches the table in the `release-and-versioning` skill.
- The root CHANGELOG has one line for a plugin's creation, version bump, rename or removal, or a marketplace change, under the right date.
- Compatibility cells equal `docs/compatibility.md` word for word.
- Every relative link and `#anchor` in the touched docs points to a file and heading that exist.
- `grep -rnoE 'nerymurillohnd/[A-Za-z0-9._-]+|@[a-z-]*claude-factory'` over the touched docs returns only the expected source and suffix.

### 5. Sources

For each command, flag, UI path, minimum version or compatibility claim that the change added or edited, confirm it in a live source and keep the URL:

- Claude Code docs and changelog through the Claude Code Docs MCP: `/en/plugins/*` (install, marketplace-reference, manifest-reference, publish, host-marketplace, troubleshooting) and `/en/changelog`.
- Claude app and Cowork claims need a source on claude.com or support.claude.com, not the Claude Code docs: <https://claude.com/docs/plugins/platform-support>, <https://claude.com/docs/cowork/guide/plugins>, <https://support.claude.com/en/articles/13837440-use-plugins-in-claude>, <https://support.claude.com/en/articles/16761823>, <https://support.claude.com/en/articles/12138966-release-notes> and <https://claude.com/docs/cowork/changelog.md>.
- Tool versions: CI installs every tool at its latest release except TypeScript, so check only that `TYPESCRIPT_VERSION` is still the newest 6.x (`npm view typescript@6 version`), and the latest tags of `actions/checkout`, `actions/setup-node` and `astral-sh/setup-uv`.
- Compare UI labels with the docs' wording character by character.

In a whole-repo sweep, fetch every source above and read every Claude Code release since the previous sweep. List unreachable sources as not fetched.

### 6. Fix

Edit each file so the pair agrees, in one coherent pass per file, and reread the whole file afterwards. Record the change in `[Unreleased]`, unless it is limited to the plugin README. Where the right value is a decision (a wording Nery owns, a borderline claim), stop and ask. For the bump level, the bump itself, a changelog entry or the root line, invoke `release-and-versioning` (unless it invoked you) instead of deciding here.

### 7. Prove

Rerun step 3 and recompare the pairs from step 4 that you edited. Repeat steps 6 and 7 until the scripts pass and every pair agrees. Show the raw output of the scripts. Prove a check can fail when you rely on a new one: break the rule on purpose once and confirm it reports.

### 8. Report

State, in this order:

1. The change, in one line.
2. A table of inconsistencies found, one row each, e.g. `plugins/<plugin>/README.md:42 · README ↔ plugin.json · badge says 0.2.0, manifest 0.3.0 · plugin.json · fixed`: file:line · pair · what disagreed · source · fix applied or left open.
3. The files edited and the version bump, if any.
4. The raw script output from step 7.
5. What is left for Nery, and what you could not check, marked **unverified**.

When another skill invoked you, hand back to it; when you were loaded alone and the change goes to a PR, invoke `github-workflow` next.
