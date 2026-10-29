---
status: accepted
date: 2026-10-29
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# github-operations enforces its own hard rules with plugin hooks

## Scope

- `plugins/github-operations/hooks/`: `hooks.json`, the Bash launchers and `github_hooks.py`, new in 0.5.0.
- The rules they enforce: no MCP file writes, no token reads or tokens sent with `curl`, no force push or history rewrite, no `--no-verify`, read-only `pr-tracker` and `repo-auditor`, merges only at a guarded head and after a permission prompt; plus two advisory hooks (contract once per session, state after compaction).
- Out of scope: other plugins of the marketplace, including `block-no-verify`, which this plugin neither requires nor references.

## Context and problem statement

The skills stated their hard rules as text, which Claude can skip when the skill is not loaded or the request is worded differently. Some of these rules overlap with what another plugin of the marketplace enforces (`block-no-verify`). Every plugin here is self-contained and targets users whose installed plugins are unknown (`.claude/CLAUDE.md`, Purpose). Should github-operations enforce its rules itself, rely on another plugin, or keep them as text?

## Decision drivers

- Each plugin is self-contained; another plugin is never a dependency or a justification.
- A rule that guards published history, credentials or merges must hold whether or not the skill was invoked.
- Least invasive design: deny only what the rule guards, never slow ordinary work into failure.
- A plugin cannot ship permission rules; hooks are the only enforcement a plugin carries.

## Considered options

- **Command hooks in the plugin's `hooks/hooks.json`: a Bash launcher, a Python 3.12 standard-library module that lexes commands with `shlex`, exact matchers, filtering inside the script, `"onFailure": "block"` on every guard**: chosen.
- **Rely on `block-no-verify` or user permission rules for force-push and `--no-verify`**: rejected, because a user may not have them, and naming another plugin as a dependency breaks self-containment.
- **Keep the rules as skill text only**: rejected, because text does not hold when the skill is not loaded.
- **Agent, `mcp_tool` or elicitation hooks, or `if` filters on enforcing hooks**: rejected; agent-type hooks are experimental, and an `if` filter can let a wrapped command through before the script lexes it.

## Decision outcome

Chosen option: **the plugin's own command hooks**, because they enforce the hard rules on every GitHub call, on any GitHub MCP server name, without depending on what else the user installed.

### Consequences

- Good, because the rules hold before the first GitHub action, however the request was worded.
- Good, because a merge always passes a person's permission prompt at a guarded head SHA, even in auto mode.
- Bad, because the plugin now needs `python3` 3.12 or later and Claude Code 2.1.295 or later (`onFailure`); without a usable `python3` the guards deny the calls they guard.
- Bad, because a user who also installs `block-no-verify` gets two denials for the same `--no-verify` command.
- Bad, because an approved history rewrite can no longer run from Claude: the force push is handed to the user to run in their own terminal.
- Hooks are a barrier for Claude, not a security boundary; the README offers optional user `deny` rules as the hard layer.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Each hook denies or asks on its target and stays silent on a neighbor input | `scripts/testers/github-operations/test_hooks.py` and `by_path.sh` | pending | Each hook change |
| Each guard blocks when its script fails | `by_path.sh` launcher section | pending | Each hook change |
| The hooks fire in a live session, in `default` and `bypassPermissions` modes | Live calls after `/reload-plugins` | pending | Each Claude Code release that changes hooks |

## More information

- Spec: `.claude/specs/2026-10-29-github-operations-0.5.0-design.md`, section "Hooks layer". Decided by Nery in the 2026-10-29 design conversation.
