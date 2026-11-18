# Phase 4: Scripts and hooks

How to write the scripts, injected commands and hooks phase 2 chose and phase 3 designed: how the body names and calls each script, how it starts, the dependencies it states, the rules for injected commands, and how a skill hook is configured.

## Contents

- Run or read, and the script list
- How the body reaches it
- How it starts
- Dependencies
- Injected commands
- Skill hooks

## Run or read, and the script list

Say in the body whether the model runs the script or reads it:

- **Run** it for its result, the usual case: "Run `python3 scripts/split_pages.py scan.pdf` to get one image per page."
- **Read** it when its logic is the knowledge: "Read `scripts/tax_rounding.py` for how each country rounds tax lines."

List every script the skill bundles in the body, each with a one-line purpose, its output format when structured, and its command beneath it, so the model never browses `scripts/` to find one. In `SKILL.md` of a Claude Code skill:

````markdown
**Scripts** (requires Python 3.10 or later)

- `to_csv.py`: extracts an invoice's line items; writes CSV.

  ```bash
  python3 ${CLAUDE_SKILL_DIR}/scripts/to_csv.py [input-pdf] [output-csv]
  ```

- `check_totals.py`: checks that the line items add up to the invoice total; prints one line per mismatch.

  ```bash
  python3 ${CLAUDE_SKILL_DIR}/scripts/check_totals.py [output-csv]
  ```
````

## How the body reaches it

- **In Claude Code**, write the path with the variable for its location, so it resolves from any working directory: `CLAUDE_SKILL_DIR` for the skill's folder, `CLAUDE_PLUGIN_ROOT` for the plugin's, `CLAUDE_PROJECT_DIR` for the project's. Write each with a dollar sign and braces, in `SKILL.md` only: Claude Code replaces them there and not in a reference file, so keep a command that uses one in `SKILL.md`, or have `SKILL.md` give the reference the resolved path.
- **Outside Claude Code**, write the path relative to the skill root, with forward slashes.
- **To run without a permission prompt**, write the command in the body exactly as the `allowed-tools` rule writes it, the same variable in both:

```yaml
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/render_chart.py *)
```

```markdown
Run `python3 ${CLAUDE_SKILL_DIR}/scripts/render_chart.py sales.csv` to render the chart.
```

## How it starts

- **Called through its interpreter** (`python3 scripts/x.py`, `bash scripts/x.sh`): it needs no shebang and no executable bit. The safest form for a skill's own scripts.
- **Called by path, from `bin/`, or by a hook that names the file**: it needs a shebang through `/usr/bin/env`, such as `#!/usr/bin/env python3`, and mode 755. Without them the call fails, and a failing hook lets the action through unchecked.
- **Call Python as `python3`.** It is the name macOS and most Linux systems guarantee; `python` may be missing.

## Dependencies

- State in the body, where the script is introduced, every interpreter, package and tool it needs.
- Pin versions in one-off commands, such as `uvx black@24.10.0 .`, so a new release doesn't change the result.
- Install nothing globally; install into the skill's or the project's environment.

## Injected commands

- Inject only commands that must succeed for the skill to make sense. Any non-zero exit aborts the skill, except exit 1 from a search or comparison command such as `grep` or `diff`. Append `|| true` to any other command that can legitimately exit non-zero, such as a check that reports problems.
- Pre-approve each injected command in `allowed-tools`.
- Write the body so it still works, or says clearly what is missing, where the command didn't run.

The exclamation mark runs a command only at a line's start or after a space, and `|| true` keeps a check that reports problems from aborting the skill:

```markdown
Inert, the mark follows a character: KEY=!`git branch --show-current`
Runs, the mark follows a space: - Branch: !`git branch --show-current`
Runs without aborting on findings: - Totals: !`python3 ${CLAUDE_SKILL_DIR}/scripts/check_totals.py out.csv || true`
```

## Skill hooks

```yaml
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: python3
          args: ["${CLAUDE_PLUGIN_ROOT}/scripts/check_output.py"]
```

Naming the interpreter as the command, with the script in `args`, passes the path as one argument and spares the script a shebang.

- **Paths**: a hook resolves `CLAUDE_PROJECT_DIR`, and in a plugin `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA`. It doesn't resolve `CLAUDE_SKILL_DIR`, so a project skill's hook reaches its script through the project root, and a personal skill's hook through its home path in a `command` with no `args`, such as `python3 ~/.claude/skills/[name]/scripts/check.py`, where `[name]` is the skill's folder: only the shell expands `~`.
- **Once**: set `once: true` on a hook that must run a single time, such as a setup check; Claude Code removes it after its first successful run.

Before writing the hook's script, consult https://code.claude.com/docs/en/hooks for the event's input and the decisions it can return.
