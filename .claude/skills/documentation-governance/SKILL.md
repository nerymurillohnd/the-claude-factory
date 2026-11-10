---
name: documentation-governance
description: Registry and launch procedure for this repository's governed documents - which agent owns each document, which chain of documents a change sets off, and how to run that chain with independent review. Load it before writing, editing or reviewing a plugin's README or CHANGELOG, after changing a plugin's components, dependencies or configuration, and whenever a hook reports a pending documentation chain.
---

# Documentation governance

Governed documents are written by owning agents, never by you. Your part is to recognize the event, run its chain, and report the result. Do not draft the documents yourself and pass them along: each agent reads the plugin and writes from its own contract.

## Registry

`chains.json`, in this skill's directory, is the single source for what is below. Read it before you launch anything, and pass its values on unchanged.

| Document | Owner | Situations |
| :-- | :-- | :-- |
| `plugins/<plugin>/CHANGELOG.md` | `changelog-writer` | `create`, `unreleased-entry`, `release`, `yank` |
| `plugins/<plugin>/README.md` | `plugin-readme-writer` | `skeleton`, `finalize`, `update` |

`doc-reviewer` owns nothing. It reviews every chain's result, read-only.

A document that is not in the registry has no owning agent yet. Write it yourself, following `.claude/architecture/project-conventions.md`, and tell the owner that it is not governed.

## Chains

A chain is the ordered set of documents one event sets off. Stages run in order; the agents inside a stage run in parallel; each stage receives the facts the earlier ones returned.

| Event | Chain | Stages |
| :-- | :-- | :-- |
| A plugin's components, dependencies or configuration changed | `component-change` | CHANGELOG (`unreleased-entry`) → README (`update`) |

A hook reports the chains the working tree has set off, one per line as `<chain> <plugin>`, after each change to a plugin and before the turn ends. You do not run that check yourself. It stays silent while a chain is running.

## Run a chain

1. Finish the change that set off the chain first. The agents read the plugin's diff, so they must see its final state.
2. Read `chains.json` and take the `stages` of the chain.
3. Launch the `documentation-chain` workflow with these arguments, as JSON values, not as a string:

```json
{
  "event": "component-change",
  "plugins": ["<plugin>"],
  "stages": [[{ "agent": "changelog-writer", "situation": "unreleased-entry" }], [{ "agent": "plugin-readme-writer", "situation": "update" }]],
  "change": "<what changed and why, in two or three sentences>",
  "values": {}
}
```

   - `plugins` takes several plugins when the same event applies to each; they run in parallel.
   - `change` carries what only this conversation knows: the intent, and any decision the owner made. The agents cannot see the conversation.
   - `values` carries what a situation needs and the files do not hold, such as `{"version": "0.2.0", "date": "2026-11-12"}` for a release. Leave it empty otherwise.
4. The workflow runs in the background. It runs each stage, sends the result to `doc-reviewer`, and returns one result per plugin. Wait for it; do not launch it twice for the same plugin. Read the result before you report.

## Read the result

| `status` | Meaning | What you do |
| :-- | :-- | :-- |
| `passed` | The review found nothing to fix | Report the files changed and what each agent wrote |
| `no_change` | No agent found anything a user would notice | Report that, with the agents' reasons |
| `needs_attention` | Findings remain after two correction rounds | Report each remaining finding to the owner; do not fix the document yourself |
| `blocked` | An agent lacked a value it needs | Report the `missing` items to the owner and ask for them |
| `failed` | An agent or the workflow stopped | Report what stopped and relaunch the workflow once the cause is clear |

Each result carries `rounds`, the number of reviews that ran, and `corrections`, the findings a writer was sent back to fix. Report both: a chain that passed on its second review found and fixed something. Report the review's `unverified` items too: they are what nobody checked.

## One document, outside a chain

When the owner asks for a single document and no chain applies, such as rewording a README section, launch the owning agent directly with the Agent tool, naming its situation, the plugin and the request. Then launch `doc-reviewer` on the file, and send its findings back to the same agent until the review passes or two rounds have gone by.

## When the gate denies a write

A hook denies any write to a governed document that does not come from its owner. That is the system working. Run the chain; do not write the file through a shell command or any other route.

## Limits

- The hooks check writes made with the Write and Edit tools. A file changed through a shell command is caught only by the review.
- The scripted checks cover structure, leftover placeholders and headings. Whether a statement is true is checked by the agents and the reviewer against the plugin's files.
