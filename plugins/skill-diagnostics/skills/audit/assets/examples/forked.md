---
name: summarize-branch
description: Summarizes what the current branch changes against its base and names the riskiest files. Use when the user asks what a branch changes or wants a change summary before a review.
context: fork
agent: Explore
argument-hint: "[base-branch]"
---

Summarize the changes of the current branch against the base branch named here: $ARGUMENTS. Empty: use `main`.

Explore loads no CLAUDE.md, so every rule this task needs is on this page.

## Steps

1. List the changed files and their line counts against the base branch.
2. Read each changed file's diff in full.
3. Rank the files by risk: changes to auth, payments or data migrations first, then public interfaces, then the rest.

## Return

Return exactly this as your final message:

```markdown
## Branch summary
- <one line per change, with its file>
## Riskiest files
1. <file> — <why>
```
