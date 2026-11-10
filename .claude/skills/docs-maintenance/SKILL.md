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

## How to work

1. **Read `references/governance.md` in full.** It holds the rules for every task: what stays with you, how to run subagents in parallel, how to brief one, how to check what it returns, what to do when something gets in the way, and the conventions every document follows.
2. **Read the state.** Run `git status` and `git diff` (against the upstream branch, or `HEAD` when there is none). List which root documents exist (`ls *.md LICENSE`) and, for each plugin involved, which of `README.md`, `CHANGELOG.md`, `LICENSE` and `NOTICE.txt` exist.
3. **Name the events.** Match what happened to the events below. One change often triggers several, for example a new plugin that bundles third-party code and calls a remote service.
4. **Read the reference of each event you named**, and follow it: it says which subagents to launch, in which stages and with which commands before and after.
5. **Settle your part first.** Make the `plugin.json` and `marketplace.json` changes, decide versions and change types, and get the owner's missing values.
6. **Launch the stages, check each result, and report to the owner** as the governance and the event references say.

## Events

| Event | It applies when | Reference |
| :-- | :-- | :-- |
| Repository foundation | The repository's own documents are created or rebuilt | `references/events/repository-foundation.md` |
| New plugin | A plugin directory with its `plugin.json` appears and is listed in `marketplace.json` | `references/events/new-plugin.md` |
| A released plugin changes | Its components, commands, configuration, prerequisites or behavior change before a version bump | `references/events/plugin-change.md` |
| A plugin gets a new version | `plugin.json` has a new `version` and the release happens now | `references/events/new-version.md` |
| A plugin is renamed | Its `name` changes | `references/events/plugin-rename.md` |
| A plugin is retired | It leaves the catalog | `references/events/plugin-retirement.md` |
| Third-party material changes | Another author's material is added to a plugin, updated or removed | `references/events/third-party-material.md` |
| Data handling changes | A plugin starts or stops calling a remote service, collecting data or keeping files on the user's machine | `references/events/data-handling.md` |
| The owner changes a policy | A copyright line, reporting channel, security policy, support channel or contribution process changes | `references/events/policy-change.md` |
| Audit or review | Someone asks whether the documentation is correct, or you suspect drift | `references/events/audit.md` |
| A small fix | A typo, a broken link or an outdated sentence | `references/events/small-fix.md` |
| A version is withdrawn | A released version must be marked yanked | `references/events/yanked-version.md` |

When no event fits, read the subagents table to find the document's owner, brief it with the governance's rules, and tell the owner which case was missing from this table.

## The references are the contract

`references/governance.md`, `references/commands.md` and the event files are the procedure itself, not background reading. Read the governance and every event file the task needs each time, even when you remember them: they change, and a step you skip is a document that goes out wrong to the people who install these plugins.
