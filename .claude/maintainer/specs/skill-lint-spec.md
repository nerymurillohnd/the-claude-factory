# Skill lint: deterministic maintainer linter for every skill in the repository

## Context

No official tool mechanically checks what breaks a skill in a third party's hands:

- `claude plugin validate --strict` (Claude Code 2.1.322, checked 2026-11-12) only checks that skill frontmatter parses. It returned `success: true` for github-operations, prompt-writer and instruction-engineering. Those same skills contain a name with a reserved word, a script without a shebang or an executable bit, and frontmatter fields that claude.ai uploads reject.
- `quick_validate.py` (skill-creator) checks only the six spec fields, the lengths and `compatibility`. It lets reserved words through.
- `/doctor prompt-audit` (v2.1.283+) is model-based, not deterministic.

Each check has one owner:

| Check | Owner |
| :-- | :-- |
| Structure | `claude plugin validate` |
| Behavior | `claude plugin eval` |
| Semantics | Agents or `/doctor prompt-audit` |
| Mechanical checks nothing official covers | **This maintainer linter** |

## Decisions taken with the owner (2026-11-12)

- **The code is our own maintainer code, independent of the `skill-diagnostics` plugin.**
  - The repository can't depend on a plugin it distributes to third parties.
  - CLAUDE.md keeps the maintainer and plugin scopes separate.
  - The plugin's rules may inspire ours. Its scripts serve only as a one-time test oracle.
- **Severity:**
  - ✗: the skill breaks, is rejected, or violates an official limit or recommendation we enforce. Exit 1.
  - ⚠: a lead that needs judgment. Exit 0.
  - `--strict` turns ⚠ into failures.
- **Reserved words** (`anthropic`, `claude`) in a name give ⚠. A rename goes in a plugin PR with a major version bump.
- **Scope:** the linter reads only files inside each skill folder, plus the git index mode of those files.
- **Every finding in every skill is reported**, project skills included. The linter filters nothing out by surface. The owner decides what gets fixed and when.
- **When and by whom the linter runs is not decided.** This work builds the script and its `npm run lint:skills` entry point only. It is not wired into `lint`, `check`, Git hooks or CI.
- **On every run,** Claude reports each defect to the owner and asks whether to fix it now, record it as technical debt, or decide something else. Claude fixes nothing on its own initiative.
- **The output is readable by the owner:**
  - A table per skill with ✓/⚠/✗ for each family.
  - A details section.
  - `--json` for Claude.

## Sources (read 2026-11-12)

- **code.claude.com/docs/en/skills:**
  - The frontmatter reference.
  - "Using skill frontmatter outside Claude Code": the six fields; anything else is a hard upload error.
  - Description + `when_to_use` is truncated at 1,536 characters (`skillListingMaxDescChars`).
  - "Available string substitutions": `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` exist only in plugin skills.
  - "Inject dynamic context" and "Permission checks on injected commands": an injected command never prompts. Outside auto mode, anything but allow aborts the invocation. `allowed-tools` pre-approves the command.
  - How synced and Cowork skills handle the body.
  - "Characters a skill name can't hold".
- **code.claude.com/docs/en/hooks:**
  - "Hooks in skills and agents": a skill's hooks stay registered for the rest of the session; `once`; project-skill hooks run even in `-p` without trust.
  - "Limits on skill hooks": 1,024 hooks and 16,384 matcher characters per source (v2.1.304+).
- **platform.claude.com, agent-skills overview and best practices:**
  - Name: at most 64 characters, `a-z0-9-`, no XML, no `anthropic` or `claude`.
  - Description: 1 to 1,024 characters, no XML.
  - Body under 500 lines.
  - References one level deep.
  - A table of contents on reference files over 100 lines.
  - No time-sensitive text.
  - Forward slashes.
  - Required packages listed; local installs only.
- **agentskills.io/specification:**
  - Name: no leading, trailing or double hyphen; matches the folder.
  - `compatibility`: 1 to 500 characters.
  - `metadata` maps strings to strings.
  - `allowed-tools` is a space-separated string (Experimental).
- **claude.com/docs/skills/how-to:**
  - In claude.ai chat, the skill folder is copied into the code-execution sandbox.
  - Script paths should stay readable relative to SKILL.md.
  - The folder name must match `name`.
- **claude.com/docs/plugins/platform-support:**
  - Plugin skills load in chat, Cowork and Claude Code.
  - What chat does with Claude Code-only fields inside a plugin is undocumented.

## Rule catalog

Each finding carries a rule id, family, severity, `file:line`, message and source URL.

### Content (CO)

| Rule | Sev | Check |
| :-- | :-- | :-- |
| CO-01 | ✗ | Frontmatter opens on line 1, closes, and parses as YAML with no duplicate keys. ruamel.yaml parses YAML 1.2, while Claude Code's parser is JavaScript: a failure that `claude plugin validate` doesn't reproduce is labeled "ruamel-only" in the message |
| CO-02 | ✗ | `name` is present and 1-64 characters of `a-z0-9-`. No leading, trailing or double hyphen. No `<>`, control or zero-width characters. Equal to the folder name |
| CO-03 | ✗ | `description` is a non-empty string of at most 1,024 characters, with no XML tags |
| CO-04 | ✗ | `description` + `when_to_use` are at most 1,536 characters. Claude Code truncates beyond that and doesn't reject, so the message says "truncated" |
| CO-05 | ✗ | `compatibility` is at most 500 characters. `metadata` is a map of strings |
| CO-06 | ✗ | The SKILL.md body (the lines after the closing `---`) has fewer than 500 lines; 500 fails, matching "under 500 lines" |
| CO-07 | ✗ | Every relative link and `#anchor` resolves (slugs as github-slugger 2.0.0 builds them; links in code and in HTML comments are ignored; a target with a URI scheme of two or more characters, or starting with `//`, is external and not checked) |
| CO-08 | ✗ | No link or path leaves the skill folder |
| CO-09 | ✗ | Depth: a `.md` file that is reached only through another bundled file, never linked from SKILL.md (depth > 1) |
| CO-10 | ✗ | A reference file over 100 lines has a table of contents: within the first 20 non-blank lines after its first heading, at least 2 list items that link to `#anchors` in the same file |
| CO-11 | ⚠ | Time-sensitive text outside code, case-insensitive: `\b(before\|after\|until\|since\|as of)\s+(January\|…\|December\|Q[1-4])?\s*(19\|20)\d{2}\b`, `\b(currently\|now\|today\|recently)\b.{0,40}\b(19\|20)\d{2}\b`, `\bin (19\|20)\d{2}\b` |
| CO-12 | ⚠ | Orphan file: no file of the skill references it at all. Exempt: `evals/`, `__pycache__`, `.DS_Store`, and `__init__.py`; `.git/`, `node_modules/` and `.venv/` are never listed (see Discovery) |

Each file produces at most one of CO-09 (reached, but too deep) and CO-12 (not reached at all).

### Portability (PO)

These rules apply to every skill, project skills included. Each finding names the surface it affects, read from the skill's own files only.

| Rule | Sev | Check |
| :-- | :-- | :-- |
| PO-01 | ✗ | `${CLAUDE_PLUGIN_ROOT}` or `${CLAUDE_PLUGIN_DATA}` in a skill outside a plugin |
| PO-02 | ✗ | A backslash in a link target or a script path |
| PO-03 | ⚠ | Frontmatter fields outside the six spec fields (they work only in Claude Code) |
| PO-04 | ⚠ | `` !`cmd` `` or ```` ```! ```` blocks (they don't run in claude.ai chat or Cowork) |
| PO-05 | — | Withdrawn (owner, 2026-11-12): relative, `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}` paths are all valid, and no rule judges the form. The id is not reused |
| PO-06 | ⚠ | `allowed-tools` written as a YAML list (the spec defines a space-separated string) |
| PO-07 | ⚠ | A name containing `anthropic` or `claude` |

### Scripts (SC)

An **entry point** is a file the skill's Markdown runs (a command line that names its path), or any file that already starts with a shebang. Not entry points: `__init__.py`, modules other scripts of the skill import, shell libraries other scripts `source` or `.`, and data or template files (JSON, YAML, Markdown, text). SC-01 and SC-02 apply only to entry points; SC-04 to SC-06 and CA-04 apply to every code file of the skill.

| Rule | Sev | Check |
| :-- | :-- | :-- |
| SC-01 | ✗ | An entry point's first line is `#!/usr/bin/env <interpreter>` |
| SC-02 | ✗ | An entry point's git index mode is `100755`. A file not in the index is checked by its filesystem exec bit instead, and the message says "untracked: filesystem mode"; when git itself failed (anything but "not a git repository"), the message names git's error instead |
| SC-03 | ✗ | Every script the skill's Markdown runs exists inside the skill folder and is called with its interpreter. The path may take any of three forms: relative to SKILL.md, through `${CLAUDE_SKILL_DIR}`, or through `${CLAUDE_PLUGIN_ROOT}` (plugin skills only). The rule resolves each form to a file and judges only existence and interpreter, never which form the path uses |
| SC-04 | ✗ | A Python script that imports a module outside the stdlib declares it in a PEP 723 block |
| SC-05 | ⚠ | An external command in a script (`jq`, `gh`, …) that neither SKILL.md nor `compatibility` mentions |
| SC-06 | ⚠ | A global package install (`pip install` outside a venv, `npm install -g`) |

### Capabilities (CA)

The manifest always lists these.

| Rule | Sev | Check |
| :-- | :-- | :-- |
| CA-00 | — | Inventory: each `!` command and block (file:line); each frontmatter hook (event, matcher, type, command or prompt, `once`); each `allowed-tools` entry |
| CA-01 | ✗ | An argument placeholder inside a `!` command (shell injection). Only `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N`, and the `$name` forms of names the skill declares in its own `arguments` field. Other `$` variables (`$HOME`, `$PATH`, shell loop variables) are not findings |
| CA-02 | ⚠ | An unscoped `Bash` or `Bash(*)` in `allowed-tools` |
| CA-03 | ⚠ | A `!` command that the skill's own `allowed-tools` approves (a self-approved injection) |
| CA-04 | ⚠ | Network or credential signals in scripts (not in Markdown): curl, wget, urllib, requests, sockets, `~/.ssh`, `.env`, `.netrc` |

### Not checked here (owned elsewhere)

- **Python syntax at the 3.12 floor:** ruff covers it. `ruff.toml` sets `per-file-target-version` to `py312` for `plugins/**/*.py` and `.claude/skills/**/*.py`. Confirmed: ruff reports syntax newer than py312. `ruff check --no-cache --isolated --target-version py312` on `def f[T = int](): ...` exits 1 with `invalid-syntax: Cannot set default type for a type parameter on Python 3.12 (syntax was added in Python 3.13)`. No rule is needed here.
- **Basic frontmatter parsing:** `claude plugin validate`.
- **Semantics:** agents and `/doctor prompt-audit`.
- **Cross-checks against files outside the skill folder** (the README surface badge, Prerequisites): excluded by the skill-folder-only rule. If the owner wants them, they become a separate script.

## Architecture

```text
scripts/validators/
├── __init__.py
├── skill-lint.py            # thin shim: from skill_lint.cli import main
└── skill_lint/
    ├── __init__.py
    ├── cli.py               # argparse, run, exit code
    ├── model.py             # Skill, Finding, Severity, Family
    ├── discover.py          # the two skill globs; plugin or project from the path; git ls-files -s modes
    ├── frontmatter.py       # ruamel.yaml strict load (duplicate keys), line numbers
    ├── markdown.py          # line scan: fences, indented code, HTML comments, headings
    ├── markdown_model.py    # the MarkdownDoc parts, slugs, links, inline code, ! commands
    ├── refs.py              # reference graph: links, path mentions, imports, source lines
    ├── rules_content.py
    ├── rules_portability.py
    ├── rules_scripts.py
    ├── rules_capabilities.py
    └── report.py            # table, details, --manifest, --json
scripts/testers/
├── __init__.py
└── skill_lint/              # importable name, so unittest discovery reaches it
    ├── __init__.py
    ├── helpers.py           # builds each fixture skill in a temporary directory
    └── test_*.py
```

### Runtime and conventions

- **Python and packages:** Python 3.15. Only the stdlib plus `ruamel.yaml==0.19.1`, already in the `dev` dependency group of `pyproject.toml` and in `uv.lock`. No new package is added.
- **Conventions:** the same as `scripts/check-github-files.py`.
- **How it runs:** `package.json` runs it as `uv run python …` (ADR_2026-11-12_maintainer-scripts-run-through-uv-run). The shebang of maintainer scripts is only informative.
- **SC-01 and SC-02 scope:** they apply to scripts inside skills, not to maintainer scripts.
- **Module size:** each module stays at or under about 250 lines.

### Discovery

- **Globs:** only `plugins/*/skills/*/SKILL.md` and `.claude/skills/*/SKILL.md`. Today they match 26 skills: 25 plugin skills and 1 project skill.
- **Fixtures:** tests build each fixture skill in a temporary directory, so no broken skill is committed and none can be discovered.
- **Command names:** each skill's command name is `plugin:skill` or `project:skill`. That name tells apart the two `ts-lifecycle` skills (typescript6 and typescript7).
- **Files listed:** every file and symlink in the skill folder, except inside `.git/`, `node_modules/` and `.venv/` (owner decision, 2026-11-12: vendored trees would flood CO-12). A file over 1 MiB is listed but not read.
- **Paths:** a relative SKILL.md path is made absolute before its kind is read, so `.claude/skills/x` is a project skill from any working directory.

### Testability

- **SC-02:** the rule reads index modes through a function that tests can replace. Its integration test builds a temporary git repository in a temporary directory.
- **Imports in tests:** the tests import `skill_lint` from `scripts/validators`, so they need two things:
  - The unittest command adds that directory: `-t scripts`, plus a `sys.path` setup in `scripts/testers/skill_lint/__init__.py`, or the equivalent.
  - basedpyright resolves it: `"extraPaths": ["validators"]` in `scripts/pyrightconfig.json`.
- **Settled in step 1 of the plan (observed):**
  - `npm run test:scripts` runs `uv run python -m unittest discover -s scripts/testers -t scripts -p 'test_*.py'`. With `-t scripts`, `from validators.skill_lint import ...` resolves in the tests with no `sys.path` change and no `sys.path` setup in `scripts/testers/skill_lint/__init__.py`.
  - `basedpyright -p scripts` resolves `validators.skill_lint` in the tests with no `extraPaths` entry. The entry script `scripts/validators/skill-lint.py` (`from skill_lint.cli import main`) needed `"extraPaths": ["validators"]` in `scripts/pyrightconfig.json`: without it basedpyright reported `reportImplicitRelativeImport`. `"."` was not needed.
  - ruff reported N999 on `skill-lint.py` and did not report INP001 on it or on the new packages (each has an `__init__.py`). `ruff.toml` now has `[lint.per-file-ignores]` with `"scripts/validators/skill-lint.py" = ["N999"]`.
  - ruff D104 requires a docstring in every `__init__.py`, so the package `__init__.py` files hold a one-line docstring and are not empty.

### Checks

- `ruff check` (`ALL`), and `basedpyright -p scripts`, which is already part of `npm run typecheck:python`.

### CLI

- **Usage:** `skill-lint.py [paths…] [--only families] [--strict] [--manifest] [--json]`
- **Exit codes:**
  - 0: no ✗.
  - 1: at least one ✗ (or ⚠ with `--strict`).
  - 2: usage error or unreadable input.
- **Colors:** only on a TTY, and never when `NO_COLOR` is set.

### Output

1. A summary line.
2. A table: `SKILL` (the command name), then ✓/⚠/✗ for each family.
3. DETAILS for each skill with findings: rule id, file:line, message and path.

### npm scripts

- `"lint:skills": "uv run python scripts/validators/skill-lint.py"`. It is not chained into any other script.
- `"test:scripts"`: `uv run python -m unittest discover` over `scripts/testers`, with the exact flags settled in step 1 (see Testability).

## Files to create or change

- **New:**
  - `scripts/validators/skill-lint.py`
  - `scripts/validators/skill_lint/*.py`
  - `scripts/validators/__init__.py` and `scripts/testers/__init__.py`
  - `scripts/testers/skill_lint/` (`__init__.py`, `helpers.py`, `test_*.py`)
- **Changed:**
  - `package.json`: the `lint:skills` and `test:scripts` scripts.
  - `scripts/pyrightconfig.json`: `extraPaths`, if step 1 confirms it is needed.
  - `ruff.toml`: a per-file ignore for the shim, only if step 1 shows N999 or INP001 fire.
- **Records:**
  - `.claude/maintainer/specs/skill-lint-spec.md`: this design, committed.
  - `.claude/maintainer/plans/2026-11-12-skill-lint.md`: the implementation plan.
  - One ADR through `project-maintainer:write-records`. It records the own linter, the severity model, the skill-folder-only scope and one owner per check.
- **Removed:** the `.gitkeep` files in `scripts/validators/` and `scripts/testers/`, once real files exist.
- **Unchanged:** no file under `plugins/` changes.

## Verification

1. **TDD for each rule with `unittest`:**
   - A failing fixture test first, then the rule, then a pass.
   - One valid fixture skill passes every rule.
2. **Checks on the new code, with the raw output shown:** `npm run test:scripts`, `npm run lint:python` and `npm run typecheck:python` pass.
3. **A read-only run of `npm run lint:skills` over the 26 skills:**
   - Show the owner the full table and details.
   - Confirm no file changed: `git status` shows only the new files.
   - Ask the owner one question per rule id, listing every affected skill: fix it now, record it as debt, or decide otherwise. The owner can split a rule's answer by skill.
4. **Oracle:**
   - Compare CO-01 verdicts with `claude plugin validate` on the 26 skills; label each ruamel-only failure.
   - For the rules that overlap `skill-diagnostics` (M-2/4-8/11-14, S-2/3/4/6/8/10/11/12, Z-1, R-4/5/10), compare verdicts on the 26 skills.
   - Explain each difference.
   - Before comparing, confirm the rule ids against the installed plugin.
5. **Exit codes:** 0 on a clean fixture, 1 on a broken one, 2 on a missing path.

## Execution sequence

1. Save this spec to `.claude/maintainer/specs/skill-lint-spec.md` and commit it.
2. Invoke `superpowers:writing-plans` for the step-by-step TDD implementation plan. Its first step settles the open items in Testability. The owner picks the execution method.
3. Implement and commit by topic. Push nothing without the owner's authorization.
