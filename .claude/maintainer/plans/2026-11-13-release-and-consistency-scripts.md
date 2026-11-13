# Release and consistency scripts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the mechanical steps the project skills run by hand with five maintainer scripts. Rewire the skills, `release.yml`, `WORKFLOW.md` and the CLAUDE draft to call those scripts. Add the Claude Code CLI commands the skills don't use yet.

**Architecture:**
- **Scripts:** Each script has a thin hyphenated entry point (`scripts/<folder>/<name>.py`) that only parses arguments. The logic lives in an importable underscore package, the same pattern as `skill-lint.py` → `skill_lint/`.
- **Scope of each script:** it reads git and the repository files, and covers only what no `claude plugin` command does (blueprint rule 2 in `.claude/architecture/refactor.md`). The one exception is `check-install.sh`, which only orchestrates and isolates CLI commands.
- **Callers:** the skills, `release.yml` and `WORKFLOW.md` call the scripts only through their npm scripts.

**Tech Stack:**
- Python 3.15 through `uv run`, stdlib only.
- Bash for `check-install.sh`.
- unittest, ruff and basedpyright (`-p scripts`), plus ShellCheck and shfmt for the shell script.
- Claude Code 2.1.323, checked with `claude --version` on 2026-11-13.

**Spec:** this plan's Decisions section, plus these sources:
- the analysis given to the owner on 2026-11-13 (CLI gaps §1, manual steps §2, the 5 scripts §3)
- `.claude/architecture/refactor.md` (blueprint rules, stages 12–15 and 19)
- the audits `maintainer-scripts-inventory-2026-11-09.md` and `scripts-vs-cli-2026-11-09.md`

## Decisions

- **Owner (2026-11-13):** consolidate into the 5 scripts proposed, rather than the ~15 that `refactor.md` lists.
- **Owner (2026-11-13):** assign each script to the skills that run it, update the CLAUDE draft (`.claude/architecture/CLAUDE.draft.md`), and add the CLI commands still missing.
- **Reading taken, not yet confirmed:**
  - Priority order is 1 → 2 → 3.
  - Checks that fail today on the 5 mods are built, but stay out of `npm run validate` and `check` until the mods pass. See Q1.

### Open questions for the owner (answer before Task 1)

**Q1. Merge preconditions.**
- `release.yml` triggers on `workflow_run` of `Validate`, and `validate.yml` does not exist. A rebuilt `validate.yml` would run `npm run validate`, which fails today on 5 mods:
  - TS2741 in `turn-meter` and `tool-ledger`
  - TS2769 in `model-trace`
  - TS5097 in `file-tree-pane` and `project-maintainer`
- So `release-notes.py` alone does **not** unblock the merge. The mod fixes and `validate.yml` sit on the merge's critical path.
- **Recommendation:** two separate plans, each run before PR #104 merges: (a) fix the 5 mods, which is plugin-scope work with version bumps; (b) rebuild `validate.yml`. This plan does not cover them.

**Q2. `release-notes.py --tag`.**
- `release.yml` installs no `claude`, so it cannot call `claude plugin tag --dry-run`.
- **Recommendation:** keep `--tag` and derive the tag from `plugin.json` as `<name>--v<version>`. Task 1 adds a test that checks the result equals `tag --dry-run` locally.

**Q3. Eval cost ceiling.**
- The smoke eval in `plugin-versioning` step 7 will run with `--no-publish --max-cost-usd <N>`.
- `<N>` is a value only the owner can give. Task 7 stops until the owner gives it.

## Global Constraints

- Every script has its npm script before its first run. Maintainer Python runs as `uv run python scripts/<path>.py`, never as bare `python3`.
- Only the stdlib, so no `uv add`.
- Tests:
  - Each test is written before its code, in `scripts/testers/<folder>/test_*.py`, and run through `npm run test:scripts`.
  - Tests are offline: throwaway git repos in `tempfile.TemporaryDirectory()` (a bare repo as `origin`), and a stub `claude` on `PATH` for the shell script.
  - No network, and no real `claude`.
- Read-only by default. Only `release-changelog.py` writes, and only the one `CHANGELOG.md` it is given.
- Dates are in UTC, `YYYY-MM-DD`, the day of publication (CLAUDE.md, Dates).
- Tag format is `<plugin>--v<version>`. Marketplace name is `the-claude-factory`. Repository is `nerymurillohnd/the-claude-factory`.
- Exit codes: 0 means OK, 1 means a finding or a failed check, 2 means a usage error. Usage errors go to stderr.
- Each module is about 250 lines at most, with lines of 100 columns at most, per `ruff.toml`.
- No file under `plugins/` changes.
- Commit by topic. Push nothing without the owner's authorization.
- Before editing `WORKFLOW.md` (imported by `CLAUDE.md`) or `CLAUDE.draft.md`, load the `instruction-engineering:claude-md-and-rules` skill.

## Review Focus

1. **A plugin new on the branch**, absent from `origin/main`: the status shows `new -> 0.1.0`; the notes and changelog don't crash. Test in Tasks 2 and 5.
2. **A version on `main` whose `## [X.Y.Z]` section is missing:** `release-notes.py` exits 1 and names the plugin. It never publishes an empty body. Test in Task 1.
3. **A tag listed as `<tag>^{}`** in `git ls-remote` (annotated tags): it is not counted as a second tag. Test in Task 2.
4. **`check-install.sh` interrupted or failing:** the temporary folder is removed (`trap`), and the exit code is the failure's, not 0. Test in Task 3.
5. **A `CHANGELOG.md` with an empty `## [Unreleased]`:** `release-changelog.py` exits 1 and changes nothing, as `changelog.md` step 4 says to stop. Test in Task 5.

---

## File structure

| Path | Responsibility |
| :-- | :-- |
| `scripts/release/__init__.py`, `scripts/release/release_tools/__init__.py` | Importable package |
| `scripts/release/release_tools/repo.py` | Shared readers: plugin list, `plugin.json` at a ref (`git show`), remote tags (`git ls-remote`), CHANGELOG sections |
| `scripts/release/release_tools/notes.py` + `scripts/release/release-notes.py` | Release body and tag |
| `scripts/release/release_tools/status.py` + `scripts/release/release-status.py` | Changed, untagged, next version, semver, dependents |
| `scripts/release/release_tools/changelog.py` + `scripts/release/release-changelog.py` | Dates `[Unreleased]` and rewrites the link references |
| `scripts/release/check-install.sh` | Isolated install and checks of what users receive |
| `scripts/validators/plugin_consistency/` + `scripts/validators/plugin-consistency.py` | Cross-file consistency (DEBT-001 check) |
| `scripts/testers/release/`, `scripts/testers/plugin_consistency/` | Tests, with `__init__.py` and a `helpers.py` that builds throwaway repos |

---

### Task 1: `release-notes.py` and `release.yml` (P1)

**Files:**
- Create: `release_tools/repo.py`, `release_tools/notes.py`, `scripts/release/release-notes.py`, `scripts/testers/release/{__init__,helpers,test_notes}.py`
- Modify: `package.json` (add `"release:notes": "uv run python scripts/release/release-notes.py"`), `.github/workflows/release.yml`

**Interfaces:**
- Produces, in `repo.py`:
  - `plugin_names(root: Path) -> list[str]` (from `marketplace.json`, in order)
  - `manifest(root: Path, plugin: str, ref: str | None = None) -> dict[str, object] | None` (None when absent at `ref`)
  - `remote_tags(root: Path, remote: str = "origin") -> set[str]` (drops `^{}`)
  - `changelog_section(text: str, version: str) -> str | None`
- Produces, in `notes.py`: `tag_name(root, plugin) -> str` and `release_body(root, plugin) -> str`
- CLI: `release-notes.py <plugin> [--tag]`
  - stdout is the tag, or the body
  - exit 1 when the version's section is missing
  - exit 2 for an unknown plugin

- [ ] **Step 1: Write the failing tests** in `test_notes.py`:
  - `test_tag_name`: a repo with `demo` at `1.2.0` gives `"demo--v1.2.0"`.
  - `test_body_is_section_then_update_command`: the body equals the section text, a blank line, then ``claude plugin update demo@the-claude-factory`` (the rule in `plugin-releases` line 26).
  - `test_missing_section_exits_1`: Review Focus 2.
  - `test_unknown_plugin_exits_2`
- [ ] **Step 2:** Run `npm run test:scripts`. Expected: FAIL (`ModuleNotFoundError: release`).
- [ ] **Step 3:** Implement the interfaces above. A section is the text after `## [X.Y.Z] - YYYY-MM-DD` up to the next `## ` heading or the link references.
- [ ] **Step 4:** Run `npm run test:scripts`. Expected: OK. Then check that the real tag matches the CLI on a committed tree:

  ```bash
  npm run release:notes -- block-no-verify --tag
  claude plugin tag plugins/block-no-verify --dry-run
  ```

  Expected: both print the same `block-no-verify--v<version>`.
- [ ] **Step 5: Edit `release.yml`.**
  - Add `astral-sh/setup-uv` pinned to a full commit SHA, with a version comment. Take the SHA from the action's GitHub releases page on the day you implement, never from memory.
  - Replace both `scripts/release/release-notes.py` calls with `npm run --silent release:notes -- "${target}" [--tag]`.
  - Before relying on `npm run` in CI: `devEngines` requires npm `^12.2.1` with `onFail: error`. Confirm in the `setup-node` run log which npm the Node from `.nvmrc` brings. If it is not 12.2.1 or later, call `uv run python scripts/release/release-notes.py` directly instead, and record why in the commit.
- [ ] **Step 6:** Run `npm run lint:workflows && npm run lint:python && npm run typecheck:python`. Expected: exit 0.
- [ ] **Step 7: Commit:** `feat(release): add release-notes script and run it through uv in release.yml`.

### Task 2: `release-status.py` (P1)

**Files:**
- Create: `release_tools/status.py`, `scripts/release/release-status.py`, `scripts/testers/release/test_status.py`
- Modify: `package.json` (add `"release:status": "uv run python scripts/release/release-status.py"`)

**Interfaces:**
- Consumes from Task 1: `plugin_names`, `manifest`, `remote_tags`.
- Produces: `status(root, base="origin/main", remote="origin") -> list[Row]`. `Row` is a frozen dataclass with `plugin`, `kind` and `detail`. `kind` is one of `changed`, `untagged`, `bad-semver` or `dependent`.
- Produces: `next_version(current: str, level: Literal["major","minor","patch"]) -> str`.
- CLI: `release-status.py [--base REF] [--next PLUGIN --level LEVEL] [--json]`.
  - Text output: one line per row, in the same shape as the loops it replaces, e.g. `changed: demo 0.3.2 -> 0.4.0`, `untagged: demo--v0.3.2`, `bad-semver: demo 1.0`, `dependent: other needs demo ^0.3`.
  - `--next` prints only the next version.
  - Exit 1 only on `bad-semver`.

- [ ] **Step 1: Write the failing tests:**
  - `test_changed_and_new`: Review Focus 1, prints `changed: demo new -> 0.1.0`.
  - `test_untagged_ignores_peeled_refs`: Review Focus 3.
  - `test_next_version_resets_lower_fields`: `next_version("0.3.2","minor") == "0.4.0"`, `("0.3.2","major") == "1.0.0"`, `("0.3.2","patch") == "0.3.3"`.
  - `test_bad_semver_exits_1`: with `"1.0"`.
  - `test_dependents_listed_with_declared_range`: from both `plugin.json` and the marketplace entry.
- [ ] **Step 2:** Run `npm run test:scripts`. Expected: FAIL.
- [ ] **Step 3:** Implement. The semver check is `^[0-9]+\.[0-9]+\.[0-9]+$`, the same as `plugin-versioning` step 7. Dependents are **listed** with the range as declared, without judging whether it is satisfied. Judging it would need a range parser outside the stdlib. As of 2026-11-13, no plugin declares `dependencies` (the two `jq` commands print nothing), and the skill keeps the judgment.
- [ ] **Step 4:** Run `npm run test:scripts`, then `git fetch origin main && npm run release:status`. Expected: OK, and the same lines as the two loops in `plugin-releases` step 2 on the same tree.
- [ ] **Step 5: Commit:** `feat(release): add release-status script`.

### Task 3: `check-install.sh` (P1)

**Files:**
- Create: `scripts/release/check-install.sh` (mode 100755, `#!/usr/bin/env bash`, `set -euo pipefail`, per `.claude/rules/hook-scripts.md` conventions), `scripts/testers/release/test_check_install.py`, `scripts/testers/release/fixtures/claude` (the stub)
- Modify: `package.json` (add `"check:install": "bash scripts/release/check-install.sh"`)

**Interfaces:**
- CLI: `check-install.sh --from local|<ref> <plugin>...`
  - `local` adds `./`.
  - `<ref>` adds `nerymurillohnd/the-claude-factory#<ref>`.
  - Plugins install in the order given. This covers all three callers:
    - versioning: `--from local <p>`
    - releases: `--from <branch> <p>`, then `--from main <p>`
    - catalog changes: `--from main <old> <new-or-target>`
- For each plugin, in one `T="$(mktemp -d)"` with `CLAUDE_CONFIG_DIR="${T}/config"` and `CLAUDE_CODE_PLUGIN_CACHE_DIR="${T}/cache"`:
  - `install`
  - `list --json`, printed, with `installPath` and `version` taken from it
  - `details <plugin>`
  - `validate --strict "<installPath>"`
  - `test "<installPath>"` when `<installPath>/tests` holds a `*.test.ts` or `*.test.tsx` file. That is the mod detection, matching `claude plugin test --help`: "runs a mod's tests".
- `trap 'rm -rf "${T}"' EXIT`.
- Exit 1 on the first failed command, or when `list --json` shows `errors` for the plugin. Exit 2 on usage.

- [ ] **Step 1: Write the failing tests.** They run the script with a stub `claude` first on `PATH`; the stub logs its argv and fails on demand through an env var.
  - `test_local_runs_commands_in_order`: checks the logged argv sequence and the isolated env vars.
  - `test_ref_source_string`: `--from main` gives `marketplace add nerymurillohnd/the-claude-factory#main`.
  - `test_failure_propagates_and_cleans_up`: Review Focus 4.
  - `test_runs_plugin_test_only_for_mods`
- [ ] **Step 2:** Run `npm run test:scripts`. Expected: FAIL.
- [ ] **Step 3:** Implement.
- [ ] **Step 4:** Run `npm run test:scripts && npm run lint:shell`. Then run it for real: `npm run check:install -- --from main block-no-verify`. Expected: exit 0, `list --json` with no `errors`, and no `${T}` left behind.
- [ ] **Step 5: Commit:** `feat(release): add isolated install check script`.

### Task 4: `plugin-consistency.py` (P2)

**Files:**
- Create: `scripts/validators/plugin_consistency/{__init__,checks,readme}.py`, `scripts/validators/plugin-consistency.py`, `scripts/testers/plugin_consistency/{__init__,test_checks}.py`
- Modify: `package.json` (add `"check:consistency": "uv run python scripts/validators/plugin-consistency.py"`)

**Interfaces:**
- Consumes from Tasks 1 and 2: `plugin_names`, `manifest`, `remote_tags`, `changelog_section`.
- Produces: `check(root, remote="origin") -> list[Finding]`. `Finding` is a frozen dataclass with `check_id`, `path` and `message`.
- CLI: `plugin-consistency.py [--json] [--offline]`. `--offline` skips the tag checks. Exit 1 on any finding.

The checks: each one gets a failing test before its code. All are offline unless noted.

| Id | Check | Source of the rule |
| :-- | :-- | :-- |
| PC-01 | Folder, `plugin.json` `name`, entry `name` and entry `source` (`./plugins/<name>`) agree | `refactor.md` stage 7 |
| PC-02 | No `renames` key is still listed in `plugins[]` (the CLI misses this, re-checked on 2.1.323) | `plugin-catalog-changes` |
| PC-03 | `forceRemoveDeletedPlugins` is `true` | ADR_2026-11-13_marketplace-force-removes-deleted-plugins |
| PC-04 | Each `## [X.Y.Z]` heading in a plugin CHANGELOG has its tag; uses the network, skipped with `--offline` | `changelog.md` Checks |
| PC-05 | `## [Unreleased]` is empty on `main` | `changelog.md` |
| PC-06 | The README has no `{{` and has at least 40 words outside code blocks | pre-submission checklist, `plugin-readme.md` |
| PC-07 | The README's version badge, install, update and uninstall commands name the plugin | `plugin-readme.md` |
| PC-08 | The root README catalog has one row per marketplace entry, under its category | `root-readme.md` step 3 |

- [ ] **Step 1:** Write a failing test per check: `test_pc01_name_mismatch` … `test_pc08_missing_catalog_row`, each with one passing fixture and one failing fixture.
- [ ] **Step 2:** Run `npm run test:scripts`. Expected: FAIL.
- [ ] **Step 3:** Implement, one function per check, in `checks.py` and `readme.py`.
- [ ] **Step 4:** Run `npm run test:scripts`, then the **baseline run** `npm run check:consistency`. Show its raw output to the owner, one question per check id, as `WORKFLOW.md` asks for lint findings. Don't add it to `check` until it exits 0. DEBT-001's check part closes only then, through the `project-maintainer:write-records` skill.
- [ ] **Step 5: Commit:** `feat(validators): add plugin consistency checks`.

### Task 5: `release-changelog.py` (P2)

**Files:**
- Create: `release_tools/changelog.py`, `scripts/release/release-changelog.py`, `scripts/testers/release/test_changelog.py`
- Modify: `package.json` (add `"release:changelog": "uv run python scripts/release/release-changelog.py"`)

**Interfaces:**
- Produces: `date_release(text: str, plugin: str, version: str, date: str, repo_url: str) -> str`.
- CLI: `release-changelog.py <plugin> [--date YYYY-MM-DD]`.
  - The default date is today in UTC.
  - It writes `plugins/<plugin>/CHANGELOG.md` in place.
  - Exit 1 when `[Unreleased]` is empty, or when `## [<version>]` already exists.

- [ ] **Step 1: Write the failing tests.** Expected values come from `changelog.md` steps 4–5:
  - `test_dates_unreleased_and_adds_empty_one`
  - `test_links_first_release`: `[Unreleased]` → `…/compare/demo--v0.1.0...HEAD`, `[0.1.0]` → `…/releases/tag/demo--v0.1.0`.
  - `test_links_later_release`: `[0.2.0]` → `…/compare/demo--v0.1.0...demo--v0.2.0`.
  - `test_empty_unreleased_exits_1_unchanged`: Review Focus 5.
  - `test_existing_version_exits_1`
- [ ] **Step 2:** Run `npm run test:scripts`. Expected: FAIL.
- [ ] **Step 3:** Implement. Take `repo_url` from the plugin's `plugin.json` `repository`. The notes text is never generated or changed.
- [ ] **Step 4:** Run `npm run test:scripts && npm run lint:python && npm run typecheck:python`. Expected: OK.
- [ ] **Step 5: Commit:** `feat(release): add changelog dating script`.

### Task 6: Extend validation with the missing CLI commands (P3)

**Files:**
- Modify: `package.json`

**Interfaces, as npm scripts:**
- `"validate:claude": "claude plugin validate --strict .claude"`. It passes today, so add it to `validate` now.
- `"validate:mods": "for d in plugins/*/; do ls \"$d\"tests/*.test.ts* >/dev/null 2>&1 || continue; claude plugin test \"$d\" || exit 1; done"`
- `"validate:hooks-catch"`: for every plugin, run `claude plugin validate --json` and fail when `.gatingHooks[] | select(.hasCatch == false)` is non-empty. Read the exact JSON path from one real `--json` report before you write the `jq` filter.
- `"validate:portable": "for d in plugins/*/; do claude plugin validate --profile directory --strict \"$d\" || exit 1; done"`

- [ ] **Step 1:** Add `validate:claude` and chain it into `validate`. Run `npm run validate:claude`. Expected: exit 0.
- [ ] **Step 2:** Add `validate:mods`, `validate:hooks-catch` and `validate:portable` as stand-alone scripts. Run each and record the raw output. Expected today: the mods failures (TS2741, TS2769, TS5097) and the 4 hooks without `.catch`. Don't chain these into `validate` or `check` until the mod-fix plan (Q1) lands. Note this in `refactor.md`.
- [ ] **Step 3: Commit:** `build: add CLI validation scripts for .claude, mods, hook catches and portability`.

### Task 7: Rewire the skills to the scripts and the missing CLI commands

**Files:**
- Modify:
  - `.claude/skills/plugin-versioning/SKILL.md`
  - `.claude/skills/plugin-releases/SKILL.md`
  - `.claude/skills/plugin-catalog-changes/SKILL.md`
  - `.claude/skills/docs-maintenance/references/documents/changelog.md`
  - `.claude/skills/docs-maintenance/references/commands.md`
  - `.claude/skills/docs-maintenance/references/documents/plugin-readme.md`
  - `.claude/agents/testers/plugin-tester.md`, if it holds its own install block

| Where | Today | After |
| :-- | :-- | :-- |
| versioning step 6 | Bump by hand from `origin/main` | `npm run release:status -- --next <plugin> --level <level>` |
| versioning step 7 | The `jq \| grep` semver command, the 5-line `T` block | `npm run release:status` (exit 0), `npm run check:install -- --from local <plugin>` |
| versioning step 7 | `claude plugin eval … --case <case> --runs 1 --ablation none` | Adds `--no-publish --max-cost-usd <owner value from Q3>` |
| versioning and releases checks | Only `validate --strict` | Add `claude plugin validate plugins/<plugin> --profile directory --strict` and, for a mod, `claude plugin test plugins/<plugin>` |
| releases step 2 | The two bash loops | `git fetch origin main && npm run release:status` |
| releases step 3 | The `<ref>` `T` block | `npm run check:install -- --from <branch> <plugin>`, then `--from main` |
| releases step 4 / changelog.md step 4 | "No script does this yet; edit the file by hand" | `npm run release:changelog -- <plugin>`; the notes stay written by hand |
| changelog.md Checks | Points to the `changed:` loop | Points to `npm run release:status` |
| releases, "Before you start" | Blocker on `release-notes.py` and `Validate` | Drop `release-notes.py` from the blocker. Keep `Validate` and the mod fixes until Q1 lands |
| catalog-changes, After the release | The `T` block | `npm run check:install -- --from main <old> <new-or-target>` |
| catalog-changes step 3 and Checks | `jq` for renames still listed | Keep the dependents `jq` (judgment). Replace the renames `jq` with `npm run check:consistency` (PC-02) once Task 4 is green |
| plugin-readme.md, Uninstall section | Saved data stated by hand | `claude plugin list --json --data-size <plugin>` from an isolated install, to confirm the plugin keeps data |
| commands.md | CLI rows | Add rows for `release:status`, `release:changelog`, `check:consistency`, `validate:claude` |

- [ ] **Step 1:** Before editing, list every reference to a replaced block:

  ```bash
  grep -rn 'mktemp -d\|changed:\|untagged:\|grep -Ex\|No script does this yet' .claude
  ```

  Each hit must be in the table above or be added to it.
- [ ] **Step 2:** Apply the table. Step 7's eval line waits for Q3.
- [ ] **Step 3:** Run `npm run lint:skills` on each of the 4 skills. Expected: 0 errors. Then run Step 1's `grep` again. Expected: no hit outside a script.
- [ ] **Step 4:** Run one release dry run end to end on a committed branch with `block-no-verify`: `release:status`, `check:install --from local` and `release:notes --tag`. Show the raw output.
- [ ] **Step 5: Commit:** one commit per skill: `docs(skills): call release scripts from <skill>`.

### Task 8: Records, `WORKFLOW.md` and the CLAUDE draft

**Files:**
- Create: an ADR for the consolidation, through the `project-maintainer:write-records` skill.
- Modify: `.claude/architecture/refactor.md`, `.claude/WORKFLOW.md`, `.claude/architecture/CLAUDE.draft.md`

- [ ] **Step 1: ADR.** "Five consolidated release and consistency scripts replace the per-check scripts of main", with the alternatives (the ~15 scripts) and the reason: the duplicated pairs in `main` drifted.
- [ ] **Step 2: `refactor.md`.**
  - Mark these lines **Replaced by** the new script: `bump-version.py`, `check-version-bump.py`, `check-published-install.sh`, `plugin-names-consistency.py`, `plugin-versions-consistency.py`, `readme-catalog-consistency.py`, and the README part of `check-repo.mjs`.
  - Mark `release-notes.py` **Implemented**, and resolve its `--tag` "decision pending" with the answer to Q2.
  - Mark the `claude plugin test` line **Implemented** as `validate:mods`, gated per Task 6.
- [ ] **Step 3: `WORKFLOW.md`** (load `instruction-engineering:claude-md-and-rules` first).
  - Stage 3: add `validate:claude`, `validate:mods`, `validate:hooks-catch`, `validate:portable`.
  - Stage 7 / 19: add `check:consistency`.
  - Stage 12: add `release:changelog`.
  - Stage 13: add `release:status`.
  - Stage 15: add `check:install`.
  - Stage 10: add `--no-publish --max-cost-usd` to the eval lines.
  - Add only npm scripts that exist at that commit.
- [ ] **Step 4: `CLAUDE.draft.md`.**
  - In the Main stack row "Plugin validation and release", add `claude plugin test`.
  - In "Testing", add `claude plugin test` for mods.
  - Add a **Release** commands table: `release:status`, `check:install`, `release:changelog`, `release:notes`.
  - Add `check:consistency` and `validate:claude` under Checks.
  - Again, only npm scripts that exist.
- [ ] **Step 5:** Run `npm run test:scripts && npm run lint && npm run typecheck && npm run lint:skills`, and show the raw output. Pre-existing failures stay as they are, and each is reported: `lint:js` on `plugins/github-operations/README.md`, and `validate` on the mods.
- [ ] **Step 6: Commit:** one commit each for the ADR, `refactor.md`, `WORKFLOW.md` and the draft. No push.

## Out of this plan

- The mod fixes and `validate.yml` (Q1).
- The P3 scripts left in `refactor.md`:
  - the schema validators
  - `check-plugin-name.py`
  - the catalog generator
  - the URL checker
