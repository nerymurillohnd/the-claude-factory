# Phase 2: Scripts

Whether the skill needs scripts, what each one does, where it lives, its language and interface, how it starts, and how the body calls it.

## Contents

- [Gotchas](#gotchas)
- [Decide whether the skill needs a script](#decide-whether-the-skill-needs-a-script)
- [Where a script lives](#where-a-script-lives)
- [Language and dependencies](#language-and-dependencies)
- [How a script starts](#how-a-script-starts)
- [The interface Claude meets](#the-interface-claude-meets)
- [How the body calls a script](#how-the-body-calls-a-script)
- [Examples](#examples)
- [Official sources](#official-sources)

## Gotchas

- In Claude Code, a command runs in the session's working directory, which moves each time Claude runs `cd`. A bare `scripts/check.py` resolves only by chance: write the path with the variable of its location. The Agent Skills guide's relative paths hold only where the agent runs from the skill root, as in an upload.
- Claude Code replaces path variables only in `SKILL.md` and in the `Bash(...)` rules of `allowed-tools`. A reference file shows them as literal text, and a script doesn't receive them in its environment: keep every command that uses one in `SKILL.md`, and have a script find its own files from its own location.
- A plugin installed from a marketplace runs from a cached copy of its folder, and `${CLAUDE_PLUGIN_ROOT}` changes with each version. A path that leaves the plugin, such as `../shared/`, doesn't exist in that copy, and anything a script writes to the plugin folder is lost on the next update: write state to `${CLAUDE_PLUGIN_DATA}`.
- claude.ai and Cowork don't install a plugin with a top-level `bin/`. A plugin that must reach them keeps its executables in `scripts/`.
- A script runs unread: only its output enters the context. A prompt for input hangs the run, and a long output reaches Claude as a file path and a short preview, or as a head-and-tail excerpt when the script fails, so Claude decides on what it gets.
- An upload to the Claude API runs scripts with no network and no package installs. claude.ai can install packages from npm and PyPI.

## Decide whether the skill needs a script

Write a script for a step that must give the same result every time, that Claude would rewrite on each run, or that a small slip breaks: an exact sequence, a strict format, a calculation, a destructive operation. Keep a step as instructions when it needs judgment, such as choosing, wording or reviewing meaning: a script only hides that judgment. A command Claude types correctly from memory needs no script; write it in the body. When an existing package already does the step, run it as a one-off command with its version pinned, such as `npx eslint@9.0.0 --fix .`, and move it into a script once it grows too complex to get right on the first try.

| The step | What the script does |
| :-- | :-- |
| Check that the input or output meets rules | Validate, and report each violation with what was expected |
| Confirm a precondition before acting | Check the branch, a file, a version or a credential's presence |
| Prove the result works | Run the tests or a smoke run, and report pass or fail |
| Produce a file from data | Generate it from a template or a schema |
| Rebuild or replace files in bulk | Regenerate them, with a `--dry-run` that lists the changes |
| Get data from outside | Download or query it, and save it where the skill states |
| Change something beyond the conversation | Act: deploy, publish, call an API, behind an explicit flag |
| Find the mechanical part of a review | List the matches, the counts or the diffs, so Claude judges only what needs judgment |

Let the skill type weigh the choice:

- A reference or background knowledge skill rarely needs one: its job is knowledge Claude applies.
- A task skill needs one for each of its steps that matches a row of the table.
- A user-only task skill with side effects puts each side effect in a script with a `--dry-run`, and its body runs the dry run first.
- A forked task skill returns only its result, so its script's output must carry what the result needs.

## Where a script lives

**A. The skill's own `scripts/`**

The default, for a script one skill uses. It travels with every copy of the skill, from a personal folder to an upload. The body reaches it with `${CLAUDE_SKILL_DIR}`.

**B. The plugin root's `scripts/`**

For a script that several skills of one plugin share, that a hook also calls, or that belongs to a skill whose `SKILL.md` sits at the plugin root. The body reaches it with `${CLAUDE_PLUGIN_ROOT}`, and the skill then works only inside its plugin.

**C. The plugin's `bin/`**

For a tool Claude calls by name: Claude Code puts `bin/` on the Bash tool's `PATH` while the plugin is enabled, after the user's own entries, so it can't shadow a system command. Use it only for a plugin that never needs claude.ai or Cowork.

**D. Hook scripts**

A hook's script lives in the project's `.claude/hooks/` or in the plugin's `hooks/`, and the hook reaches it with `${CLAUDE_PROJECT_DIR}` or `${CLAUDE_PLUGIN_ROOT}`. No hook runs a skill: a hook can add context that tells Claude to invoke one, and it can block a skill's invocation or add context to it. A skill can also declare its own hooks. Design the hook itself in the hooks file of Phase 2.

**E. The user's project**

For a project skill, call the project's own scripts through its runner, such as `npm run check`, with the versions its lockfile pins. A plugin skill relies on a project script only when its body states that the project must provide it.

Keep every script inside the skill or its plugin: users receive only that folder.

## Language and dependencies

Choose the language by who runs the skill:

- A personal or project skill: the project's language and toolchain, which the user already has and maintains.
- A plugin for third parties: an interpreter every user has, because it runs on machines you never see. Prefer POSIX `sh` or bash and the Python 3 standard library. On macOS, bash is an old version and the tools are BSD, so avoid GNU-only options such as `sed -i` without a suffix, `grep -P` and `readlink -f`. Use forward slashes in every path, and run shell scripts on Windows only through Git Bash, in a plugin that declares Windows support.

Keep dependencies to what each surface can run:

- Prefer the standard library. A script with no dependencies runs everywhere the interpreter exists.
- When a package is needed, declare it inside the script with its version pinned: PEP 723 metadata run with `uv run`, or `npm:` imports run with `deno run`. State in the body that the runner is required.
- A plugin's Node.js packages go in its `package.json` with an npm lockfile: Claude Code installs registry packages pinned to exact versions when it caches the plugin, without running their install scripts. Install anything else, such as Python packages, from a hook into `${CLAUDE_PLUGIN_DATA}`.
- Install nothing globally: install into the skill's, the plugin's data or the project's environment.
- For a skill that must also run as an upload to the Claude API, use only the standard library or packages that surface already provides.
- State in the body, where the script is introduced, every interpreter, package and tool it needs, and list them in the plugin's prerequisites. For a skill that is also uploaded, put the runtime requirements in the `compatibility` field too, as the frontmatter file of Phase 2 shows: Claude Code accepts it without acting on it, and it travels with the upload.

## How a script starts

- Through its interpreter: `python3 [path]` or `bash [path]`. The script needs no shebang and no executable bit, so this is the form for a skill's own scripts. Call Python as `python3`, the name macOS and Linux provide; `python` may be missing.
- By its own path, from `bin/`, or as a hook's command: the script needs a shebang through `/usr/bin/env`, such as `#!/usr/bin/env python3`, and mode 755 committed to the repository. Without either, the call fails.

## The interface Claude meets

Claude reads the script's output to choose its next step, so design the output for that reader:

- Take every input as an argument, a flag, an environment variable or standard input, never as a prompt.
- Give `--help` the purpose, the arguments, the exit codes and one example: it is how Claude learns the interface.
- Handle what the script can recover from, and report what it did. Fail on anything else with what failed, what was expected and what to try: `--format must be json, csv or table; received xml`.
- Write results to standard output in a fixed shape, such as JSON or CSV, and progress and warnings to standard error.
- Reject ambiguous input with a clear error instead of guessing, and accept closed sets of values where you can.
- Give each failure type its own exit code: not found, invalid argument, missing tool.
- Make a second run safe, because Claude retries: create only what doesn't exist yet.
- Give a destructive or stateful script a `--dry-run`, and require an explicit flag to really act.
- Keep the default output short, with more behind a flag such as `--offset`, or in a file named by `--output`.
- Give each constant a comment that says why it has its value, so neither Claude nor a maintainer has to guess.

## How the body calls a script

Write each path with the variable of the script's location:

| Where the skill or script lives | The path the body writes |
| :-- | :-- |
| The skill's `scripts/`, in any location of Claude Code | `${CLAUDE_SKILL_DIR}/scripts/[file]` |
| The plugin root's `scripts/` | `${CLAUDE_PLUGIN_ROOT}/scripts/[file]` |
| The plugin's `bin/` | The tool's bare name |
| The project | The project's runner, or `${CLAUDE_PROJECT_DIR}/[path]` |
| An upload to claude.ai or the Claude API | `scripts/[file]`, relative to the skill root |

- For a skill that targets Claude Code and an upload, write the Claude Code form, and say in the body that where the variable shows unreplaced, the path is relative to the skill's folder.
- To run a script without a permission prompt, write the same command, with the same variable, in the body and in an `allowed-tools` rule. Write the rule as the frontmatter file of Phase 2 shows.
- Say whether Claude runs the script or reads it. Run it for its result, the usual case. Read it only when its logic is the knowledge the step needs.
- List every bundled script in the body, each with its purpose, its output format and its command, so Claude never has to browse `scripts/`.
- Show each command in the body as the embedding file of Phase 2 shows. To run a script as the skill loads, read the injected commands file of Phase 2.


## Examples

```markdown
<!-- Weak: resolves only while the working directory is the skill's folder -->
Run `python3 scripts/check_totals.py out.csv`.

<!-- Strong -->
Run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_totals.py out.csv`.

<!-- Weak: leaves the plugin, so it doesn't exist in the installed copy -->
Run `bash ${CLAUDE_SKILL_DIR}/../../shared/build.sh`.

<!-- Strong: the shared script lives at the plugin root -->
Run `bash ${CLAUDE_PLUGIN_ROOT}/scripts/build.sh`.

<!-- Weak: installs globally, with no version, and assumes `python` -->
Run `pip install pypdf`, then `python scripts/fill.py form.pdf`.

<!-- Strong: the dependency is pinned inside the script, and the body names the runner -->
Run `uv run ${CLAUDE_SKILL_DIR}/scripts/fill.py form.pdf`. It requires `uv`; the script declares `pypdf>=5,<6`.

<!-- Weak: the script asks for the environment, and the run hangs -->
Run `python3 ${CLAUDE_SKILL_DIR}/scripts/deploy.py` and choose the environment.

<!-- Strong -->
Run `python3 ${CLAUDE_SKILL_DIR}/scripts/deploy.py --env staging --dry-run`, then again without `--dry-run` once the user approves the plan it prints.
```

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide: each holds the full rules, edge cases and version notes this file leaves out.

- Read [Using scripts in skills](https://agentskills.io/skill-creation/using-scripts#designing-scripts-for-agentic-use) when you design a script's interface. It gives the `--help`, error, output and exit-code patterns, with examples.
- Read [One-off commands](https://agentskills.io/skill-creation/using-scripts#one-off-commands) when an existing package already does the step. It shows `uvx`, `pipx`, `npx`, `bunx`, `deno run` and `go run`, each with a pinned version and the tool it needs installed.
- Read [Self-contained scripts](https://agentskills.io/skill-creation/using-scripts#self-contained-scripts) when a script needs a package. It shows inline dependencies for Python, Deno, Bun and Ruby, and how to pin them.
- Read [Advanced: Skills with executable code](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#advanced-skills-with-executable-code) when a script validates, plans or acts in bulk. It shows explicit error handling, verifiable intermediate files and each surface's runtime limits.
- Read [Generate visual output](https://code.claude.com/docs/en/skills#generate-visual-output) when you want a whole skill that bundles and runs a script. It shows the folder, the `SKILL.md` and the Python script of a working skill.
- Read [Available string substitutions](https://code.claude.com/docs/en/skills#available-string-substitutions) when the body calls a script with a path variable. It lists each variable, where Claude Code replaces it, and the `allowed-tools` pattern that runs a script without a prompt.
- Read [Executables](https://code.claude.com/docs/en/plugins/components#executables) when a plugin puts a tool on the `PATH`. It shows `bin/` and the surfaces that refuse it.
- Read [Reference plugin paths and store data](https://code.claude.com/docs/en/plugins/components#path-variables-and-persistent-data) when a plugin script stores state or dependencies. It explains `${CLAUDE_PLUGIN_ROOT}` across updates and `${CLAUDE_PLUGIN_DATA}`, with a hook that installs packages.
- Read [Node.js package dependencies](https://code.claude.com/docs/en/plugins/loading#node-js-package-dependencies) when a plugin script needs npm packages. It gives the lockfiles Claude Code reads and the limits of its install.
- Read [Reference scripts by path](https://code.claude.com/docs/en/hooks#reference-scripts-by-path) when a hook calls a script. It gives the variables a hook resolves and when to use the exec form.
