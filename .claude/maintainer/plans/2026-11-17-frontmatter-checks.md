# Frontmatter mechanical checks Implementation Plan (v5)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the 14 frontmatter checks (spec FM-1 to FM-14), each one stable, read-only and release ready.
- Each check covers only what its spec's Coverage line marks as missing. Whatever `claude plugin validate` already reports stays with that command.
- FM-1 and FM-11 are covered by commands. FM-6 is covered by a command for the folder and by `frontmatter.name` for the name.
- The rest are standard-library Python modules in the package `skills/auditing-skills/scripts/frontmatter/`, run through one thin entry script, `scripts/frontmatter-checks.py`.
- Each one is wired in the same commit that adds it: its logic goes into `MECHANICAL-CHECKS.md`, and its file goes into `SKILL.md`'s file list.
- The entry's `run` subcommand (Task 1B) runs every frontmatter check in one call, writes each result to a per-run temporary folder and prints a short summary with that folder's path. The main session hands each reviewer its part and removes the folder through the runner when the audit ends.

**Architecture:**
- The scripts share one `common/` package. Its own frontmatter reader handles the YAML forms skills use, with file positions, styles, anchors and tags. Each script prints one JSON result.
- Anything the reader cannot read with certainty is reported as unreadable. It is never guessed.
- **Progressive disclosure** (Task 0B):
  - `SKILL.md` keeps the role, the end-to-end flow, the reviewers, the report format and the orchestration rules.
  - It lists, for each phase and each reviewer, every file that belongs to it (agent, reference, assets, scripts), one level deep.
  - Its step 3 links `MECHANICAL-CHECKS.md` with "read it in full before running any check, and read it again whenever it is no longer in your context".
  - The reason: after auto-compaction, Claude Code re-attaches only "the first 5,000 tokens" of each invoked skill (skills docs, "Skill content lifecycle"), never the files it links.
- **Where it lives:** `MECHANICAL-CHECKS.md` sits at the skill root, next to `SKILL.md`, not in `references/`.
  - The sources allow both. The Agent Skills spec ("Optional directories") says "A skill directory may contain any files and directories beyond the required `SKILL.md`. The conventions below are recommendations", and lists `REFERENCE.md` and `FORMS.md` under `references/`. Anthropic's best practices ("Pattern 1") and its `pdf` skill keep `FORMS.md` and `REFERENCE.md` at the root.
  - What decides it is this skill's own layout: the build rule fixes `references/<area>.md` as one reviewer's reference, and each reviewer reads only its own. This file is the main session's playbook and no reviewer reads it, so it stays out of `references/`. Best practices: "Organize for discovery: Structure directories by domain or feature."
  - Links use the exact case, `MECHANICAL-CHECKS.md`, because Linux file systems are case-sensitive.
- `MECHANICAL-CHECKS.md` tells the main session, for every check:
  - the exact command;
  - what it is for and why;
  - what `claude plugin validate` already covers and what the check adds;
  - how to read its output;
  - which reviewer receives it;
  - what to do when it is not run.

**Tech Stack:**
- Python ≥ 3.12, standard library only, `unittest`, ruff, basedpyright;
- POSIX `head`, `od`, `grep`, `awk`, `basename` and `dirname`.

**Spec:** `.claude/maintainer/specs/2026-11-17-frontmatter-checks.md`, Nery's FM-1 to FM-14 cards, copied verbatim.

## Global Constraints

- **Python floor 3.12**, the marketplace's floor for plugin Python (`ruff.toml` `per-file-target-version`, `pyrightconfig.json` `pythonVersion`).
  - The thin entry checks the version before it imports any check module and prints `frontmatter-checks.py: needs Python 3.12 or later; this is X.Y.Z.` to stderr, exit 2. The guard can't sit in a file that also uses 3.12 syntax: Python compiles the whole file first, so `type Alias = int` on 3.11 stops with `SyntaxError` and exit 1 before the guard runs (tested on `/usr/bin/python3.11`). The entry therefore uses only syntax older Pythons parse.
  - The guard compares with a named constant, `MINIMUM_PYTHON = (3, 12)` and `if sys.version_info < MINIMUM_PYTHON:`. Written with the literal, Ruff's UP036 ("Version block is outdated for minimum Python version") fires under the py312 target; with the constant, Ruff, `ruff format` and basedpyright are clean (tested).
- **`allowed-tools` (Nery, 2026-11-17): one wildcard rule per interpreter for the one entry**, not one per command. `SKILL.md`'s frontmatter gets `allowed-tools: Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/frontmatter-checks.py" *), Bash(python "${CLAUDE_SKILL_DIR}/scripts/frontmatter-checks.py" *)`, plus the same two with the `"${CLAUDE_PLUGIN_ROOT}/skills/auditing-skills/scripts/frontmatter-checks.py"` fallback path. The path is quoted in the rule and in every command, because Task 0 found that the rule and the command must match quote for quote. `SKILL.md` and `MECHANICAL-CHECKS.md` write out each exact command.
  - Sources: "A `*` in a Bash rule matches any text, including spaces" and "Claude Code matches everything before the first `*` as written" (permissions, "Wildcard patterns"); with the rule and the body using the same `${CLAUDE_SKILL_DIR}` path, "the script runs without prompting" (skills, "Available string substitutions"). The rule never covers a chained command: "a rule like `Bash(safe-cmd *)` won't give it permission to run the command `safe-cmd && other-cmd`" (permissions, "Compound commands").
  - Why not a repository `settings.json` or `settings.local.json`: those files reach only sessions opened in this repository, never a third party's machine, and in project cloud threads "none of a repository's `.claude/settings.json` permission rules, hooks, or `env` apply" (settings, "Settings in cloud sessions"). `allowed-tools` travels with the skill.
  - Known costs, stated in `MECHANICAL-CHECKS.md`: since 2.1.325 "scheduled tasks and `/loop` ask before running a skill that declares `allowed-tools` or hooks; add `Skill(name)` to `permissions.allow` to run it unattended" (changelog), and under managed `allowManagedPermissionRulesOnly` plugins outside an official or vouched source lose the pre-approval (changelog).
  - `clean` deletes, and the wildcard lets it run without a prompt. That is acceptable only because `clean` refuses any folder without its prefix and marker (Task 1B, Review Focus 4).
  - Settled in Task 0 (Appendix): an unquoted rule doesn't approve the quoted command, and a quoted rule approves the quoted command, even in a path with a space, and not the unquoted one.
- **Packages and the entry (Python docs, tested on 3.12, 3.13 and 3.15):**
  - Layout: `scripts/frontmatter-checks.py` (the only file run by path), `scripts/common/` and `scripts/frontmatter/`, each package with its own `__init__.py`. A regular package "is typically implemented as a directory containing an `__init__.py` file" (Python reference, "The import system", Regular packages); no folder relies on an implicit namespace package, which Ruff's INP001 also rejects.
  - The entry, in this order: imports `pathlib`, `runpy` and `sys`; runs the version guard; sets `sys.dont_write_bytecode = True`; inserts its own folder with `sys.path.insert(0, str(Path(__file__).resolve().parent))`; then hands over with `runpy.run_module("frontmatter.cli", run_name="__main__", alter_sys=True)`. This is the repo's own thin-entry pattern (`scripts/release/release-status.py`), and Ruff's E402 exempts `sys.path` changes between imports, so nothing needs a suppression.
  - Why the explicit path: "The first entry in the module search path is the directory that contains the input script" (Python docs, "The initialization of the sys.path module search path"), and under `-I` "sys.path contains neither the script's directory nor the user's site-packages directory" (Python docs, command line, `-I`). The explicit insert finds `common/` from any working directory, with or without `-I`, and never relies on `PYTHONPATH`. Inserting at position 0 also keeps another package named `common` on the user's path from shadowing ours.
  - No bytecode in the installed plugin: `sys.dont_write_bytecode`: "If this is true, Python won't try to write .pyc files on the import of source modules … you can set it yourself" (Python docs, `sys`). Set in the entry, it holds however the entry is launched, so the documented command and any `allowed-tools` rule need no `-B`. Tested: without it, a run wrote `scripts/common/__pycache__/`; with it, nothing. A read-only skill folder doesn't make Python fail either way (tested, exit 0); the reason is a clean plugin cache on the user's machine.
  - The repository's `.gitignore` already lists `__pycache__/` and `*.pyc` (checked with `git check-ignore`).
- **Python 3.12 idioms allowed:** PEP 695 `type` aliases and type parameters, `typing.override`, PEP 701 f-strings, `match`, dataclasses with `slots=True`.
- **Python 3.13+ APIs and syntax banned:**
  - `warnings.deprecated`, `copy.replace`, `TypeIs`, `ReadOnly`;
  - type parameter defaults;
  - unparenthesized `except A, B` (PEP 758);
  - t-strings;
  - `lazy import`, `frozendict`, `sentinel`.

  Ruff (`py312` target) and basedpyright (3.12) enforce this. Tests run on 3.12, 3.13 and 3.15.
- **No `from __future__ import annotations`:** Python 3.14 "What's New" says "this statement is now deprecated and it is expected to be removed in a future version of Python". Annotations are ordered so that none needs it.
- **Explicit encoding on every read and write.**
  - Each script reconfigures stdout to UTF-8 with `errors="replace"`, wrapped for `AttributeError` and `ValueError`, as Anthropic's `math-proof` `ledger.py` does for Windows consoles.
  - Python 3.15 "What's New", PEP 686: "For best compatibility between versions of Python, ensure that an explicit encoding argument is always provided."
- **Invocation:** `python3 "${CLAUDE_SKILL_DIR}/scripts/frontmatter-checks.py" <subcommand> …`, the pattern of the skills docs ("Generate visual output") and of Anthropic's plugins. Subcommands: `run <SKILL.md>`, `show <folder> …`, `clean <folder>` (Task 1B) and `check <check-id> <SKILL.md>` for one check alone.
  - Never a bare relative path such as `python3 scripts/...` in Claude Code. The skills docs ("Working directory"): "Claude Code runs each command in the session shell's current working directory. That directory moves when Claude runs `cd`. Use `${CLAUDE_SKILL_DIR}` or `${CLAUDE_PROJECT_DIR}` in paths that must resolve the same way every time." A bare path resolves against the audited project, not the skill.
  - Paths relative to the skill root are the open standard's form (agentskills.io "Using scripts": "script execution paths (in code blocks) are relative to the **skill directory root**, because the agent runs commands from there"). They fit hosts that run commands from the skill folder. auditing-skills runs only in Claude Code (it calls `claude plugin` and subagents), so it needs no fallback for other hosts.
  - Fallback when the variable is left unfilled (the path before `/scripts` doesn't exist): `${CLAUDE_PLUGIN_ROOT}/skills/auditing-skills/scripts/...`, as Anthropic's `math-proof` plugin does for its `ledger.py`. If both are unfilled, the check is `not_run` and the main session says so.
  - If `python3` is not found, or Windows answers with the Store message, the main session uses `python` from then on, as in Anthropic's `math-proof` plugin.
  - Scripts carry `#!/usr/bin/env python3` and the executable bit but never rely on either.
- **Wiring in the same commit:** each task that adds a check also registers it in `common/registry.py` (Task 1B), adds its entry to `MECHANICAL-CHECKS.md`, adds its script path under the reviewers that receive it in `SKILL.md`, updates what each of those reviewers receives in `MECHANICAL-CHECKS.md`, and updates `.claude/maintainer/skills-engineering/mechanical-check-sources.md`, as the rule's sync point requires.
  - Each entry follows the "Mechanical-checks entry shape" below.
  - Run `npm run lint:frontmatter` on `SKILL.md` and `claude plugin validate --strict plugins/skills-engineering` after each wiring.
- **Read-only:** no network and no subprocess. A check script writes nothing. A script reads only the `SKILL.md` it is given and its folder name, never settings, MCP or credential files. The runner writes only inside the results folder it created, and deletes only a folder that carries its prefix and its marker file (Task 1B).
- **CLI:** `<check>.py <SKILL.md> [check options]`.
  - Exit 0 whenever a result was printed, with or without findings. Exit 2 when the check could not run: a usage error, a missing path, a directory path, an unreadable file or a Python below 3.12. stderr then gets one line and stdout stays empty.
  - Never exit 1 for findings. The tools reference ("Output limits") says: "A command that exits 1 counts as a valid result for the Bash tool only when Claude Code recognizes exit code 1 as a benign outcome for that command: grep, rg, egrep, fgrep, find, diff, test, [, git diff, and git grep. Every other command that exits 1 counts as a failure." A failure is shown as a head-and-tail excerpt of about 10,000 characters with no saved file, so findings would read as an error and could be cut. Counts of findings go in the output instead.
  - stdout carries only data; stderr carries only diagnostics.
  - An uncaught exception is a bug.
- **Output of a check script:** one line of compact JSON on stdout (`separators=(",", ":")`, `ensure_ascii=False`), keys in this order:
  - `check`, `status` (`ran` | `not_run`), `reason` (string or null), `skill` (the skill's folder name as given), `findings`, `data`.
  - A finding holds, in this order: `check`, `rule`, `file` (relative to the skill folder, so `SKILL.md`), `line`, `column` (1-based file positions or null), `field` (the frontmatter key or null), `found` (an excerpt of at most 120 characters plus `…`, or null), `found_length` (the full value's length in characters, or null), `expected` (one short sentence of what the rule wants), `basis` (`official` | `convention` | `inference`), `surfaces` (a subset of `claude-code`, `open-spec`, `upload`, in that order) and `condition` (string or null).
  - `upload` means claude.ai uploads, the Skills API and `package_skill.py`, which the skills docs group as one path.
  - **No severity, not even a hint.** Severity belongs to each reviewer's severity model, which depends on facts a script doesn't know, such as the surfaces the skill targets: "A surface the skill doesn't target gets no finding" and "When the consequence differs by target, set the severity of the most affected target" (`references/frontmatter-description.md`). A count-based label is the error `references/size-limits-and-budgets.md` shows as "Wrong severity: The body has 612 lines, over the limit: Critical." `basis`, `surfaces` and `condition` carry the facts the reviewer grades from.
  - **Deterministic:** no timestamps and no absolute paths. Findings sorted by `line`, `column`, `rule`; `data` keys in a fixed order per check. Two runs on the same file print the same bytes.
  - The meaning of each `rule` lives once in `MECHANICAL-CHECKS.md`, not in every finding.
- **Results lifecycle (Task 1B):**
  - The runner creates its folder with `tempfile.mkdtemp(prefix="auditing-skills-fm-")`, which follows `TMPDIR`, then `TEMP`, then `TMP`, then the platform list (Python `tempfile.gettempdir`). The random suffix is the run id. The folder is "readable, writable, and searchable only by the creating user ID" (Python `tempfile.mkdtemp`).
  - It prints the folder's absolute path, and `show` and `clean` take that path as an argument and never recompute it. The sandboxing docs ("Temporary directories") say sandboxed and unsandboxed commands "resolve `$TMPDIR` to different directories" while filesystem isolation is on.
  - Not `${CLAUDE_PLUGIN_DATA}`: the plugins docs describe it as "a directory that survives updates, for `node_modules`, virtual environments, and caches", so per-audit results would stay there across sessions.
  - The main session reads results only through `frontmatter-checks.py show`, a Bash command, never with the Read tool, because reads outside the working directory and additional directories prompt (permissions docs). Reviewers never open the folder; each gets its part in its brief.
- **Prerequisites:** a check whose prerequisite failed returns `status: not_run` with `reason` naming the check that failed, for example `"frontmatter.yaml failed"`.
- **Identifiers:** check ids are `frontmatter.<slug>`. FM-n appears only in this plan, never in plugin files, because no plugin file names a maintainer validator rule id.
- **Field tables:** only in `common/fields.py`, taken from the Claude Code 2.1.326 docs (`/en/skills` Frontmatter reference), `agentskills.io/specification` and anthropics/skills `quick_validate.py`.
- **Quality:** ruff check and ruff format clean, basedpyright 0 errors, and an `__init__.py` in `common/`.
- **No suppressions, ever (Nery):** no `# noqa`, `# type: ignore`, `# pyright: ignore` or `# basedpyright: ignore`, and no per-file ignore, `exclude` or rule change in `ruff.toml`, `pyrightconfig.json` or `pyproject.toml` added to silence a finding. Fix the code. If a finding truly can't be fixed, stop and ask Nery. Task 10 Step 5 gates this.
- **Portability:** no POSIX-only Python APIs. Commands use only POSIX options, avoid `grep -P`, `sed -i` and `$'…'`, and contain no `$` followed by a digit, because skills substitute `$N` with arguments.
- **Tests:** in `plugins/skills-engineering/tests/test_frontmatter_*.py`, stdlib `unittest`, run by `npm run test:plugins`.
- **Git:** one commit per task, and no push without Nery's authorization.

## Coverage split: what the existing command does and what each check adds

`claude plugin validate --json`, already in the mechanical step, is "the command" in the spec's Coverage lines. No check re-reports what it already reports.

| Spec | `claude plugin validate` already reports (spec Coverage) | Added by this plan | Form |
| :-- | :-- | :-- | :-- |
| FM-1 | no block (unclosed, blank first line, none); not a mapping | the files validate never reads: a `SKILL.md` at a plugin root and a skill in a symlinked folder. Step 3 copies them, following symlinks (`cp -RL`), into `skills/<name>/` of the temporary plugin step 3 already builds, so validate reads them. BOM and CRLF follow Task 0. | command |
| FM-2 | unclosed quote, tab in indentation | duplicate keys, `: ` inside a value, unclosed flow collection, key indented under a scalar | script `frontmatter.yaml` |
| FM-3 | nothing | all of it | script `frontmatter.plain-values` |
| FM-4 | nothing (passed `Other_Name-claude-`) | all of it, plus the name's character counts for size-limits | script `frontmatter.name` |
| FM-5 | nothing | all of it | script `frontmatter.name-plain` |
| FM-6 | nothing | the reserved words in `name` (in `frontmatter.name`); the folder name by command, read against the location from step 2 | script + command |
| FM-7 | nothing (passed an XML tag and 1,100 characters) | all of it | script `frontmatter.description` |
| FM-8 | nothing | all of it | script `frontmatter.listing-cap` |
| FM-9 | nothing (passed 600 characters) | all of it | script `frontmatter.compatibility` |
| FM-10 | nothing (passed `metadata: {a: 1}`) | all of it | script `frontmatter.metadata` |
| FM-11 | nothing (`--strict` passed `bogus-key`) | the top-level keys with their lines, by command; the reviewer compares them with the field table in its reference | command |
| FM-12 | `allowed-tools: 42`, `shell: fish` | the boolean forms, `context`, `effort`, `model`, and the string-or-list types of `disallowed-tools`, `paths` and `arguments` | script `frontmatter.field-values` |
| FM-13 | nothing | all of it | script `frontmatter.field-combinations` |
| FM-14 | nothing | all of it | script `frontmatter.allowed-tools` |

When the reader stops on an error that validate already reports (an unclosed quote or a tab), the script returns `status: not_run` with `reason: "the frontmatter has an error claude plugin validate reports"`. It never re-reports that error.

Task 10 checks this split against validate on 2.1.326. A case where validate now reports something the spec says it missed moves to validate and leaves the script. Report it to Nery with both outputs.

## Mechanical-checks entry shape

`MECHANICAL-CHECKS.md` holds one shared section (Tasks 1 and 1B) and then one entry per check. The shared section states once:
- how to run the runner and a single script (`python3`, then `python`, with quoted paths);
- the summary lines, the JSON fields and what `status`, `findings`, `found_length`, `surfaces` and `condition` mean;
- that exit 2 or a missing interpreter means the check was not run: name it to its reviewers with the exit code and message;
- that `not_run` means its prerequisite failed, which also goes to its reviewers;
- that findings are passed verbatim, with no severity added and none dropped;
- the lifecycle: `run` once in step 3; `show --reviewer <name>` for each reviewer's brief; before dispatch, confirm that every reviewer named in the summary got its part; `clean` after the report, and also when the audit stops early.

Each entry then holds:
- **the exact command**;
- **what it checks and why**, in one sentence;
- **what validate already covers and what the check adds**, or "no other command covers this; this check is the only source";
- **how to read the result**: which rules exist and what a finding on each means;
- **who receives it**: the reviewer names, matching each reviewer's "Receives" list in the same file.

## Review Focus

1. A `SKILL.md` that isn't UTF-8 (UTF-16 with a BOM, Latin-1) gives `frontmatter.yaml` the rule `not-utf8` and no traceback (Task 4).
2. Recursive or deeply nested YAML (`a: &x [*x]`, 5,000 nested `[`) terminates within 5 s with `too-deep` or `unsupported`, and no other script hangs (Task 3).
3. Characters outside the Basic Multilingual Plane (emoji) in `description` or `when_to_use`: lengths are in code points, with `utf16_length` in `data` (Task 6).
4. `frontmatter-checks.py clean` given a folder it did not create (`/`, the home folder, the working directory, a symlink to a results folder, a folder with the prefix but no marker) removes nothing and exits 2 (Task 1B).
5. CRLF, a BOM and a trailing space on the markers give the same reader result as clean LF (Task 2). Validate's handling of them, from Task 0, decides whether Task 9 adds a command for them.

---

### Task 0: Pin the open behaviors before code

No code ships from this task. Its results fill the Appendix, and the later tests encode them.

- [ ] **Step 1:** Run `claude plugin validate --json` (2.1.326) on throwaway plugins with these cases:
  - a BOM;
  - CRLF line endings;
  - `--- ` with a trailing space as the opening and as the closing marker;
  - a U+2028 character in a value;
  - a duplicate key, to see which value Claude Code keeps;
  - Latin-1 and UTF-16 bytes, to see whether validate reports a file that isn't UTF-8.

  Record each outcome.
- [ ] **Step 2:** With ruamel.yaml 0.19.1 (`uv run`), confirm that `a: foo:` and `a: x: y` fail to parse. Then settle each of these and record its source:
  - the separator Claude Code puts between `description` and `when_to_use` (docs: "Appended to `description`");
  - whether `Bash` and `Bash(*)` both approve every command (`/en/permissions`);
  - whether plugin skills that reach claude.ai hit the six-field upload rule (support.claude.com). The spec says they do; this is unverified;
  - with a throwaway plugin skill declaring `allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/x.py *)`, whether `python3 "<expanded path>/scripts/x.py" a` and `python3 <expanded path>/scripts/x.py a` each run without a prompt in `claude -p` with no other allow rules.
- [ ] **Step 3:** If any result contradicts the spec, stop and report it to Nery with both texts quoted.
- [ ] **Step 4:** Commit the Appendix: `git commit -m "Record the loader behaviors the frontmatter checks rely on"`.

### Task 0B: Split the mechanical step out of `SKILL.md`

`SKILL.md` measures 20,277 bytes today, already about the 5,000-token mark, before any check is wired.

**Files:**
- Create: `plugins/skills-engineering/skills/auditing-skills/MECHANICAL-CHECKS.md`
- Modify: `.../auditing-skills/SKILL.md`, `.claude/rules/plugins/skills-engineering.md` (sync points), `.claude/maintainer/skills-engineering/mechanical-check-sources.md`

Steps:
- [ ] **Step 1:** Run `claude --plugin-dir plugins/skills-engineering plugin details skills-engineering` and record the skill's on-invoke token estimate (the "before" figure).
- [ ] **Step 2:** Move step 3's commands and every reviewer's "Receives" list, unchanged in meaning, into `MECHANICAL-CHECKS.md`, under these headings:
  - "How to run the checks";
  - one heading per data domain;
  - "What each reviewer receives".
- [ ] **Step 3:** Rewrite `SKILL.md`:
  - Step 3 holds one link with when to read it: "read it in full before running any check, and read it again whenever it is no longer in your context".
  - Each reviewer entry keeps its name, agent, domain sentence and its files: the agent, its reference, the report template and, as they land, its scripts. Each file is linked one level deep.
  - Step 4's "results of the mechanical checks that reviewer receives" points to the Receives section of `MECHANICAL-CHECKS.md`.
- [ ] **Step 4:** Update the rule's sync points. "Receives entry and the step 3 command in `SKILL.md`" becomes "the Receives list and the command entry in `MECHANICAL-CHECKS.md`, and the reviewer's file list in `SKILL.md`". Add that `references/` holds only reviewer references and that the root `MECHANICAL-CHECKS.md` is the main session's playbook, which no reviewer reads. Load `instruction-engineering:cc-md-and-rules` first, as the repo requires for any rule edit.
- [ ] **Step 5:** Run `npm run lint:frontmatter`, `npx biome lint` on both Markdown files, `claude plugin validate --strict plugins/skills-engineering` and `plugin details` again. Expected:
  - `valid`;
  - an on-invoke estimate lower than Step 1's;
  - the whole orchestration inside the first 5,000 tokens of `SKILL.md`.

  Show both figures.
- [ ] **Step 6:** Commit: `git commit -m "Move the audit's mechanical step into MECHANICAL-CHECKS.md"`.

### Task 1: Shared foundation

**Files:**
- Create in `.../auditing-skills/scripts/common/`: `__init__.py`, `report.py`, `context.py`, `cli.py`, `skill_file.py`, `text.py`, `fields.py`
- Test: `plugins/skills-engineering/tests/frontmatter_helpers.py`, `tests/test_frontmatter_foundation.py`

**Interfaces (produced):**
- `type Surface = Literal["claude-code","open-spec","upload"]`. `type Basis = Literal["official","convention","inference"]`.
- `report.Finding(check: str, rule: str, line: int | None, column: int | None, field: str | None, found: str | None, expected: str, basis: Basis, surfaces: tuple[Surface, ...], condition: str | None = None, file: str = "SKILL.md")`, a frozen, slotted dataclass; `found_length` is computed from the untruncated `found`.
- `report.CheckResult(check: str, status: Literal["ran","not_run"], reason: str | None, skill: str, findings: list[Finding], data: dict[str, object])`.
- `report.to_json(result: CheckResult) -> str`: one line of compact JSON in the key order above, findings sorted, `found` cut to 120 characters plus `…`. `report.emit(result: CheckResult) -> None` writes it and a newline to stdout.
- `context.Context(skill_md: Path, skill_dir: Path, folder_name: str, resolved_folder_name: str, options: dict[str, object])`.
- `cli.run(check_id: str, check: Callable[[Context], CheckResult], extra: Callable[[argparse.ArgumentParser], None] | None = None) -> NoReturn`: reconfigures stdout, validates the path (exit 2 cases), builds `Context`, calls `check`, emits, exits 0.
- `skill_file.read(path: Path) -> SkillFile`, holding:
  - `text: str | None`, decoded UTF-8 with the BOM stripped and CRLF and CR normalized to LF;
  - `decode_error: str | None`, `had_bom: bool`, `had_crlf: bool`;
  - `block: Block | None`, `problem: Literal["no-opening-marker","unclosed","empty"] | None`.
  - `Block(close_line: int, yaml_text: str, first_yaml_line: int)`: the opening marker is line 1, and `first_yaml_line` is 2. Marker equality follows Task 0's trailing-whitespace result.
- `text.utf16_len(s: str) -> int`. `text.snippet(s: str, index: int, width: int = 40) -> str` returns `before|after`.
- `fields`, constant tuples:
  - `CLAUDE_CODE_FIELDS`: the 20 docs fields in table order: `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `background`, `hooks`, `paths`, `shell`, `metadata`, `license`, `compatibility`.
  - `SPEC_FIELDS`: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`.
  - `BOOLEAN_FIELDS`: `disable-model-invocation`, `user-invocable`, `background`.
  - `BOOLEAN_FORMS`: {`true`, `false`, `yes`, `no`, `on`, `off`, `1`, `0`}, matched case-insensitively.
  - `EFFORT_LEVELS`: `low`, `medium`, `high`, `xhigh`, `max`.
  - `MODEL_VALUES`: `default`, `best`, `fable`, `sonnet`, `opus`, `haiku`, `sonnet[1m]`, `opus[1m]`, `opusplan`, `inherit`.
  - `TEXT_FIELDS`: `name`, `description`, `when_to_use`, `argument-hint`, `model`, `effort`, `context`, `agent`, `shell`, `license`, `compatibility`.
  - `SOURCES`: a dict of rule area to doc URL.
- `frontmatter_helpers.run_check(check_id: str, skill_md: str | bytes, *, folder: str = "demo-skill", args: tuple[str, ...] = (), python: str = sys.executable) -> tuple[int, dict[str, object]]`. It writes `<tmp>/<folder>/SKILL.md`, runs `frontmatter-checks.py check <check_id>` with that file and parses stdout. `rules(result) -> list[tuple[str, int | None]]`.

- [ ] **Step 1: Write the failing tests.** In `test_frontmatter_foundation.py`:

  | test | input | expected |
  | :-- | :-- | :-- |
  | `test_read_valid` | `---\nname: a\n---\nbody` | `problem is None`, `block.close_line == 3` |
  | `test_blank_first_line` | `\n---\nname: a\n---\n` | `problem == "no-opening-marker"` |
  | `test_unclosed` | `---\nname: a\n` | `problem == "unclosed"` |
  | `test_empty_block` | `---\n---\n` | `problem == "empty"` |
  | `test_bom_crlf` | BOM + CRLF version of `test_read_valid` | same block, and `had_bom` and `had_crlf` true |
  | `test_latin1` | `b"---\nname: \xe9\n---\n"` | `decode_error` set, `text is None` |
  | `test_utf16_len` | `"a😀"` | `3` |
  | `test_snippet` | `("abcdef", 3, 2)` | `"bc|de"` |
  | `test_emit_order_and_truncation` | a 200-character `found` | keys in order; `found` is 121 characters ending `…`; `found_length == 200` |
  | `test_json_compact_one_line` | any result | no newline inside, no `", "` or `": "` separators |
  | `test_findings_sorted` | findings given out of order | sorted by line, column, rule; unpositioned last |
  | `test_deterministic` | the same file checked twice | byte-identical stdout, no absolute path in it |

  Add the CLI cases, run through a throwaway check registered in the test:
  - a missing path exits 2 with empty stdout;
  - a directory exits 2;
  - a symlink `link -> real` gives `folder_name == "link"` and `resolved_folder_name == "real"`;
  - `/usr/bin/python3.11` gets exit 2 and the floor message, with the test skipped when that interpreter is absent;
  - run from an unrelated working directory, and again under `python3 -I`, the entry finds its packages, and no `__pycache__` appears under `scripts/`.
- [ ] **Step 2:** Run `python3 -m unittest discover -s plugins/skills-engineering/tests -p 'test_frontmatter_*.py' -v`. Expected: the tests fail with a missing module.
- [ ] **Step 3:** Implement the interfaces.
- [ ] **Step 4: Wire.** Add the shared section from "Mechanical-checks entry shape" to `MECHANICAL-CHECKS.md`, before any check entry, and list `scripts/common/` in `SKILL.md`'s file list as shared by every frontmatter script.
- [ ] **Step 5:** Run the tests on `/usr/bin/python3.12`, `/usr/bin/python3.13` and `python3` (3.15). Expected: all pass. Then run ruff and basedpyright on the new files: 0 findings. Then run `npm run lint:frontmatter` and `claude plugin validate --strict plugins/skills-engineering`. Expected: `valid`.
- [ ] **Step 6:** Commit: `git commit -m "Add the shared foundation for the frontmatter checks"`.

### Task 1B: Runner and results lifecycle

**Files:**
- Create: `.../auditing-skills/scripts/common/registry.py`, `.../auditing-skills/scripts/frontmatter-checks.py`, `.../auditing-skills/scripts/frontmatter/cli.py`
- Test: `tests/test_frontmatter_runner.py`

**Interfaces (produced):**
- `registry.CheckSpec(check: str, module: str, receivers: tuple[str, ...], requires: tuple[str, ...] = ())`, frozen and slotted. `registry.CHECKS: tuple[CheckSpec, ...]`, in run order, empty at this task; each later task appends its check. `requires` names the checks whose failure makes this one `not_run`.
- Each check module exposes `check(ctx: Context) -> CheckResult`. `frontmatter/cli.py` parses the subcommands, imports the check modules and calls `check` in-process: no subprocess. `check <id>` goes through `cli.run`, so a single check prints exactly what `run` writes to its file.
- `frontmatter-checks.py run <SKILL.md>`:
  - sweeps folders in `tempfile.gettempdir()` named `auditing-skills-fm-*` that hold the marker `.auditing-skills-results` and are older than 24 hours, skipping symlinks;
  - creates the results folder and the marker, writes `<check>.json` per check and `summary.json` (check, status, finding count, receivers);
  - prints one line per check, `<check> <status> <n> finding(s) -> <receivers>`, then `results: <absolute folder path>`. Exit 0; exit 2 if the file can't be read or the folder can't be created, with the folder removed.
- `frontmatter-checks.py show <folder> (--check <check> | --reviewer <name>)`: prints the matching results, one JSON line each. Exit 2 for a folder without the marker or prefix, or an unknown check or reviewer.
- `frontmatter-checks.py clean <folder>`: removes the folder only when it is a real directory (not a symlink) directly under a temp root, named with the prefix, and holding the marker; prints `removed <path>`. Otherwise removes nothing and exits 2.

- [ ] **Step 1: Write the failing tests**, with a throwaway check registered in the test:
  - `run` prints one line per registered check plus the `results:` line, and the folder holds `summary.json`, the marker and one file per check;
  - each `<check>.json` is byte-identical to that script's own stdout on the same file;
  - two runs give byte-identical per-check files in different folders;
  - a check whose `requires` failed is `not_run` with the reason naming it;
  - `show --reviewer` prints exactly the checks whose receivers include that reviewer;
  - `clean` removes its folder; on `/`, the home folder, the cwd, a symlink to a results folder, and a prefixed folder without the marker it removes nothing and exits 2;
  - the sweep removes a marked folder older than 24 hours (set with `os.utime`) and keeps a fresh one, an unmarked one and a symlink;
  - with `TMPDIR` pointed at a test folder, the results folder is created there.
- [ ] **Step 2:** Run the tests. Expected: they fail with a missing module.
- [ ] **Step 3:** Implement the interfaces. Use `shutil.rmtree` only after the checks in `clean`, and never follow symlinks.
- [ ] **Step 4: Wire.** In `MECHANICAL-CHECKS.md`'s shared section, add the runner command, how to read its summary, `show` and `clean`, and the delivery check before dispatch. In `SKILL.md`, add the `allowed-tools` rules from Global Constraints to the frontmatter, written as Task 0 found they match; step 3 runs the runner, each reviewer's brief gets its `show --reviewer` output, and the report step ends with `clean`. Re-measure the first 5,000 tokens with `claude plugin details`.
- [ ] **Step 5:** Run the tests on 3.12, 3.13 and 3.15, then ruff, basedpyright, `npm run lint:frontmatter` and `claude plugin validate --strict plugins/skills-engineering`. Expected: all pass, 0 findings, `valid`.
- [ ] **Step 6:** Commit: `git commit -m "Add the frontmatter checks runner and its results lifecycle"`.

### Task 2: Frontmatter reader, block structure and scalars

**Files:**
- Create: `common/yaml_reader.py`
- Test: `tests/test_frontmatter_reader.py`

**Interfaces (produced):**
- `Node`, a slotted dataclass:
  - `kind: Literal["map","seq","scalar","alias"]`;
  - `style: Literal["plain","single","double","literal","folded","flow"] | None`;
  - `raw: str`, the exact source text of a scalar;
  - `value: str`, the scalar's text after unquoting and folding;
  - `pairs: list[tuple[Node, Node]]`, `items: list[Node]`;
  - `line: int`, `column: int`, `end_line: int`, `anchor: str | None`, `tag: str | None`.
- `ReadError(rule: Literal["colon-in-value","unclosed-quote","unclosed-flow","key-under-scalar","tab-indent","duplicate-key","syntax-error","too-deep","unsupported"], message: str, line: int, column: int)`, an exception carrying file positions.
- `read(yaml_text: str, first_line: int) -> Node`: raises `ReadError`.

What this task supports:
- block mappings with plain or quoted single-line keys;
- block sequences, including `- ` entries inside a mapping value;
- plain scalars over several lines (folded with one space, a blank line giving `\n`);
- single-quoted (`''` escape) and double-quoted scalars (YAML escapes `\\ \" \n \t \uXXXX \UXXXXXXXX`, line folding), over several lines;
- `#` comments, both full-line and after a space.

What it rejects:
- `colon-in-value`: `: ` or a trailing `:` inside a plain value in block context ("mapping values are not allowed here").
- `unclosed-quote`: an unclosed quote.
- `key-under-scalar`: a key indented under a scalar.
- `syntax-error`: any other malformed input, such as a plain value starting with `,`, `%`, `@` or `` ` ``.
- `tab-indent`: a tab in indentation.
- `duplicate-key`: the second occurrence of a key in the same mapping, compared by key text after unquoting.
- `unsupported`: anything this task does not parse yet, such as `?` complex keys, `%` directives, a `...` document end or a multi-document stream.

The parser is a recursive-descent over lines with an explicit depth counter: beyond 100 levels it raises `too-deep`. It never raises `RecursionError`.

- [ ] **Step 1: Write the failing tests.** Each case calls `read(text, 2)`:
  - `name: a\ndescription: b` gives two pairs, values `a` and `b`, at lines 2 and 3;
  - `description: one\n  two\n\n  three` gives `value == "one two\nthree"`, `style == "plain"` and `end_line == 5`;
  - `d: 'it''s'` gives `it's`, and `d: "a\tb\u00e9"` gives `a<TAB>bé`;
  - `metadata:\n  a: "1"` gives a nested map;
  - `tools:\n  - Read\n  - Grep` gives a seq of 2;
  - `d: x # note` gives `value == "x"`;
  - errors with their lines:
    - `d: Use when: x` gives `colon-in-value` at line 2;
    - `d: "abc` gives `unclosed-quote`;
    - `m:\n\tk: v` gives `tab-indent` at line 3;
    - `name: a\n  b: c` gives `key-under-scalar` at line 3;
    - `name: a\nname: b` gives `duplicate-key` at line 3;
    - `? a` gives `unsupported`.
- [ ] **Step 2:** Run the Task 1 test command. Expected: these tests fail.
- [ ] **Step 3:** Implement `read` for this subset.
- [ ] **Step 4:** Run the tests on 3.12, 3.13 and 3.15, plus ruff and basedpyright. Expected: pass and 0 findings.
- [ ] **Step 5:** Commit: `git commit -m "Add the frontmatter reader for block structure and scalars"`.

### Task 3: Reader, block scalars, flow collections, anchors, tags and type resolution

**Files:**
- Modify: `common/yaml_reader.py`
- Create: `common/yaml_types.py`
- Test: `tests/test_frontmatter_reader_advanced.py`

**Interfaces (produced):**
- `read` additionally supports:
  - `|` and `>` with the chomping indicators `-` and `+` and an indentation digit;
  - flow sequences and mappings `[a, b]` and `{a: 1}`, nested and over several lines;
  - `&anchor`, `*alias` (kind `alias`, `value` = the anchor name) and `!tag` or `!!tag` on any node.
- An unclosed flow collection raises `unclosed-flow` at the line of its opening bracket.
- An alias to an unknown anchor raises `syntax-error`.
- An alias is never expanded, so recursion is impossible.
- `yaml_types.yaml11_tag(node: Node) -> Literal["str","bool","int","float","null","timestamp"]`: YAML 1.1 implicit resolution for plain scalars, using the regular expressions of the YAML 1.1 type repository (`bool`, `int`, `float`, `null`, `timestamp`). Quoted and block scalars are `str`.
- `yaml_types.yaml12_tag(node: Node)`, the same for the YAML 1.2 core schema.
- `yaml_types.to_python(node: Node, schema: Literal["1.1","1.2"]) -> object`.

- [ ] **Step 1: Write the failing tests.**
  - `d: |\n  a\n  b\n` gives `"a\nb\n"`, and `d: >-\n  a\n  b` gives `"a b"`.
  - `t: [Read, "Bash(git *)"]` gives a seq of 2 with `style == "flow"`, and `m: {a: 1}` gives a map.
  - `t: [Read` gives `unclosed-flow` at line 2.
  - `name: &n demo` gives `anchor == "n"`, `x: *n` gives an alias, and `d: !!str 1` gives `tag == "!!str"`.
  - `a: &x [*x]` returns in under 1 s.
  - 5,000 nested `[` give `too-deep`.
  - With `yaml11_tag`:
    - `on`, `Yes` and `n` give `bool`;
    - `0o7` gives `str` (YAML 1.1 octal is `0[0-7]+`);
    - `017` gives `int`;
    - `1_000` gives `int`;
    - `1e3` gives `float`;
    - `2026-11-17` gives `timestamp`;
    - `~` gives `null`.
  - With `yaml12_tag`, `on` gives `str` and `0o7` gives `int`.
  - **Differential test** (`@unittest.skipUnless(importlib.util.find_spec("ruamel"))`): for 40 valid fixtures covering every form above, `to_python(node, "1.2")` equals `ruamel.yaml.YAML(typ="safe", pure=True).load(text)`. For 15 invalid fixtures, both reject.
- [ ] **Step 2:** Run the tests. Expected: they fail. Run them a second time with `uv run`, so the differential test is not skipped.
- [ ] **Step 3:** Implement.
- [ ] **Step 4:** Run the tests on 3.12, 3.13 and 3.15, and under `uv run`, plus ruff and basedpyright. Expected: all pass and 0 findings.
- [ ] **Step 5:** Commit: `git commit -m "Complete the frontmatter reader and add YAML 1.1 and 1.2 type resolution"`.

### Task 4: FM-2 strict YAML (`frontmatter.yaml`) and FM-3 plain values (`frontmatter.plain-values`)

**Files:** Create `common/frontmatter.py`, `frontmatter/yaml_syntax.py` and `frontmatter/plain_values.py`. Tests: `tests/test_frontmatter_yaml.py` and `tests/test_frontmatter_plain_values.py`.

**Interfaces:** `frontmatter.load(ctx: Context) -> Loaded` with these fields:
- `file: SkillFile`;
- `root: Node | None`;
- `error: ReadError | None`;
- `fields: dict[str, tuple[Node, Node]]`, keyed by the top-level key text, holding the key node and the value node.

`yaml_syntax.py` reports only the four failures validate misses:
- `duplicate-key`: basis `inference`, because Claude Code's parser accepted it;
- `colon-in-value`: `: ` or a trailing `:` inside a plain value;
- `unclosed-flow`;
- `key-under-scalar`.

The last three have basis `official` (skills docs: the skill "still loads with no fields set"). All four use surfaces `("open-spec","upload")` and the condition "Claude Code accepted it when tested; packaging and upload reject it".

It does not report:
- an unclosed quote or a tab, which return `not_run` with the reason from the coverage split;
- a missing block or a non-mapping root, which return `not_run` with the reason "no frontmatter block: claude plugin validate reports it";
- not-UTF-8 bytes, which give the single rule `not-utf8`, since validate's handling of them is unverified. Task 0 checks it and drops the rule if validate covers it.

`data` = `{close_line}`.

`plain_values.py`, surfaces `("upload","open-spec")`, basis `inference`, with these rules:
- `comment-truncates`: a plain value followed by ` #` on its line;
- `leading-indicator`: a plain value starting with `-`, `?` or `:`;
- `reads-as-collection`: a `TEXT_FIELDS` value that is a seq or map;
- `anchor-alias-tag`: a `TEXT_FIELDS` value with an anchor, an alias or a tag;
- `reads-as-boolean` and `reads-as-null`: a plain `TEXT_FIELDS` value or a `metadata` value, at any depth, whose lowercase text is in the spec's list.
- `data.colon_cases = "reported by frontmatter.yaml"`, as Task 0 confirmed.

- [ ] **Step 1: Write the failing tests.**
  - For `yaml_syntax.py`:
    - `name: a\nname: b` gives `("duplicate-key", 3)`;
    - `d: Use when: x` gives `("colon-in-value", 2)`;
    - `t: [Read` gives `("unclosed-flow", 2)`;
    - `name: a\n  b: c` gives `("key-under-scalar", 3)`;
    - `d: "abc` gives `not_run` with the validate reason, and so does `m:\n\tk: v`;
    - `- a` and `\n---` give `not_run`;
    - Latin-1 bytes give `not-utf8`;
    - a valid block gives `[]`.
  - For `plain_values.py`:
    - `description: Run it # carefully` gives `("comment-truncates", 2)`;
    - `argument-hint: [file]` gives `reads-as-collection`;
    - `name: yes` gives `reads-as-boolean`;
    - `description: ~` gives `reads-as-null`;
    - `compatibility: -x` gives `leading-indicator`;
    - `description: "yes"` gives `[]`;
    - `metadata:\n  flag: on` gives `("reads-as-boolean", 3)`;
    - `user-invocable: no` gives `[]`;
    - `description: &d text` gives `anchor-alias-tag`;
    - a syntax error gives `status == "not_run"` and `reason == "frontmatter.yaml failed"`.
- [ ] **Step 2:** Run the tests. Expected: they fail.
- [ ] **Step 3:** Implement the scripts and set the executable bit.
- [ ] **Step 4: Wire.** Add the two entries to `MECHANICAL-CHECKS.md`, and list both scripts under their reviewers in `SKILL.md`.
  - `frontmatter.yaml`:
    - adds the four strict-YAML failures validate passes;
    - a finding means packaging and upload reject the file, while Claude Code may still load it;
    - `not_run` with the validate reason means read validate's output instead;
    - goes to `frontmatter-description` and `runtime-contract`.
  - `frontmatter.plain-values`:
    - no other command covers it;
    - a finding means the parsed value differs from what the line shows;
    - goes to `frontmatter-description`.
  - Update both reviewers' Receives lists in `MECHANICAL-CHECKS.md` and the sync file.
- [ ] **Step 5:** Run the tests on 3.12, 3.13 and 3.15, plus ruff, basedpyright, `lint:frontmatter` and `validate --strict`. Expected: pass, 0 findings and `valid`.
- [ ] **Step 6:** Commit: `git commit -m "Add and wire the strict YAML and plain-value frontmatter checks"`.

### Task 5: FM-4 (`frontmatter.name`) and FM-5 (`frontmatter.name-plain`)

**Files:** Create `frontmatter/name_format.py` and `frontmatter/name_plain.py`. Tests: `tests/test_frontmatter_names.py`.

`name_format.py`:
- `missing`: basis official, surfaces `("open-spec","upload")`, with `data.name_source = "folder"`.
- `not-a-string`, decided by `yaml11_tag`.
- `length`: under 1 or over 64 characters.
- `charset`: anything outside `[a-z0-9-]`.
- `hyphen`: a leading, trailing or consecutive hyphen.
- `folder-mismatch`: compared against `ctx.folder_name`.
  - These five use surfaces `("open-spec","upload")`.
- `refused-character`, surfaces `("claude-code",)`, for any of:
  - `<` or `>`;
  - a character in category `Cc`, `Cf`, `Co` or `Cn`;
  - a `Zs` character other than U+0020;
  - two spaces in a row;
  - a leading or trailing space.
- `reserved-word` (FM-6's name part): `anthropic` or `claude` in the name, case-insensitive, or in the folder name when `name` is absent. Surfaces `("upload",)`, basis official.
- `data` = `{name, length, utf16_length, folder_name, matches_folder, unicode_version}`, where `unicode_version` comes from `unicodedata.unidata_version`, because `Cn` depends on it.

`name_plain.py`:
- `quoted`, `block-scalar`, `multi-line`, `anchor-alias-tag`: basis `convention`, surfaces `()`.
- `yaml11-type`: when `yaml11_tag` is `int`, `float` or `timestamp`. Booleans and null belong to `frontmatter.plain-values`. Basis `inference`, surfaces `("upload",)`.

- [ ] **Step 1: Write the failing tests.**
  - For `name_format.py`:
    - `name: demo-skill` in the folder `demo-skill` gives `[]`;
    - `name: Other_Name-claude-` in the folder `x` gives `charset`, `hyphen` and `folder-mismatch`;
    - 65 characters give `length`;
    - `a--b` gives `hyphen`;
    - `"a\u200bb"` gives `refused-character` and `charset`;
    - `"<x>"` gives `refused-character`;
    - `"a\u00a0b"` gives `refused-character`;
    - no name gives `missing`;
    - `name: 12` gives `not-a-string`.
  - For `name_plain.py`:
    - `name: demo` gives `[]`;
    - `name: "demo"` gives `quoted`;
    - `name: |\n  demo` gives `block-scalar`;
    - `name: &a demo` gives `anchor-alias-tag`;
    - `name: 2026-11-17` gives `yaml11-type`;
    - `name: 1e3` gives `yaml11-type`;
    - `name: on` gives `[]`.
- [ ] **Step 2:** Run the tests. Expected: they fail.
- [ ] **Step 3:** Implement the scripts and set the executable bit.
- [ ] **Step 4: Wire.** Add the entries to `MECHANICAL-CHECKS.md`, and list the scripts under their reviewers in `SKILL.md`. `frontmatter.name`: validate passed a malformed name, so this check is the only source for the name rules; it also covers the reserved words in the name and gives the name's character counts. Its findings and `data` go to `frontmatter-description`, and its counts to `size-limits-and-budgets`. `frontmatter.name-plain`: no other command covers it; its findings follow a project convention, not an official rule; goes to `frontmatter-description`. Update each named reviewer's Receives list in `MECHANICAL-CHECKS.md` and the sync file.
- [ ] **Step 5:** Run the tests on 3.12, 3.13 and 3.15, plus ruff, basedpyright, `lint:frontmatter` and `validate --strict`. Expected: pass, 0 findings and `valid`.
- [ ] **Step 6:** Commit: `git commit -m "Add and wire the name and plain-name frontmatter checks"`.

### Task 6: FM-7 (`frontmatter.description`), FM-8 (`frontmatter.listing-cap`) and FM-9 (`frontmatter.compatibility`)

**Files:** Create `frontmatter/description.py`, `listing_cap.py` and `compatibility.py`. Tests: `tests/test_frontmatter_text_limits.py`.

Every length is in code points, with `utf16_length` in `data`.

`description.py`:
- `missing`: surfaces `("open-spec","upload")`, with `data.claude_code_fallback = "first non-empty body line"`.
- `not-a-string`, `empty` (whitespace only).
- `too-long`: over 1,024 characters.
- `angle-bracket`: any `<` or `>`. Surfaces `("upload","claude-code")`. `quick_validate.py` rejects it, and Claude Code shows `&lt;` and `&gt;`. `data.xml_tags` comes from the regex `<[A-Za-z/!?][^<>]*>`.

`listing_cap.py`:
- Option `--cap N`, default 1536.
- Combined text = `description` + Task 0 separator + `when_to_use`.
- `over-cap`, with `data` = `{description_length, when_to_use_length, combined_length, cap, first_lost_field, first_lost_offset, around_cut, line}`.
  - `line` is set only when the field is a single-line plain or single-quoted scalar.
- Surfaces `("claude-code",)`, basis official. `data.cap_setting = "skillListingMaxDescChars"`.

`compatibility.py`:
- Absent gives `[]`.
- `not-a-string`, `empty`, and `too-long` over 500 characters.
- Surfaces `("open-spec","upload")`.

- [ ] **Step 1: Write the failing tests.**
  - For `description.py`:
    - 1,024 characters give `[]` and 1,025 give `too-long`;
    - `<tag>` gives `angle-bracket` with `xml_tags == ["<tag>"]`;
    - `a > b` gives `angle-bracket`;
    - no description gives `missing`;
    - `description: 5` gives `not-a-string`;
    - `"  "` gives `empty`;
    - 1,000 emoji give `[]` with `utf16_length == 2000`.
  - For `listing_cap.py`:
    - a description of 1,000 and a `when_to_use` of 600 give `over-cap` with `first_lost_field == "when_to_use"` and `first_lost_offset == 536` (adjusted by the separator's length from Task 0);
    - a combined length of 1,536 gives `[]`;
    - `--cap 100` with 150 characters gives offset 100;
    - a description of 1,600 alone gives `first_lost_field == "description"` with offset 1536.
  - For `compatibility.py`:
    - 500 characters give `[]` and 501 give `too-long`;
    - `""` gives `empty`;
    - `7` gives `not-a-string`.
- [ ] **Step 2:** Run the tests. Expected: they fail.
- [ ] **Step 3:** Implement the scripts and set the executable bit.
- [ ] **Step 4: Wire.** Add the entries to `MECHANICAL-CHECKS.md`, and list the scripts under their reviewers in `SKILL.md`. `frontmatter.description` and `frontmatter.compatibility`: validate passed an XML tag and over-long values, so these checks are the only source; findings go to `frontmatter-description`, and the lengths to `size-limits-and-budgets`. `frontmatter.listing-cap`: no command reports where the cap cuts (`/skill-doctor` gives the listing cost, not the cut point); this check is the only source; `first_lost_field`, `first_lost_offset` and `around_cut` show which trigger words never reach Claude; goes to `size-limits-and-budgets` and `frontmatter-description`. Update each named reviewer's Receives list in `MECHANICAL-CHECKS.md` and the sync file.
- [ ] **Step 5:** Run the tests on 3.12, 3.13 and 3.15, plus ruff, basedpyright, `lint:frontmatter` and `validate --strict`. Expected: pass, 0 findings and `valid`.
- [ ] **Step 6:** Commit: `git commit -m "Add and wire the description, listing-cap and compatibility frontmatter checks"`.

### Task 7: FM-10 (`frontmatter.metadata`) and FM-12 (`frontmatter.field-values`)

**Files:** Create `frontmatter/metadata.py` and `field_values.py`. Tests: `tests/test_frontmatter_fields.py`.

`metadata.py`, under YAML 1.1 resolution, which is what upload uses:
- `not-a-map`: surfaces `("claude-code","open-spec","upload")`.
- `non-string-key` and `non-string-value`: surfaces `("open-spec","upload")`.
- `reused-field-name`: a key in `CLAUDE_CODE_FIELDS`, surfaces `("claude-code",)`, basis official.

`field_values.py`:
- `boolean-form`, for `BOOLEAN_FIELDS`:
  - a plain value outside `BOOLEAN_FORMS` gives the finding with basis official;
  - a quoted value gives the finding with basis inference and the condition "quoted: unverified whether Claude Code reads it as a boolean".
- `context-value`: anything other than `fork`.
- `effort-value`: a value outside `EFFORT_LEVELS`.
- `string-or-list`, for `disallowed-tools`, `paths` and `arguments`: a string scalar or a seq of string scalars, under YAML 1.1.
- It does not check `shell` or the type of `allowed-tools`, which validate already rejects (spec Coverage).
- `model-value`:
  - a value in `MODEL_VALUES` gives nothing;
  - a value matching `^(claude-|anthropic\.|[a-z]{2,4}\.anthropic\.|arn:)` gives nothing, with `data.model_id_unchecked = true`;
  - anything else gives the finding with basis inference.
- `empty-value`: a field present with a null value.
- Surfaces `("claude-code",)`.

- [ ] **Step 1: Write the failing tests.**
  - For `metadata.py`:
    - `metadata: {a: 1}` gives `non-string-value`;
    - `metadata: x` gives `not-a-map`;
    - `metadata:\n  paths: x` gives `reused-field-name`;
    - `version: "1.0"` gives `[]` and `version: 1.0` gives `non-string-value`.
  - For `field_values.py`:
    - `user-invocable: maybe` gives `boolean-form`;
    - `effort: turbo` gives `effort-value`;
    - `context: spoon` gives `context-value`;
    - `allowed-tools: 42` gives `[]`, because that is validate's;
    - `shell: fish` gives `[]`, because that is validate's;
    - `model: gpt-4` gives `model-value`;
    - `model: opus[1m]` gives `[]`;
    - `model: claude-opus-5-5` gives `[]`;
    - `background: "true"` gives `boolean-form` with basis inference;
    - `paths: [a, 1]` gives `string-or-list`;
    - `user-invocable: NO` gives `[]`;
    - `effort:` gives `empty-value`.
- [ ] **Step 2:** Run the tests. Expected: they fail.
- [ ] **Step 3:** Implement the scripts and set the executable bit.
- [ ] **Step 4: Wire.** Add the entries to `MECHANICAL-CHECKS.md`, and list the scripts under their reviewers in `SKILL.md`. `frontmatter.metadata`: validate passed `metadata: {a: 1}`, so this check is the only source; goes to `frontmatter-description`. `frontmatter.field-values`: validate already rejects a non-string `allowed-tools` and an unknown `shell`, so read those in validate's output; this check adds the boolean forms, `context`, `effort`, `model` and the types of `disallowed-tools`, `paths` and `arguments`; goes to `frontmatter-description`. Update each named reviewer's Receives list in `MECHANICAL-CHECKS.md` and the sync file.
- [ ] **Step 5:** Run the tests on 3.12, 3.13 and 3.15, plus ruff, basedpyright, `lint:frontmatter` and `validate --strict`. Expected: pass, 0 findings and `valid`.
- [ ] **Step 6:** Commit: `git commit -m "Add and wire the metadata and field-value frontmatter checks"`.

### Task 8: FM-13 (`frontmatter.field-combinations`) and FM-14 (`frontmatter.allowed-tools`)

**Files:** Create `frontmatter/field_combinations.py` and `allowed_tools.py`. Tests: `tests/test_frontmatter_combinations_tools.py`.

`field_combinations.py`, booleans read through `BOOLEAN_FORMS`, surfaces `("claude-code",)`:
- `uninvocable`: basis inference.
- `paths-ignored`: basis inference.
- `fork-only-field`: `agent` or `background` without `context: fork`, basis official.

`allowed_tools.py`:
- Entries are split on whitespace and commas outside parentheses. Each seq item counts as one entry.
- `list-form`: surfaces `("open-spec","upload")`, condition "for a skill meant to work outside Claude Code", basis official. The spec, verified 2026-11-17, says "A space-separated string of tools that are pre-approved to run".
- `unscoped-bash`: an entry that, with spaces removed, is `Bash`, `Bash(*)` or `Bash(:*)`. Surfaces `("claude-code",)`, with the basis Task 0 decided.
- Unbalanced parentheses give `data.unparsed_entries` and no crash.
- `data.entries` lists the parsed entries.

- [ ] **Step 1: Write the failing tests.**
  - For `field_combinations.py`:
    - `disable-model-invocation: true` with `user-invocable: false` gives `uninvocable`;
    - `paths: "*.py"` with `disable-model-invocation: yes` gives `paths-ignored`;
    - `agent: Explore` without `context` gives `fork-only-field`;
    - the same with `context: fork` gives `[]`;
    - `background: false` with `context: fork` gives `[]`.
  - For `allowed_tools.py`:
    - `[Read, Grep]` gives `list-form`;
    - `Bash` gives `unscoped-bash`;
    - `Read Bash(git diff:*)` gives `[]` with two entries;
    - `"Read, Bash(*)"` gives `unscoped-bash`;
    - `"Bash(git"` gives `[]` with `unparsed_entries == ["Bash(git"]`.
- [ ] **Step 2:** Run the tests. Expected: they fail.
- [ ] **Step 3:** Implement the scripts and set the executable bit.
- [ ] **Step 4: Wire.** Add the entries to `MECHANICAL-CHECKS.md`, and list the scripts under their reviewers in `SKILL.md`. `frontmatter.field-combinations` and `frontmatter.allowed-tools`: no other command covers them, so these checks are the only source. A combination finding means part of the skill silently does nothing. An `unscoped-bash` finding means the skill pre-approves every command. Both go to `frontmatter-description`, and `frontmatter.allowed-tools` also goes to `runtime-contract`, which audits tool pre-approval. Update each named reviewer's Receives list in `MECHANICAL-CHECKS.md` and the sync file.
- [ ] **Step 5:** Run the tests on 3.12, 3.13 and 3.15, plus ruff, basedpyright, `lint:frontmatter` and `validate --strict`. Expected: pass, 0 findings and `valid`.
- [ ] **Step 6:** Commit: `git commit -m "Add and wire the field-combination and allowed-tools frontmatter checks"`.

### Task 9: Commands for FM-1, FM-6 and FM-11 in `MECHANICAL-CHECKS.md`

**Files:**
- Modify: `MECHANICAL-CHECKS.md` (the command entries and the Receives lists of `frontmatter-description` and `runtime-contract`)
- Modify: `.claude/maintainer/skills-engineering/mechanical-check-sources.md` (the rule's sync point)
- Test: `tests/test_frontmatter_commands.py`

What the commands cover, POSIX only, with every path quoted:

- **FM-1, the files validate never reads:**
  - When the audited `SKILL.md` sits at a plugin root, or the skill's folder is a symlink, copy the skill folder with `cp -RL "<skill folder>" "<temporary plugin>/skills/<skill name>"` into the temporary plugin that step 3 already builds.
  - Then run `claude plugin validate --json "<temporary plugin>"`, so validate reads the file.
  - Its frontmatter errors are FM-1's result, with nothing re-checked by a script.
  - Task 0 decides whether a BOM or CRLF also needs `head -c 3 "<SKILL.md>" | od -An -tx1` and `grep -c "$(printf '\r')" "<SKILL.md>"`. They are added only if validate does not already handle them.
- **FM-11, top-level keys with their lines**, which no command reports:

  ```sh
  awk 'NR==1 && !/---[[:space:]]*$/{exit} NR>1 && /^---[[:space:]]*$/{exit} NR>1 && /^[^[:space:]#]/{print NR": "substr($(0),1,80)}' "<SKILL.md>"
  ```

  - The reviewer compares each key with its reference's field table, for unknown keys, and with the six open-spec fields, for upload, by the skill's origin.
- **FM-6, the folder name:** `basename "$(dirname "<SKILL.md>")"`.
  - Read it against the location from step 2: `synced` in any capitalization in a personal, project or managed location, and `anthropic-skills` or a name starting with `anthropic-skills:` outside a plugin.
  - The reserved words in `name` come from `frontmatter.name`.

Each command's entry in `MECHANICAL-CHECKS.md` follows "Mechanical-checks entry shape", with these points:
- FM-1 covers the files validate skips, and validate's output is the result. It goes to `runtime-contract` and `frontmatter-description`.
- FM-11 has no other command coverage. It goes to `frontmatter-description`.
- FM-6 has no other command coverage. It goes to `runtime-contract`, which audits discovery.

- [ ] **Step 1: Write the failing tests.** Each runs the command with `sh -c` on fixtures and asserts its result:
  - a plugin-root `SKILL.md` with no frontmatter, once copied, makes validate report the missing block;
  - a symlinked skill folder is copied as real files, and validate reads it;
  - FM-11 on a BOM + CRLF fixture lists the keys with their file lines;
  - a file without frontmatter prints nothing;
  - a folder `Synced` prints `Synced`.

  One test asserts each command string appears verbatim in `MECHANICAL-CHECKS.md`. Another asserts that no `$` followed by a digit appears in it or in `SKILL.md`. This matters even in a linked file only if it is ever injected; the test keeps both safe.
- [ ] **Step 2:** Run the tests. Expected: they fail.
- [ ] **Step 3: Wire.** Add the command entries and the Receives lists to `MECHANICAL-CHECKS.md`, and the sync file, then run `npm run lint:frontmatter -- <SKILL.md>`.
- [ ] **Step 4:** Run the tests and `claude plugin validate --strict plugins/skills-engineering`. Expected: pass and `valid`. Report that the commands were tested with GNU tools only; macOS (BSD) and Git Bash were not run.
- [ ] **Step 5:** Commit: `git commit -m "Add the block, folder and key commands to the audit's mechanical step"`.

### Task 10: Release verification

- [ ] **Step 1:** Run `npm run test:plugins`, the full suite on `/usr/bin/python3.12` and `/usr/bin/python3.13`, and the suite under `uv run` (3.15 with ruamel). Expected: all pass. Show the raw output.
- [ ] **Step 2: Corpus run.** Run `frontmatter-checks.py run`, then `frontmatter-checks.py clean`, and the commands on every `SKILL.md` in `plugins/*/skills/*/` and in the synced skills under `/root/.claude/`. Expected:
  - exit 0 everywhere;
  - no traceback;
  - under 1 s per file;
  - no `auditing-skills-fm-*` folder left in the temp folder afterwards.

  Show a table of findings per rule. Confirm by hand every finding on `auditing-skills` itself.
- [ ] **Step 3: Differential check.** A scratchpad script compares the reader with ruamel.yaml on the corpus and lists each divergence with the YAML 1.1 versus 1.2 rule that explains it. A divergence no rule explains is a bug: go back to the owning task.
- [ ] **Step 4: Claude Code cross-check.** Run `claude plugin validate --json` and the scripts on every spec case marked tested in Coverage. Expected:
  - every case validate reports appears in no script's findings;
  - every case validate passes appears in exactly one check.

  Show both outputs side by side.
- [ ] **Step 4b: Skill check.** Read `SKILL.md` and then `MECHANICAL-CHECKS.md` as the main session would. Confirm:
  - each of the 14 checks has an entry with the five parts of "Mechanical-checks entry shape";
  - every "only source" line is present;
  - every Receives list names what the file gives it;
  - `SKILL.md` lists every script, reference and asset under its phase or reviewer, one level deep;
  - `SKILL.md`'s first 5,000 tokens hold the whole orchestration. Measure with `claude plugin details`, not by hand.
- [ ] **Step 5:** Run ruff check, ruff format check and `basedpyright --outputjson` over `plugins/skills-engineering`, plus `claude plugin validate --strict`. Expected: 0 findings and `valid`.
- [ ] **Step 5a: No-bytecode gate.** Copy the skill folder with `cp -R` to a fresh temp folder, run `frontmatter-checks.py run`, `show` and `clean` from it with `python3` and with `python3 -I`, from a working directory outside it, then run `find <copy> -name __pycache__ -o -name '*.pyc'`. Expected: no output. Show it raw.
- [ ] **Step 5b: Suppressions gate.** Run `grep -rnE '(noqa|type:[[:space:]]*ignore|pyright:[[:space:]]*ignore)' plugins/skills-engineering --include='*.py'` and `git diff main -- ruff.toml pyrightconfig.json pyproject.toml`. Expected: no grep output, and no diff that adds an ignore, exclude or rule change. Show both raw outputs. Any hit fails the release.
- [ ] **Step 6: Independent review.** One fresh reviewer on the most capable model reviews the whole branch against this plan and the spec. Fix every confirmed finding and rerun Steps 1 to 5.
- [ ] **Step 7:** Commit fixes and report to Nery with the raw outputs. No push.

## Out of scope (next plan)

- The CHANGELOG entry.
- The other data domains.

## Appendix: Task 0 results

Run on 2026-11-17 with Claude Code 2.1.326 and ruamel.yaml 0.19.1. Loader results come from `claude -p --plugin-dir <lab>` sessions asked to copy each lab skill's listed description character for character, so they rest on the model's copy of its own listing.

| Case | `claude plugin validate --strict --json` | What Claude Code loads |
| :-- | :-- | :-- |
| UTF-8 BOM before `---` | nothing reported | fields read normally |
| CRLF line endings | nothing reported | fields read normally |
| `--- ` with a trailing space, opening marker | nothing reported | fields read normally |
| `--- ` with a trailing space, closing marker | nothing reported | fields read normally |
| U+2028 inside `description` | nothing reported | kept as U+2028 |
| duplicate `description` key | nothing reported | the last value wins |
| Latin-1 byte (`caf\xe9`) | nothing reported | decoded with U+FFFD in place of the byte, silently |
| UTF-16 with BOM | "No frontmatter block found" (warning) | no fields |
| `description: COLON-A: COLON-B marker.` | nothing reported | the whole text, `COLON-A: COLON-B marker.` |

Consequences for later tasks:
- FM-1 needs no BOM or CRLF command (Task 9): Claude Code reads both. The reader still normalizes them (Task 2) and marker equality ignores trailing spaces and tabs.
- A non-UTF-8 file is never reported by validate, and Claude Code silently replaces the bad bytes: `frontmatter.yaml`'s `not-utf8` finding is the only source (Review Focus 1).
- Duplicate keys: report that Claude Code keeps the last value, in the finding's `expected`.
- `a: b: c` style values: Claude Code keeps the whole text while ruamel (YAML 1.2) rejects them, confirming FM-2's surfaces: a finding for `open-spec` and `upload`, not `claude-code`.

Step 2 results:
- ruamel.yaml 0.19.1 (`typ="safe"`, `pure=True`) rejects `a: foo:`, `a: x: y` and `a: "q": r` with `ScannerError: mapping values are not allowed here`.
- `description` + `when_to_use`: the listing shows `WTU-DESC part. - WTU-WHEN part.`, so the separator is ` - ` (space, hyphen, space), 3 characters, counted toward the 1,536 cap (FM-8). The docs say only "Appended to `description`".
- `Bash` and `Bash(*)`: permissions docs: "`Bash(*)` is equivalent to `Bash` and matches all Bash commands." FM-14 flags both.
- Six-field upload rule for plugin skills: the skills docs ("Using skill frontmatter outside Claude Code") list "Claude Code skills at any level, including plugin skills" as using every field, and "claude.ai skill uploads, the Skills API, and packaging with `package_skill.py`" as limited to the six. Whether a plugin added in claude.ai Customize > Plugins passes through that upload check stays unverified; FM-11 keeps "a personal skill gets a warning" and reports plugin skills under `upload` only as a condition.
- `allowed-tools` quoting (lab plugin, `--permission-mode default`, only `Skill` pre-allowed):
  - rule `Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/x.py *)`: the unquoted command ran (`RAN ['unquoted']`); the quoted command was denied ("This command requires approval");
  - rule `Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/x.py" *)` in a plugin path with a space: the quoted command ran (`RAN ['quoted']`); the unquoted one was denied.
  - So the rule and the command must be written identically, quotes included. The plan quotes both.

Step 3: no result contradicts the spec.
