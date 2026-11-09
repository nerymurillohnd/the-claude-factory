# Scripts

When to bundle a script, how to reference and call it on each surface, how to declare its dependencies, and how to design it for an agent.

## Contents

- [When to bundle](#when-to-bundle)
- [How to reference](#how-to-reference)
- [How to call a script](#how-to-call-a-script)
- [Self-contained dependencies](#self-contained-dependencies)
- [Design for an agent](#design-for-an-agent)

## When to bundle

Bundle a tested script when the agent keeps rewriting the same logic or an operation must be deterministic; scripts are more reliable than generated code, and only their output costs tokens \[AS\]\[PL\].

If execution traces show the agent reinventing the same helper (charts, parsers, validators) on every run, write it once in `scripts/` \[AS\]. Prefer `validate_form.py` over asking Claude to generate validation code \[PL\]. A one-off pinned command (`npx eslint@9.0.0`, `uvx ruff@0.8.0`) is fine until it gets hard to get right first time \[AS\].

## How to reference

- **List and show the command.** List the scripts in `SKILL.md` with one line each, then show the exact command; paths are relative to the skill root \[AS\].
- **State prerequisites** ("Requires Node.js 18+") instead of assuming them \[AS\]\[PL\].

## How to call a script

- **Through `${CLAUDE_SKILL_DIR}` in Claude Code.** In Claude Code, commands run in the session's directory, never the skill's, so reach a script through `${CLAUDE_SKILL_DIR}` \[CC\].
- **Interpreter prefix by default.** Call it with its interpreter as a prefix: `python3 ${CLAUDE_SKILL_DIR}/scripts/<file>`, or `bash ${CLAUDE_SKILL_DIR}/scripts/<file>` for a shell script `default`. The official pages show both forms: the interpreter prefix in the skills page's codebase-visualizer example \[CC\] and in "Add scripts" \[CP\], and direct execution in the skills page's `allowed-tools` example (`${CLAUDE_SKILL_DIR}/scripts/render.sh`) \[CC\]. So the default is a design choice, not a rule; the prefix is chosen because it doesn't depend on the executable bit.
- **Shebang and executable bit.** Still give every script a `#!/usr/bin/env <interpreter>` line and the executable bit \[SD\] `default`.
- **Direct execution is the exception.** Direct execution is the documented exception; a skill that uses it pre-approves it with its own pattern ([claude-code-features.md](claude-code-features.md#substitutions-and-pre-approved-tools)).
- **Uploads and the API.** For a claude.ai upload or the API, call the script through its interpreter with a path relative to the skill (`python3 scripts/<file>`), because a zip upload can lose the executable bit and the Platform docs show only relative paths \[SD\] `default`.

## Self-contained dependencies

- **Declare them inline.** PEP 723 for Python (`uv run`), `npm:` specifiers for Deno, versioned imports for Bun, `bundler/inline` for Ruby; pin versions \[AS\].
- **Installing packages depends on the surface.** The Platform's best-practices page shows "Install required package: `pip install pypdf`" \[PL\], while its overview says that in Claude Code "Global package installation discouraged" and that the API allows no network or installs \[PL\]. What a skill may install depends on the surface ([surfaces.md](surfaces.md#runtime-limits-by-surface)); for a portable skill prefer self-contained scripts \[AS\].

## Design for an agent

\[AS\]\[PL\]:

- **No interactive prompts.** Agents can't answer a TTY; take flags, env vars or stdin, and fail with usage guidance.
- **A concise `--help`** with flags and examples.
- **Specific error messages** that say what went wrong, what was expected and what to try.
- **Structured output** (JSON, CSV) on stdout; diagnostics on stderr.
- **Safe to repeat.** Idempotent ("create if not exists"), closed input sets, `--dry-run` for destructive operations, documented distinct exit codes, explicit `--confirm` or `--force` for risky actions.
- **Predictable output size.** Default to a summary or a limit with `--offset`, or require `--output`, because harnesses truncate long output.
- **Solve, don't defer.** Handle errors in the script instead of failing and leaving it to Claude \[PL\].
- **No "voodoo constants".** Document why each value is what it is \[PL\].
- **Exit 0 when Claude needs the output.** In Claude Code a failing command reaches Claude inline only up to roughly 10,000 characters, as a head-and-tail excerpt with no file path; a valid result stays inline up to roughly 30,000 characters and past that arrives as a file path plus a 2,000-character preview \[CC\]. So a script whose findings Claude must read prints them, reports problems inside its output, and exits 0; it keeps non-zero exits for "could not run" \[SD\] `req`.
