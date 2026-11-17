# Frontmatter mechanical checks Implementation Plan (v2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the 14 frontmatter checks (spec FM-1 to FM-14), each one stable, read-only and release ready:
- FM-1, FM-6 and FM-11 as portable shell commands in step 3 of `SKILL.md`;
- the other eleven as standalone Python scripts under `skills/auditing-skills/scripts/frontmatter/`, standard library only.

**Architecture:**
- The commands print raw facts: bytes, marker lines, top-level keys, the folder name. The reviewer judges them against its reference.
- The scripts share one `common/` package. Its own frontmatter reader handles the YAML forms skills use, with file positions, styles, anchors and tags. Each script prints one JSON result.
- Anything the reader cannot read with certainty is reported as unreadable. It is never guessed.
- The entry script and the wiring of the eleven scripts into `SKILL.md` belong to the next plan.

**Tech Stack:**
- Python ≥ 3.12, standard library only, `unittest`, ruff, basedpyright;
- POSIX `head`, `od`, `grep`, `awk`, `basename` and `dirname`.

**Spec:** `.claude/maintainer/specs/2026-11-17-frontmatter-checks.md`, Nery's FM-1 to FM-14 cards, copied verbatim.

## Global Constraints

- **Python floor 3.12**, the marketplace's floor for plugin Python (`ruff.toml` `per-file-target-version`, `pyrightconfig.json` `pythonVersion`).
  - Each script checks the version before any other import and prints `<script>: needs Python 3.12 or later; this is X.Y.Z.` to stderr, exit 2.
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
- **Invocation:** `python3 "${CLAUDE_SKILL_DIR}/scripts/frontmatter/<check>.py" "<SKILL.md>"`, the pattern of the skills docs ("Generate visual output") and of Anthropic's plugins.
  - Scripts carry `#!/usr/bin/env python3` and the executable bit but never rely on either.
  - The `python` fallback on Windows belongs to the wiring plan.
- **Read-only:** no network, no subprocess, and no writes outside the test temp dirs. A script reads only the `SKILL.md` it is given and its folder name, never settings, MCP or credential files.
- **CLI:** `<check>.py <SKILL.md> [check options]`.
  - Exit 0 when a JSON result was printed. Exit 2 on a usage error, a missing path, a directory path or an unreadable file; stderr then gets one line and stdout stays empty.
  - An uncaught exception is a bug.
- **Output:** one JSON object on stdout (`ensure_ascii=False`), keys in this order:
  - `check`, `status` (`ran` | `not_run`), `reason`, `skill_md` (absolute path), `findings`, `data`.
  - A finding holds `rule`, `message`, `line`, `column` (1-based file positions or null), `evidence` (at most 120 characters plus `…`, or null), `basis` (`official` | `convention` | `inference`), `surfaces` (a subset of `claude-code`, `open-spec`, `upload`) and `condition` (string or null).
  - `upload` means claude.ai uploads, the Skills API and `package_skill.py`, which the skills docs group as one path.
  - Findings never carry a severity: that belongs to the reviewers.
- **Prerequisites:** a check whose prerequisite failed returns `status: not_run` with `reason` naming the check that failed, for example `"frontmatter.yaml failed"`.
- **Identifiers:** check ids are `frontmatter.<slug>`. FM-n appears only in this plan, never in plugin files, because no plugin file names a maintainer validator rule id.
- **Field tables:** only in `common/fields.py`, taken from the Claude Code 2.1.326 docs (`/en/skills` Frontmatter reference), `agentskills.io/specification` and anthropics/skills `quick_validate.py`.
- **Quality:** ruff check and ruff format clean with no suppressions, basedpyright 0 errors, and an `__init__.py` in `common/`.
- **Portability:** no POSIX-only Python APIs. Commands use only POSIX options, avoid `grep -P`, `sed -i` and `$'…'`, and contain no `$` followed by a digit, because skills substitute `$N` with arguments.
- **Tests:** in `plugins/skills-engineering/tests/test_frontmatter_*.py`, stdlib `unittest`, run by `npm run test:plugins`.
- **Git:** one commit per task, and no push without Nery's authorization.

## Review Focus

1. A `SKILL.md` that isn't UTF-8 (UTF-16 with a BOM, Latin-1) gives `frontmatter.yaml` the rule `not-utf8` and no traceback (Task 4).
2. Recursive or deeply nested YAML (`a: &x [*x]`, 5,000 nested `[`) terminates within 5 s with `too-deep` or `unsupported`, and no other script hangs (Task 3).
3. Characters outside the Basic Multilingual Plane (emoji) in `description` or `when_to_use`: lengths are in code points, with `utf16_length` in `data` (Task 6).
4. A missing path or a directory exits 2. A symlinked folder takes its name from the path as given, with the resolved name in `data` (Task 1).
5. CRLF, a BOM and a trailing space on the markers give the same reader result as clean LF, and the commands show them visibly (Tasks 2 and 9).

---

### Task 0: Pin the open behaviors before code

No code ships from this task. Its results fill the Appendix, and the later tests encode them.

- [ ] **Step 1:** Run `claude plugin validate --json` (2.1.326) on throwaway plugins with these cases:
  - a BOM;
  - CRLF line endings;
  - `--- ` with a trailing space as the opening and as the closing marker;
  - a U+2028 character in a value;
  - a duplicate key, to see which value Claude Code keeps.

  Record each outcome.
- [ ] **Step 2:** With ruamel.yaml 0.19.1 (`uv run`), confirm that `a: foo:` and `a: x: y` fail to parse. Then settle each of these and record its source:
  - the separator Claude Code puts between `description` and `when_to_use` (docs: "Appended to `description`");
  - whether `Bash` and `Bash(*)` both approve every command (`/en/permissions`);
  - whether plugin skills that reach claude.ai hit the six-field upload rule (support.claude.com). The spec says they do; this is unverified.
- [ ] **Step 3:** If any result contradicts the spec, stop and report it to Nery with both texts quoted.
- [ ] **Step 4:** Commit the Appendix: `git commit -m "Record the loader behaviors the frontmatter checks rely on"`.

### Task 1: Shared foundation

**Files:**
- Create in `.../auditing-skills/scripts/common/`: `__init__.py`, `report.py`, `context.py`, `cli.py`, `skill_file.py`, `text.py`, `fields.py`
- Test: `plugins/skills-engineering/tests/frontmatter_helpers.py`, `tests/test_frontmatter_foundation.py`

**Interfaces (produced):**
- `type Surface = Literal["claude-code","open-spec","upload"]`. `type Basis = Literal["official","convention","inference"]`.
- `report.Finding(rule: str, message: str, line: int | None, column: int | None, evidence: str | None, basis: Basis, surfaces: tuple[Surface, ...], condition: str | None = None)`, a frozen, slotted dataclass.
- `report.CheckResult(check: str, status: Literal["ran","not_run"], reason: str | None, skill_md: Path, findings: list[Finding], data: dict[str, object])`.
- `report.emit(result: CheckResult) -> None`: prints the JSON in the key order above and truncates `evidence` to 120 characters plus `…`.
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
  - `SHELLS`: `bash`, `powershell`.
  - `MODEL_VALUES`: `default`, `best`, `fable`, `sonnet`, `opus`, `haiku`, `sonnet[1m]`, `opus[1m]`, `opusplan`, `inherit`.
  - `TEXT_FIELDS`: `name`, `description`, `when_to_use`, `argument-hint`, `model`, `effort`, `context`, `agent`, `shell`, `license`, `compatibility`.
  - `SOURCES`: a dict of rule area to doc URL.
- `frontmatter_helpers.run_check(script: str, skill_md: str | bytes, *, folder: str = "demo-skill", args: tuple[str, ...] = (), python: str = sys.executable) -> tuple[int, dict[str, object]]`. It writes `<tmp>/<folder>/SKILL.md`, runs the script and parses stdout. `rules(result) -> list[tuple[str, int | None]]`.

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
  | `test_emit_order_and_truncation` | a 200-character evidence | keys in order; evidence is 121 characters ending `…` |

  Add the CLI cases, run through a throwaway check registered in the test:
  - a missing path exits 2 with empty stdout;
  - a directory exits 2;
  - a symlink `link -> real` gives `folder_name == "link"` and `resolved_folder_name == "real"`;
  - `/usr/bin/python3.11` gets exit 2 and the floor message, with the test skipped when that interpreter is absent.
- [ ] **Step 2:** Run `python3 -m unittest discover -s plugins/skills-engineering/tests -p 'test_frontmatter_*.py' -v`. Expected: the tests fail with a missing module.
- [ ] **Step 3:** Implement the interfaces.
- [ ] **Step 4:** Run the tests on `/usr/bin/python3.12`, `/usr/bin/python3.13` and `python3` (3.15). Expected: all pass. Then run ruff and basedpyright on the new files: 0 findings.
- [ ] **Step 5:** Commit: `git commit -m "Add the shared foundation for the frontmatter checks"`.

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
- `ReadError(rule: Literal["syntax-error","duplicate-key","tab-indent","too-deep","unsupported"], message: str, line: int, column: int)`, an exception carrying file positions.
- `read(yaml_text: str, first_line: int) -> Node`: raises `ReadError`.

What this task supports:
- block mappings with plain or quoted single-line keys;
- block sequences, including `- ` entries inside a mapping value;
- plain scalars over several lines (folded with one space, a blank line giving `\n`);
- single-quoted (`''` escape) and double-quoted scalars (YAML escapes `\\ \" \n \t \uXXXX \UXXXXXXXX`, line folding), over several lines;
- `#` comments, both full-line and after a space.

What it rejects:
- `syntax-error`:
  - `: ` or a trailing `:` inside a plain value in block context ("mapping values are not allowed here");
  - an unclosed quote;
  - a key indented under a scalar;
  - a plain value starting with `,`, `%`, `@` or `` ` ``.
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
    - `d: Use when: x` gives `syntax-error` at line 2;
    - `d: "abc` gives `syntax-error`;
    - `m:\n\tk: v` gives `tab-indent` at line 3;
    - `name: a\n  b: c` gives `syntax-error` at line 3;
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
- An unclosed flow collection raises `syntax-error` at the line of its opening bracket.
- An alias to an unknown anchor raises `syntax-error`.
- An alias is never expanded, so recursion is impossible.
- `yaml_types.yaml11_tag(node: Node) -> Literal["str","bool","int","float","null","timestamp"]`: YAML 1.1 implicit resolution for plain scalars, using the regular expressions of the YAML 1.1 type repository (`bool`, `int`, `float`, `null`, `timestamp`). Quoted and block scalars are `str`.
- `yaml_types.yaml12_tag(node: Node)`, the same for the YAML 1.2 core schema.
- `yaml_types.to_python(node: Node, schema: Literal["1.1","1.2"]) -> object`.

- [ ] **Step 1: Write the failing tests.**
  - `d: |\n  a\n  b\n` gives `"a\nb\n"`, and `d: >-\n  a\n  b` gives `"a b"`.
  - `t: [Read, "Bash(git *)"]` gives a seq of 2 with `style == "flow"`, and `m: {a: 1}` gives a map.
  - `t: [Read` gives `syntax-error` at line 2.
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

`yaml_syntax.py`:
- Reports the block problems `not-utf8`, `no-opening-marker`, `unclosed` and `empty` as their own rules.
- Reports the reader error as its rule.
- Adds `not-a-mapping` when the root is not a map.
- Basis is `official` for `syntax-error` and `not-a-mapping` (skills docs: "the skill still loads with no fields set") and `inference` for `duplicate-key` and `tab-indent`.
- Surfaces are `("open-spec","upload")` plus `claude-code`, with the condition "if Claude Code's own parser also rejects it". Task 9's commands and `claude plugin validate` show the Claude Code side.
- `data` = `{had_bom, had_crlf, close_line, keys}`.

`plain_values.py`, surfaces `("upload","open-spec")`, basis `inference`, with these rules:
- `comment-truncates`: a plain value followed by ` #` on its line;
- `leading-indicator`: a plain value starting with `-`, `?` or `:`;
- `reads-as-collection`: a `TEXT_FIELDS` value that is a seq or map;
- `anchor-alias-tag`: a `TEXT_FIELDS` value with an anchor, an alias or a tag;
- `reads-as-boolean` and `reads-as-null`: a plain `TEXT_FIELDS` value or a `metadata` value, at any depth, whose lowercase text is in the spec's list.
- `data.colon_cases = "reported by frontmatter.yaml"`, as Task 0 confirmed.

- [ ] **Step 1: Write the failing tests.**
  - For `yaml_syntax.py`:
    - the six spec failures give their rules at their lines, as in Task 2;
    - `- a` gives `not-a-mapping`;
    - Latin-1 bytes give `not-utf8`;
    - `\n---` gives `no-opening-marker`;
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
- [ ] **Step 4:** Run the tests on 3.12, 3.13 and 3.15, plus ruff and basedpyright. Expected: pass and 0 findings.
- [ ] **Step 5:** Commit: `git commit -m "Add the strict YAML and plain-value frontmatter checks"`.

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
- [ ] **Step 4:** Run the tests on 3.12, 3.13 and 3.15, plus ruff and basedpyright. Expected: pass and 0 findings.
- [ ] **Step 5:** Commit: `git commit -m "Add the name and plain-name frontmatter checks"`.

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
- [ ] **Step 4:** Run the tests on 3.12, 3.13 and 3.15, plus ruff and basedpyright. Expected: pass and 0 findings.
- [ ] **Step 5:** Commit: `git commit -m "Add the description, listing-cap and compatibility frontmatter checks"`.

### Task 7: FM-10 (`frontmatter.metadata`) and FM-12 (`frontmatter.field-values`)

**Files:** Create `frontmatter/metadata.py` and `field_values.py`. Tests: `tests/test_frontmatter_fields.py`.

`metadata.py`, under YAML 1.1 resolution, which is what upload uses:
- `not-a-map`: surfaces `("claude-code","open-spec","upload")`.
- `non-string-key` and `non-string-value`: surfaces `("open-spec","upload")`.
- `reused-field-name`: a key in `CLAUDE_CODE_FIELDS`, surfaces `("claude-code",)`, basis official.

`field_values.py`:
- `boolean-form`, for `BOOLEAN_FIELDS`:
  - a plain value outside `BOOLEAN_FORMS` gives the finding with basis official;
  - a quoted value gives the finding with basis inference and the message "quoted: unverified whether Claude Code reads it as a boolean".
- `context-value`: anything other than `fork`.
- `effort-value`: a value outside `EFFORT_LEVELS`.
- `shell-value`: a value outside `SHELLS`.
- `string-or-list`, for `allowed-tools`, `disallowed-tools`, `paths` and `arguments`: a string scalar or a seq of string scalars, under YAML 1.1.
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
    - `allowed-tools: 42` gives `string-or-list`;
    - `shell: fish` gives `shell-value`;
    - `model: gpt-4` gives `model-value`;
    - `model: opus[1m]` gives `[]`;
    - `model: claude-opus-5-5` gives `[]`;
    - `background: "true"` gives `boolean-form` with basis inference;
    - `paths: [a, 1]` gives `string-or-list`;
    - `user-invocable: NO` gives `[]`;
    - `effort:` gives `empty-value`.
- [ ] **Step 2:** Run the tests. Expected: they fail.
- [ ] **Step 3:** Implement the scripts and set the executable bit.
- [ ] **Step 4:** Run the tests on 3.12, 3.13 and 3.15, plus ruff and basedpyright. Expected: pass and 0 findings.
- [ ] **Step 5:** Commit: `git commit -m "Add the metadata and field-value frontmatter checks"`.

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
- [ ] **Step 4:** Run the tests on 3.12, 3.13 and 3.15, plus ruff and basedpyright. Expected: pass and 0 findings.
- [ ] **Step 5:** Commit: `git commit -m "Add the field-combination and allowed-tools frontmatter checks"`.

### Task 9: Commands for FM-1, FM-6 and FM-11 in step 3 of `SKILL.md`

**Files:**
- Modify: `plugins/skills-engineering/skills/auditing-skills/SKILL.md` (step 3, and the Receives entries of `frontmatter-description` and `runtime-contract`)
- Modify: `.claude/maintainer/skills-engineering/mechanical-check-sources.md` (the rule's sync point)
- Test: `tests/test_frontmatter_commands.py`

The exact commands, POSIX only, with `<SKILL.md>` quoted:

- **FM-1, block placement:**
  - `head -c 3 "<SKILL.md>" | od -An -tx1`: `ef bb bf` is a BOM;
  - `grep -n -m 2 -E '^---[[:space:]]*$' "<SKILL.md>"`: the marker lines. The first must be `1:`;
  - `grep -c "$(printf '\r')" "<SKILL.md>"`: the number of CRLF lines.
- **FM-11, top-level keys with their lines:**

  ```sh
  awk 'NR==1 && !/---[[:space:]]*$/{exit} NR>1 && /^---[[:space:]]*$/{exit} NR>1 && /^[^[:space:]#]/{print NR": "substr($(0),1,80)}' "<SKILL.md>"
  ```

- **FM-6, the folder name:** `basename "$(dirname "<SKILL.md>")"`.
  - The reviewer compares it, and the `name` from `frontmatter.name`, with the reserved words, `synced` and `anthropic-skills`, using the skill's location from step 2.

- [ ] **Step 1: Write the failing tests.** Each runs the command with `sh -c` on fixtures and asserts its stdout:
  - a BOM file gives `ef bb bf`, and a plain file gives `2d 2d 2d`;
  - `test_valid` gives `1:---` and `4:---`;
  - a CRLF file gives a count equal to its number of lines;
  - FM-11 on the BOM + CRLF fixture lists the keys with their file lines;
  - a file without frontmatter prints nothing;
  - a folder `Synced` prints `Synced`.

  One test asserts each command string appears verbatim in `SKILL.md`. Another asserts that no `$` followed by a digit appears in it.
- [ ] **Step 2:** Run the tests. Expected: they fail.
- [ ] **Step 3:** Add the commands to step 3 and the Receives entries, keeping both in sync per the rule, then run `npm run lint:frontmatter -- <SKILL.md>`.
- [ ] **Step 4:** Run the tests and `claude plugin validate --strict plugins/skills-engineering`. Expected: pass and `valid`. Report that the commands were tested on GNU tools only, with macOS (BSD) and Git Bash not run.
- [ ] **Step 5:** Commit: `git commit -m "Add the block, folder and key commands to the audit's mechanical step"`.

### Task 10: Release verification

- [ ] **Step 1:** Run `npm run test:plugins`, the full suite on `/usr/bin/python3.12` and `/usr/bin/python3.13`, and the suite under `uv run` (3.15 with ruamel). Expected: all pass. Show the raw output.
- [ ] **Step 2: Corpus run.** Run the 11 scripts and 3 commands on every `SKILL.md` in `plugins/*/skills/*/` and in the synced skills under `/root/.claude/`. Expected:
  - exit 0 everywhere;
  - no traceback;
  - under 1 s per file.

  Show a table of findings per rule. Confirm by hand every finding on `auditing-skills` itself.
- [ ] **Step 3: Differential check.** A scratchpad script compares the reader with ruamel.yaml on the corpus and lists each divergence with the YAML 1.1 versus 1.2 rule that explains it. A divergence no rule explains is a bug: go back to the owning task.
- [ ] **Step 4: Claude Code cross-check.** Run `claude plugin validate --json` on every spec case marked tested in Coverage, and confirm the scripts catch what validate misses and agree where it reports.
- [ ] **Step 5:** Run ruff check, ruff format check and `basedpyright --outputjson` over `plugins/skills-engineering`, plus `claude plugin validate --strict`. Expected: 0 findings and `valid`.
- [ ] **Step 6: Independent review.** One fresh reviewer on the most capable model reviews the whole branch against this plan and the spec. Fix every confirmed finding and rerun Steps 1 to 5.
- [ ] **Step 7:** Commit fixes and report to Nery with the raw outputs. No push.

## Out of scope (next plan)

- The entry script, the wiring of the eleven scripts into step 3 of `SKILL.md`, its `allowed-tools`, and the `python` fallback on Windows (Anthropic's `math-proof` pattern).
- The CHANGELOG entry.
- The other data domains.

## Appendix: Task 0 results

To be filled by Task 0.
