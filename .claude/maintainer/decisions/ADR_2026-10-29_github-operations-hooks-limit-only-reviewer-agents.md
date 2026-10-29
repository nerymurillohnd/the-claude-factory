---
status: accepted
date: 2026-10-29
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-29_github-operations-hooks-enforce-its-own-rules
superseded-by: none
---

# github-operations hooks deny only the reviewer agents' named writes

## Scope

- `plugins/github-operations/hooks/`: `hooks.json`, `run-hook.sh`, `github_hooks.py`; `deny-mcp-file-writes.sh` is removed.
- The two reviewer agents, `pr-tracker` and `repo-auditor`, and their `disallowedTools`.
- Out of scope: the advisory hooks (contract once per session, state after compaction), which block nothing and stay.

## Context and problem statement

0.5.0 had the plugin's hooks deny, for every caller, MCP file writes, token reads, force pushes, `--no-verify`, signing and hook switches through git configuration, and unguarded merges, and ask before every merge. They also let the reviewer agents run only git and `gh` reads and MCP tools whose names start with `get_`, `list_` or `search_`. Nery rejected both: the plugin is for third parties who refactor, clean up and debug repositories with it, and total write blocking or a read-only allowlist takes away the MCP tools and commands that work needs. Which calls, if any, should the plugin's hooks block?

## Decision drivers

- Third-party users must keep every tool and command for refactor, cleanup and debugging (Nery).
- Write limits belong only on auditor or reviewer agents, never on executors or the main session (Nery).
- A limit names what it withholds (a denylist), never what it allows (Nery).
- In a subagent file, a `disallowedTools` entry with a specifier such as `Bash(git push *)` removes the whole Bash tool ([sub-agents](https://code.claude.com/docs/en/sub-agents#restrict-which-tools-a-subagent-can-use)), so per-command shell limits need a hook.

## Considered options

- **Hooks deny only the reviewer agents' named writes; the main session and every other agent are never blocked**: chosen.
- **Keep the hard rules for every caller (ADR_2026-10-29_github-operations-hooks-enforce-its-own-rules)**: rejected by Nery; for the main session and executors he chose that the hooks block nothing.
- **Reviewer agents limited by an allowlist of read operations**: rejected; it removes tools by omission.

## Decision outcome

Chosen option: **hooks deny only the reviewer agents' named writes**, because it keeps every tool for the main session and executors and still keeps the two reviewers from changing state.

- Reviewer agents: `disallowedTools: Write, Edit, NotebookEdit`; the hook denies the named git write subcommands (`GIT_WRITE` and the write forms of mixed ones such as `branch`, `tag`, `stash`), `gh` write verbs (`GH_WRITE_VERBS`) and non-reading `gh api` calls, and the named GitHub MCP write tools (`MCP_WRITES`) on any server. Every other command and tool passes, including `awk`, `sed`, `cat`, redirects and MCP reads.
- Main session and every other agent: never denied or asked.
- No handler sets `onFailure: "block"`, because a failing hook would then block the main session; an unreadable input is denied only when its raw text names a reviewer agent.
- The merge approval moves back to the skill: ADR_2026-10-29_github-operations-merge-approval-asked-by-the-skill.

### Consequences

- Good, because users keep every tool, and a hook crash never blocks their work.
- Bad, because the plugin no longer stops a force push, `--no-verify`, a token read or an MCP file write in the main session; those rest on the skill's instructions and the user's own permission rules, which the README must offer.
- Bad, because a hook crash lets a reviewer's git or `gh` write pass; `disallowedTools` still removes the file tools.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Main session and other agents never blocked; reviewers denied each named write and nothing else | `scripts/testers/github-operations/test_hooks.py`, `by_path.sh` | pass, 2026-10-29 | each change to the hooks |
| Each reviewer's write is denied in a live run | eval cases `auditor-write-denied`, `tracker-write-denied` | pending | Task 13 of the 0.5.0 plan |
