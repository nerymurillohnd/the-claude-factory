# Scripts and hooks

When a skill should run code, where the code lives so every user's machine finds it, how the body calls it, and when an injected command or a skill hook fits.

## Contents

- Script or instructions
- Where the script lives
- How the body reaches it
- How it starts
- The interface the model meets
- Dependencies
- Injected commands
- Skill hooks

## Script or instructions

Write a script when the step is deterministic, when the work you extracted shows the model rewriting the same helper each time, or when a small slip breaks it: an exact sequence, a strict format, a destructive operation. Keep a step as instructions when it needs judgment, such as choosing, wording or reviewing: a script only hides the judgment.

Say in the body whether the model runs the script or reads it:

- **Run** it for its result, the usual case: "Run `python3 scripts/split_pages.py scan.pdf` to get one image per page."
- **Read** it when its logic is the knowledge: "Read `scripts/tax_rounding.py` for how each country rounds tax lines."

A command the model can type correctly from memory needs no script; write it in the body.

## Where the script lives

Choose by who must reach it, and where the skill travels:

- **Inside the skill folder** (`scripts/`): travels with the skill to every copy and upload. The default for a script one skill uses.
- **At the plugin level**, shared by several skills of one plugin: reached through the plugin root. The skill then works only inside its plugin.
- **In the plugin's `bin/`**: Claude Code puts it on the shell's PATH while the plugin is enabled, so the body calls the tool by name. Use it for a command-line tool several skills or the user call, and only for a plugin that never needs claude.ai or Cowork: neither installs a plugin that has a `bin/` folder.
- **In the user's project**: only for a project skill, or when the skill states the project must provide it.
- **Outside the plugin**: never. Installing a plugin copies only its own folder, so a path above the plugin root doesn't exist on users' machines.

Incorrect:

```text
my-plugin/skills/deploy/SKILL.md   →  Run `bash ../../../shared/deploy.sh`
~/.claude/skills/report/SKILL.md   →  Run `python3 ~/work/tools/build_report.py`
```

The first breaks after installation; the second works only on its author's machine.

## How the body reaches it

- **In Claude Code**, write the path with the variable for its location, so it resolves from any working directory: `CLAUDE_SKILL_DIR` for the skill's folder, `CLAUDE_PLUGIN_ROOT` for the plugin's, `CLAUDE_PROJECT_DIR` for the project's. Write each with a dollar sign and braces.
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

## The interface the model meets

The model reads the script's output to choose its next step. Design for that reader:

- No interactive prompts: the model can't answer one, and the run hangs. Take every input as an argument, flag, environment variable or standard input.
- A `--help` that states the purpose, the arguments and one example.
- Errors that say what failed, what was expected and what to do: "Column 'net_amount' not found in invoices.csv. Columns found: invoice_id, date, gross_amount, tax."
- Results on standard output in a fixed shape (JSON, CSV or set lines); diagnostics on standard error.
- Exit codes that mean something, listed in `--help`.
- Errors handled inside the script, with a report of what it did, instead of a failure the model must interpret.
- Safe to run twice, because the model retries.
- A `--dry-run` for anything destructive, and an explicit flag to really do it.
- Short output by default, with detail behind a flag or in a file.
- A comment on each constant saying why it has that value.

## Dependencies

- State in the body, where the script is introduced, every interpreter, package and tool it needs.
- Pin versions in one-off commands, such as `uvx black@24.10.0 .`, so a new release doesn't change the result.
- Prefer the standard library. For packages, declare them inside the script where the language allows it, such as inline metadata run with `uv run`.
- Install nothing globally; install into the skill's or the project's environment.
- Write shell scripts for bash or POSIX sh, with forward slashes. A skill that supports Windows runs them through Git Bash; state that requirement.

## Injected commands

In Claude Code, an injected command runs when the skill loads and its output replaces it in the body. Use one to hand the model current data it would otherwise fetch first, such as the diff, the branch or open pull requests.

- Inject only commands that must succeed for the skill to make sense. Append `|| true` to one that can legitimately exit non-zero, such as a check that reports problems.
- Pre-approve each injected command in `allowed-tools`.
- Write the body so it still works, or says clearly what is missing, where the command didn't run.

## Skill hooks

A hook in the skill's `hooks` field registers when the skill is invoked and runs for the rest of the session. Use one for a check that must hold on every event once the skill is active, such as validating each file the model writes. A check that must hold whether or not the skill was invoked belongs in the plugin's hooks or in settings instead.

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

- **Paths**: a hook resolves `CLAUDE_PROJECT_DIR`, and in a plugin `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA`. It doesn't resolve `CLAUDE_SKILL_DIR`, so a skill hook outside a plugin reaches its script through the project root.
- **Once**: set `once: true` on a hook that must run a single time, such as a setup check; Claude Code removes it after its first successful run.

Before writing the hook's script, consult https://code.claude.com/docs/en/hooks for the event's input and the decisions it can return.
