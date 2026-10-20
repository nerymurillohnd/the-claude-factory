---
status: accepted
date: 2026-10-19
decision-makers:
  - "Nery Murillo"
supersedes: none
superseded-by: none
---

# Merge Session Handoff into Project Maintainer

## Scope

The `session-handoff` plugin and the new `project-maintainer` plugin of this marketplace, and where a project keeps the records that both write. Out of scope: the content of the handoff itself, which moves unchanged apart from the reconciliation step.

## Context and problem statement

`session-handoff` writes an end-of-session handoff. `project-maintainer` writes architecture decision records (ADRs) and keeps a technical-debt ledger. A handoff that does not know the debt and the decisions of the project leaves the next session reading two sources, and the two plugins overlap by domain: both keep a project's memory in its `.claude/` folder. Should they stay two plugins, depend on each other, or become one?

## Decision drivers

- One package for a project's maintenance documentation.
- A plugin stays self-contained: no plugin depends on another.
- Everything a plugin writes about a project lives in the project's `.claude/` folder, never in `docs/`.
- The next session reads the handoff alone and still sees every open debt item.
- Existing installs of `session-handoff` keep working.

## Considered options

- **Merge `session-handoff` into `project-maintainer` as its second skill (`write-handoff`)**: chosen.
- **Keep two plugins and let the handoff depend on the other plugin's folders**: rejected because it makes the handoff depend on a plugin that may not be installed.
- **Keep two unrelated plugins**: rejected because the handoff would repeat or contradict the ledgers.

## Decision outcome

Chosen option: **merge into `project-maintainer`**, because one self-contained plugin can reconcile the handoff with the records it keeps itself, which none of the other options achieves without a dependency.

`write-handoff` reads the pending debt, the closed-debt index and the decisions, adds every pending debt item to its open items and closes the ones the ledger shows closed. The marketplace renames `session-handoff` to `project-maintainer`, so existing installs move over. `session-handoff` is removed in the same pull request as the merge.

### Consequences

- Good, because the next session reads one file and already knows what is open.
- Good, because a project installs one plugin for its records and its handoffs.
- Bad, because a user who wanted only the handoff now installs the records and the guardrails too.
- Bad, because `project-maintainer` needs Claude Code 2.1.304 or later, which `session-handoff` did not.

### Risks and mitigations

| Risk | Likelihood or condition | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| The start-of-session reminder appears twice | A user keeps `session-handoff` installed from another source | Noise in the first reply | The README tells the user to turn the old one off | Nery Murillo |
| A user on an older Claude Code cannot use the new plugin | Claude Code older than 2.1.304 | The renamed plugin loads without the approval guard | The README states the minimum version up front | Nery Murillo |

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| `session-handoff` is gone and the rename is in the marketplace | `node .github/scripts/check-repo.mjs` and `claude plugin validate --strict .` | pending | Before the pull request merges |
| The renamed handoff still loads at session start | `.github/scripts/tests/project-maintainer/by_path.sh` | pending | Before the pull request merges |

## More information

The same pattern merged `git-hygiene` into `github-operations`: a `renames` entry in `marketplace.json` and a line under Removed in the root changelog. The alternative of two plugins was weighed under the Plugin Gate rule for plugins that overlap by domain, and the owner chose to merge.
