---
status: accepted
date: 2026-11-04
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# The PR lifecycle agents deny tools in their frontmatter

## Scope

The frontmatter of `plugins/github-operations/agents/pr-lifecycle/pr-tracker.md`, `pr-fixer.md` and `pr-finalizer.md` (commits 560479a and c90db85).

## Context and problem statement

With the hooks removed, the agents' limits were kept by their instructions alone, and their frontmatter held six fields only (`name`, `description`, `model`, `effort`, `color`, `maxTurns`). Should Claude Code remove tools the agents must never use?

## Decision drivers

- A limit Claude Code enforces is stronger than an instruction.
- Plugin agents support `disallowedTools` and ignore `hooks` and `permissionMode` (code.claude.com/docs/en/sub-agents, read 2026-11-04).
- A subagent still returns its result as its final message, with no tool, so removing tools cannot block its report.

## Considered options

- **`disallowedTools` per agent**: chosen.
  - All three agents: `Agent`.
  - `pr-tracker` and `pr-finalizer` also: `Write`, `Edit`, `NotebookEdit`.
- **Keep the six-field frontmatter and rely on instructions**: rejected, at Nery's request.

## Decision outcome

Chosen option: **`disallowedTools` per agent**. It reverses the six-field frontmatter rule of the earlier redesign.

### Consequences

- Good, because no agent can launch another, and the read-only agents cannot write files through the file tools.
- Bad, because `Bash` stays available to all three: blocking it would remove `git` and `gh`, which they need. Their read-only shell use and their GitHub-write bans are still kept by instructions.

## More information

Requested by Nery on 2026-11-04, with the tool name corrected from "Notebook" to `NotebookEdit`.
