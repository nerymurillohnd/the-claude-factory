# Scripts and hooks

A script gives a skill what instructions can't: the same result every run, at the cost of only its output in context. A hook gives what neither can: a rule the harness applies every time, whatever Claude decides. Claude never reads a script it runs and never sees a hook's code, so everything it needs from either has to come through the interface and the skill's text.

## Contents

- 1. Whether a script earns its place
- 2. Where a script lives
- 3. How `SKILL.md` runs a script, by surface
- 4. The interface Claude meets
- 5. Failures, constants and prerequisites
- 6. Dependencies on each surface
- 7. Portability
- 8. Security
- 9. Testing scripts
- 10. Injected commands
- 11. Hooks
- 12. Questions to ask yourself

## 1. Whether a script earns its place

- Write a script when the same computation must come out the same way every run: parsing a fixed format, transforming data, rendering a file, counting, validating. If Claude would otherwise rewrite that logic on each run, bundle it once, tested.
- Keep judgment out of it. The script returns the facts; the skill tells Claude how to judge them (which changes are breaking, which findings matter, how to phrase a summary).
- Decide whether Claude runs the script or reads it, and say which: "Run `scripts/parse_changelog.py` to get the entries" or "Read `scripts/match.py` for the matching rule." Running is the usual case. A script meant to be read opens with a comment that states what it shows and keeps that logic in one named place.
- List every script in `SKILL.md` with a one-line purpose, the command, and its output format, at the step that uses it, so Claude never has to discover a script by browsing.
- A one-off command too complex to get right first time is a script candidate too.

## 2. Where a script lives

- Put a script only this skill uses inside the skill's own folder. It travels on every route: plugin, personal or project copy, upload, Skills API.
- Put a script several skills of one plugin share at the plugin level, reached through the plugin-root variable. One copy avoids drift; the cost is that it exists only where the whole plugin is installed. A skill that is also uploaded or copied on its own needs its own copy, or must say it runs only inside the plugin.
- Never write state (caches, lock files, virtual environments, downloads) next to the script under the plugin root, which is replaced on every update. Write it to the plugin-data directory, passed to the script as an argument.
- A plugin's `bin/` folder puts executables on the shell's `PATH` in Claude Code, after the user's own entries, so a name that matches a command the user has runs theirs instead. Pick names no common tool uses, and check the plugin docs for surfaces that refuse a `bin/` folder.
- A script that opens its own data files must find them from its own location (`Path(__file__).resolve().parent` in Python, `"$(dirname "$0")"` in shell), never from the working directory or from path variables in its environment: Claude's shell may be anywhere, and those variables aren't set for commands Claude runs.

## 3. How `SKILL.md` runs a script, by surface

The path that reaches a bundled script depends on where the skill runs, so choose its form from the target surfaces and record why in the delivery.

- Agent Skills clients, claude.ai and the API: the open standard writes script paths relative to the skill's root (`python3 scripts/fill_form.py`), because the client runs commands from there and resolves those paths itself.
- Claude Code: each command runs in the session shell's current directory, which moves whenever Claude runs `cd`. A relative path works only while the shell happens to sit in the skill folder. Write `python3 ${CLAUDE_SKILL_DIR}/scripts/fill_form.py` for this skill's own script, or the plugin-root variable for a plugin-level one. These variables are substituted only in `SKILL.md` and in `allowed-tools`, so the command belongs in `SKILL.md`.
- Both: either write the path relative to the skill's root and tell Claude to run it by its absolute path, resolved from the folder that holds `SKILL.md`, or write the variable form and tell Claude what to use where the variable reaches it unsubstituted. State which in the skill, so Claude never runs a bare relative path from a moved shell, or a literal `${...}` string.
- Write the same path in the `allowed-tools` rule as in the command, through the same variable, or the pre-approval doesn't match.

## 4. The interface Claude meets

- No interactive input, ever: an agent's shell can't answer prompts, password dialogs or `[y/N]` menus, and a script that waits hangs. Take input from flags, environment variables or stdin. When a required input is missing, exit with an error that names it and its valid values.
- Give a short `--help`: one-line description, each flag with its default, an example or two, the exit codes. It enters context, so keep it brief.
- Reject ambiguous or unknown input by name; never reinterpret it silently. Prefer named flags and closed sets of values.
- Use distinct exit codes for distinct failures (invalid arguments, missing input, auth failure), documented in `--help`. In Claude Code most commands that exit non-zero count as failures and their output is cut to an excerpt, so report normal findings with exit 0 and the findings in the output.
- Write structured data (JSON, CSV) to stdout and diagnostics to stderr. Injected commands merge stderr into the text, so a script whose output is injected or parsed writes nothing to stderr on success.
- Make reruns safe: create-if-missing rather than fail-on-duplicate. Give destructive or stateful actions a `--dry-run`, and make the destructive path opt-in (`--confirm`), never the default.
- Bound the output: past an inline size limit Claude gets a file path and a preview instead of the answer. Default to a summary, with an option for the rest. Check the current limits on the Claude Code tools reference.
- Write output files to a path given as an argument, and print that path, so Claude can find what the script made.

## 5. Failures, constants and prerequisites

- Handle every predictable failure in the script (missing or unreadable file, empty input, missing tool, network error, malformed record): resolve it when no decision is needed, otherwise exit with a message that says what went wrong, what was expected and what to try. "`--format` must be one of json, csv, table; received xml", never "invalid input" or a bare stack trace. Never swallow a failure that matters, and never substitute a default without saying so.
- Justify every constant that sets behavior (timeouts, retries, thresholds, limits) with a comment or a name, and expose as a flag any value the task may need to change.
- Check at the top of the script for each external command it calls (`jq`, `git`, `gh`), and exit with the tool's name and how to install it. Name the same prerequisites in `SKILL.md` or `compatibility`.

## 6. Dependencies on each surface

- Prefer the standard library. When a package is needed, declare and pin it with the script, for example a PEP 723 block run with `uv run`, so one command installs and runs it, and run it with the command that honors the declaration. Unpinned dependencies change behavior over time.
- The Skills API runs scripts in a container with no network and no package installation: use only what its current environment page lists as preinstalled, with its Python version.
- claude.ai may have full, partial or no network access depending on settings: give network-dependent scripts a stated fallback.
- In Claude Code, install only locally (a virtual environment, the plugin-data directory), never globally, and never edit the user's shell startup files.
- A container has no browser of the user's: a script that opens its output in a browser also prints the file's path, and the skill tells Claude to give the user that path.

## 7. Portability

- A script Claude runs through its interpreter needs no executable bit. One run by path, from `bin/` or by a hook needs an interpreter line through `/usr/bin/env` and the executable bit.
- Write for the operating systems the skill declares. Without a declaration, stay within POSIX shell behavior and avoid tools whose flags differ between GNU and BSD versions (`sed -i`, `readlink -f`, `date -d`).
- Use forward slashes in every path, including in text for Windows users.
- Quote every variable that holds a path or user input.
- Don't rely on an `export` or a `cd` from an earlier command: each command starts fresh. Pass values as arguments.

## 8. Security

A skill's scripts run with the user's permissions, and the user's permission rules for Claude's file tools don't contain a script that opens files itself.

- Never put a credential in a script or a shipped file. Read it from an environment variable the skill names, fail clearly when it's missing, and never print, log or echo it, including in verbose output and error messages.
- Read credential files, settings, keys or `.env` only when the skill's purpose requires it and the skill says so.
- Make no network call, and write nowhere, beyond what the skill states, and name each host it contacts and what it sends. Never download and run code (`curl ... | sh`, `eval` on fetched text).
- Treat every input as untrusted: build commands as argument vectors, never with `eval`, `sh -c` or string-built shell; check that every path taken from input stays where the script means it to, rejecting `..`.

## 9. Testing scripts

- Run every script yourself before delivering: the normal case, an empty input, a malformed record, a missing file, and each destructive path in dry-run mode, checking each exit code and message.
- Keep tests beside the skill in its repository rather than in the shipped folder, unless users need them: shipped tests reach every user and add to the package.

## 10. Injected commands

An injected command (`` !`command` `` or a ```` ```! ```` block) runs while the skill loads, and its output replaces it in the text Claude reads. Use it only for context the skill needs before Claude starts, such as the current branch, and only for Claude Code.

- It doesn't run in claude.ai chat or through the API, and synced routes skip or replace it. Where the skill targets those, put the command in a step Claude runs instead.
- It runs only when the `!` starts a line or follows whitespace.
- Any failure aborts the whole skill. A command expected to exit non-zero on a normal result needs `|| true`.
- It never prompts. A deny rule aborts the skill; outside auto mode, so does any command no rule allows, unless `allowed-tools` pre-approves it. Add the matching rule.
- It runs under the shell tool's timeout and output limits; keep it fast and its output small.
- Escape a literal `$` before a digit or an argument name with a backslash.

## 11. Hooks

- Use a hook only for a rule with zero exceptions (see the scope-and-type guide), and use a `command` or `http` hook: a `prompt` or `agent` hook hands the decision back to a model. Keep the check named in the skill too, with its command, so Claude can run it as it works and isn't surprised when it blocks.
- Choose where it lives by when the rule must hold: the skill's `hooks` frontmatter registers on the skill's first invocation and keeps running for the rest of the session (`once: true` removes it after its first successful run); a plugin's `hooks/hooks.json` applies whenever the plugin is enabled. A frontmatter hook can't act on anything before the invocation, such as this session's start.
- claude.ai chat ignores plugin hooks, and uploads reject the `hooks` key. When those are targets, give the skill an inline fallback for the check.
- A hook that guards or prepares a skill must cover both ways in: Claude invoking it through the Skill tool and the user typing its command. Check the hooks reference for the event each path fires, and anchor the matcher on the full `plugin:skill` name.
- A hook script reads its input as JSON on stdin, treating a missing field as empty. To block, it exits 2 with the reason on stderr, saying what Claude should do instead; exit 1 doesn't block, and the action goes ahead. When it returns JSON, stdout holds that one object and nothing else, built with a JSON encoder. It never waits for input.
- Reach the hook's script through the quoted plugin-root variable, never a relative path or the project-directory variable, which point at the user's project. Hook processes do receive the plugin variables in their environment.
- Test each hook script by piping sample JSON into it and checking the exit code, for both the allow and the block path.
- Hooks have registration and output limits per source and per message; check the current figures on the hooks reference before a skill registers many.

## 12. Questions to ask yourself

- Which computation would Claude otherwise redo by hand on every run?
- On each target surface, does the command in `SKILL.md` reach the script from any working directory?
- Could Claude use each script knowing only its `--help`, its output and its exit codes?
- What does each script do on an empty input, a missing file, a missing tool, and a second run?
- Which rule here would do damage on a single miss, and what enforces it on every surface?
