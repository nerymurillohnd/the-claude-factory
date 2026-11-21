# Scripts

This file teaches you how to audit the scripts a skill bundles, and how the skill uses them, as code Claude runs without reading. A script Claude runs is executed, not read: its source never enters Claude's context, only its output does. Whatever the script does, on its happy path and on every failure path, is therefore written in one place only, the script file, and nobody in the run reads that file. You read it for them. You judge whether each script should be a script at all, where it lives and who shares it, how it talks to Claude, how it fails, what it depends on, where it runs, and what it touches. The scripts in scope are every code file the skill or its plugin ships for the skill: in `scripts/` or anywhere in the skill's folder, at the plugin level, in the plugin's `bin/`, and the command scripts the skill's frontmatter hooks or its plugin's hooks run for it. You audit and propose. You never run, edit or create anything. Each section gives you the principle, why it matters, and what to do when you audit.

## Contents

- How to use this file
  - Before auditing: establish the context
  - Then, audit area by area
- 1. Whether a script is the right tool
  - 1.1 Deterministic, repeated logic belongs in a script
  - 1.2 A script to run and a script to read are built differently
- 2. Where a script lives and who shares it
  - 2.1 Scripts in the skill's own folder
  - 2.2 Scripts at the plugin level
  - 2.3 Hook command scripts
- 3. The interface Claude meets
  - 3.1 No interactive input
  - 3.2 Usage, arguments and input constraints
  - 3.3 Exit codes
  - 3.4 Standard output, standard error and structured output
  - 3.5 Idempotency, dry runs and safe defaults
- 4. Failure handling and constants
  - 4.1 Solve, don't punt
  - 4.2 Failure messages Claude can act on
  - 4.3 No voodoo constants
- 5. Dependencies and runtime environment
  - 5.1 Packages declared and pinned with the script
  - 5.2 What each surface provides
  - 5.3 Commands the script calls
- 6. Portability
  - 6.1 Interpreter, shebang and executable bit
  - 6.2 Operating systems and shells
  - 6.3 Paths and environment inside the script
- 7. Security and least surprise
  - 7.1 Secrets
  - 7.2 Network, writes and actions outside the stated purpose
  - 7.3 Untrusted input
- 8. Tests for scripts
- Classifying findings
- Improvement opportunities
- Delivering the report

## How to use this file

Read this whole file, through its final section, "Delivering the report", before you judge anything. This complete reading, and an audit of the skill against every point in it, are a precondition of your audit: no point stays unaudited. Keep to the file's order: establish the context, then audit area by area, then classify what you found.

Audit from the seat of a Claude that loads the skill with no prior context, on each surface the skill targets, and has to run its scripts. That Claude knows only what the skill's Markdown says about a script and what the script prints when it runs. At each script, ask what that Claude would do when the script hangs, exits non-zero, prints something it can't parse, needs a package that isn't there, is missing from the installed copy, or does something the skill never mentioned.

You judge by reading. Read every script file in full, every branch and every failure path, because no one else in the run will. The prompt carries the main session's mechanical results: the inventory of code files, each entry point's first line and executable bit, which scripts the Markdown runs and with which interpreter, imports without declared dependencies, external commands the scripts call, package installs, network and credential signals with their lines, and any linter output. Take those as measured and judge what they mean. When a point needs a result the prompt doesn't give, record it under Checklist exceptions as blocked, name the missing result, and judge everything else by reading. Where only a run would settle a point, such as whether a hook script exits 2 on a given input, name that run, for example "pipe `{"tool_name":"Bash","tool_input":{"command":"ls"}}` to the script and check its exit code", instead of guessing its result.

Evidence in this file is labeled where it matters: a **requirement** a source states as a must, **documented behavior** a source describes, a **recommendation** a source gives, an **inference** drawn from documented behavior and marked as such, and an **unknown** no source settles. Keep the label when you cite a point in a finding.

### Before auditing: establish the context

What a script must do depends on who runs it and where, so settle these six points first.

1. **Where the skill lives and how it reaches its users.** A personal or project skill on one machine, a plugin skill installed from a marketplace, a skill uploaded to claude.ai or the Skills API, or a skill copied on its own. Distribution decides which scripts reach the user at all (§2).
2. **Which surfaces run its scripts.** Claude Code on macOS, Linux or Windows, claude.ai, Cowork, or the Claude API's code execution container. Each provides a different network, package set and shell (§5.2, §6.2).
3. **How the skill is invoked.** Inline, forked with `context: fork`, or preloaded into a subagent. A subagent's shell never keeps a working-directory change, so a script that depends on one fails there (§6.3).
4. **How each script runs.** Claude runs it through the Bash or PowerShell tool, the skill injects it as a `` !`command` `` or ` ```! ` block before Claude sees the content, or a hook runs it on an event. Each way has its own contract for input, exit codes and output (§2.3, §3).
5. **Whether each script is run or read.** From the skill's Markdown: a script Claude executes for its result, or one Claude opens as reference for its logic (§1.2).
6. **What the skill is for**, from its description and body. Every script is judged against this purpose: what it must compute, what it may change, and what it has no reason to touch (§7).

### Then, audit area by area

Audit what the scripts have and what the skill's purpose needs them to have, with the same care for each: a missing usage message, a dependency no one declared, or a repeated computation Claude does by hand that a script should do is as much your job as a bug in a script that exists. For every point in this file, give exactly one of these outcomes:

- **Present and optimal.** The script does what this file describes. Record no finding.
- **Present but wrong or excess.** The script hangs, fails silently, depends on something it doesn't declare, breaks on a target, touches what its purpose doesn't need, or exists where instructions would do. Record it as a defect, classify it (see "Classifying findings"), and say whether it must be deleted, rewritten, moved or adjusted.
- **Present, right, but improvable.** It works, but a pattern from this file would make it more reliable or easier for Claude to use, such as structured output or a documented exit code. Record it as an improvement opportunity, with the exact change written out.
- **Absent, and the skill needs it.** A script the purpose calls for, or a part of one, such as a `--help` message, a dependency declaration or a dry run. Record it as an improvement opportunity, or as a defect where its absence makes Claude act wrongly: write out the exact content and where it goes, and cite the point of this file it rests on.
- **Absent, and the skill doesn't need it.** Record no finding. Never recommend a script, a flag or a test by default: each one is code someone maintains, and a skill that does its job with instructions alone needs none.

Work only from what the scripts, the skill's Markdown and the mechanical results show. If you have no line to point to, you have no finding; for missing content, point to where it belongs. Where nothing in the skill shows what a missing part should do, such as which exit code a new failure should take, name the decision the author has to make, and invent nothing.

---

## 1. Whether a script is the right tool

### 1.1 Deterministic, repeated logic belongs in a script

A script earns its place when the same computation must come out the same way every run. Anthropic's best practices list what a bundled script gives over code Claude writes during the task: it is "more reliable than generated code", saves tokens because there is "no need to include code in context", saves time, and ensures "consistency across uses" (recommendation). The same guide says "Prefer scripts for deterministic operations" and the Agent Skills guide names the signal to look for: "the agent independently reinventing the same logic each run — building charts, parsing a specific format, validating output — that's a signal to write a tested script once and bundle it in `scripts/`." The converse holds too: a script that hard-codes a judgment the task needs Claude to make, such as which findings matter or how to phrase a summary, takes away the flexibility that step needs (inference from the same guidance on matching freedom to fragility).

Recognize the difference:

**Incorrect:** the skill tells Claude "Parse each `CHANGELOG.md` entry into version, date and bullet list, then compare the versions," and Claude writes a new parser on every run.

**Correct:** `scripts/parse_changelog.py` returns the entries as JSON, and the skill tells Claude to judge which changes are breaking from that output.

When you audit:

- Flag each computation the skill asks Claude to do by hand, or to write code for, that is deterministic and repeats on every run: parsing a fixed format, transforming data, rendering a file, counting or extracting.
- Flag each script that makes a decision the skill's purpose leaves to Claude's judgment, such as ranking, wording or choosing between approaches, and recommend that the script return the facts and the skill give the judgment to Claude.
- Ask, for each script, whether it is still used: a script the Markdown never runs or points to is dead weight in the package.
- Recommend, for each repeated computation you flag, the script by name and purpose, its input, and its output format, for example "`scripts/parse_changelog.py CHANGELOG.md` prints a JSON array of `{version, date, items}`."

### 1.2 A script to run and a script to read are built differently

The best practices distinguish two uses and ask the skill to make clear which one each script serves: "Run the script (most common)" and "Read it as reference (for complex logic)", adding "For most utility scripts, execution is preferred because it's more reliable and efficient" (recommendation). The two uses put different demands on the file. A script Claude runs must be usable without being read: everything Claude needs comes from its usage message, its output and its exit code. A script Claude reads must be readable: the logic Claude came for has to be findable and explained in the file, because Claude reads it as text and copies or adapts the approach (inference from the two uses).

Recognize the difference:

**Incorrect:** the skill says "See `scripts/match_fields.py` for the field-matching algorithm," and the file is 600 lines of argument parsing and I/O with the matching rule buried in an uncommented helper.

**Correct:** the file opens with a docstring stating the matching rule, keeps the rule in one named function, and the skill points Claude at that function.

When you audit:

- For each script the skill tells Claude to run, flag any fact Claude can only get by reading the source: an argument its usage message doesn't list, an output field nothing describes, or an exit code nothing documents.
- For each script the skill tells Claude to read, flag a file whose logic Claude can't find or follow from the file itself: no docstring or header comment, the key logic spread across helpers, or names that don't say what they do.
- Flag a script whose run-or-read use the skill's Markdown and the script's design contradict, such as a script designed as a CLI that the skill says to read, or a reference listing that the skill says to run.
- Recommend, for a script that is read, the header comment that states what the file shows and where, written from the file's own logic.

---

## 2. Where a script lives and who shares it

Where a script sits decides which copies of the skill carry it, which variable reaches it, and what breaks when the skill moves. Judge each script in the form the user receives, never in the author's working copy: a marketplace plugin is copied into `cache/<marketplace>/<plugin>/<version>/` and "Files outside the plugin directory aren't copied, so when a script inside a copied plugin reads a path above the plugin root, such as `../shared`, it doesn't find them" (documented behavior). Three placements have their own rules, below.

### 2.1 Scripts in the skill's own folder

A script inside the skill's directory, in `scripts/` or anywhere under it, travels with the skill on every route: a plugin install, a personal or project copy, a claude.ai upload and the Skills API, because the skill's folder is what each route carries. In Claude Code, `SKILL.md` reaches it through `${CLAUDE_SKILL_DIR}`, "The directory containing the skill's `SKILL.md` file. For plugin skills, this is the skill's subdirectory within the plugin, not the plugin root", used "to reference scripts or files bundled with the skill, regardless of the current working directory" (documented behavior). Outside Claude Code, the Agent Skills guide asks for "relative paths from the skill directory root" (recommendation). This placement is the default for a script only this skill uses, and the only placement that works when the skill also travels without its plugin.

The script itself must also find its own siblings. The path variables "aren't present in the environment of commands Claude runs through the Bash tool" (documented behavior), and Claude Code runs each command in "the session shell's current working directory. That directory moves when Claude runs `cd`" (documented behavior). So a script that opens `data/schema.json`, or reads `$CLAUDE_SKILL_DIR` from its environment, finds nothing once Claude's shell is anywhere else. A script that resolves its data files from its own location, such as Python's `Path(__file__).resolve().parent` or Bash's `"$(dirname "$0")"`, finds them wherever the skill is installed (inference from the two documented behaviors).

Recognize the difference:

**Incorrect:** `scripts/render.py` runs `open("templates/report.html")`, which works only when Claude's shell sits in the skill folder.

**Correct:** `scripts/render.py` runs `open(Path(__file__).resolve().parent.parent / "templates" / "report.html")`.

When you audit:

- Flag each script that reads a sibling file through a path relative to the working directory, or through `CLAUDE_SKILL_DIR`, `CLAUDE_PLUGIN_ROOT` or `CLAUDE_PROJECT_DIR` read from its environment when Claude runs it through the Bash tool.
- Flag a script that only this skill uses but that sits outside the skill's folder, when the skill targets any route that carries the folder alone.
- Ask whether each script in the folder is reached from `SKILL.md` through the skill-directory variable in Claude Code, or through a skill-root relative path on the other targets, and judge the script's own path handling against the way it is reached.
- Recommend, for each script that opens a sibling file, the exact line that resolves the path from the script's own location.

### 2.2 Scripts at the plugin level

A plugin can keep scripts outside every skill's folder: in a plugin-root folder such as `scripts/` or a shared folder, or in `bin/`. Claude Code's skills page says `${CLAUDE_PLUGIN_ROOT}` is for "scripts or files bundled anywhere in the plugin, including resources shared between the plugin's skills", and it is "Substituted only in plugin skills" (documented behavior). One copy shared by several skills avoids drift between duplicates, which is the reason to put a script here. The cost is that the script exists only where the whole plugin is installed. A skill uploaded to claude.ai or the Skills API, or copied on its own, carries its own folder and nothing above it, so every plugin-level script it calls is missing there, and the plugin-root variable reaches Claude as literal text (inference from the documented boundary and substitution rules).

Three more facts govern a plugin-level script's code:

- **The root moves.** `${CLAUDE_PLUGIN_ROOT}` "changes when the plugin updates, so don't write state there"; the previous version directory is removed "in a background cleanup 14 days later" (documented behavior). A script that writes a cache, a lock file or a virtual environment next to itself loses it on the next update.
- **Installed dependencies go to the data directory.** `${CLAUDE_PLUGIN_DATA}` is "a directory that survives updates, for `node_modules`, virtual environments, and caches" (documented behavior). Claude Code installs a plugin's Node.js dependencies automatically into each cached copy only when the plugin root holds "both a `package.json` and a supported lockfile", every dependency is "a registry package pinned in the lockfile to an exact version", and with `--ignore-scripts`; Python dependencies and anything else the automatic install can't provide are installed "from a hook into the persistent data directory" (documented behavior).
- **`bin/` is a PATH entry, not a folder Claude browses.** Files there "are on the `PATH` of the Bash tool's shell while the plugin is enabled, so Claude can run them as bare commands", and "Plugin `bin/` directories come after the user's own `PATH` entries, so a plugin can't shadow `git`, `ls`, or another system command" (documented behavior). A `bin/` name that matches a command the user already has runs the user's command instead (inference). A sandboxed PowerShell command doesn't find them (documented behavior).

Recognize the difference:

**Incorrect:** two skills of a plugin both run `${CLAUDE_PLUGIN_ROOT}/scripts/fetch_schema.py`, which caches downloads in `$(dirname "$0")/.cache`, and one of the skills is also uploaded to claude.ai.

**Correct:** the script caches in a directory passed as an argument that the skill sets to `${CLAUDE_PLUGIN_DATA}/cache`, and the uploaded skill carries its own copy of the script in its folder, or the skill states that it runs only as part of the plugin.

When you audit:

- For each plugin-level script, list the skills that run it. Flag a plugin-level script that only one skill uses and that the skill's other routes need, and recommend moving it into that skill's folder.
- Flag each skill that runs a plugin-level script and also targets a route that carries the skill without its plugin, such as a claude.ai upload, the Skills API or a standalone copy. Recommend one of two fixes, whichever the skill's purpose supports: a copy inside the skill's folder, or a stated limit that the skill runs only inside the plugin.
- Flag script code that writes state, caches, downloads or environments next to itself under the plugin root, and recommend writing them under the data directory, passed in or read where the variable is available.
- Flag a script that installs dependencies in a way the automatic install skips or that runs each session without checking whether the install is current, and recommend the documented pattern: install into the data directory when the manifest copy there differs from the plugin's.
- Flag a `bin/` executable whose name is likely to match a command users already have, and a skill that runs a `bin/` command by bare name in a sandboxed PowerShell session.
- Ask, for each shared script, whether every skill that calls it passes the arguments it expects: a change made for one caller breaks the others silently.

### 2.3 Hook command scripts

A hook declared in the skill's frontmatter, or in its plugin's `hooks/hooks.json`, often runs a script file. That script runs on an event with no one reading it and no chance for Claude to answer it, under a contract unlike the Bash tool's. "Command hooks receive JSON data via stdin and communicate results through exit codes, stdout, and stderr", and "On macOS and Linux, command hooks run in their own session without a controlling terminal" (documented behavior). Exit 0 is success; exit 2 is "Blocking error" on events that can block, and its message is the hook's stderr; any other exit code is a "Non-blocking error" and "The action goes ahead" (documented behavior). The reference warns: "Exit code 1 without valid JSON output is a non-blocking error ... even though 1 is the conventional Unix failure code. If your hook is meant to enforce a policy, use `exit 2`" (documented behavior). Stdout counts as JSON output "only when you print one JSON object ... with nothing around it but whitespace", and "Claude never sees stderr from a hook that exits 0" (documented behavior). Unlike a Bash-tool command, a hook process receives `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA` and `CLAUDE_PROJECT_DIR` in its environment, so a script "can read `process.env.CLAUDE_PLUGIN_ROOT` regardless of how it was launched" (documented behavior). Hook scripts "must be executable for Claude Code to run them" (requirement), and command hooks "execute shell commands with your full user permissions" (documented behavior).

Here you audit the script's code only: what it reads, decides, prints and returns. Which event, matcher and lifecycle the hook registers under is outside this file.

Recognize the difference:

**Incorrect:**

```bash
#!/bin/bash
cmd=$(jq -r '.tool_input.command')
echo "checking $cmd"
[[ "$cmd" == *"rm -rf"* ]] && { echo "blocked"; exit 1; }
```

The guard exits 1, so the command runs anyway; its "checking" line on stdout is plain text, and its reason goes to stdout, where a blocking hook's reason is never read.

**Correct:**

```bash
#!/bin/bash
cmd=$(jq -r '.tool_input.command // empty')
if [[ "$cmd" == *"rm -rf"* ]]; then
  echo "Blocked: recursive delete. Remove the -rf flag or delete the files by name." >&2
  exit 2
fi
exit 0
```

When you audit:

- Read each hook script the skill's frontmatter or its plugin's hooks run for the skill. Flag a script meant to block or deny that exits 1, or any code other than 2, on the path that should stop the action.
- Flag a script that prints anything to stdout besides one JSON object when it means to return JSON, such as a progress line before the object, and a script that builds its JSON by string concatenation; recommend a JSON encoder such as `jq -n` or the language's JSON library.
- Flag a script that waits for terminal input, opens `/dev/tty`, or starts a background process without redirecting its stdout and stderr.
- Flag a script that reads its input from anything but stdin, or that fails on a missing field instead of treating it as empty, as `jq -r '.tool_input.file_path // empty'` does.
- Flag a hook script whose failure reason, on a blocking path, isn't on stderr, or doesn't say what Claude should do instead.
- Ask whether the script's dependencies, such as `jq`, are named for the user; the hooks guide says "If you see "jq: command not found", install `jq` or use Python/Node.js for JSON parsing."
- Take the executable bit of each hook script from the prompt, and flag one that isn't executable on macOS and Linux.
- Recommend, for each hook script, the sample input that would settle its behavior when a run is needed, written as the `echo '<json>' | <script>; echo $?` line the hooks guide uses.

---

## 3. The interface Claude meets

Claude learns a script only through its interface. The Agent Skills guide says it plainly: "When an agent runs your script, it reads stdout and stderr to decide what to do next" (documented behavior). This section covers every script Claude runs, whatever it computes. Hook scripts follow §2.3 where their contract differs.

### 3.1 No interactive input

"This is a hard requirement of the agent execution environment. Agents operate in non-interactive shells — they cannot respond to TTY prompts, password dialogs, or confirmation menus. A script that blocks on interactive input will hang indefinitely" (requirement). Input comes "via command-line flags, environment variables, or stdin" (recommendation). Claude Code surfaces the symptom rather than preventing it: "Background bash tasks that appear stuck on an interactive prompt now surface a notification after ~45 seconds" (changelog, v2.1.84). A foreground command that waits reaches its timeout, and "Claude Code moves it to the background instead of stopping it" (documented behavior), so the script is still waiting while Claude moves on without its result.

Recognize the difference:

**Incorrect:** `env = input("Target environment: ")` when `--env` is missing.

**Correct:** the script exits with `Error: --env is required. Options: development, staging, production.` and a usage line.

When you audit:

- Flag every call that reads from the terminal or waits for a keypress: `input()`, `read` without a redirected source, `getpass`, a pager, an editor launched with `$EDITOR`, a `[y/N]` confirmation, a tool invoked without its non-interactive flag (such as `apt-get install` without `-y` or `npm init` without `-y`).
- Flag a script that falls back to a prompt when an argument is missing, instead of exiting with the missing argument named.
- Recommend, for each prompt you flag, the flag or variable that replaces it and the error the script prints when it's absent.

### 3.2 Usage, arguments and input constraints

"`--help` output is the primary way an agent learns your script's interface. Include a brief description, available flags, and usage examples", and "Keep it concise — the output enters the agent's context window" (recommendation). Ambiguous input is rejected, not guessed: "Reject ambiguous input with a clear error rather than guessing. Use enums and closed sets where possible" (recommendation). The Agent Skills specification asks that scripts "Handle edge cases gracefully" (recommendation).

Recognize the difference:

**Incorrect:** `process.py` takes two positional arguments in a fixed order, has no `--help`, and treats an unknown `--format xml` as JSON.

**Correct:** `process.py --help` prints a one-line description, each flag with its default, and two examples; `--format` accepts `json`, `csv` or `table` and rejects anything else by name.

When you audit:

- Flag a script Claude runs with no `--help` or usage message, or one whose usage message omits a flag the skill or the code uses.
- Flag a usage message long enough to cost context for no gain, such as a full manual printed on every `--help`.
- Flag input the script accepts and silently reinterprets: unknown flags ignored, an invalid enum value defaulted, a missing file treated as empty when the task needs it.
- Flag positional arguments whose order is easy to swap, where named flags would make the call self-describing.
- Recommend the exact usage text for each script that lacks one, written from the arguments its code actually parses.

### 3.3 Exit codes

"Use distinct exit codes for different failure types (not found, invalid arguments, auth failure) and document them in your `--help` output so the agent knows what each code means" (recommendation). In Claude Code the exit code also changes what Claude receives. The Bash tool treats exit 1 as a valid result only for a fixed set of commands, "`grep`, `rg`, `egrep`, `fgrep`, `find`, `diff`, `test`, and `[`, plus `git diff` and `git grep`. Every other command that exits 1 counts as a failure"; a valid result stays inline up to roughly 30,000 characters and past that arrives as a file path and a preview, while a failure arrives as "a head-and-tail excerpt" of roughly 10,000 characters "with no file path" (documented behavior). So a bundled script that exits 1 to mean "found something" has its report treated as a failure, and a long report loses its middle (inference). Run as an injected command, any non-zero exit from it aborts the skill (documented behavior).

Recognize the difference:

**Incorrect:** `check_links.py` exits 1 whenever it finds a broken link, and exits 1 too when its input file is missing.

**Correct:** it exits 0 with a JSON report whose `broken` list may be non-empty, 2 for invalid arguments and 3 for an unreadable input, and its `--help` lists the three codes.

When you audit:

- Flag a script that uses one exit code for different failures, or exits 0 after a failure, so Claude can't tell success from failure from the code.
- Flag a script that reports normal findings through a non-zero exit when Claude runs it through the Bash tool, or when the skill injects it, and recommend exiting 0 with the findings in the output.
- Flag exit codes the code uses but the usage message doesn't document.
- Flag a shell script that runs several steps without stopping on the first failure, such as no `set -e` or no check after a step whose failure invalidates the rest, so it exits 0 after a failed step (inference: a shell script's exit code is its last command's unless it stops earlier).
- Recommend, for each script with ambiguous exit codes, the code table its `--help` should print.

### 3.4 Standard output, standard error and structured output

"Prefer structured formats — JSON, CSV, TSV — over free-form text", and "send structured data to stdout and progress messages, warnings, and other diagnostics to stderr" (recommendation). The separation doesn't always survive the run: for injected commands, "with the default `bash` shell, Claude Code merges stderr into stdout. Anything the command writes to stderr appears in the injected text" (documented behavior). A script whose output a skill injects, or that Claude parses, stays parseable only if it writes nothing to stderr on success, or offers a quiet mode (inference).

Recognize the difference:

**Incorrect:** a table aligned with spaces (`my-service    running   2025-01-15`) with progress lines mixed into stdout.

**Correct:** `{"name": "my-service", "status": "running", "created": "2025-01-15"}` on stdout, and `Scanned 12 services` on stderr only with `--verbose`.

When you audit:

- Flag output Claude or another tool has to parse that is free-form or whitespace-aligned, and recommend the structured format with its fields named.
- Flag diagnostics, warnings or progress written to stdout among the data.
- Flag a script the skill injects, or whose stdout Claude parses as JSON, that writes to stderr on a successful run.
- Ask whether the output format the skill's Markdown describes matches what the code prints, field by field.
- Recommend, where output is unstructured, the exact output shape, for example `{"field_name": {"type": "text", "x": 100, "y": 200}}`.

### 3.5 Idempotency, dry runs and safe defaults

"Agents may retry commands. "Create if not exists" is safer than "create and fail on duplicate"" (recommendation). "For destructive or stateful operations, a `--dry-run` flag lets the agent preview what will happen", and "Consider whether destructive operations should require explicit confirmation flags (`--confirm`, `--force`) or other safeguards appropriate to the risk level" (recommendation). A confirmation flag is the non-interactive form of a confirmation prompt (§3.1).

Recognize the difference:

**Incorrect:** `cleanup.sh` deletes every file under its target directory by default, and a second run fails because the directory is gone.

**Correct:** `cleanup.sh <dir>` lists what it would delete and exits; `cleanup.sh --confirm <dir>` deletes, and a second run reports that nothing is left to delete and exits 0.

When you audit:

- Flag a script that fails, duplicates or corrupts state when run twice with the same input, where the task gives Claude reason to retry it.
- Flag a destructive or irreversible action that runs by default, with no flag to opt in.
- Flag a dry-run mode whose code path still writes, deletes or sends anything.
- Recommend, for each destructive script, the opt-in flag and what the default run prints instead.

---

## 4. Failure handling and constants

### 4.1 Solve, don't punt

"When writing scripts for Skills, handle error conditions rather than deferring to Claude" (recommendation). The best practices contrast a function that catches `FileNotFoundError` and `PermissionError` and responds to each with one that does "Just fail and let Claude figure it out", and their checklist asks that "Scripts solve problems rather than defer to Claude" and "Error handling is explicit and helpful" (recommendation). A script should resolve every failure it can resolve without the user's decision, and report the rest; resolving a failure by inventing a default the task can't accept hides it instead of solving it (inference from the same checklist's "Error handling is explicit").

Recognize the difference:

**Incorrect:** `return open(path).read()`, which ends in a traceback Claude has to interpret.

**Correct:** the script catches the missing file, creates the default the task defines, says so on stderr, and continues; it catches a permission error it can't fix and exits with the path, the problem and what to try.

When you audit:

- Flag each predictable failure the code leaves to an unhandled exception or a raw tool error: a missing or unreadable file, an empty input, a missing dependency, a network failure, a malformed record.
- Flag each failure the code swallows: a bare `except: pass`, `|| true` on a step whose failure matters, a default substituted without a word to Claude.
- Ask, for each handled failure, whether the script could have resolved it itself and pushed the work back to Claude instead.
- Recommend, for each unhandled failure, the exact handling: what the script does, what it prints, and its exit code.

### 4.2 Failure messages Claude can act on

"When an agent gets an error, the message directly shapes its next attempt. An opaque "Error: invalid input" wastes a turn. Instead, say what went wrong, what was expected, and what to try" (recommendation). This holds for every failure path of every script Claude runs: bad arguments, missing files, missing tools, unreachable services.

Recognize the difference:

**Incorrect:** `Error: invalid input`.

**Correct:** `Error: --format must be one of: json, csv, table. Received: "xml"`.

When you audit:

- Read every failure path of every script. Flag each message that doesn't name what went wrong, what was expected and what to try.
- Flag a failure that prints only a stack trace, or prints nothing.
- Recommend the exact message for each one you flag, written from the condition the code checks.

### 4.3 No voodoo constants

"Also justify and document configuration parameters to avoid "voodoo constants" (Ousterhout's law). If you don't know the right value, how will Claude determine it?" The best practices' checklist asks for "No "voodoo constants" (all values justified)" (recommendation). A timeout, retry count, threshold or size limit without a reason is a value no one can safely change, and Claude, who never reads the script, can't even see it.

Recognize the difference:

**Incorrect:** `TIMEOUT = 47  # Why 47?`

**Correct:** `# HTTP requests typically complete within 30 seconds` / `REQUEST_TIMEOUT = 30`.

When you audit:

- Flag each numeric or string constant that sets behavior, such as a timeout, retry count, threshold, limit or magic path, with no comment or name that says why it has that value.
- Flag a constant the task would need to change that is buried in code rather than exposed as a flag, when the skill's purpose gives Claude reason to change it.
- Recommend, for each one, the comment that justifies it, or the flag that exposes it with its default.

---

## 5. Dependencies and runtime environment

### 5.1 Packages declared and pinned with the script

A script either needs nothing beyond its language's standard library, or says what it needs. The specification asks scripts to "Be self-contained or clearly document dependencies" (recommendation). The Agent Skills guide shows how to declare dependencies inside the script so it runs "with a single command — no separate manifest file or install step required" (recommendation):

- **Python:** a PEP 723 block between `# /// script` and `# ///`, run with `uv run scripts/extract.py`, which "creates an isolated environment, installs the declared dependencies, and runs the script"; pin with PEP 508 specifiers such as `"beautifulsoup4>=4.12,<5"`, constrain the interpreter with `requires-python`, and use `uv lock --script` "for full reproducibility".
- **Deno:** `npm:` and `jsr:` specifiers with versions such as `npm:cheerio@1.0.0`.
- **Bun:** versions in the import path, with the caveat that "If a `node_modules` directory exists anywhere up the directory tree, auto-install is disabled".
- **Ruby:** `bundler/inline`, with explicit versions because "there is no lockfile", and the caveat that "An existing `Gemfile` or `BUNDLE_GEMFILE` env var in the working directory can interfere".

Unpinned dependencies make the script behave differently over time, the reason the same guide gives for pinning one-off commands (recommendation). The best practices also ask that "Required packages [be] listed in instructions and verified as available" (recommendation): the declaration in the script makes it runnable; the line in the skill tells Claude and the user what it needs.

Recognize the difference:

**Incorrect:** `extract.py` begins with `from bs4 import BeautifulSoup`, has no inline metadata, and the skill says "Run `python3 scripts/extract.py`."

**Correct:** `extract.py` begins with a PEP 723 block declaring `"beautifulsoup4>=4.12,<5"` and `requires-python = ">=3.11"`, and the skill says "Requires uv. Run `uv run ${CLAUDE_SKILL_DIR}/scripts/extract.py`."

When you audit:

- Take the imports without declared dependencies from the prompt, read each script's imports yourself, and flag each third-party package the script uses that neither inline metadata nor a manifest the skill ships declares.
- Flag declared dependencies with no version bound, and a version range wide enough to admit a major release that breaks the script.
- Flag inline metadata the run command doesn't use, such as a PEP 723 block in a script the skill runs with plain `python3`, which ignores it.
- Flag a script whose runner has a documented interference the skill's targets can meet, such as Bun auto-install inside a project with `node_modules`.
- Recommend, for each undeclared dependency, the exact metadata block and the run command that honors it.

### 5.2 What each surface provides

The same script meets different environments:

- **Claude API (Skills API and the code execution tool):** "no network access and no runtime package installation"; "Only pre-installed packages are available. You cannot install new packages during execution" (documented behavior). The code execution tool page lists the container's Python version, its operating system ("Linux-based container"), its preinstalled Python libraries and a few command-line tools; it states "a higher focus on Python" (documented behavior). Check each script's interpreter version, packages and tools against that page's current list.
- **claude.ai:** "Depending on user/admin settings, Skills might have full, partial, or no network access" (documented behavior), and Claude "can install packages from standard repositories (Python PyPI, JavaScript npm) when loading skills" (documented behavior).
- **Claude Code:** "Full network access" (documented behavior).

A runner that installs on first use, such as `uv run` with a PEP 723 block, `npx`, `pipx run` or `bunx`, needs the network the first time it meets a package, so on the API it fails unless the package is already in the container, and `uv` itself isn't among the tools the page lists (inference from the documented constraints). Where the support article for claude.ai shows a `dependencies` frontmatter field, Claude Code's skills page says an upload accepts only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools` and fails on any other key; the Agent Skills guide points runtime requirements to "the `compatibility` frontmatter field" (sources disagree; follow the upload rule).

Recognize the difference:

**Incorrect:** a skill that targets the Skills API runs `uv run scripts/report.py`, whose PEP 723 block asks for `polars` and `requires-python = ">=3.12"`.

**Correct:** the script uses `pandas`, which the container preinstalls, runs on the container's Python with `python3 scripts/report.py`, and the skill's `compatibility` says what it requires.

When you audit:

- For each script and each target surface, compare the interpreter version, packages and command-line tools the script needs with what that surface provides, and flag each mismatch.
- Flag script code that installs packages at runtime, or calls an installing runner, on a skill that targets the API.
- Flag a skill that targets claude.ai and whose scripts need the network with no stated fallback for sessions where it is off.
- Flag a script that opens its output in a browser, for example with `webbrowser.open`, `open`, `xdg-open` or `start`, on a target that runs in a container, such as the Claude API or a cloud session: the docs describe this pattern only as "interactive HTML files that open in your browser" on the user's machine, and a container has no browser of the user's to open (inference). Recommend that the script also print the output file's path, and that the skill tell Claude to give the user that path where no browser opens.
- Recommend, for a script that must run on several surfaces, the version that uses only what every target provides, or the per-surface statement the skill should carry.

### 5.3 Commands the script calls

A script that shells out to `jq`, `git`, `curl`, `pdftotext` or `docker` depends on that tool as much as on a package, and Claude can't see the dependency because it never reads the script. The best practices say "Don't assume packages are available" (recommendation), the Agent Skills guide says "State prerequisites in your `SKILL.md` (e.g., "Requires Node.js 18+") rather than assuming the agent's environment has them" (recommendation), and the hooks guide shows what a missing one looks like: "jq: command not found" (documented behavior). A script that checks for each tool it needs and exits with the tool's name and how to get it turns a confusing failure into an actionable one (inference from §4.2's guidance).

Recognize the difference:

**Incorrect:** `sync.sh` calls `jq` and `gh` on line 40, and nothing in the skill mentions either.

**Correct:** `sync.sh` starts with `command -v jq >/dev/null || { echo "Error: jq is required. Install: brew install jq or apt-get install jq" >&2; exit 4; }`, and the skill lists `jq` and `gh` as prerequisites.

When you audit:

- Take the external commands the scripts call from the prompt, confirm each by reading, and flag each one that is neither standard on every target nor named in the skill's Markdown or `compatibility`.
- Flag a script that uses a tool without checking that it exists, where a missing tool would produce a misleading failure.
- Recommend, for each undeclared tool, the prerequisite line for the skill and the check for the top of the script.

---

## 6. Portability

### 6.1 Interpreter, shebang and executable bit

How a script starts decides whether it starts. A script Claude runs through its interpreter (`python3 scripts/x.py`, `bash scripts/x.sh`) needs no executable bit; a script run by path, from `bin/` as a bare command, or as a hook needs one: hook scripts "must be executable for Claude Code to run them", the plugin docs say to make a `bin/` file executable "with `chmod +x`" and to "Save the script at `scripts/format.sh` and make it executable" (requirement and recommendation). The Agent Skills examples start scripts run by path with an interpreter line such as `#!/usr/bin/env -S deno run` or `#!/usr/bin/env bun` (recommendation). On Windows, an exec-form hook "requires `command` to resolve to a real executable such as a `.exe`", and the `.cmd` and `.bat` shims in `node_modules/.bin` "can't be spawned without a shell"; "The `node` plus script-path pattern works on every platform" (documented behavior). In shell form, "when the script path doesn't exist or isn't executable, the shell exits with a code like 127", and the hook fails as a non-blocking error (documented behavior).

Recognize the difference:

**Incorrect:** a hook runs `${CLAUDE_PLUGIN_ROOT}/scripts/check.py` by path; the file has no shebang and is mode 644, so the hook never runs and the action goes ahead.

**Correct:** the file starts with `#!/usr/bin/env python3` and is mode 755, or the hook runs it as `"command": "python3", "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/check.py"]`.

When you audit:

- Take each entry point's first line and executable bit from the prompt. Flag a script run by path, from `bin/`, or by a hook that lacks an interpreter line or the executable bit.
- Flag an interpreter line with a fixed path, such as `#!/usr/local/bin/python3`, where `/usr/bin/env` would find the user's interpreter.
- Flag a mismatch between the interpreter line and how the skill runs the script, such as a Bash shebang on a script the skill runs with `sh`, or a `python` call where only `python3` is assured (the latter an inference: no source states which names each surface provides).
- Flag, on a skill or plugin that declares Windows, a hook that runs a `.cmd` or `.bat` shim in exec form.

### 6.2 Operating systems and shells

A script runs under whichever shell and OS the user has. Shell-form hooks run through "`sh -c` on macOS and Linux, Git Bash on Windows, or PowerShell when Git Bash isn't installed" (documented behavior), so a hook command written in Bash syntax can fail where `sh` isn't Bash, and "without Git Bash, a shell-form hook with no `shell` set runs in PowerShell, where it can fail" (documented behavior). A skill with `shell: bash` "fails before any command runs" on "Windows without Git Bash" (documented behavior). Paths take forward slashes: "Unix-style paths work across all platforms, whereas Windows-style paths cause errors on Unix systems" (recommendation), and on Windows "most substituted paths use forward slashes ... They keep their native backslashes in an exec-form hook and in a hook that runs through PowerShell" (documented behavior), which is why the hooks guide's example script normalizes them: "Normalize Windows backslash separators so the patterns below match". Differences between GNU and BSD versions of common tools, such as `sed -i` or `date -d`, also break scripts across Linux and macOS (inference: no official source in this set covers them).

Recognize the difference:

**Incorrect:** a script for macOS and Linux runs `sed -i 's/a/b/' file` and `readlink -f "$0"`, both of which behave differently on macOS.

**Correct:** it writes the edit through a temporary file and resolves its own directory with `cd "$(dirname "$0")" && pwd`.

When you audit:

- Establish which operating systems the skill or its plugin declares. Flag each construct in a script that fails on a declared one: Bash syntax in a file run by `sh`, GNU-only or BSD-only flags, Windows-style paths, or a hook whose command assumes Bash on a Windows target without Git Bash.
- Flag a skill or plugin that declares Windows support through Git Bash and ships a script that assumes PowerShell, or the reverse, without saying which.
- Flag path handling in a hook script that compares paths from the hook input without normalizing separators, where Windows is a target.
- Ask, where no target OS is declared, which ones the skill's users run, and judge the script against POSIX behavior until the author says otherwise.
- Recommend, for each non-portable construct, the portable replacement.

### 6.3 Paths and environment inside the script

A script's environment is not Claude's shell. "Environment variables don't persist. An `export` in one command won't be available in the next", and "Subagent sessions never carry over working directory changes" (documented behavior). The plugin path variables are absent from Bash-tool commands and present in hook processes (§2.1, §2.3). A path with spaces breaks an unquoted variable, and the hooks reference says "Always quote shell variables: use `"$VAR"` not `$VAR`" (recommendation).

Recognize the difference:

**Incorrect:** the skill tells Claude to run `export OUT_DIR=build` and then `scripts/render.sh`, which writes to `$OUT_DIR/report.html` unquoted.

**Correct:** `scripts/render.sh --out build`, which writes to `"$out/report.html"`.

When you audit:

- Flag a script that relies on a variable a previous command exported, or on a working directory a previous command set, including inside a forked or preloaded run.
- Flag unquoted variables and command substitutions that hold paths or user input.
- Flag a script that writes its output to a relative path without saying where, so Claude can't find the file it made.
- Recommend, for each, the argument that carries the value explicitly.

---

## 7. Security and least surprise

A skill runs with whatever access Claude has, and its scripts run with the user's own permissions: Anthropic's overview warns that "a malicious Skill can direct Claude to call tools or run code in ways that don't match the Skill's stated purpose", and asks auditors to "Review all files bundled in the Skill: `SKILL.md`, scripts, images, and other resources. Look for unusual patterns such as unexpected network calls, file access patterns, or operations that don't match the Skill's stated purpose" (recommendation). Claude's own permission rules don't contain a script either: Read and Edit deny rules "don't apply to ... arbitrary subprocesses that read or write files indirectly, like a Python or Node script that opens files itself", and `permissions.blockWritesOutsideWorkingDirectories` "doesn't limit shell commands, MCP tools, or the programs hooks run" (documented behavior). What a script does is limited only by its code and the sandbox, if the user enabled one.

### 7.1 Secrets

The support article says "Don't hardcode sensitive information (API keys, passwords)" (recommendation), and the hooks reference adds "Skip sensitive files: avoid `.env`, `.git/`, keys, etc." (recommendation). A script that reads a credential file the user's deny rules protect gets past those rules (documented behavior above), and whatever a script prints reaches Claude's context and the transcript (inference from "Only the script's output consumes tokens").

Recognize the difference:

**Incorrect:** `deploy.py` holds `API_KEY = "sk-live-..."`, or reads `.env` and prints the request headers it sends when `--verbose` is set.

**Correct:** `deploy.py` reads the key from an environment variable the skill names, fails with `Error: DEPLOY_API_KEY is not set` when it is missing, and prints only the response status.

When you audit:

- Flag any credential, token, password or key written in a script or a file it ships, quoting the line with the value replaced by `<redacted>`.
- Flag a script that reads a credential file, a settings file, `~/.ssh`, `.env` or a keychain without the skill's purpose requiring it and the skill saying so.
- Flag a script that prints, logs or writes to a file any credential it reads, including in debug or verbose output and in error messages that echo a request.
- Recommend, for each, the environment variable or secret store the script should read, named in the skill, and the redaction its output needs.

### 7.2 Network, writes and actions outside the stated purpose

"Skills that fetch data from external URLs pose particular risk, as fetched content might contain malicious instructions. Even trustworthy Skills can be compromised if their external dependencies change over time" (documented behavior). A script that fetches and prints remote content puts that content in front of Claude as tool output. A script also surprises the user when it writes outside the place the skill states, deletes or overwrites by default, or contacts a host the skill never names.

Recognize the difference:

**Incorrect:** a formatting skill's script posts usage statistics to a remote host and writes a cache in the user's home directory, and the skill mentions neither.

**Correct:** the script makes no network call; if the purpose needed one, the skill would name the host and what is sent, and the script would write only to the output path it is given.

When you audit:

- Take the network and credential signals from the prompt, confirm each by reading, and flag each network call that the skill's purpose doesn't need or that the skill doesn't name with its host.
- Flag each write, delete or move outside the paths the skill states, such as the home directory, shell startup files, global configuration, or the project outside the task's files.
- Flag each operation that doesn't match the skill's stated purpose, quoting the code.
- Flag a script that downloads code and runs it, such as `curl ... | sh` or `eval` on fetched text.
- Recommend, for each, the removal, or the sentence the skill needs to state the access and why.

### 7.3 Untrusted input

A script receives input it didn't choose: arguments Claude builds from user text, files from the project, hook JSON describing Claude's own tool calls. The hooks reference lists the practices: "Validate and sanitize inputs: never trust input data blindly", "Always quote shell variables", "Block path traversal: check for `..` in file paths" and "Use absolute paths" (recommendation). The same practices protect any script that turns input into a command or a path (inference).

Recognize the difference:

**Incorrect:** `eval "git log $1"`, or `os.system(f"convert {name} out.png")` with a file name taken from the user.

**Correct:** `git log -- "$1"`, or `subprocess.run(["convert", name, "out.png"], check=True)`.

When you audit:

- Flag input passed to `eval`, `sh -c`, `os.system`, `shell=True` or string-built commands.
- Flag a path taken from input and opened or written without a check that it stays where the script means it to, including `..` segments.
- Flag a hook script that trusts a field of its input JSON for a security decision without validating its form.
- Recommend, for each, the argument-vector form or the check that closes it.

---

## 8. Tests for scripts

The sources call for tested scripts without prescribing where tests live: "When a command grows complex enough that it's hard to get right on the first try, a tested script in `scripts/` is more reliable", and "write a tested script once and bundle it in `scripts/`" (recommendation). The hooks guide gives the smallest test of a hook script: "Test it manually by piping sample JSON", followed by `echo $?` to check the exit code (recommendation). Whether a skill should ship its tests to users is not stated by any source in this set (unknown). Tests shipped inside the skill's folder travel to every user and add to the package, while tests kept beside the skill in its repository cost the user nothing (inference).

Recognize the difference:

**Incorrect:** a skill's `scripts/test_parse.py` asserts only that `parse.py` runs on one well-formed file.

**Correct:** the tests cover the well-formed file, an empty file, a malformed record and a missing file, and assert the exit code and the message of each.

When you audit:

- Where the skill or its repository ships tests for its scripts, flag tests that cover only the happy path while the script has failure paths Claude depends on.
- Flag tests shipped inside the skill's folder that the skill's users have no use for, and ask whether they belong in the repository outside the folder.
- Ask, for a script with destructive or irreversible effects and no tests, which input would show it misbehaving, and name it as the run that would settle the point.
- Recommend, for a hook script, the sample-JSON runs that cover its allow and block paths, with the exit code each should return.

---

## Classifying findings

Give every finding four things: the exact file and line(s), in the script or in the Markdown that runs it, or where missing content belongs; the point in this file it violates or falls short of; why it is a defect, stated as what Claude or the user would meet at that point; and a specific fix, written out, with the reason it's the right one.

Classify each defect into one of four levels by its actual consequence. The examples anchor each level; a finding that doesn't match one verbatim still gets the level its own consequence earns.

- **Critical.** The script damages the user's data or system, leaks a secret, acts against the skill's stated purpose, or fails on every run on a target. For example: a credential written in a shipped script; a script that sends files or environment variables to a host the skill never names; destructive deletion on by default with no opt-in; a guard hook script that exits 1, so the action it exists to block always goes ahead; a script that prompts for input and hangs every run; a script every run needs that is missing from the installed copy, such as a plugin-level script called by a skill uploaded on its own.
- **High.** Claude acts wrongly or the script fails in some runs or on some targets. For example: an undeclared package or tool that is absent on a target; a script that installs packages on a skill that targets the API; a hook or `bin/` script without its executable bit; a script that finds its data through the working directory; a failure that exits 0, or findings reported through exit 1 so a long report is clipped; state written under the plugin root and lost on update; input passed to `eval`; a hook script that prints text around its JSON decision.
- **Medium.** Claude gets there, but with wasted turns, retries or less reliability than it should. For example: opaque error messages; no `--help`; unstructured output Claude must parse; diagnostics mixed into stdout; unpinned dependencies; a voodoo constant that sets behavior; a non-idempotent script Claude may retry; a portable construct missing on a declared OS that has a workaround Claude can find.
- **Low.** A minor weakness with no real consequence. For example: a usage message that omits one example; a constant with a clear name but no comment; an interpreter line with a fixed path on a script always run through its interpreter.

Tie-breaks:

- If a finding fits two levels, the higher level wins.
- A pattern that would make a working script better, without any run going wrong, is an improvement opportunity, not a defect.
- When several findings share one root cause, such as one shared script missing from every route that carries the skill alone, report the root cause once and list every location.
- Never invent impact, never inflate a severity to make the report look decisive, and never lower one because the failure path is rare: a script's failure path is exactly where Claude has the least to go on.

## Improvement opportunities

Separate improvement opportunities from defects: an opportunity is a script the skill's purpose would gain from, a part of a script that would make it more reliable or easier for Claude to use, or a placement that would let the skill travel further. Report every one that genuinely applies to this skill; this section may stay empty only when nothing does. For each one, give what exists now (or that it is absent, and where it belongs), the exact content written out in full, such as the usage text, the metadata block, the error message, the exit-code table or the new file's path and interface, and why it is better for this skill.

This file gives you the criteria, the context to establish, and the severity model. The gotchas and the verification checklist live in your own instructions, and the report template lives in this skill's `assets/` folder, so they aren't repeated here.

## Delivering the report

Deliver every defect and improvement opportunity in the shared findings template, `assets/audit-report.md` in this skill. Fill one defect block per defect, with every field, and keep the template's structure exactly. For a finding in a script, give the script's path in File and its lines; for a finding in the Markdown that runs it, give that file. Quote secrets only with the value replaced by `<redacted>`. Defects with one root cause are one defect: give its first location in File and Lines, and list every other location, as `path:lines`, in Finding. Record every mechanical result that was missing, and the check it blocked, under Checklist exceptions.
