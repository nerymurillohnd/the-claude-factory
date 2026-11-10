---
name: docs-maintenance
description: Operating guide for maintaining The Claude Factory's documentation, the reference and guidelines for every file that documents the project or informs its users, such as each plugin's README.md and CHANGELOG.md, the root README.md, LICENSE and CODE_OF_CONDUCT.md, each kept by its own specialized subagent. Use before and while creating, editing, reviewing, auditing or reading any of these documents.
---

# Docs maintenance

You are the maintainer who keeps this repository's documentation true, complete and consistent. You do not write the documents yourself: each one has a specialized subagent that holds its template, its rules and its instructions checked against the official sources. Your work is to recognize which documents a change affects, launch the right subagents in the right order, give each one everything it needs, check what it did, and report to the owner.

This matters because everything here reaches third parties. A plugin's README tells a stranger what runs on their machine; a changelog tells them what an update breaks; a license and a notice carry legal terms. A document written outside its subagent skips the template and the checks that keep all of them reproducible, so route every document through its subagent, even for a one-line fix.

## The subagents

They live in `.claude/agents/docs-maintainers/`. Launch them with the Agent tool, by `subagent_type`.

| Subagent | Files it owns | Values only the owner can give |
| :-- | :-- | :-- |
| `changelog-writer` | `plugins/<plugin>/CHANGELOG.md`, root `CHANGELOG.md` | Release date; marketplace display name |
| `plugin-readme-writer` | `plugins/<plugin>/README.md` | Plugin emoji, surfaces, minimum Claude Code version when no changelog entry sets it |
| `marketplace-readme-writer` | Root `README.md` and its plugin catalog | Marketplace display name and emoji |
| `license-writer` | Root `LICENSE`, `plugins/<plugin>/LICENSE` | Copyright year and holders |
| `notice-writer` | `plugins/<plugin>/NOTICE.txt` | Source, exact version and license of each third-party work, when the files do not show them |
| `code-of-conduct-writer` | `CODE_OF_CONDUCT.md` | Private reporting channel; enforcement policy, if not the Covenant's |
| `contributing-writer` | `CONTRIBUTING.md` | How the owner triages issues, when it changes |
| `security-writer` | `SECURITY.md` | Reporting channel; supported versions policy; response targets and disclosure practice, if any |
| `support-writer` | `SUPPORT.md` | Support channels and any response expectations |
| `privacy-writer` | `PRIVACY.md` | Effective date; marketplace display name; maintainer; what the author collects |

What each subagent knows:

- Its own file, template, rules, workflow and checklist. It does not see this conversation, this skill or the other subagents: everything it needs about the task comes from the prompt you write.
- It writes, edits, audits and reviews only its own files, and names in its final message any change another file needs.
- It runs on Sonnet, in auto mode, with project memory in `.claude/agent-memory/<subagent>/`.
- It ends with a message in a fixed form: **Result** (or **Findings** for an audit), **Files**, **Missing values**, **Changes other files need**.

## What stays with you

These are not documents and no subagent touches them:

- `plugins/<plugin>/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`: versions, names, descriptions, catalog entries. Change them yourself, before you launch the subagents that read them.
- The decisions: which version a release gets, which change type and whether it is breaking, what changed for the user and why.
- The owner's values in the table above. Ask the owner for any that are missing; never invent one and never let a subagent guess it.
- Commits, pull requests and releases, under the rules in `.claude/CLAUDE.md`.

## How to work

1. **Read the state.** Run `git status` and `git diff` (against the upstream branch, or `HEAD` when there is none). List which root documents exist (`ls *.md LICENSE`) and, for each plugin involved, which of `README.md`, `CHANGELOG.md`, `LICENSE` and `NOTICE.txt` exist.
2. **Name the events.** Match what happened to the events below. One change often triggers several, for example a new plugin that bundles third-party code and calls a remote service.
3. **Settle your part first.** Make the `plugin.json` and `marketplace.json` changes, decide versions and change types, and get the owner's missing values.
4. **Launch the stages in order.** Within a stage, launch every subagent in one message so they run in parallel. Wait for all of a stage's results before the next stage starts: later stages read what earlier ones wrote.
5. **Check each result** as described in "Check what came back".
6. **Report to the owner**: what changed in which file, the missing values, the changes still waiting, and the next step (commit, pull request, release).

Two rules keep parallel work safe:

- Never run two subagents on the same file at the same time. Every file has one owner, so this only happens if you launch the same subagent twice for one file.
- Subagents start in the background. Wait for their completion notices instead of doing their work in the meantime.

## Commands you run

The subagents check their own facts. These commands are yours, because they check the files you own or the state the subagents read. Run them from the repository root and read the exit code (`0` passes, `1` fails), not the symbols: without a terminal, ✔ ⚠ ✘ print as √ ‼ ×.

| Command | When | What it tells you |
| :-- | :-- | :-- |
| `claude --version` and `claude plugin <subcommand> --help` | Before you rely on a flag below | The installed CLI is the authority on which flags exist |
| `claude plugin validate plugins/<plugin> --strict` | After you change a plugin's `plugin.json`, before you launch any subagent that reads it | The manifest the subagents will copy values from is valid |
| `claude plugin validate . --strict` | After you change `marketplace.json` | The catalog is valid, and each entry's version agrees with its `plugin.json` |
| `claude plugin validate plugins/<plugin> --strict --profile directory` | After a plugin's README is written or rewritten | Exit `1` when the README is missing or too short for Anthropic's directory. Also read the `Advice` lines: one appears when the README has no install-from-marketplace line, and it never changes the exit code |
| `claude --plugin-dir plugins/<plugin> plugin details <name>` | Before you brief `plugin-readme-writer` on a new or changed plugin | The plugin's real component inventory, to check the brief against. A mod's hooks module shows as `Hooks (0)` |
| `claude plugin tag plugins/<plugin> --dry-run` | Before you brief `changelog-writer` on a release | The version `plugin.json` and the marketplace entry agree on, and the tag name `<name>--v<version>` the changelog links use. It creates nothing |

Three things these commands do not do:

- A marketplace run (`validate .`) does not open each plugin's skills, agents, hooks or servers. Validate each changed plugin directory too.
- `validate` accepts a `renames` key that is still a listed plugin. Check it yourself after a rename or a retirement.
- Creating the tag (`claude plugin tag plugins/<plugin>`) and pushing it (`--push`) are the release itself. Run them only when the owner authorizes the release; the tag needs a clean working tree, so commit the documents first.

## Events and the subagents they need

"Stage 1, 2, 3" means order. Subagents named in the same stage run in parallel.

### Repository foundation

The repository's own documents are created or rebuilt, for example when the marketplace is set up or restructured.

1. Stage 1: `license-writer` (root `LICENSE`), `code-of-conduct-writer`, `security-writer`, `privacy-writer`.
2. Stage 2: `contributing-writer` and `support-writer`. They link to the code of conduct and the security policy, so those must exist first.
3. Stage 3: `marketplace-readme-writer`. The front page links to every policy and lists the catalog.
4. Stage 4: `changelog-writer` for the root `CHANGELOG.md`. It takes the marketplace display name from the root README's title.

Gather all owner values before stage 1: the copyright line, the reporting channels, the security policy, the effective date of the privacy policy, the marketplace display name.

### New plugin

A directory appears under `plugins/` with its `plugin.json`, and is listed in `marketplace.json`.

Before stage 1, run `claude plugin validate plugins/<plugin> --strict` and `claude plugin validate . --strict`, and fix what they report. After stage 2, run `claude plugin validate plugins/<plugin> --strict --profile directory`.

1. Stage 1: `license-writer` (the plugin's `LICENSE`), `changelog-writer` (the plugin's `CHANGELOG.md`), and `notice-writer` only if the plugin contains third-party material.
2. Stage 2: `plugin-readme-writer`. The README states the license and links the changelog.
3. Stage 3: `marketplace-readme-writer` adds the plugin to the catalog, `changelog-writer` records the launch in the root `CHANGELOG.md` once the plugin's first version is dated, and `privacy-writer` adds the plugin to `PRIVACY.md`, the single policy that covers every plugin.

A plugin that is not released yet gets its changelog with "Initial release." under `## [Unreleased]` and no dated version. The root changelog entry waits for the release.

### A released plugin changes

Its components, commands, configuration, prerequisites or behavior change, before a version bump.

1. Stage 1: `changelog-writer`: record each change under `## [Unreleased]`. Give it each change in user terms, its type (Added, Changed, Deprecated, Removed, Fixed or Security) and whether it is breaking.
2. Stage 2: `plugin-readme-writer`, if the change alters anything the README describes. Run `claude --plugin-dir plugins/<plugin> plugin details <name>` first when components were added or removed, so your brief matches the real inventory.
3. Add the events "Third-party material changes" or "Data handling changes" when they apply.

A change limited to formatting, tests or internal refactoring with no effect for users needs no changelog entry.

### A plugin gets a new version

You have set the new `version` in `plugin.json`, and the release (tag and GitHub Release) happens now.

Before stage 1, run `claude plugin tag plugins/<plugin> --dry-run`: it must exit `0` and show the version you set. A mismatch with the marketplace entry is yours to fix first.

1. Stage 1: `changelog-writer`: turn `## [Unreleased]` into the version's section. Pass the version and the release date: the UTC day the tag and GitHub Release are created, never the day the bump was prepared.
2. Stage 2: `plugin-readme-writer`, to bring version-dependent content in line (badges, minimum versions, update notes).
3. Stage 3: `changelog-writer` records the release in the root `CHANGELOG.md`, and `marketplace-readme-writer` updates the catalog row if it shows the version.

If `## [Unreleased]` is empty, the release has nothing to record: stop and ask the owner what the version changes.

Once the documents are committed, the owner decides when to create and push the tag and the GitHub Release. Do it the same UTC day as the date written in the changelog.

### A plugin is renamed

A rename makes it a different plugin to every existing install, so users must install the new name.

1. You: update `plugin.json` and the `marketplace.json` entry, then run `claude plugin validate plugins/<new-name> --strict` and `claude plugin validate . --strict`. Check that the old name is not still listed as a plugin.
2. Stage 1: `changelog-writer` records the rename as a breaking change in the plugin's changelog, and `plugin-readme-writer` updates every command and name in the README.
3. Stage 2: `marketplace-readme-writer` updates the catalog, and `changelog-writer` records the rename in the root `CHANGELOG.md`.

### A plugin is retired

1. You: remove its entry from `marketplace.json`, as the owner decides, then run `claude plugin validate . --strict`.
2. Stage 1: `marketplace-readme-writer` removes it from the catalog, `changelog-writer` records the retirement in the root `CHANGELOG.md`, and `privacy-writer` removes what the policy says about it.
3. Leave the plugin's own directory and documents to the owner's decision: retiring it from the catalog does not delete them.

### Third-party material changes

Material from another author is added to a plugin, updated to another version or removed.

1. Stage 1: `notice-writer` creates or updates the plugin's `NOTICE.txt`. Pass the source, its exact version and its license for each work. A source with no license cannot be redistributed: tell the owner before anything is written.
2. Stage 2: `plugin-readme-writer` updates the credits and license notes.

### Data handling changes

A plugin starts or stops calling a remote service, collecting data or keeping files on the user's machine.

1. Stage 1: `privacy-writer` updates `PRIVACY.md`, and `plugin-readme-writer` updates the plugin's "What this plugin runs and sends" section. Both read the plugin's files; tell them what changed.

### The owner changes a policy

Send only the owner of the affected document, with the new value:

| Change | Subagent |
| :-- | :-- |
| Copyright year or holders | `license-writer`, then `notice-writer` for any notice that repeats the holder |
| Conduct reporting channel or enforcement policy | `code-of-conduct-writer` |
| Vulnerability reporting channel, supported versions or response targets | `security-writer` |
| Issue forms or how users report problems | `contributing-writer`, then `support-writer` |
| Support channels or guides | `support-writer` |
| How the marketplace is added or its plugins installed | `marketplace-readme-writer` |

Then check the root README: if it states the changed policy, add `marketplace-readme-writer`.

### Audit or review

Someone asks whether the documentation is correct, or you suspect drift.

1. Launch the owner of each document in scope with the audit scenario and an explicit "report only, do not fix". For a whole plugin, that is `plugin-readme-writer`, `changelog-writer`, `license-writer` and `notice-writer` (if the plugin has a notice). For the whole repository, all ten, in parallel: an audit writes nothing.
2. Show the owner the findings, grouped by file.
3. Fix what the owner approves: launch the same subagents again with the findings to fix and "fix these findings".

### A small fix

A typo, a broken link, an outdated sentence. Send the document's owner with the exact fix. A plugin's documentation fix needs no version bump and no changelog entry when it changes nothing about how the plugin works.

### A version is withdrawn

`changelog-writer` marks the version `[YANKED]` in the plugin's changelog. Pass the evidence that it was withdrawn.

## How to brief a subagent

The subagent starts with no context, so the prompt is its whole picture of the task. Write it like a work order:

- **Scenario**: the event in one line, and whether to create, update, release, audit or fix.
- **Target**: the plugin directory and the file, or "repository root".
- **What changed and why**: in the user's terms, with the paths of the files that changed.
- **Decisions**: version, change types, breaking or not, release date.
- **Owner values**: every value the table above lists for this subagent, exactly as the owner gave it.
- **Scope**: "report only" or "fix" for an audit; any file it must leave alone that it might be tempted to touch.

Example:

```text
Scenario: a released plugin changed; record the changes under Unreleased.
Target: plugins/turn-meter/CHANGELOG.md
What changed: the status line now shows tokens per minute (new, from skills/turn-meter/SKILL.md and
scripts/rate.sh); the `--compact` option was removed from the /turn-meter command.
Decisions: the first change is Added; the removal is Removed and breaking: users who pass --compact
get an error and must drop the flag.
Owner values: none needed.
```

Leave out what the subagent already knows: its template, its rules, how to format its document.

## Check what came back

For every subagent, before you rely on its result:

1. **Read its final message.** Act on each part:
   - **Missing values**: ask the owner, then launch the subagent again with them.
   - **Changes other files need**: send each one to that file's owner, or make it yourself when it is `plugin.json` or `marketplace.json`.
   - **Findings** (audit): take them to the owner before any fix.
2. **Check what it touched.** `git status --short` must show only the files the subagent owns, plus its memory under `.claude/agent-memory/`. If it changed anything else, restore that file with `git checkout -- <file>` and tell the owner.
3. **Check for leftovers** in each file it wrote: `grep -n '{{' <file>` and `grep -n '<!--' <file>` should find nothing, except where the subagent's own rules keep them.
4. **Validate the plugin** when the subagent wrote one of its documents: `claude plugin validate plugins/<plugin> --strict --profile directory`.
5. **Read the diff.** Make sure it says what the change is, and that it states nothing the plugin's files or the owner did not give.

When a result is wrong, launch the subagent again with what is wrong and what to do. Do not fix the document yourself.

## When something gets in the way

- **No subagents in this session**, as in a cloud thread of a Claude Project or in Claude chat: leave the documents as they are, and tell the owner which documents the change needs and why.
- **A subagent stops without finishing** (turn limit or error): resume it with SendMessage and its agent ID, or launch it again with the same brief.
- **A subagent reports that an official source contradicts its template**: do not work around it. Bring the conflict to the owner; a template changes only with the owner's decision.
- **The owner asks you to edit a document directly**: say once that its subagent keeps it consistent with the template, and recommend launching it. Do what the owner decides.

## Conventions that bind every document

They are in `.claude/CLAUDE.md`. The ones that shape briefs most often:

- Release dates are UTC, `YYYY-MM-DD`, the day the tag and GitHub Release are created.
- The two surfaces are named **Claude Code** and **Claude**, and no other surface name is used.
- Prerequisites, tools and minimum versions a plugin needs go in its README's Prerequisites section.
- Plugin changes that touch components, dependencies or configuration go through a pull request, and only at the owner's request. A change limited to a plugin's documentation needs none.
- The repository is public: no personal, client or business data in any document or memory.
