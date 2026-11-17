# Scripts and hooks

When a skill should run code, where that code lives so it is found on every machine, how the model calls it, and how injected commands and skill hooks behave.

## Contents

- When a script earns its place
- Where a script lives
- Reaching the script
- The interface the model meets
- Dependencies and portability
- Injected commands
- Hooks in a skill

## When a script earns its place

Write a script when the operation:

- must give the same result every run: parsing, validating, converting, computing;
- would otherwise be rewritten by the model on every run, as seen when test runs keep producing the same helper;
- is fragile: an exact sequence, a format a small error breaks, a destructive step.

Keep it as instructions when the step needs judgment: choosing, wording, reviewing. A script only moves the judgment out of sight.

Running a script costs only its output; its code never enters context. Tell the model which it should do:

- **Run it** (most scripts): "Run `python scripts/analyze_form.py input.pdf` to extract the fields."
- **Read it** (when the logic itself is the knowledge): "Read `scripts/analyze_form.py` for the field-extraction algorithm."

A short command the model can type from memory, such as `git log --oneline -20`, needs no script: write the command in the body.

## Where a script lives

Choose by who must reach it and where the skill travels.

**Inside the skill folder** (`scripts/` or a subfolder): travels with the skill to every surface, upload and copy. The default for any script one skill uses.

```text
my-skill/scripts/validate.py
→ body: Run `python "${CLAUDE_SKILL_DIR}/scripts/validate.py" out/`   (Claude Code)
→ body: Run `python scripts/validate.py out/`                          (claude.ai, API)
```

**At the plugin level**, shared by several skills of one plugin: reached through the plugin root. The skill is no longer self-contained: uploaded or copied alone, it loses the script.

```text
my-plugin/scripts/common.sh
→ body: Run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/common.sh"`
```

**In the plugin's `bin/`**: Claude Code puts `bin/` on the PATH of the shell it runs commands in while the plugin is enabled, so the model runs the tool by name. Use it for a command-line tool the plugin offers to several skills or to the user.

```text
my-plugin/bin/lint-skill
→ body: Run `lint-skill path/to/skill`
```

**In the user's project**: reached through the project root. Use it only when the script belongs to the project and the skill is a project skill, or when the skill tells the user to provide it; state that prerequisite.

```text
<project>/.claude/scripts/release.sh
→ body: Run `bash "${CLAUDE_PROJECT_DIR}/.claude/scripts/release.sh"`
```

**Outside the plugin**: never. Installing a plugin copies only its own folder into a cache. A path above the plugin root does not exist on users' machines. Symlinks to a file elsewhere in the plugin are kept; to a file elsewhere in the same marketplace repository they are replaced with a copy; to anything outside the marketplace they are skipped.

Incorrect:

```text
my-plugin/skills/deploy/SKILL.md   → Run `bash ../../../shared/deploy.sh`
~/.claude/skills/report/SKILL.md   → Run `python ~/work/tools/build_report.py`
```

The first fails after installation; the second works only on the author's machine.

Never write state next to a plugin script: the install folder is replaced on every update. Use the plugin data folder; read [components.md](components.md) for setup and state.

## Reaching the script

- `CLAUDE_SKILL_DIR`, `CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA`, written with a dollar sign and braces, are replaced in the skill body and in `allowed-tools` Bash rules before the model reads them. They are not environment variables in the model's shell. The plugin ones exist only in plugin skills.
- Quote every substituted path: install folders can contain spaces.
- Without these variables (claude.ai, the API), write paths relative to the skill root with forward slashes.
- To run a bundled script without a permission prompt, write the same path in the rule and in the body:

```yaml
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/render.py *)
```

```markdown
Run `python3 ${CLAUDE_SKILL_DIR}/scripts/render.py data.csv` to render the chart.
```

## The interface the model meets

The model reads a script's output to decide its next step. Design for that reader:

- **No interactive prompts.** The model's shell can't answer one, so the run hangs. Take every input as an argument, a flag, an environment variable or stdin.
- **`--help`** that states the purpose, arguments, flags and one example. The model reads it to learn the interface instead of the code.
- **Errors that say what failed, what was expected and what to try**: "Field 'signature_date' not found. Available fields: customer_name, order_total, signature_date_signed."
- **Structured output on stdout** (JSON, CSV or a fixed text shape) and diagnostics on stderr, so the result can be parsed and piped.
- **Exit codes with meaning**: 0 for success, distinct non-zero codes for distinct failures, documented in `--help`.
- **Handle errors in the script.** Create a missing file with a default, fall back on a permission error, and report what happened; don't stop and leave the model to guess.
- **Idempotent**: running it twice gives the same result, because the model retries.
- **Safe defaults and a dry run** for anything destructive: `--dry-run` shows what would change; destruction needs an explicit flag such as `--confirm`.
- **Bounded output**: summarize by default; offer `--verbose` or an output file for full detail. Long output may be truncated before the model sees it.
- **Every constant explained**: a comment on why the timeout is 30 seconds or the retry count is 3. A value with no reason can't be adjusted by the model or the next author.

## Dependencies and portability

- State each prerequisite in `SKILL.md` where the script is introduced: interpreter version, packages, system tools.
- Pin versions in one-off commands so a new release doesn't change behavior: `uvx ruff@0.8.0 check .`, `npx eslint@9 .`.
- For a Python script with packages, declare them inline (PEP 723) and run it with `uv run`; Deno, Bun and Ruby have equivalents. Otherwise prefer the standard library.
- Never install packages globally from a skill; install into the skill's or project's environment.
- Check what each target surface provides: the Claude API has no network and only preinstalled packages; claude.ai can install from npm and PyPI depending on settings; Claude Code has the user's machine.
- Write shell scripts for POSIX sh or bash, with forward slashes. On Windows they run through Git Bash; say so where the skill states its requirements.

## Injected commands

An injected command runs when the skill loads, in Claude Code only, and its output replaces it before the model reads the body. Use one to hand the model current data it would otherwise fetch with a tool call: the diff, the branch, the PR comments.

Forms:

- Inline: an exclamation mark directly before a backtick command, at the start of a line or after whitespace. After any other character it stays literal text.
- Block: a fenced code block opened with three backticks followed by an exclamation mark, for several commands.

Behavior to design for:

- A failing command aborts the whole invocation; the model never sees the skill. Any non-zero exit fails, except exit code 1 from search and comparison commands. Append `|| true` to a command that can legitimately exit non-zero.
- Commands run in the session's current working directory, under the shell tool's 2-minute timeout; stderr is merged into the output with bash. Use a path variable for anything that must resolve the same way every time.
- They never prompt: a command a deny or ask rule matches aborts the invocation, and outside auto mode so does one no rule allows. Pre-approve each one with `allowed-tools`.
- Output is not re-scanned, so a command can't inject another command.
- They don't run in Cowork, in synced skills in a terminal session, on claude.ai or through the API, and administrators can disable them with `disableSkillShellExecution`. Write the body so it still works, or fails clearly, when the output is missing.

## Hooks in a skill

A skill's `hooks` frontmatter registers hooks when the skill is invoked; they then run for the rest of the session, not only during the skill's turn. Use them for a check that must hold every time once the skill is active, such as validating each file the model writes.

```yaml
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: '"${CLAUDE_PLUGIN_ROOT}/scripts/check-output.sh"'
          once: true
```

- `once: true` removes a hook after its first successful run; a failure, a block or a timeout keeps it. It works only in skill frontmatter.
- Hook commands resolve `CLAUDE_PROJECT_DIR`, and in plugins `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA`. Point a plugin skill's hook at a script under the plugin root, and a project skill's at a script under the project. Prefer the exec form with `args` when a command contains a path variable; in the shell form, double-quote each variable.
- Under an organization's `strictPluginOnlyCustomization` lock on hooks, only plugin, bundled and managed skills keep their frontmatter hooks, and a personal or project skill with `hooks` also loses its `allowed-tools`. Ship hooks that must work everywhere in a plugin.
- Since v2.1.304, each source of skills (the project, the personal folder, each plugin) can register at most 1,024 hooks with 16,384 characters of matchers per session; past that, the skill registers none of its hooks.
- A hook that must run whether or not the skill was invoked belongs in the plugin's `hooks/hooks.json` or in settings, not in the skill.
- A project skill's frontmatter hooks register even in a `-p` run in an untrusted folder; keep them to checks a user would expect from reading the skill.

Before writing a hook's script, input handling or output, consult https://code.claude.com/docs/en/hooks for the event's input fields and the decisions it can return.
