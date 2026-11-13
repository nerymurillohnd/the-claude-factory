# Skill lint Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A deterministic maintainer linter, `npm run lint:skills`, that checks every skill in the repository against the spec's CO, PO, SC and CA rules and prints a table, details, a manifest or JSON.

**Architecture:**
- **Entry point:** `scripts/validators/skill-lint.py` handles the CLI. It drives the package `scripts/validators/skill_lint/`.
- **The package:**
  - `discover.py` loads each skill: its files, parsed frontmatter, parsed Markdown and git index modes.
  - Four `rules_*.py` modules each expose `check(skill) -> list[Finding]`.
  - `report.py` renders the result.
- **Tests:** they build throwaway skills in temporary directories and run with stdlib `unittest`.

**Tech Stack:**
- Python 3.15, run through `uv run`.
- Only the stdlib plus `ruamel.yaml==0.19.1`, which is already in the `dev` dependency group.
- unittest, ruff (`ALL`), and basedpyright (`-p scripts`).

**Spec:** `.claude/maintainer/specs/skill-lint-spec.md`

## Global Constraints

- **Allowed tools:**
  - Python 3.15 with only the stdlib plus `ruamel.yaml`. No new package.
  - Every command goes through an npm script: `npm run test:scripts`, `npm run lint:python`, `npm run typecheck:python` and `npm run lint:skills`.
  - Never run bare `python3` or `.venv/bin/python`.
- **Scope:**
  - The linter reads only files inside each skill folder, plus the git index mode of those files.
  - Discovery uses only `plugins/*/skills/*/SKILL.md` and `.claude/skills/*/SKILL.md`.
- **Severity and exit codes:**
  - ✗ is `Severity.ERROR` and gives exit 1.
  - ⚠ is `Severity.WARNING` and gives exit 0, unless `--strict` is set.
  - A usage error or unreadable input gives exit 2.
- **Size and style:**
  - Each module is at most about 250 lines.
  - Lines are at most 100 columns, per ruff.toml.
  - Colors appear only on a TTY, and never when `NO_COLOR` is set.
- **Files that stay unchanged:** no file under `plugins/` changes, and the plan does not wire the linter into `lint`, `check`, hooks or CI.
- **Commits and pushes:** commit by topic, and push nothing without the owner's authorization.
- **Commit trailers:** every commit ends with:

  ```text
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01BpBwAst9Schq121rRxcra9
  ```

- **Rule metadata:** each finding's `source` is the spec URL for its rule. Each rules module keeps a `SOURCES: dict[str, str]` that maps rule ids to URLs, taken from the spec's Sources section.

## Deviations from the first spec (approved by the owner 2026-11-12; the spec now matches)

1. **No committed fixture tree.** The tests build each fixture skill in a `tempfile.TemporaryDirectory`, through `testers/skill_lint/helpers.py`.
   - Broken SKILL.md files therefore never land in the repository.
   - The spec's ruff, Biome and shellcheck exclusions for fixtures become unnecessary.
   - The SC-02 test needs a temporary git repository anyway.
2. **A `refs.py` module is added to the spec's module list.** It holds the reference graph: links, path mentions, Python imports and shell `source` lines. CO-09, CO-12 and the SC entry-point test all share it.
3. **The plan lives in `.claude/maintainer/plans/`,** next to `specs/`, not in the skill's default `docs/superpowers/plans/`. A new top-level `docs/` folder would mix maintainer material into what users browse.

## Review Focus

1. **A SKILL.md with CRLF line endings or a UTF-8 BOM** must parse normally, with no CO-01 finding. Test in Task 2.
2. **Binary or non-UTF-8 files in a skill folder** (images, `.pyc`) are skipped by every text rule without crashing. They still take part in CO-12. Test in Task 2.
3. **Markdown links with a title, `%20` or angle brackets** resolve to the right file: `[a](b%20c.md "t")` and `[a](<b c.md>)`. Test in Task 3.
4. **A symlink inside the skill that points outside the folder** gives CO-08. Test in Task 5.
5. **Frontmatter that is valid YAML but not a mapping** (a list or a scalar), or an empty `---`/`---` block, gives CO-01 without raising. Test in Task 2.

---

### Task 1: Settle the layout, then scaffold the model and the test runner

Before code is written, this task settles the spec's open Testability items.

**Files:**
- Create:
  - `scripts/validators/__init__.py` (empty)
  - `scripts/validators/skill_lint/__init__.py`
  - `scripts/validators/skill_lint/model.py`
  - `scripts/validators/skill_lint/cli.py` (placeholder)
  - `scripts/validators/skill-lint.py` (shim)
  - `scripts/testers/__init__.py` (empty)
  - `scripts/testers/skill_lint/__init__.py` (empty)
  - `scripts/testers/skill_lint/helpers.py`
  - `scripts/testers/skill_lint/test_model.py`
- Modify:
  - `package.json`: add `test:scripts`.
  - `.claude/maintainer/specs/skill-lint-spec.md`: record the step-1 results under "Testability" and "Not checked here".
- Delete: `scripts/validators/.gitkeep` and `scripts/testers/.gitkeep`.

**Interfaces:**
- **Produces in `skill_lint/model.py`:**
  - `class Severity(StrEnum)`: `ERROR = "error"`, `WARNING = "warning"`.
  - `class Family(StrEnum)`: `CONTENT = "CO"`, `PORTABILITY = "PO"`, `SCRIPTS = "SC"`, `CAPABILITIES = "CA"`.
  - `@dataclass(frozen=True, slots=True) class Finding`:
    - Fields: `rule: str`, `severity: Severity`, `path: str` (relative to the skill root), `line: int | None`, `message: str`, `source: str`.
    - Property `family -> Family`, from the prefix of `rule`.
  - `type SkillKind = Literal["plugin", "project", "standalone"]`
- **Produces in `testers/skill_lint/helpers.py`:**
  - `build_skill(root: Path, files: Mapping[str, str | bytes], *, layout: SkillKind = "plugin", plugin: str = "demo", name: str = "demo-skill") -> Path`
    - Writes the files under the layout path and returns the skill folder:
      - plugin: `root/plugins/<plugin>/skills/<name>/`
      - project: `root/.claude/skills/<name>/`
      - standalone: `root/<name>/`
  - `VALID_SKILL_MD: str`: a SKILL.md that passes every rule, with `name: demo-skill` and a one-line description.
- **Imports:**
  - Tests import `from validators.skill_lint import model`.
  - Inside the package, imports are relative (`from .model import Finding`).

- [ ] **Step 1: Write a probe test**

  `scripts/testers/skill_lint/test_model.py`:

  ```python
  class FindingTest(unittest.TestCase):
      def test_family_from_rule_prefix(self) -> None:
          f = Finding("SC-02", Severity.ERROR, "scripts/x.sh", 1, "m", "https://e")
          self.assertIs(f.family, Family.SCRIPTS)
  ```

- [ ] **Step 2: Add the npm script**

  ```json
  "test:scripts": "uv run python -m unittest discover -s scripts/testers -t scripts -p 'test_*.py'"
  ```

  Run: `npm run test:scripts`

  Expected: an ERROR whose cause is that `validators.skill_lint.model` is not importable.

- [ ] **Step 3: Implement `model.py`**

  Implement it exactly as the Interfaces list says. `skill_lint/__init__.py` holds only a docstring.

- [ ] **Step 4: Confirm the tests pass**

  Run: `npm run test:scripts`

  Expected: `Ran 1 test … OK`. This confirms the `-t scripts` layout without any `sys.path` change.

- [ ] **Step 5: Probe basedpyright and ruff on the layout**

  1. Create two placeholders:
     - `scripts/validators/skill_lint/cli.py` with `def main(argv: list[str] | None = None) -> int: return 0`.
     - The shim `scripts/validators/skill-lint.py`: a shebang, a docstring, `from skill_lint.cli import main` and `sys.exit(main())`.
  2. Run `npm run typecheck:python`.
     - Expected: 0 errors.
     - If the entry-script import does not resolve, add `"extraPaths": ["validators"]` to `scripts/pyrightconfig.json`.
     - If `validators.skill_lint` does not resolve in the tests, add `"."` to the same list.
     - Re-run until it shows 0 errors.
  3. Run `npm run lint:python`.
     - Note whether N999 or INP001 fire on `skill-lint.py`.
     - If they do, add a `[lint.per-file-ignores]` entry for exactly `scripts/validators/skill-lint.py`, with a comment: "hyphenated entry script run by path, never imported".
     - Expected after that: exit 0.

- [ ] **Step 6: Probe ruff's syntax floor**

  Write `def f[T = int](): ...` (Python 3.13 syntax) to the scratchpad as `probe.py`, then run:

  ```bash
  ruff check --no-cache --isolated --target-version py312 <scratchpad>/probe.py
  ```

  Expected: a syntax error that names Python 3.12.
  - If ruff reports it, write in the spec's "Not checked here" section: "confirmed: ruff reports syntax newer than py312".
  - If not, stop and tell the owner. The spec would then need a rule.

- [ ] **Step 7: Confirm the oracle rule ids**

  Run:

  ```bash
  grep -rhoE '\b[MSZR]-[0-9]+\b' plugins/skill-diagnostics/skills/skills-best-practices/scripts | sort -u
  ```

  Expected: the list includes M-2, M-4…M-8, M-11…M-14, S-2, S-3, S-4, S-6, S-8, S-10, S-11, S-12, Z-1, R-4, R-5 and R-10. Checked on 2026-11-12: all present. Record the mapping in Task 11.

- [ ] **Step 8: Remove the `.gitkeep` files, record the results, run all three checks**

  Run each of these:
  - `npm run test:scripts`
  - `npm run lint:python`
  - `npm run typecheck:python`

  Expected: each exits 0.

- [ ] **Step 9: Commit**

  Commit message: `feat(maintainer): scaffold the skill-lint package, its model and the test:scripts runner`

---

### Task 2: Frontmatter parsing, skill loading and CO-01

**Files:**
- Create:
  - `scripts/validators/skill_lint/frontmatter.py`
  - `scripts/validators/skill_lint/discover.py`
  - `scripts/validators/skill_lint/rules_content.py`
  - `scripts/testers/skill_lint/test_frontmatter.py`
  - `scripts/testers/skill_lint/test_discover.py`
  - `scripts/testers/skill_lint/test_rules_content.py`

**Interfaces:**
- **Consumes:** `model.*`.
- **Produces in `frontmatter.py`:**
  - `@dataclass(frozen=True) class Frontmatter`:
    - `data: Mapping[str, object] | None`
    - `key_lines: Mapping[str, int]`: the 1-based file line of each top-level key.
    - `body_start: int`: the first line after the closing `---`.
    - `error: tuple[int, str] | None`
  - `parse_frontmatter(text: str) -> Frontmatter`
    - Strips a BOM and treats CRLF as LF.
    - Uses `YAML(typ="rt")` with `allow_duplicate_keys = False`.
    - Each of these sets `error` and `data=None`: a missing opening `---` on line 1, a missing closing `---`, a YAML error, a duplicate key, or a non-mapping value.
- **Produces in `discover.py`:**
  - `type ModeReader = Callable[[Path], Mapping[str, str]]`: takes the skill folder and returns a map from relative POSIX path to git mode, holding tracked files only.
  - `git_modes(skill_dir: Path) -> dict[str, str]`
    - Runs `git -C <dir> ls-files -s -z -- .`.
    - Returns `{}` when the folder is outside git or git fails.
  - `@dataclass(frozen=True) class Skill`:
    - `root: Path`, `kind: SkillKind`, `plugin: str | None`, `command: str`
    - `plugin_root: Path | None`
    - `files: tuple[str, ...]`: relative POSIX paths, sorted, symlinks included.
    - `text: Mapping[str, str]`: UTF-8-decodable files only.
    - `modes: Mapping[str, str]`
    - `frontmatter: Frontmatter`
    - Task 3 adds `body: MarkdownDoc`.
    - `def is_executable(self, rel: str) -> tuple[bool, bool]`: returns `(executable, tracked)`. It uses the git mode when tracked, otherwise `stat` `& 0o111`.
  - `load_skill(skill_md: Path, *, mode_reader: ModeReader = git_modes) -> Skill`
    - `kind` comes from the path: `…/plugins/<p>/skills/<s>/SKILL.md` gives `plugin` and the command `<p>:<s>`; `…/.claude/skills/<s>/SKILL.md` gives `project` and the command `project:<s>`; any other path gives `standalone` and the command `<s>`.
    - It skips `__pycache__` and `.DS_Store` when it reads text, but lists them in `files`.
  - `discover(repo: Path) -> list[Skill]`: covers only the spec's two globs, sorted by command.

- [ ] **Step 1: Write the failing tests**

  - `test_frontmatter.py`:
    - `test_valid_mapping`: `data["name"] == "demo-skill"`, `key_lines["name"] == 2`, `error is None`.
    - `test_crlf_and_bom_parse` (Review Focus 1).
    - `test_missing_open`: `error[0] == 1`.
    - `test_missing_close`.
    - `test_duplicate_key`: `"duplicate"` is in `error[1]`.
    - `test_list_not_mapping` (Review Focus 5).
    - `test_empty_block` (Review Focus 5).
  - `test_discover.py`:
    - `test_plugin_kind_and_command`: `"demo:demo-skill"`.
    - `test_project_kind`: `"project:demo-skill"`.
    - `test_standalone_kind`.
    - `test_binary_file_listed_not_text` (Review Focus 2): writes `b"\x89PNG\x00"` to `assets/a.png`; the path is in `files` and not in `text`.
    - `test_is_executable_untracked_uses_stat`.
    - `test_discover_ignores_other_skill_md`: a SKILL.md under `scripts/testers/x/` is not returned.
    - `test_git_modes_in_temp_repo`: runs `git init`, `add`, `update-index --chmod=+x`, then checks the mode is `"100755"`.

- [ ] **Step 2: Run the tests**

  Run: `npm run test:scripts`

  Expected: FAIL, because the modules don't exist yet.

- [ ] **Step 3: Implement `frontmatter.py` and `discover.py`**

  Implement them as the Interfaces list says.

- [ ] **Step 4: Add the CO-01 rule**

  Create `rules_content.py` with `check(skill: Skill) -> list[Finding]`. Its first rule is CO-01: one ERROR at `error[0]` with `error[1]`.

  Add `test_co01_reports_parse_error` to the new `test_rules_content.py`.

- [ ] **Step 5: Run the checks**

  Run each of these:
  - `npm run test:scripts`
  - `npm run lint:python`
  - `npm run typecheck:python`

  Expected: every test passes, and the other two exit 0.

- [ ] **Step 6: Commit**

  Commit message: `feat(maintainer): load skills, parse frontmatter strictly and report CO-01`

---

### Task 3: Markdown model and the reference graph

**Files:**
- Create:
  - `scripts/validators/skill_lint/markdown.py`
  - `scripts/validators/skill_lint/refs.py`
  - `scripts/testers/skill_lint/test_markdown.py`
  - `scripts/testers/skill_lint/test_refs.py`

**Interfaces:**
- **Modifies:** `discover.Skill` gains `body: MarkdownDoc`. `load_skill` sets it with `parse_markdown(<SKILL.md text after the frontmatter>, first_line=frontmatter.body_start)`. Add `test_load_skill_parses_body` to `test_discover.py`.
- **Produces in `markdown.py`:**
  - `Link(target: str, line: int)`: link targets are already unwrapped from `<…>`, have any `"title"` removed, and are percent-decoded.
  - `Heading(text: str, line: int, slug: str)`
  - `BangCommand(command: str, line: int, block: bool)`
  - `CodeSnippet(text: str, line: int, lang: str | None, inline: bool)`
  - `MarkdownDoc(links, headings, anchors: frozenset[str], bang_commands, code: tuple[CodeSnippet, ...], prose: tuple[tuple[int, str], ...])`
  - `parse_markdown(text: str, first_line: int = 1) -> MarkdownDoc`
    - Links are read only outside code.
    - Covers inline links and reference definitions; skips `http:`, `https:` and `mailto:`.
    - `anchors` holds the heading slugs plus any `<a id|name="…">`.
  - `github_slug(text: str, seen: dict[str, int]) -> str`
    - Lowercases the text.
    - Keeps `[\w\- ]`, where `\w` is Unicode, and drops other characters.
    - Turns spaces into `-`.
    - Duplicates get `-1`, `-2` and so on.
- **Produces in `refs.py`:**
  - `resolve(skill: Skill, token: str, from_file: str) -> str | None`
    - Maps `${CLAUDE_SKILL_DIR}/x`, `${CLAUDE_PLUGIN_ROOT}/x` (plugin skills only), and paths relative to `from_file` or the skill root.
    - Returns the relative POSIX path when the target is a file inside `skill.root`, and `None` otherwise.
  - `escapes(skill: Skill, token: str, from_file: str) -> bool`
    - True when the resolved real path, after following symlinks, is outside `skill.root`, or when the token is an absolute path.
  - `reference_graph(skill: Skill) -> dict[str, set[str]]`
    - Maps each file to the files it references.
    - What counts as a reference:
      - Markdown links.
      - Path-looking tokens in code and in prose: the regex `[\w${}./-]+\.\w+`, or any token that starts with a known prefix.
      - Python `import x` or `from x import` of a sibling `x.py`.
      - Shell `source p` or `. p`.
  - `depths(graph: Mapping[str, set[str]], start: str = "SKILL.md") -> dict[str, int]`: a breadth-first search.
  - `imported_or_sourced(skill: Skill) -> set[str]`: files that another skill file imports or sources.

- [ ] **Step 1: Write the failing tests**

  - `test_markdown.py`:
    - `test_link_title_and_encoding` (Review Focus 3): both `[a](b%20c.md "t")` and `[a](<b c.md>)` give the target `"b c.md"`.
    - `test_links_in_code_ignored`.
    - `test_slug_duplicates`: two `## Use it` headings give `use-it` and `use-it-1`.
    - `test_slug_punctuation`: `## Step 1: Run` gives `step-1-run`.
    - `test_bang_inline_and_block`: `` !`git status` `` and a fence with the info string `!` give two commands, with `block` False and True.
    - `test_explicit_anchor`.
  - `test_refs.py`:
    - `test_resolve_three_forms`: each of the three forms resolves to `"scripts/run.py"`.
    - `test_plugin_root_only_in_plugin`.
    - `test_escape_dotdot`.
    - `test_depths_two_levels`.
    - `test_python_sibling_import_is_reference`.
    - `test_shell_source_is_reference`.

- [ ] **Step 2: Run the tests**

  Run: `npm run test:scripts`

  Expected: FAIL.

- [ ] **Step 3: Implement both modules**

  Use a line scanner that tracks fences (`` ``` `` or `~~~`, with the info string). Use regex for inline code and links. Use `ast.parse` for Python imports, and skip files that raise `SyntaxError`.

- [ ] **Step 4: Run the checks**

  Run each of these:
  - `npm run test:scripts`
  - `npm run lint:python`
  - `npm run typecheck:python`

  Expected: every test passes, and the other two exit 0.

- [ ] **Step 5: Commit**

  Commit message: `feat(maintainer): parse skill Markdown and build the skill's reference graph`

---

### Task 4: Content rules CO-02 to CO-06 (frontmatter values and size)

**Files:**
- Modify: `scripts/validators/skill_lint/rules_content.py`
- Test: `scripts/testers/skill_lint/test_rules_content.py`

**Interfaces:**
- **Consumes:** `Skill`, `Frontmatter.key_lines`, `Finding`.
- **Produces:** each rule is a private function `_coNN(skill) -> list[Finding]`, called from `check`. Rules that need parsed data are skipped when CO-01 failed.

- [ ] **Step 1: Write the failing tests**

  Each test asserts `rules == [...]` on the findings of a built skill. Every finding is an ERROR at the key's line.

  | Test | Input | Expected finding |
  | :-- | :-- | :-- |
  | `test_co02_missing_name` | no `name` | CO-02 |
  | `test_co02_bad_chars` | `name: Demo_Skill` | CO-02 |
  | `test_co02_double_hyphen` | `name: demo--skill` | CO-02 |
  | `test_co02_length` | 65 characters | CO-02 |
  | `test_co02_folder_mismatch` | `name: other` in folder `demo-skill` | CO-02 |
  | `test_co02_zero_width` | a name that contains U+200B | CO-02 |
  | `test_co03_empty` | an empty `description` | CO-03 |
  | `test_co03_1025` | 1,025 characters | CO-03 |
  | `test_co03_xml` | `<tag>` in the description | CO-03 |
  | `test_co04_1537` | description + `when_to_use` = 1,537 characters | CO-04, with `"truncated"` in the message |
  | `test_co04_1536_ok` | exactly 1,536 characters | none |
  | `test_co05_compat_501` | `compatibility` of 501 characters | CO-05 |
  | `test_co05_metadata_non_string` | `metadata: {a: 1}` | CO-05 |
  | `test_co06_body_500_fails` | a body of exactly 500 lines | CO-06 |
  | `test_co06_body_499_ok` | a body of 499 lines | none |
  | `test_valid_skill_clean` | `VALID_SKILL_MD` | no findings from CO-02 to CO-06 |

- [ ] **Step 2: Run the tests**

  Run: `npm run test:scripts`

  Expected: the new tests FAIL.

- [ ] **Step 3: Implement the rules**

  Implement `_co02` to `_co06` with the spec's values:
  - The name regex is `^[a-z0-9]+(-[a-z0-9]+)*$`, 1 to 64 characters, equal to `skill.root.name`.
  - The XML regex is `<[A-Za-z/!?][^>]*>`.
  - The body count is the number of lines from `body_start` to the end of the file.

- [ ] **Step 4: Run the checks**

  Run each of these:
  - `npm run test:scripts`
  - `npm run lint:python`
  - `npm run typecheck:python`

  Expected: every test passes, and the other two exit 0.

- [ ] **Step 5: Commit**

  Commit message: `feat(maintainer): check skill frontmatter values and SKILL.md length (CO-02..CO-06)`

---

### Task 5: Content rules CO-07 to CO-12 (links, depth and files)

**Files:**
- Modify: `scripts/validators/skill_lint/rules_content.py`. If the file passes about 250 lines, split it into `rules_content_files.py` and have `check` call both.
- Test: `scripts/testers/skill_lint/test_rules_content_files.py`

**Interfaces:**
- **Consumes:** `refs.resolve`, `refs.escapes`, `refs.reference_graph`, `refs.depths`, `MarkdownDoc.anchors`.
- **Produces:** additions to `check` only.

- [ ] **Step 1: Write the failing tests**

  | Test | Input | Expected |
  | :-- | :-- | :-- |
  | `test_co07_missing_file` | a link to `references/none.md` | CO-07 |
  | `test_co07_missing_anchor` | `[x](references/a.md#nope)` | CO-07 |
  | `test_co07_same_file_anchor_ok` | a link to an anchor in the same file | none |
  | `test_co08_dotdot_link` | `[x](../other/SKILL.md)` | CO-08 |
  | `test_co08_symlink_outside` (Review Focus 4) | `references/x.md` is a symlink to a file outside the folder | CO-08 |
  | `test_co09_depth_two` | SKILL.md → `a.md` → `b.md`, and SKILL.md never names `b.md` | CO-09 on `b.md` only, with no CO-12 |
  | `test_co10_toc_missing` | a 101-line reference with no table of contents | CO-10 |
  | `test_co10_toc_present` | a 101-line reference with 2 in-file anchor links in the first 20 non-blank lines after the first heading | none |
  | `test_co10_100_lines_ok` | a 100-line reference | none |
  | `test_co11_dated_conditional` | `Before March 2026, use X` | CO-11 WARNING |
  | `test_co11_in_code_ignored` | the same text inside a fence | none |
  | `test_co12_orphan` | `assets/unused.txt`, which nothing names | CO-12 WARNING |
  | `test_co12_exemptions` | `evals/x.json`, `__init__.py` and `__pycache__/a.pyc` | none |
  | `test_co12_binary_referenced_ok` | `assets/a.png`, linked from SKILL.md | none |

- [ ] **Step 2: Run the tests**

  Run: `npm run test:scripts`

  Expected: the new tests FAIL.

- [ ] **Step 3: Implement the rules**

  Implement `_co07` to `_co12`. CO-11 uses these regexes, case-insensitive, on `prose` only. `MONTH` is the 12 English month names joined with `|`.

  ```python
  CO11 = (
      rf"\b(before|after|until|since|as of)\s+((?:{MONTH}|Q[1-4])\s+)?(19|20)\d{{2}}\b",
      r"\b(currently|now|today|recently)\b.{0,40}\b(19|20)\d{2}\b",
      r"\bin (19|20)\d{2}\b",
  )
  ```

  Each file gets at most one of CO-09 (it is in `depths` with a value above 1 and it is a `.md` file) and CO-12 (it is not in `depths` and is not exempt).

- [ ] **Step 4: Run the checks**

  Run each of these:
  - `npm run test:scripts`
  - `npm run lint:python`
  - `npm run typecheck:python`

  Expected: every test passes, and the other two exit 0.

- [ ] **Step 5: Commit**

  Commit message: `feat(maintainer): check skill links, reference depth, TOCs, dated text and orphans (CO-07..CO-12)`

---

### Task 6: Portability rules

**Files:**
- Create:
  - `scripts/validators/skill_lint/rules_portability.py`
  - `scripts/testers/skill_lint/test_rules_portability.py`

**Interfaces:**
- **Produces:** `check(skill: Skill) -> list[Finding]`, and `SPEC_FIELDS = frozenset({"name", "description", "license", "compatibility", "metadata", "allowed-tools"})`.

- [ ] **Step 1: Write the failing tests**

  | Test | Input | Expected |
  | :-- | :-- | :-- |
  | `test_po01_plugin_root_in_project_skill` | a project skill whose body uses `${CLAUDE_PLUGIN_ROOT}` | PO-01 ERROR |
  | `test_po01_ok_in_plugin` | the same in a plugin skill | none |
  | `test_po02_backslash_link` | `[x](references\\a.md)` | PO-02 ERROR |
  | `test_po03_extra_fields` | `when_to_use`, `hooks` | a single PO-03 WARNING that names both fields |
  | `test_po04_bang` | one inline and one block command | two PO-04 WARNINGs |
  | `test_po06_allowed_tools_list` | `allowed-tools: [Read, Grep]` | PO-06 |
  | `test_po06_string_ok` | `allowed-tools: Read Grep` | none |
  | `test_po07_reserved_word` | `name: claude-helper` in a folder with the same name | PO-07 WARNING |
  | `test_no_po05_ever` | a script reached only through `${CLAUDE_SKILL_DIR}` | no PO-05 finding |

- [ ] **Step 2: Run the tests**

  Run: `npm run test:scripts`

  Expected: FAIL.

- [ ] **Step 3: Implement the rules**

  Implement PO-01, PO-02, PO-03, PO-04, PO-06 and PO-07. Each finding's message names the surface it affects:
  - PO-03: "Claude Code only".
  - PO-04: "does not run in claude.ai chat or Cowork".

- [ ] **Step 4: Run the checks**

  Run each of these:
  - `npm run test:scripts`
  - `npm run lint:python`
  - `npm run typecheck:python`

  Expected: every test passes, and the other two exit 0.

- [ ] **Step 5: Commit**

  Commit message: `feat(maintainer): check skill portability across Claude surfaces (PO rules)`

---

### Task 7: Script rules

**Files:**
- Create:
  - `scripts/validators/skill_lint/rules_scripts.py`
  - `scripts/testers/skill_lint/test_rules_scripts.py`

**Interfaces:**
- **Consumes:** `refs.resolve`, `refs.imported_or_sourced`, `Skill.is_executable`, `MarkdownDoc.code` and `bang_commands`.
- **Produces:**
  - `entry_points(skill: Skill) -> set[str]`
    - Includes files run from a run context that `resolve` maps to a skill file, plus files whose first bytes are `#!`.
    - Excludes `__init__.py`, the files in `imported_or_sourced`, and data extensions (`.json`, `.yaml`, `.yml`, `.md`, `.txt`, `.toml`, `.csv`).
    - Run contexts are bang commands, fences tagged `bash`, `sh`, `shell`, `console` or `zsh`, and inline code that starts with an interpreter.
  - `INTERPRETERS: Mapping[str, frozenset[str]]`:
    - `.py` → `{"python3", "python", "uv run python", "uv run"}`
    - `.sh` and `.bash` → `{"bash", "sh"}`
    - `.js`, `.mjs` and `.cjs` → `{"node"}`
  - `check(skill: Skill) -> list[Finding]`

- [ ] **Step 1: Write the failing tests**

  | Test | Input | Expected |
  | :-- | :-- | :-- |
  | `test_sc01_entry_without_shebang` | a script that SKILL.md runs, without a shebang | SC-01 |
  | `test_sc01_not_for_init_or_imported` | `scripts/__init__.py`, and `scripts/util.py` imported by `scripts/run.py` | no SC-01 on them |
  | `test_sc01_bad_shebang` | `#!/usr/bin/python3` | SC-01 (it must be `#!/usr/bin/env …`) |
  | `test_sc02_tracked_not_exec` | a temporary git repo, mode 100644 | SC-02 |
  | `test_sc02_untracked_uses_stat` | untracked, mode 0644 | SC-02 with `"untracked: filesystem mode"` in the message |
  | `test_sc03_missing_script` | ``python3 ${CLAUDE_SKILL_DIR}/scripts/none.py`` | SC-03 |
  | `test_sc03_no_interpreter` | ``${CLAUDE_SKILL_DIR}/scripts/run.py`` alone | SC-03 |
  | `test_sc03_all_three_forms_ok` | relative, `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}/skills/demo-skill/scripts/run.py`, each with `python3` | none |
  | `test_sc04_third_party_without_pep723` | `import yaml` | SC-04 |
  | `test_sc04_pep723_ok` | a `# /// script` block with a non-empty `dependencies` | none |
  | `test_sc04_stdlib_and_local_ok` | `import json` and `import util`, where `util.py` is a sibling | none |
  | `test_sc05_unmentioned_command` | a shell script that calls `jq`, which nothing mentions | SC-05 WARNING |
  | `test_sc05_mentioned_in_compatibility_ok` | `compatibility: Requires jq` | none |
  | `test_sc06_global_installs` | `pip install x` with no venv in the file, and `npm install -g y` | two SC-06 WARNINGs |

- [ ] **Step 2: Run the tests**

  Run: `npm run test:scripts`

  Expected: FAIL.

- [ ] **Step 3: Implement the rules**

  - **SC-04:** "stdlib" means `sys.stdlib_module_names`, plus the skill's own module names.
  - **SC-05:**
    - Commands come from the first word of each simple command in shell files, split on `;`, `&&`, `||`, `|` and `$(`.
    - In Python, they come from the first literal element of `subprocess.*([...])` and from `shutil.which("…")`.
    - These are ignored: shell builtins and keywords, the `BASELINE` set, and any command whose name appears as a whole word in any `.md` file of the skill or in `compatibility`.
    - `BASELINE` holds POSIX and coreutils commands: `cat cp mv rm mkdir ls ln chmod find grep sed awk head tail sort uniq wc tr cut xargs dirname basename date env mktemp tee printf echo test true false sleep`.
  - **SC-06:** the regexes are `\bpip3?\s+install\b` and `-m pip install`, unless the file contains `venv`, plus `\bnpm\s+(i|install)\b.*\s(-g|--global)\b`.

- [ ] **Step 4: Run the checks**

  Run each of these:
  - `npm run test:scripts`
  - `npm run lint:python`
  - `npm run typecheck:python`

  Expected: every test passes, and the other two exit 0.

- [ ] **Step 5: Commit**

  Commit message: `feat(maintainer): check skill scripts' entry points, invocation and dependencies (SC rules)`

---

### Task 8: Capability rules and the inventory

**Files:**
- Create:
  - `scripts/validators/skill_lint/rules_capabilities.py`
  - `scripts/testers/skill_lint/test_rules_capabilities.py`

**Interfaces:**
- **Produces:**
  - `@dataclass(frozen=True) class Hook(event: str, matcher: str | None, type: str, run: str, once: bool)`
  - `@dataclass(frozen=True) class Inventory(bang: tuple[BangCommand, ...], hooks: tuple[Hook, ...], allowed_tools: tuple[str, ...])`
  - `inventory(skill: Skill) -> Inventory`
    - `allowed-tools` is accepted as a string, split on whitespace outside parentheses, or as a list.
    - `hooks` follows the frontmatter shape `{Event: [{matcher, hooks: [{type, command|prompt, once}]}]}`.
  - `check(skill: Skill) -> list[Finding]`

- [ ] **Step 1: Write the failing tests**

  | Test | Input | Expected |
  | :-- | :-- | :-- |
  | `test_inventory_lists_all` | one bang command, one `PreToolUse` hook with `once: true`, and `allowed-tools: Read Bash(git status*)` | each listed exactly |
  | `test_ca01_arguments_placeholder` | `` !`grep $ARGUMENTS x` `` | CA-01 ERROR |
  | `test_ca01_index_and_positional` | `$ARGUMENTS[0]`, `$1` | CA-01 |
  | `test_ca01_declared_name` | `arguments: [file]` with `$file` | CA-01 |
  | `test_ca01_shell_vars_ok` | `$HOME`, `$PATH`, and `$f` with no `f` argument declared | none |
  | `test_ca02_unscoped_bash` | `Bash` and `Bash(*)` | two CA-02 WARNINGs |
  | `test_ca03_self_approved` | `allowed-tools: Bash(git status*)` with `` !`git status` `` | CA-03 |
  | `test_ca04_network_in_script` | `curl` in `scripts/a.sh`, and `import requests` in a `.py` file | two CA-04 |
  | `test_ca04_markdown_ignored` | `curl` in SKILL.md | none |

- [ ] **Step 2: Run the tests**

  Run: `npm run test:scripts`

  Expected: FAIL.

- [ ] **Step 3: Implement the rules**

  - **CA-03:** matching uses `fnmatch.fnmatchcase(command, pattern)`, where `pattern` is the text inside `Bash(…)`. A bare `Bash` matches everything.
  - **CA-04:** the regexes, applied to code files only, are:
    - `\bcurl\b`, `\bwget\b`
    - `\burllib\b`, `\brequests\b`, `\bsocket\b`, `\bhttp\.client\b`
    - `\bfetch\(`
    - `~/\.ssh`, `(^|/)\.env\b`, `\.netrc`

- [ ] **Step 4: Run the checks**

  Run each of these:
  - `npm run test:scripts`
  - `npm run lint:python`
  - `npm run typecheck:python`

  Expected: every test passes, and the other two exit 0.

- [ ] **Step 5: Commit**

  Commit message: `feat(maintainer): inventory skill capabilities and flag risky ones (CA rules)`

---

### Task 9: Report, CLI and `lint:skills`

**Files:**
- Create:
  - `scripts/validators/skill_lint/report.py`
  - `scripts/testers/skill_lint/test_report.py`
  - `scripts/testers/skill_lint/test_cli.py`
- Modify:
  - `scripts/validators/skill_lint/cli.py`: replace the Task 1 placeholder.
  - `package.json`: add `lint:skills`.
- Unchanged: the `scripts/validators/skill-lint.py` shim from Task 1.

**Interfaces:**
- **Consumes:** `discover`, `load_skill`, the four `check` functions and `inventory`.
- **Produces in `report.py`:**
  - `family_status(findings: Sequence[Finding], family: Family, *, strict: bool) -> Literal["pass", "warn", "fail"]`
  - `render_text(results: Sequence[tuple[Skill, list[Finding]]], *, color: bool, strict: bool) -> str`
    - Output order: a summary line `"<n> skills · <e> errors · <w> warnings"`, then the table, then a `DETAILS` section.
    - The table has the columns `SKILL`, `CO`, `PO`, `SC` and `CA`, with the cells `✓`, `⚠` or `✗`.
    - Each `DETAILS` line is `"  <rule> <path>:<line> <message>"`, sorted by rule and then by path.
  - `render_manifest(results: Sequence[tuple[Skill, Inventory]]) -> str`
  - `render_json(results: …, inventories: … | None) -> str`
    - The shape is `{"skills": [{"command", "path", "families": {"CO": status, …}}], "findings": [asdict(f) + {"skill": command}], "manifest": {command: …} | null}`.
- **Produces in `skill_lint/cli.py`:** `main(argv: list[str] | None = None) -> int`. `test_cli` imports it as `validators.skill_lint.cli.main`; the hyphenated shim is never imported.
  - **Arguments:**
    - `paths` (zero or more). Each is a skill folder or a SKILL.md file. With none, it runs `discover(ROOT)`.
    - `--only CO,PO,SC,CA`
    - `--strict`, `--manifest`, `--json`
  - **Exit 2** when a path has no SKILL.md or cannot be read. argparse already exits 2 on bad flags.
  - **Colors:** used when `sys.stdout.isatty()` and `"NO_COLOR" not in os.environ`.

- [ ] **Step 1: Write the failing tests**

  - `test_report.py`:
    - `test_status_ordering`: ERROR gives `fail`; WARNING alone gives `warn`, or `fail` with `strict`.
    - `test_table_has_command_names`.
    - `test_no_ansi_when_color_false`.
    - `test_json_round_trip`: `json.loads` works, and the counts match.
  - `test_cli.py`, which calls `main([...])` with stdout redirected:
    - `test_exit_0_clean`
    - `test_exit_1_error`
    - `test_exit_0_warning_only`
    - `test_exit_1_warning_strict`
    - `test_exit_2_missing_path`
    - `test_only_filters_families`
    - `test_no_color_env`: with `NO_COLOR=1` and a fake TTY, the output has no `\x1b[`.

- [ ] **Step 2: Run the tests**

  Run: `npm run test:scripts`

  Expected: FAIL.

- [ ] **Step 3: Implement the report and the CLI, add the npm script**

  Implement `report.py` and `cli.py`, following `scripts/check-github-files.py`: argparse and a `main` that returns an int. The shim already ends with `sys.exit(main())`.

  Add to `package.json`:

  ```json
  "lint:skills": "uv run python scripts/validators/skill-lint.py"
  ```

  Do not chain it into `lint` or `check`.

- [ ] **Step 4: Run the checks**

  Run each of these:
  - `npm run test:scripts`
  - `npm run lint:python`
  - `npm run typecheck:python`
  - `npx biome check package.json`

  Expected: every test passes and the other checks exit 0.

  Do not use `npm run lint:js` here. It checks the whole repository, which fails today with 10 known Biome errors in `plugins/`, and no file under `plugins/` may change.

- [ ] **Step 5: Commit**

  Commit message: `feat(maintainer): add the skill-lint report, CLI and npm run lint:skills`

---

### Task 10: ADR

**Files:**
- Create: `.claude/maintainer/decisions/ADR_2026-11-12_own-deterministic-skill-linter.md`, through `project-maintainer:write-records`.

- [ ] **Step 1: Write the ADR with the skill**

  Invoke `project-maintainer:write-records`. The ADR records:
  - The linter is our own maintainer code, independent of `skill-diagnostics`.
  - The ✗/⚠ severity model with `--strict`.
  - The skill-folder-only scope.
  - One owner per check.
  - PO-05 is withdrawn: every script path form is valid.
  - When and by whom it runs is still to be decided.

- [ ] **Step 2: Check the record**

  Run: `grep -n 'status:' <the ADR file>`

  Expected: `status: accepted`.

- [ ] **Step 3: Commit**

  Commit message: `docs(maintainer): record the decision to own a deterministic skill linter`

---

### Task 11: Read-only run, oracle comparison and the owner's decisions

**Files:** none change. The record is the owner's decisions; fixes or debt entries come after them.

- [ ] **Step 1: Run the linter on the whole repository**

  Run each of these:
  - `npm run lint:skills`
  - `npm run lint:skills -- --manifest`
  - `git status --porcelain`

  Expected:
  - The table lists 26 skills.
  - `git status --porcelain` is empty. Every file is already committed, which shows the run changed nothing.

- [ ] **Step 2: Compare CO-01 with `claude plugin validate`**

  Run `claude plugin validate --strict plugins/<p>` for each plugin. Every CO-01 failure that `claude plugin validate` doesn't report is labeled "ruamel-only".

  `claude plugin validate` only accepts plugins, so `project:docs-maintenance` gets no CO-01 cross-check. Say so in the report.

- [ ] **Step 3: Compare with the oracle**

  Run the `skill-diagnostics` check scripts for each skill, with their documented invocation; read their `--help` first.

  Then compare verdicts with these pairs. They were checked on 2026-11-12 against the oracle scripts' own messages:

  | Ours | Oracle | Oracle message |
  | :-- | :-- | :-- |
  | CO-01 | M-2 | the frontmatter parses as strict YAML |
  | CO-02 | M-4, M-5, M-6, M-7 | name length, `a-z0-9-`, no leading, trailing or double hyphen, matches the folder |
  | PO-07 | M-8 | no reserved word |
  | CO-03 | M-11, M-12, M-13 | non-empty string, length, no XML tag |
  | CO-04 | M-14 | description + `when_to_use` length |
  | CO-07 | S-2, S-3 | every local link resolves; every anchor names a heading |
  | CO-09 | S-4 | every linked file is linked from SKILL.md |
  | CO-10 | S-6 | a Markdown file over 100 lines has a table of contents |
  | PO-02 | S-8 | no backslash in link targets or script paths |
  | SC-01 | S-10 | every script has a `#!/usr/bin/env` line |
  | SC-02 | S-11 | every script is executable |
  | CO-08 | S-12 | no path leaves the skill folder |
  | CO-06 | Z-1 | SKILL.md line count |
  | CA-01 | R-4 | no argument placeholder inside a `!` command |
  | CA-02 | R-5 | an unscoped Bash pre-approves every command |

  These differences are expected, by design:
  - SC-01 and SC-02 check entry points only; the oracle checks every script.
  - CO-06 counts only the body.
  - R-10 ("every `Bash()` pattern matches a command the body runs") has no counterpart in our rules.

  Explain every difference with evidence.

- [ ] **Step 4: Take the results to the owner**

  Send the owner the full table, the details, and the explanation of the differences. Then ask one question per rule id, listing the affected skills:
  - fix it now (in a plugin PR, with a version bump where users are affected);
  - record it as technical debt, through `project-maintainer:write-records`;
  - or another decision.

  Fix nothing without the owner's answer.

- [ ] **Step 5: Final verification**

  Run each of these:
  - `npm run test:scripts`
  - `npm run lint:python`
  - `npm run typecheck:python`
  - `npm run lint:skills`

  Show the raw output. Expected: the first three exit 0, and `lint:skills` exits with whatever code the real findings give.

  Push nothing without authorization.
