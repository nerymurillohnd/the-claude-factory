# Mechanical checks

This file is yours, the orchestrator's: it tells you how to run every mechanical check of the audit, how to read each result, and which reviewer receives it. No reviewer reads this file. Each reviewer gets only the results its entry under "What each reviewer receives" lists, written into its prompt.

## Contents

- How to run the checks
- Plugin structure and loading
- Dependencies
- Code files
- Registration and listing
- Instruction leads
- What each reviewer receives

## How to run the checks

Run the checks the selected reviewers receive, and read every result. They need the `claude` command, Claude Code's CLI; where it isn't available, every check below is not run. In each command, `<plugin root>` is the directory that holds the plugin's `.claude-plugin/` folder and `<plugin name>` is the `name` in its `plugin.json`.

A check no command in this file covers is not run: name it to the reviewer as not run, and never measure it by hand, because a figure you estimate reads to the reviewer as measured. A command that fails or is unavailable is also not run: name it with its exit code and message.

## Plugin structure and loading

- `claude plugin validate --json <plugin root>` for a plugin skill, or `claude plugin validate --json <skills directory>`, the directory named `skills` that holds the skill, otherwise. It doesn't read a `SKILL.md` at a plugin's root, doesn't follow symlinks, and accepts some malformed YAML, so its pass proves only what it reports.
- `claude --plugin-dir <plugin root> plugin details <plugin name>`: the inventory, and each skill's always-on and on-invoke token estimates. For a skill outside a plugin, copy its folder into `skills/<skill name>/` inside a new empty directory, and use that directory as `<plugin root>` and its folder name as `<plugin name>`. Its `Hooks` line lists the plugin's hooks by event.
- `claude --plugin-dir <plugin root> plugin list --json`: from the audited plugin's entry, its `errors`, `errorDetails`, `notes` and `noteDetails`, which appear only when the plugin has load errors, unmet dependencies or packages not installed; from every entry, the `id`, `scope` and `enabled` of the plugins installed with it. Never pass an entry's `mcpServers`, because a server definition can hold a credential's value.

## Dependencies

- For each plugin dependency whose source is its own git repository: `git ls-remote --tags <repository URL>`, keeping the tags named `<dependency>--v*`, the tags that can satisfy its version range. It needs network access to that repository; offline or without access, it is not run.

## Code files

- For each code file in the inventory: `head -n 1 <file>` for its first line, and `ls -l <file>` for its executable bit.
- `shellcheck <script>` for each shell script and `ruff check <script>` for each Python script, each only where `command -v` finds the linter; otherwise that linter is not run.

## Registration and listing

- `claude -p "/skill-doctor"` and `claude -p "/context"`, run in the project directory the skill loads in, adding `--plugin-dir <plugin root>` for a plugin that isn't installed: the name each skill registers under, its source, its listing cost after the budget, its recent use, and the Skills total.

## Instruction leads

- `claude -p "/doctor prompt-audit <skill directory>"`, where `<skill directory>` is the folder that holds the skill's `SKILL.md`: Claude Code's own audit of the skill's instructions, such as wording written for older models, references to files or commands that don't exist, and files that contradict each other. It is a model's judgment, not a measurement: give its report to every selected reviewer as leads to verify in its own areas, never as verified findings.

## What each reviewer receives

Write into each reviewer's prompt the results listed under its name, and name every one of them that was not run. Every reviewer also gets the `/doctor prompt-audit` leads.

- `content-patterns`: misplaced inline `!` commands; every injected command; unescaped `$` before a digit, `ARGUMENTS` or a declared argument name; path variables written in reference files; backslash paths; unqualified MCP tool names; `@` references.
- `runtime-contract`: the `claude plugin validate --json` output; the component inventory from `claude plugin details`; the name each skill registers under and its source, from `/context` and `/skill-doctor`; frontmatter parse errors; which referenced files and links exist and stay inside the skill folder; reference depth and unreferenced files; symlinks and their targets; plugin variables in a skill outside a plugin; `allowed-tools` entries against the injected commands; each script the Markdown runs and whether its file exists; archive listings; the skill's frontmatter hooks by event, matcher and command, with the path variable each command uses; the hooks of the skill's own plugin by event and matcher, marking those that match `Skill` or `UserPromptExpansion`; every skill name the body tells Claude to invoke or stack, with whether it resolves in the plugin or its dependencies and that skill's `disable-model-invocation`, `user-invocable`, `context`, `agent` and `background` values; every subagent in the plugin that preloads or invokes the skill, with its `tools`, `disallowedTools` and `skills`; the plugin's `dependencies`, its marketplace entry and `allowCrossMarketplaceDependenciesOn`, and each dependency's source type and the tags that satisfy its range; the plugin's load errors and notes from `claude plugin list --json`; the plugin's `engines` range.
- `size-limits-and-budgets`: where the body's first 5,000 tokens end; the always-on and on-invoke token estimates from `claude plugin details`; the skill's listing cost after the budget from `/skill-doctor`, and the Skills total from `/context`; character counts of `name`, `description`, `when_to_use` and `compatibility`, and where the 1,536th character of `description` plus `when_to_use` falls; the body's line and approximate token counts; line counts of supporting files and which references over 100 lines lack a table of contents; bundle size and file count; the source's frontmatter hook count and total matcher characters; the length of any preload list shipped with the skill.
- `knowledge-delta`: no mechanical result of its own; only the `/doctor prompt-audit` leads.
- `task-mechanisms`: no mechanical result of its own; only the `/doctor prompt-audit` leads.
- `frontmatter-description`: the `claude plugin validate --json` output; frontmatter parse errors; the frontmatter's keys and values as parsed; the descriptions of the skill's sibling skills; whether each field is valid on each target surface.
- `comprehension`: where the body's first 5,000 tokens end; capitalized absolutes; time-sensitive wording.
- `feature-fit`: the mode, with or without an environment; the paths of the environment's Markdown instruction files (every CLAUDE.md and CLAUDE.local.md level, rules with their `paths`, other skills with their names and descriptions, and subagents), with the contents of any outside the working directory, such as `~/.claude/`, read for it; the hooks by event, matcher and source; the installed plugins with their scope and whether each is enabled, from `claude plugin list --json`; the MCP server names; the permission rules; and the active output style. Extract these from settings and MCP files without their values, and never pass the reviewer a settings, MCP or credential file.
- `scripts`: the inventory of code files in the skill's folder, at the plugin level, in `bin/` and run by its hooks, each with its path and language; each one's first line and executable bit; each script the Markdown runs, with its interpreter and whether the file exists; the scripts each hook command runs; Python imports outside the standard library with no inline dependency declaration; external commands a script calls that neither the Markdown nor `compatibility` mentions; package installs in scripts, global or local; the packages `claude plugin list --json` notes as not installed; network and credential signals in scripts, by file and line, never with a value; and the output of any linter run on the scripts, such as ShellCheck or Ruff, or the name of each linter not run.
