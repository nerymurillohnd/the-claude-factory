---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Remove the github-workflow skill

## Scope

The project skill `.claude/skills/github-workflow/`, which covered issues, commits, pushes and pull requests on this repository, and the hand-offs to it in `plugin-consistency` and `plugin-development`. ADR_2026-10-20_procedures-live-in-project-skills created it; its decision that procedures live in project skills still holds.

## Context and problem statement

An audit on 2026-10-25 compared the skills rebuilt in the current consolidation against the older ones. `github-workflow` contradicted them and `.claude/CLAUDE.md`:

- It required a pull request for every change to `scripts/` (`SKILL.md:18`), while CLAUDE.md → Change Control says a change outside `plugins/` needs none.
- It made the `pr-tracker` report conditional ("if available", `:22`), while `release-and-versioning`, `plugin-renames-and-removals` and `~/.claude/CLAUDE.md` require it before a merge.
- It split the bump and changelog into topic commits (`:82`), while the release and rename skills require one release commit.
- It reproduced an issue with `--plugin-dir` (`:66`), while the testing skills reproduce from an isolated install of the copy users receive.
- It routed every docs-only fix to `plugin-consistency` (`:39`), which the `maintaining-user-docs` skill now covers.

Should it be corrected now, or removed?

## Decision drivers

- No two procedures may give conflicting orders in the same session.
- GitHub operations (issues, labels, triage, pull requests) are a later stage of `.claude/rules/workflow.md`, to be built after the stages before it are done.
- Broken work is removed, not patched.

## Considered options

- **Remove the skill now and rebuild it as the GitHub operations skill later**: chosen.
- **Correct its conflicting lines now**: rejected, because it would patch a skill that the later stage replaces, against the rule to remove broken work.

## Decision outcome

Chosen option: **remove the skill now**, because it removes the conflicts and the later stage builds the procedure from current docs.

- `.claude/skills/github-workflow/` is deleted (commit 8517729).
- `plugin-consistency` and `plugin-development` no longer hand off to it.

### Consequences

- Good, because the rebuilt skills and CLAUDE.md are the only sources for pushes, pull requests and release commits.
- Bad, because until the GitHub operations skill exists, no skill covers triaging and answering issues; `.claude/CLAUDE.md` and `~/.claude/CLAUDE.md` still set the approval rules for replies, pushes and merges.

## More information

Decided by Nery on 2026-10-25 in this session. Revisit when the stage "Issue handling and resolution" of `.claude/rules/workflow.md` is built.
