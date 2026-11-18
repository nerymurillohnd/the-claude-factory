# Phase 2: Scripts

Decide each script and injected command the skill needs, and how the body calls it. This file covers:

- [script or instructions](#script-or-instructions)
- [where a script lives](#where-a-script-lives)
- [the interface the model meets](#the-interface-the-model-meets)
- [language, dependencies and how a script starts](#language-dependencies-and-how-it-starts)
- [how the body calls a script](#how-the-body-calls-a-script)
- [injected commands](#injected-commands)

## Script or instructions

Write a script when the step is deterministic, when the model would rewrite the same helper each time, or when a small slip breaks it: an exact sequence, a strict format, a destructive operation. Keep a step as instructions when it needs judgment, such as choosing, wording or reviewing: a script only hides the judgment. A command the model types correctly from memory needs no script. Write it in the body.

## Where a script lives

- Inside the skill folder, in `scripts/`: travels with every copy and upload. The default for a script one skill uses.
- At the plugin root, in `scripts/`: for a script that several skills of one plugin share, or that a hook also calls. The body reaches it with `${CLAUDE_PLUGIN_ROOT}`, and the skill then works only inside its plugin.
- In the plugin's `bin/`: on the PATH while the plugin is enabled, so the body calls the tool by name. claude.ai and Cowork don't install a plugin with a top-level `bin/`, so a plugin that must reach them keeps its executables in `scripts/`.
- In the user's project: only for a project skill, or when the skill states that the project must provide it.
- Outside the plugin: never. Installing a plugin copies only its own folder.

```text
Incorrect: Run `bash ../../../shared/deploy.sh`        (leaves the plugin; breaks after installation)
Incorrect: Run `python3 ~/work/tools/build_report.py`  (works only on its author's machine)
```

## The interface the model meets

The model reads the script's output to choose its next step.

- No interactive prompts: the model can't answer one, and the run hangs. Take every input as an argument, flag, environment variable or standard input.
- `--help` states the purpose, the arguments and one example.
- Recoverable problems: handle them inside the script and report what it did. Anything else: fail with an error that says what failed, what was expected and what to do.
- Results on standard output in a fixed shape (JSON, CSV or set lines). Diagnostics on standard error.
- Exit codes that mean something, listed in `--help`.
- Safe to run twice, because the model retries.
- A `--dry-run` for anything destructive, and an explicit flag to really do it.
- Short output by default, with detail behind a flag or in a file.
- A comment on each constant saying why it has that value.

## Language, dependencies and how it starts

- Prefer the standard library. Declare other packages inside the script where the language allows it.
- State in the body, where the script is introduced, every interpreter, package and tool it needs.
- Pin versions in one-off commands that fetch a package, so a new release doesn't change the result.
- Install nothing globally. Install into the skill's or the project's environment.
- The Claude API has no network and no runtime package installation. On claude.ai, network and installs depend on the user's and the admin's settings. A skill that must work there uses only the standard library or packages the surface already has.
- Write shell scripts for bash or POSIX sh, with forward slashes. On Windows they run through Git Bash, so state that requirement.
- Call Python as `python3`: macOS and most Linux systems guarantee that name, and `python` may be missing.
- Called through its interpreter (`python3 x.py`, `bash x.sh`): no shebang and no executable bit. The safest form for a skill's own scripts.
- Called by path, from `bin/`, or by a hook that names the file: it needs a shebang through `/usr/bin/env`, such as `#!/usr/bin/env python3`, and mode 755. Without them the call fails.

## How the body calls a script

- In Claude Code, write the path with the variable for its location, so it resolves from any working directory: `${CLAUDE_SKILL_DIR}` for the skill's folder, `${CLAUDE_PLUGIN_ROOT}` for the plugin's (plugin skills only), `${CLAUDE_PROJECT_DIR}` for the project's. The working directory moves whenever Claude runs `cd`, so a bare `scripts/x.py` can fail.
- Claude Code replaces these variables in the skill's `SKILL.md` content and in the Bash rules of `allowed-tools`. Keep each command that uses one in `SKILL.md`.
- Outside Claude Code, write the path relative to the skill root, with forward slashes.
- To run without a permission prompt, write the same variable in the body and in the `allowed-tools` rule, so the rule matches the exact command:

```yaml
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/render_chart.py *)
```

```markdown
Run `python3 ${CLAUDE_SKILL_DIR}/scripts/render_chart.py sales.csv` to render the chart.
```

- Say in the body whether the model runs the script or reads it. Run it for its result, the usual case. Read it when its logic is the knowledge.
- List every script the skill bundles in the body, each with a one-line purpose, its output format when structured, and its command beneath it, so the model never browses `scripts/`:

````markdown
Scripts (requires Python 3.10 or later):

- `to_csv.py`: extracts an invoice's line items and writes CSV.

  ```bash
  python3 ${CLAUDE_SKILL_DIR}/scripts/to_csv.py [input-pdf] [output-csv]
  ```
````

## Injected commands

An injected command runs when the skill loads, and its output replaces it in the body. Use one to hand the model current data it would otherwise fetch first, such as the diff or the branch. It works in Claude Code only.

- Inline form: an exclamation mark directly before a backtick command, at a line's start or after a space. After any other character it stays literal text. For several commands, open a fenced block with three backticks and the mark.
- Inject only commands that must succeed. A failed command aborts the whole skill and Claude never sees its content. Any non-zero exit fails, except exit 1 from search and comparison commands such as `grep` and `diff`. Append `|| true` to any other command that can legitimately exit non-zero, such as a check that reports problems.
- Pre-approve each injected command in `allowed-tools`. Outside auto mode, a command that needs permission aborts the skill.
- Each command runs in the session's current directory, with stderr merged into the output and the Bash tool's 2-minute timeout. Use the path variables.
- Write the body so it still works, or says what is missing, where the command didn't run: outside Claude Code, in skills synced from claude.ai when used in a terminal or VS Code session, and where `disableSkillShellExecution` is on.

```markdown
- Branch: !`git branch --show-current`
- Totals: !`python3 ${CLAUDE_SKILL_DIR}/scripts/check_totals.py out.csv || true`
```

Read [Inject dynamic context](https://code.claude.com/docs/en/skills#inject-dynamic-context) when the skill needs injected commands, including their failure and permission rules.

Read [Using scripts in skills](https://agentskills.io/skill-creation/using-scripts) when you design a script's interface.

Read [Advanced: skills with executable code](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#advanced-skills-with-executable-code) when a script is more than a short helper.

Read [Executables](https://code.claude.com/docs/en/plugins/components#executables) when a plugin puts a tool on the PATH.
