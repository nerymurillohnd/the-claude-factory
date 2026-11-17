# Mechanical checks

This file is yours, the orchestrator's: it tells you how to run every mechanical check of the audit, how to read each result, and which reviewer receives it. No reviewer reads this file. Each reviewer gets only the results its entry under "What each reviewer receives" lists, written into its prompt.

## Contents

- How to run the checks
- Running the frontmatter checks
- Reading a frontmatter check's result
- Frontmatter checks
- Plugin structure and loading
- Dependencies
- Code files
- Registration and listing
- Instruction leads
- What each reviewer receives

## How to run the checks

Run the checks the selected reviewers receive, and read every result. They need the `claude` command, Claude Code's CLI; where it isn't available, every check below is not run. In each command, `<plugin root>` is the directory that holds the plugin's `.claude-plugin/` folder and `<plugin name>` is the `name` in its `plugin.json`.

A check no command in this file covers is not run: name it to the reviewer as not run, and never measure it by hand, because a figure you estimate reads to the reviewer as measured. A command that fails or is unavailable is also not run: name it with its exit code and message.

## Running the frontmatter checks

Every frontmatter check runs through one entry script, whose path step 3 of `SKILL.md` gives already quoted. Below, `<entry>` stands for exactly that quoted path: the skill's permission rules approve only that spelling, and a command written any other way asks the user first. If the path doesn't exist, use the fallback path step 3 gives; if neither exists, every frontmatter check is not run.

- `python3 <entry> run <SKILL.md>`, once, in step 3: runs every frontmatter check. It prints one line per check, `<check> <status> <n> finding(s) -> <receivers>`, then `results: <folder>`. Keep the folder's path exactly as printed, because the commands below take it as written.
- `python3 <entry> show <folder> --reviewer <name>`: the results that reviewer receives, one JSON line each, to write into its prompt verbatim. `--check <id>` prints one check's result instead.
- `python3 <entry> check <id> <SKILL.md>`: one check alone, printing the same line `run` stores for it. Use it only to run a single check again.
- `python3 <entry> clean <folder>`: removes that results folder and nothing else. Run it after presenting the reports, and also whenever the audit stops before that.
- If `python3` isn't found, or Windows answers with a message about the Microsoft Store, use `python` in its place from then on.
- Before you launch the reviewers, check against the summary that every selected reviewer it names has its `show` output in its prompt.

## Reading a frontmatter check's result

Each frontmatter check prints one line of JSON and exits 0, whether or not it found anything.

- Exit 2 means the check could not run: stdout is empty and stderr holds one line with the reason. Name the check to its reviewers as not run, with the exit code and that line. Do the same when no Python interpreter is found.
- `status` is `ran` or `not_run`. `not_run` means a check it depends on failed, and `reason` names that check: name it to its reviewers as not run, with that reason.
- `skill` is the skill's folder name as given, and `data` holds the check's own measurements, which its entry describes.
- Each finding holds:
  - `rule`: the rule it breaks, which the check's entry explains;
  - `file`, `line` and `column`: where it is, relative to the skill's folder and counted from 1, or `null` when it has no position;
  - `field`: the frontmatter key, or `null`;
  - `found`: what the file holds there, cut at 120 characters with `…`, and `found_length`, its full length in characters;
  - `expected`: what the rule wants, in one sentence;
  - `basis`: `official` when the docs or the specification state the rule, `convention` when it is a project convention rather than an official rule, and `inference` when it follows from documented behavior without being stated;
  - `surfaces`: where it applies: `claude-code`; `open-spec`, the Agent Skills specification; `upload`, claude.ai uploads, the Skills API and skill packaging;
  - `condition`: the case it depends on, or `null` when it always applies.
- Pass every finding to its reviewers verbatim: add no severity, and drop or merge none. Each reviewer grades findings by its own severity model, from `basis`, `surfaces` and `condition`.

## Frontmatter checks

`run` runs each of these; `check <id>` runs one again. The YAML reader stops at the first failure it meets, so a file can hold more failures than one run reports.

### frontmatter.yaml

- Command: `python3 <entry> check frontmatter.yaml <SKILL.md>`.
- What it checks: the frontmatter against strict YAML, because Claude Code's parser accepts some YAML that packaging, uploads and other parsers reject, and a skill whose YAML doesn't parse still loads, with no fields set.
- `claude plugin validate` already reports a missing block, a root that isn't a mapping, an unclosed quote and a tab in the indentation; this check adds the four failures validate passes, and bytes that aren't UTF-8.
- Reading the result:
  - `duplicate-key`: a key appears twice; Claude Code keeps the last value.
  - `colon-in-value`: `: ` inside a plain value, or a plain value ending with `:`.
  - `unclosed-flow`: a `[` or `{` that never closes, at the line it opens on.
  - `key-under-scalar`: a key indented under a key that already has a value.
  - `not-utf8`: the first byte that isn't UTF-8, in hex; Claude Code replaces such bytes without a word.
  - A finding on the first four means packaging and uploads reject the file, while Claude Code may still load it.
  - `not_run` with the reason that validate reports the error, or that there is no frontmatter block: read validate's output for that file instead. `not_run` because the reader can't read the YAML names the line; validate's output decides it.
  - `data.close_line`: the line of the closing `---`.
- Goes to: `frontmatter-description` and `runtime-contract`.

### frontmatter.plain-values

- Command: `python3 <entry> check frontmatter.plain-values <SKILL.md>`.
- What it checks: plain values that a YAML parser reads differently than they are written.
- No other command covers this; this check is the only source. It needs `frontmatter.yaml` to pass first.
- Reading the result:
  - `comment-truncates`: ` #` after a plain value starts a comment, so the text after it is dropped.
  - `leading-indicator`: a plain value starting with `-`, `?` or `:`.
  - `reads-as-collection`: a text field written as a list or a mapping.
  - `anchor-alias-tag`: a text field with an anchor, an alias or a tag.
  - `reads-as-boolean` and `reads-as-null`: a plain text field, or a `metadata` value at any depth, whose text a parser reads as a boolean or null; `condition` says when only YAML 1.1 parsers read it so.
  - A finding means the parsed value differs from what the line shows.
  - `data.colon_cases`: `: ` inside a value is reported by `frontmatter.yaml`.
- Goes to: `frontmatter-description`.

### frontmatter.name

- Command: `python3 <entry> check frontmatter.name <SKILL.md>`.
- What it checks: the name's format against the open specification, its folder, the characters Claude Code refuses and the reserved words, because a refused name hides the skill from the `/` menu and a name unlike its folder renames the command and breaks uploads.
- `claude plugin validate` passed a malformed name when tested, so this check is the only source for these rules. It needs `frontmatter.yaml` to pass first.
- Reading the result:
  - `missing`: no `name`; Claude Code uses the folder name, and the open specification and uploads require one.
  - `not-a-string`: the value reads as another type, such as a number, or as a collection.
  - `length`, `charset` and `hyphen`: the open specification's limits of 1 to 64 characters, `a-z`, `0-9` and `-`, and no leading, trailing or consecutive hyphen.
  - `folder-mismatch`: the name differs from the skill's folder name.
  - `refused-character`: a character Claude Code refuses, which hides the skill from the `/` menu.
  - `reserved-word`: `anthropic` or `claude` in the name, or in the folder name when the name is missing; the Claude API and claude.ai reject them.
  - `data`: the name and whether it came from the `name` field or the folder, its length in characters and in UTF-16 units, the folder name, whether they match, and the Unicode version the character categories come from.
- Goes to: `frontmatter-description`, and `size-limits-and-budgets` for the counts in its `data`.

### frontmatter.name-plain

- Command: `python3 <entry> check frontmatter.name-plain <SKILL.md>`.
- What it checks: that the name is written as one plain line, so its text in the file is exactly the parsed name.
- No other command covers this; its findings follow a project convention, not an official rule, except `yaml11-type`. It needs `frontmatter.yaml` to pass first.
- Reading the result:
  - `quoted`, `block-scalar`, `multi-line` and `anchor-alias-tag`: the name is quoted, written with `|` or `>`, folded over lines, or carries an anchor, an alias or a tag.
  - `yaml11-type`: YAML 1.1 parsers read the name as a number or a date; booleans and null are in `frontmatter.plain-values`.
- Goes to: `frontmatter-description`.

### frontmatter.description

- Command: `python3 <entry> check frontmatter.description <SKILL.md>`.
- What it checks: that the description, which Claude chooses the skill by, is present, a string with text, at most 1,024 characters, and free of `<` and `>`.
- `claude plugin validate` passed an XML tag and 1,100 characters when tested, so this check is the only source. It needs `frontmatter.yaml` to pass first.
- Reading the result:
  - `missing`: no `description`; the open specification and uploads require one, and Claude Code uses the body's first non-empty line, as `data.claude_code_fallback` says.
  - `not-a-string`, `empty` and `too-long`: not text, only blanks, or over 1,024 characters.
  - `angle-bracket`: a `<` or `>`; uploads reject it and Claude Code shows `&lt;` and `&gt;`. `data.xml_tags` lists the XML tags among them.
  - `data.length` and `data.utf16_length`: the length in characters and in UTF-16 units.
- Goes to: `frontmatter-description`, and `size-limits-and-budgets` for the lengths.

### frontmatter.listing-cap

- Command: `python3 <entry> check frontmatter.listing-cap <SKILL.md>`, with `--cap <N>` when the user's `skillListingMaxDescChars` setting is known and differs from 1,536.
- What it checks: where Claude Code's skill listing cuts `description` and `when_to_use`, joined by ` - `, because the text past the cut never reaches Claude.
- No command reports the cut: `/skill-doctor` gives the listing cost, not where it cuts. This check is the only source. It needs `frontmatter.yaml` to pass first.
- Reading the result:
  - `over-cap`: the joined text is longer than the cap. `found` is the text that is cut off.
  - `data.first_lost_field` and `data.first_lost_offset`: the field the first lost character is in, and its 0-based offset there; `data.around_cut` shows 40 characters on each side of the cut, marked with `|`. These show which trigger words never reach Claude.
  - `data.line`: the cut's file line, given only when that field is a plain or single-quoted value on one line.
  - Lengths are in characters; `data.combined_utf16_length` is the same text in UTF-16 units, and where the two differ, whether the cap counts characters or UTF-16 units is unverified.
- Goes to: `size-limits-and-budgets` and `frontmatter-description`.

### frontmatter.compatibility

- Command: `python3 <entry> check frontmatter.compatibility <SKILL.md>`.
- What it checks: that `compatibility`, when present, is a string of 1 to 500 characters, as the open specification and Claude Code allow.
- `claude plugin validate` passed 600 characters when tested, so this check is the only source. It needs `frontmatter.yaml` to pass first.
- Reading the result: `not-a-string`, `empty` and `too-long`, as in `frontmatter.description`; `data.length` and `data.utf16_length` are its lengths, or null when the field is absent.
- Goes to: `frontmatter-description`, and `size-limits-and-budgets` for the lengths.

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
- `runtime-contract`: the `claude plugin validate --json` output; the component inventory from `claude plugin details`; the name each skill registers under and its source, from `/context` and `/skill-doctor`; the `frontmatter.yaml` result; which referenced files and links exist and stay inside the skill folder; reference depth and unreferenced files; symlinks and their targets; plugin variables in a skill outside a plugin; `allowed-tools` entries against the injected commands; each script the Markdown runs and whether its file exists; archive listings; the skill's frontmatter hooks by event, matcher and command, with the path variable each command uses; the hooks of the skill's own plugin by event and matcher, marking those that match `Skill` or `UserPromptExpansion`; every skill name the body tells Claude to invoke or stack, with whether it resolves in the plugin or its dependencies and that skill's `disable-model-invocation`, `user-invocable`, `context`, `agent` and `background` values; every subagent in the plugin that preloads or invokes the skill, with its `tools`, `disallowedTools` and `skills`; the plugin's `dependencies`, its marketplace entry and `allowCrossMarketplaceDependenciesOn`, and each dependency's source type and the tags that satisfy its range; the plugin's load errors and notes from `claude plugin list --json`; the plugin's `engines` range.
- `size-limits-and-budgets`: where the body's first 5,000 tokens end; the always-on and on-invoke token estimates from `claude plugin details`; the skill's listing cost after the budget from `/skill-doctor`, and the Skills total from `/context`; character counts of `name`, `description`, `when_to_use` and `compatibility`, and where the 1,536th character of `description` plus `when_to_use` falls, from the `frontmatter.name`, `frontmatter.description`, `frontmatter.compatibility` and `frontmatter.listing-cap` results; the body's line and approximate token counts; line counts of supporting files and which references over 100 lines lack a table of contents; bundle size and file count; the source's frontmatter hook count and total matcher characters; the length of any preload list shipped with the skill.
- `knowledge-delta`: no mechanical result of its own; only the `/doctor prompt-audit` leads.
- `task-mechanisms`: no mechanical result of its own; only the `/doctor prompt-audit` leads.
- `frontmatter-description`: the `claude plugin validate --json` output; the `frontmatter.yaml`, `frontmatter.plain-values`, `frontmatter.name`, `frontmatter.name-plain`, `frontmatter.description`, `frontmatter.listing-cap` and `frontmatter.compatibility` results; the frontmatter's keys and values as parsed; the descriptions of the skill's sibling skills; whether each field is valid on each target surface.
- `comprehension`: where the body's first 5,000 tokens end; capitalized absolutes; time-sensitive wording.
- `feature-fit`: the mode, with or without an environment; the paths of the environment's Markdown instruction files (every CLAUDE.md and CLAUDE.local.md level, rules with their `paths`, other skills with their names and descriptions, and subagents), with the contents of any outside the working directory, such as `~/.claude/`, read for it; the hooks by event, matcher and source; the installed plugins with their scope and whether each is enabled, from `claude plugin list --json`; the MCP server names; the permission rules; and the active output style. Extract these from settings and MCP files without their values, and never pass the reviewer a settings, MCP or credential file.
- `scripts`: the inventory of code files in the skill's folder, at the plugin level, in `bin/` and run by its hooks, each with its path and language; each one's first line and executable bit; each script the Markdown runs, with its interpreter and whether the file exists; the scripts each hook command runs; Python imports outside the standard library with no inline dependency declaration; external commands a script calls that neither the Markdown nor `compatibility` mentions; package installs in scripts, global or local; the packages `claude plugin list --json` notes as not installed; network and credential signals in scripts, by file and line, never with a value; and the output of any linter run on the scripts, such as ShellCheck or Ruff, or the name of each linter not run.
