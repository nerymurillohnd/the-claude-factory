# Phase 2: Injected commands

Whether the skill injects commands as it loads, how to write each one so it runs, and what makes it abort the skill or not run at all.

## Contents

- [Gotchas](#gotchas)
- [Decide whether to inject a command](#decide-whether-to-inject-a-command)
- [Write an injected command](#write-an-injected-command)
- [Pre-approve each command](#pre-approve-each-command)
- [Where an injected command doesn't run](#where-an-injected-command-doesnt-run)
- [Examples](#examples)
- [Official sources](#official-sources)

## Gotchas

- A failing injected command aborts the whole skill, and only `grep`, `rg`, `egrep`, `fgrep`, `find`, `diff`, `test`, `[`, `git diff` and `git grep` may exit 1: append `|| true` to any other command that can exit non-zero.
- An injected command never prompts: outside auto mode, one that no rule allows aborts the skill, so pre-approve it in `allowed-tools`.
- An exclamation mark right after another character, as in ``KEY=!`cmd` ``, stays literal and the command doesn't run: put it at a line's start or after a space.

## Decide whether to inject a command

Inject a command when Claude needs current data before its first step, and fetching it would cost a turn on every run: the diff, the branch, the status, the tool versions, or the result of a check script.

Leave it to Claude to run, with the command written in the body, when:

- It changes something: an injected command runs on every invocation, including when Claude invokes the skill on its own.
- Only some runs need its data.
- It can be slow: each command has the Bash tool's timeout.
- Its output can be long: past the inline limit, it arrives as a file path and a short preview, not as the data.
- Whether to run it is a judgment the step makes.

## Write an injected command

- For one command, write the exclamation mark directly before a backtick command, at the start of a line or after a space. For several, open a fenced block with three backticks and the mark, one command per line.
- Write every path with a variable, `${CLAUDE_SKILL_DIR}` or `${CLAUDE_PROJECT_DIR}`: each command runs in the session's working directory, which moves each time Claude runs `cd`.
- Append `|| true` to a command that can exit non-zero as a normal result, such as a check script that exits 1 when it finds problems, or catch the failure with a message, such as `git describe --tags 2>/dev/null || echo "no tags yet"`.
- Expect standard error in the injected text: with the default bash shell, it is merged into the output.
- Keep each command inside the timeout. When the Bash tool moves a slow command to the background, the skill still loads, and the text names the background task and the file that collects its output. A command it never moves to the background is killed at the timeout, and the skill aborts.
- Leave `shell` unset, so the commands run in bash where it exists and in PowerShell where it doesn't. Set `shell: powershell` only for a Windows-only skill, as the frontmatter file of Phase 2 shows: its exit-1 exceptions differ and cover `grep` and `git diff` but not `find` or `diff`. `shell: bash` fails before any command runs on Windows without Git Bash.
- Show a command the skill only mentions without the mark, as the embedding file of Phase 2 shows.

## Pre-approve each command

Write a rule in `allowed-tools` that matches each injected command, so it runs outside auto mode:

```yaml
allowed-tools: Bash(git diff *) Bash(git log *)
```

- Match the command as written, with the same path variable when it calls a bundled script: `Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check.py *)`.
- Keep each rule as narrow as the command: a rule such as `Bash(*)` pre-approves far more than the skill runs.
- Write the rules in the frontmatter as the frontmatter file of Phase 2 shows.

## Where an injected command doesn't run

Write the body so it still works, or tells Claude what to fetch, where its commands don't run:

- Outside Claude Code, as an upload to claude.ai or the Claude API: the line reaches Claude as literal text.
- In a skill synced from claude.ai and used in the terminal or VS Code: the line reaches Claude as literal text.
- In a Cowork session on the desktop, and where the user's settings turn on `disableSkillShellExecution`: each command becomes `[shell command execution disabled by policy]`. Bundled and managed skills keep their commands.

## Examples

```markdown
<!-- Weak: the check exits 1 when it finds problems, so the skill aborts exactly when it is needed -->
- Lint report: !`python3 ${CLAUDE_SKILL_DIR}/scripts/lint.py`

<!-- Strong -->
- Lint report: !`python3 ${CLAUDE_SKILL_DIR}/scripts/lint.py || true`

<!-- Weak: resolves only while the working directory is the skill's folder -->
- Totals: !`python3 scripts/check_totals.py out.csv`

<!-- Strong -->
- Totals: !`python3 ${CLAUDE_SKILL_DIR}/scripts/check_totals.py out.csv`

<!-- Weak: exits 128 in a repository with no tags, and aborts the skill -->
- Last release: !`git describe --tags --abbrev=0`

<!-- Strong -->
- Last release: !`git describe --tags --abbrev=0 2>/dev/null || echo "no tags yet"`
```

A skill that loads the data of a pull request before Claude summarizes it, with each command pre-approved:

```yaml
---
name: pr-summary
description: Use when the user asks to summarize a pull request or what changed in one. Summarizes the diff and the review comments of the current branch's pull request.
context: fork
agent: Explore
allowed-tools: Bash(gh pr diff *) Bash(gh pr view *)
---

## Pull request
- Changed files: !`gh pr diff --name-only`
- Diff: !`gh pr diff`
- Comments: !`gh pr view --comments`

## Your task
Summarize what the pull request changes and what its reviewers asked for.
```

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide: each holds the full rules, edge cases and version notes this file leaves out.

- Read [Inject dynamic context](https://code.claude.com/docs/en/skills#inject-dynamic-context) when the skill injects a command. It gives the inline and fenced forms, an example skill, and the setting that turns the commands off.
- Read [How injected commands run](https://code.claude.com/docs/en/skills#how-injected-commands-run) when a command depends on the shell, the working directory, a long run or a long output. It gives how the `shell` key picks the tool, and the timeout and output handling the commands share with Claude's own.
- Read [When an injected command fails](https://code.claude.com/docs/en/skills#when-an-injected-command-fails) when a command can exit non-zero. It gives the abort, the exit-1 exceptions per shell, and the error when no command ran.
- Read [Permission checks on injected commands](https://code.claude.com/docs/en/skills#permission-checks-on-injected-commands) when you write the `allowed-tools` rules. It gives what aborts outside auto mode, the limits of pre-approval, and what changes in auto mode.
- Read [Output limits](https://code.claude.com/docs/en/tools-reference#output-limits) when a command's output can be long or exit 1. It gives the inline ceilings, the file and preview past them, and the full list of commands whose exit 1 is a normal result.
- Read [How Claude Code handles the body of a synced skill](https://code.claude.com/docs/en/skills#how-claude-code-handles-the-body-of-a-synced-skill) when the skill is synced from claude.ai. It gives what each surface does with its commands, `@` references and placeholders.
