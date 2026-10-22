---
status: accepted
date: 2026-10-22
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The hook-engineer agent inherits the session's tools instead of an allowlist

## Scope

- In scope: the frontmatter of `plugins/hook-engineering/agents/hook-engineer.md` (`tools` and `disallowedTools`) and how the agent reaches the Claude Code docs server.
- Out of scope: whether the plugin bundles the docs server (ADR_2026-10-22_docs-server-is-a-user-prerequisite) and the agent's modes and workflow.

## Context and problem statement

Once the docs server became a user prerequisite, its tools can carry several names: `mcp__claude-code-docs__*` when the user adds it in Claude Code as the README says, another `mcp__<name>__*` when the user picks another name, or `mcp__claude_ai_<connector name>__*` when it arrives as a Claude app connector. The 0.1.0 agent had a `tools` allowlist with two fixed MCP prefixes and a `disallowedTools` entry for each server's `submit_feedback` tool. The plan for 0.2.0 proposed keeping an allowlist with `mcp__claude-code-docs__*`; on 2026-10-22 Nery corrected it: remove `tools` and `disallowedTools` from the agent.

## Decision drivers

- The agent reaches the docs server under any name, a Claude app connector included, without the plugin guessing prefixes (Nery, 2026-10-22).
- Less maintenance: an allowlist breaks when tool names change (Nery, 2026-10-22).

## Considered options

- **Inherit every session tool (no `tools`, no `disallowedTools`)**: chosen.
- **A. An allowlist with `mcp__claude-code-docs__*` only**: rejected, because a connector or a server under another name is not callable from the agent, and the list needs maintenance.
- **B. An allowlist that also names `mcp__claude_ai_Claude_Code_Docs__*`, with the README requiring that connector name**: rejected, because it rests on a connector-name sanitization that was observed but not documented, and it still breaks under any other name.

## Decision outcome

Chosen option: **Inherit every session tool**, because it lets the agent use the docs server under any name and removes a list that would need maintenance. Per the [sub-agents docs](https://code.claude.com/docs/en/sub-agents#available-tools), a subagent without `tools` inherits the main conversation's built-in and MCP tools, narrowed only by Claude Code's own filters.

### Consequences

- Good, because the agent finds the docs tools with ToolSearch (query `claude_code_docs`) under any server name.
- Bad, because the agent also inherits every other session tool, including the docs server's `submit_feedback` and the write tools of any other MCP server the user has connected; only its instructions limit them.

### Risks and mitigations

| Risk | Likelihood or condition | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| The agent calls the docs server's `submit_feedback` tool and sends text to Anthropic's docs team | Only if the model ignores the instruction in the agent body | Low: an unwanted message to the docs team | The agent body says "Never call the server's `submit_feedback` tool". Risk accepted by Nery on 2026-10-22, with no `disallowedTools` entry | Nery Samuel Murillo |
| The agent uses a write tool of another connected MCP server | Only if the model goes outside the hook task the body scopes | Depends on the server | The agent body limits its scope and its write mode to hook files | Nery Samuel Murillo |

## More information

- Implemented in [PR #42](https://github.com/nerymurillohnd/the-claude-factory/pull/42), merged on 2026-10-22 as `31ad541` and released as `hook-engineering--v0.2.0`.
- Not verified live: that the agent uses an inherited Claude app connector, in Claude Code or in a Cowork session.
- To restore a tool-level block, add `disallowedTools: mcp__claude-code-docs__submit_feedback` to the agent; it covers only a server named `claude-code-docs`.
