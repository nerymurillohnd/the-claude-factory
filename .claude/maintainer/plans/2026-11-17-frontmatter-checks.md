# Frontmatter mechanical checks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, test and harden the 14 frontmatter checks (spec FM-1 to FM-14) as standalone, read-only Python scripts under `skills/auditing-skills/scripts/frontmatter/`. Each one emits a JSON result the main session hands to the reviewers.

**Architecture:**
- One script per check, all sharing one `common/` package: reading the file, the YAML layer, the field tables, the result format and the CLI.
- The YAML layer composes the frontmatter with a vendored, unmodified PyYAML 6.0.3 (pure Python, SafeLoader, `compose` only, never `load`).
- On top of that layer sit the strict checks PyYAML lacks: duplicate keys, depth and recursion.
- Each script runs alone from its path. The future entry script will import the same `check()` functions; it is out of scope here.

**Tech Stack:** Python ≥ 3.12, standard library, vendored PyYAML 6.0.3 (MIT), `unittest`, ruff, basedpyright.

**Spec:** `.claude/maintainer/specs/2026-11-17-frontmatter-checks.md`, Nery's FM-1 to FM-14 check cards, copied verbatim. The folder architecture comes from the thread proposal of the same day.

## Global Constraints

- **Runtime:** Python 3.12 or later, the marketplace's floor for plugin Python (`ruff.toml` `per-file-target-version`).
  - Each script checks the version before any other import. On an older Python it prints `<script>: needs Python 3.12 or later; this is X.Y.Z.` to stderr and exits 2.
  - It uses only the standard library and `scripts/vendor/yaml`.
- **Read-only:**
  - No network, no subprocess, and no writes outside the test temp dirs.
  - The only thing read is the `SKILL.md` given as the argument, plus its folder name. The scripts never read settings, MCP or credential files.
- **CLI:** `<check>.py <path to SKILL.md> [--origin plugin|personal|project|managed|account|unknown] [check options]`.
  - `--origin` defaults to `unknown`.
  - Exit 0 when a JSON result was printed, even one with findings or `not_run`.
  - Exit 2 on a usage error, a missing path, a directory path or an unreadable file. In that case stderr gets one line and stdout stays empty.
  - Exit 1 never happens by design: an uncaught exception is a bug.
- **Output:** exactly one JSON object on stdout, UTF-8, `ensure_ascii=False`, keys in this order:
  - `check`, `status` (`ran` | `not_run`), `reason` (string or null), `skill_md` (absolute path), `findings`, `data`.
  - Each finding holds `rule`, `message`, `line`, `column` (1-based file positions or null), `evidence` (at most 120 characters, or null), `basis` (`official` | `convention` | `inference`), `surfaces` (a subset of `claude-code`, `open-spec`, `upload`) and `condition` (string or null).
  - `upload` means claude.ai skill uploads, the Skills API and `package_skill.py`, which the docs group as one distribution path.
- **Scope of judgment:** findings state facts and surfaces, never a severity: severity belongs to the reviewers.
- **Prerequisites:** a check whose prerequisite failed returns `status: not_run` with `reason` naming the prerequisite's check id, such as `"frontmatter.yaml failed"`.
- **Identifiers:** check ids are descriptive (`frontmatter.<slug>`).
  - The spec ids FM-1 to FM-14 appear only in this plan, never in plugin files, because the plugin must not name maintainer validator rule ids.
- **Field tables:** pinned to the Claude Code 2.1.326 docs (`/en/skills`, Frontmatter reference, read 2026-11-17), to `agentskills.io/specification`, and to anthropics/skills `quick_validate.py`, which uses `yaml.safe_load` and rejects `<` and `>` in the description. All of them live in `common/fields.py` only.
- **Lint and portability:**
  - `ruff check` and `ruff format` clean with no suppressions, `basedpyright` 0 errors, a shebang plus the executable bit on every script, and an `__init__.py` in `common/`.
  - Files are read as bytes and decoded explicitly. No POSIX-only APIs (Windows through Git Bash).
- **Tests:** in `plugins/skills-engineering/tests/test_frontmatter_*.py`, stdlib `unittest`, picked up by `npm run test:plugins`.
- **Git:** one commit per task, and no push without Nery's authorization.

## Review Focus

1. A `SKILL.md` that isn't UTF-8, such as UTF-16 with a BOM or Latin-1 bytes, gives a `frontmatter.block` finding `not-utf8`, never a traceback (Task 1).
2. Recursive or deeply nested YAML (`a: &x [*x]`, 5,000 nested `[`) terminates: `frontmatter.yaml` reports `too-deep` and no other script hangs (Task 3).
3. Characters outside the Basic Multilingual Plane (emoji) in `description` or `when_to_use`: every length is in code points, with UTF-16 units alongside in `data` (Tasks 5 and 6).
4. A missing path or a directory exits 2. A symlinked skill folder takes its folder name from the path as given, with the resolved name in `data`. A `SKILL.md` at a plugin root is checked like any other (Task 1).
5. CRLF, BOM and a trailing space on the markers give the same result as clean LF, as Task 0 pins (Task 1).

---

### Task 0: Pin the open behaviors before writing code

No code ships from this task. Its results go into the Appendix of this plan, and the later tests encode them.

- [ ] **Step 1:** Run `claude plugin validate --json` (2.1.326) on throwaway plugins whose `SKILL.md` has each of these:
  - a BOM;
  - CRLF line endings;
  - `--- ` with a trailing space, as the opening and as the closing marker;
  - a U+2028 character in a value.

  Record "frontmatter found: yes/no" for each.
- [ ] **Step 2:** Settle the remaining points with ruamel.yaml 0.19.1 (`uv run`) and with the docs. Record each answer with its source:
  - whether `a: foo:` and `a: x: y` fail to parse, so FM-3's colon cases surface through `frontmatter.yaml`;
  - the separator Claude Code puts between `description` and `when_to_use` (docs: "Appended to `description`");
  - whether `Bash` and `Bash(*)` both approve every command (`/en/permissions`);
  - whether plugin skills on claude.ai hit the six-field upload rule (support.claude.com). The spec says they do; this is unverified.
- [ ] **Step 3:** If any result contradicts the spec, stop and report it to Nery with both texts quoted before Task 1 starts.
- [ ] **Step 4:** Commit the updated Appendix: `git commit -m "Record the loader behaviors the frontmatter checks rely on"`.

### Task 1: Foundation and FM-1, the block check (`frontmatter.block`)

**Files:**
- Create: `plugins/skills-engineering/skills/auditing-skills/scripts/common/__init__.py`, `report.py`, `context.py`, `cli.py`, `skill_file.py`, `text.py`, `fields.py`
- Create: `.../scripts/frontmatter/block.py` (executable)
- Create: `plugins/skills-engineering/tests/frontmatter_helpers.py`, `tests/test_frontmatter_block.py`, `tests/test_frontmatter_cli.py`

**Interfaces (produced):**
- `report.Finding(rule: str, message: str, line: int | None, column: int | None, evidence: str | None, basis: Basis, surfaces: tuple[Surface, ...], condition: str | None = None)`
- `report.CheckResult(check: str, status: Literal["ran","not_run"], reason: str | None, skill_md: Path, findings: list[Finding], data: dict[str, object])`
- `report.emit(result: CheckResult) -> None` prints the JSON in the key order above, with `evidence` truncated to 120 characters plus `…`.
- `context.Context(skill_md: Path, skill_dir: Path, folder_name: str, resolved_folder_name: str, origin: Origin, options: dict[str, object])`. `ORIGINS: tuple[str, ...]`.
- `cli.run(check_id: str, check: Callable[[Context], CheckResult], extra: Callable[[argparse.ArgumentParser], None] | None = None) -> NoReturn`: validates the path (exit 2 cases above), builds `Context`, calls `check`, emits, exits 0.
- `skill_file.read(path: Path) -> SkillFile` with `text: str | None` (decoded, BOM stripped, CRLF and CR normalized to LF), `decode_error: str | None`, `had_bom: bool`, `had_crlf: bool`, `block: Block | None`, `problem: Literal["not-utf8","no-opening-marker","unclosed","empty"] | None`.
  - `Block(open_line=1, close_line: int, yaml_text: str, first_yaml_line=2)`.
  - The closing marker is the first later line equal to `---`, with trailing-whitespace handling as Task 0 decided.
- `text.utf16_len(s: str) -> int`. `text.snippet(s: str, index: int, width: int = 40) -> str` returns `before|after` around `index`.
- `fields.CLAUDE_CODE_FIELDS`: the 20 names in docs table order (`name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `background`, `hooks`, `paths`, `shell`, `metadata`, `license`, `compatibility`).
  - `SPEC_FIELDS`: (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`).
  - `BOOLEAN_FIELDS`: (`disable-model-invocation`, `user-invocable`, `background`).
  - `BOOLEAN_FORMS`: {`true`, `false`, `yes`, `no`, `on`, `off`, `1`, `0`}, matched case-insensitively.
  - `EFFORT_LEVELS`: (`low`, `medium`, `high`, `xhigh`, `max`).
  - `SHELLS`: (`bash`, `powershell`).
  - `MODEL_VALUES`: (`default`, `best`, `fable`, `sonnet`, `opus`, `haiku`, `sonnet[1m]`, `opus[1m]`, `opusplan`, `inherit`).
  - `TEXT_FIELDS`: every field whose value is text: `name`, `description`, `when_to_use`, `argument-hint`, `model`, `effort`, `context`, `agent`, `shell`, `license`, `compatibility`.
- `frontmatter_helpers.run_check(script: str, skill_md: str | bytes, *, folder: str = "demo-skill", origin: str = "unknown", args: tuple[str, ...] = ()) -> tuple[int, dict[str, object]]`.
  - It writes the file into a fresh temp dir `<tmp>/<folder>/SKILL.md`, runs it with `sys.executable`, parses stdout and returns the exit code and the JSON.
  - `rules(result) -> list[tuple[str, int | None]]` returns `(rule, line)` pairs.

`block.py` reports `skill_file.problem` as a finding. Its `not-a-mapping` rule (a block that is a list or a scalar) needs the Task 2 layer, so Task 2 adds that rule and its tests to `block.py`.

- [ ] **Step 1: Write the failing tests.** In `test_frontmatter_block.py`, each case asserts exit 0 and `rules(result)`:

  | test | SKILL.md | expected |
  | :-- | :-- | :-- |
  | `test_valid` | `---\nname: demo-skill\ndescription: x\n---\nbody` | `[]` and `data.close_line == 4` |
  | `test_blank_first_line` | `\n---\nname: a\n---\n` | `[("no-opening-marker", 1)]` |
  | `test_no_frontmatter` | `# Title\n` | `[("no-opening-marker", 1)]` |
  | `test_unclosed` | `---\nname: a\n` | `[("unclosed", 1)]` |
  | `test_empty_block` | `---\n---\n` | `[("empty", 1)]` |
  | `test_bom_crlf_same_as_lf` | the `test_valid` bytes with a UTF-8 BOM and CRLF | `[]` and `data.had_bom` and `data.had_crlf` are true |
  | `test_not_utf8` | `b"---\nname: \xe9\n---\n"` | `[("not-utf8", None)]` |
  | `test_utf16` | `test_valid` encoded as UTF-16 with a BOM | `[("not-utf8", None)]` |
  | `test_marker_trailing_space` | per Task 0 | per Task 0 |

  In `test_frontmatter_cli.py`:
  - a missing path exits 2 with empty stdout;
  - a directory path exits 2;
  - `--origin bogus` exits 2;
  - a symlinked folder `link -> real` gives `data.folder_name == "link"` and `data.resolved_folder_name == "real"`;
  - with Python patched to look older (subprocess, `-c` wrapper setting `sys.version_info`), the script exits 2 with the documented message.
- [ ] **Step 2:** Run `python3 -m unittest discover -s plugins/skills-engineering/tests -p 'test_frontmatter_*.py' -v`. Expected: the tests fail because the module isn't found.
- [ ] **Step 3:** Implement the interfaces above and `block.py` (`check_id = "frontmatter.block"`).
  - The `not-utf8` evidence is the decoder's message.
  - Findings use basis `official`, surfaces `("claude-code", "open-spec", "upload")`.
  - Then run `chmod +x frontmatter/block.py`.
- [ ] **Step 4:** Run the same command. Expected: every test passes. Then run `ruff check`, `ruff format --check` and `basedpyright` on the new files: 0 findings.
- [ ] **Step 5:** Commit: `git commit -m "Add the shared check foundation and the frontmatter block check"`.

### Task 2: YAML layer on vendored PyYAML

**Files:**
- Create: `.../scripts/vendor/__init__.py`, `.../scripts/vendor/yaml/` (PyYAML 6.0.3 `lib/yaml/*.py`, unmodified, without `cyaml.py`), `.../scripts/vendor/yaml/LICENSE` (PyYAML's own)
- Create: `.../scripts/common/frontmatter.py`
- Modify: `ruff.toml` (`extend-exclude` the vendor folder), `pyrightconfig.json` (`exclude` it)
- Test: `tests/test_frontmatter_layer.py`

**Interfaces (produced):**
- `frontmatter.load(ctx: Context) -> Loaded`, with these fields:
  - `file: SkillFile`;
  - `root: MappingNode | None`;
  - `problems: list[YamlProblem]`;
  - `fields: dict[str, Field]`, holding the top-level keys whose key is a string, first occurrence wins.
- `YamlProblem(rule: Literal["syntax-error","duplicate-key","too-deep","not-a-mapping"], message: str, line: int, column: int)`, with file positions.
- `Field(key: str, key_line: int, node: Node, style: str | None, anchor: str | None, tag: str | None, is_alias: bool, start_line: int, end_line: int)`.
  - `style`, `anchor`, `tag` and `is_alias` come from `yaml.parse` events for that top-level value. PyYAML nodes don't keep anchors.
- `frontmatter.resolved(node: Node) -> object`: the value under YAML 1.1 safe resolution, which is what `package_skill.py` sees.
  - Built with `SafeConstructor` on an already composed node.
  - Guarded against recursion: a node seen twice on the current path becomes the string `"<recursive>"`.
- `frontmatter.yaml11_tag(raw: str) -> str`: PyYAML `Resolver().resolve(ScalarNode, raw, (True, False))`.
- `frontmatter.iter_scalars(node: Node) -> Iterator[tuple[tuple[str, ...], ScalarNode]]`: every value scalar with its key path. It visits each node id once and never recurses deeper than 100 levels.

Algorithm decisions:
- Compose with `yaml.compose(yaml_text, Loader=yaml.SafeLoader)`, and map `MarkedYAMLError.problem_mark` to `line = first_yaml_line + mark.line`, `column = mark.column + 1`.
- Catch `RecursionError`, which becomes `too-deep` at the block's first line.
- Find duplicate keys by walking every `MappingNode` and comparing each key's `resolved` value. The second occurrence is the problem.
- A root that is not a `MappingNode` gives `not-a-mapping`.
- Never call `yaml.load`, `full_load` or `unsafe_load`.

- [ ] **Step 1: Write the failing tests.**
  - `test_marks_are_file_lines`: `---\nname: a\ndescription: "x\n---` gives a `syntax-error` with `line >= 3`.
  - `test_duplicate_key`: `name: a\nname: b` gives `("duplicate-key", 3)`.
  - `test_not_a_mapping_list` (`- a`) and `test_not_a_mapping_scalar` (`hello`) give `not-a-mapping`. Add the same two cases to `test_frontmatter_block.py`.
  - `test_events`: `name: &n demo` gives `fields["name"].anchor == "n"`, and `argument-hint: [x]` gives `fields["argument-hint"].node` as a `SequenceNode`.
  - `test_yaml11`: `yaml11_tag("on")` is `tag:yaml.org,2002:bool` and `yaml11_tag("2026-11-17")` is `...timestamp`.
  - `test_recursive_alias_terminates`: `a: &x [*x]` completes in under 2 s.
  - `test_no_unsafe_construct`: `a: !!python/object/apply:os.system ["echo"]` is reported as `syntax-error` (a SafeLoader constructor error). Nothing runs.
- [ ] **Step 2:** Run the Task 1 test command. Expected: these tests fail.
- [ ] **Step 3:** Vendor PyYAML from the 6.0.3 sdist after checking its sha256 against PyPI. Record both in the commit message. Then implement `frontmatter.py`.
- [ ] **Step 4:** Run the tests, `ruff` and `basedpyright`. Expected: pass and 0 findings.
- [ ] **Step 5:** Commit: `git commit -m "Vendor PyYAML 6.0.3 and add the strict frontmatter layer"`.

### Task 3: FM-2 strict YAML (`frontmatter.yaml`) and FM-3 plain values (`frontmatter.plain-values`)

**Files:** Create `frontmatter/yaml_syntax.py` and `frontmatter/plain_values.py`. Tests: `tests/test_frontmatter_yaml.py` and `tests/test_frontmatter_plain_values.py`.

**Interfaces:** each consumes `frontmatter.load`.

`yaml_syntax.py`:
- Emits each `YamlProblem` except `not-a-mapping`, which belongs to the block check.
- Basis is `official` for `syntax-error` and `too-deep` (the skills docs: the skill "still loads with no fields set"), and `inference` for `duplicate-key`.
- Surfaces are `("open-spec","upload")`, with the condition `"Claude Code also drops every field if its own parser rejects this; run claude plugin validate"`.

`plain_values.py`:
- `reads-as-collection`: a field in `TEXT_FIELDS` whose node is a sequence or mapping.
- `anchor-alias-tag`: a field in `TEXT_FIELDS` that carries an anchor, an alias or a tag.
- `comment-truncates`: a plain scalar whose source line continues with a `#` comment after the value ends.
- `leading-indicator`: a plain value that starts with `-`, `?` or `:`.
- `reads-as-boolean` and `reads-as-null`: a plain value in `TEXT_FIELDS`, or a `metadata` value, whose lowercase text is in {`yes`, `no`, `on`, `off`, `true`, `false`} or {`null`, `~`, empty}.
- Basis is `inference` and surfaces are `("upload","open-spec")`.
- `data.colon_cases` = `"reported by frontmatter.yaml: such values do not parse"`, as Task 0 confirmed.

- [ ] **Step 1: Write the failing tests.** All frontmatter starts at line 2.
  - For `yaml_syntax.py`:
    - `description: Use when: x` gives `("syntax-error", 2)`;
    - `allowed-tools: [Read` gives `syntax-error`;
    - `description: "abc` gives `syntax-error`;
    - `metadata:\n\tk: v` gives `("syntax-error", 3)`;
    - `name: a\n  b: c` gives `("syntax-error", 3)`;
    - `name: a\nname: b` gives `("duplicate-key", 3)`;
    - 5,000 nested `[` give `too-deep` within 5 s;
    - a valid block gives `[]`;
    - a block with no frontmatter gives `status == "not_run"`.
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
    - a syntax error gives `not_run` with `reason == "frontmatter.yaml failed"`.
- [ ] **Step 2:** Run the tests. Expected: they fail.
- [ ] **Step 3:** Implement both scripts and set their executable bit.
- [ ] **Step 4:** Run the tests, `ruff` and `basedpyright`. Expected: pass and 0 findings.
- [ ] **Step 5:** Commit: `git commit -m "Add the strict YAML and plain-value frontmatter checks"`.

### Task 4: Name family, FM-4 (`frontmatter.name`), FM-5 (`frontmatter.name-plain`) and FM-6 (`frontmatter.reserved`)

**Files:** Create `frontmatter/name_format.py`, `name_plain.py` and `reserved_names.py`. Tests: `tests/test_frontmatter_names.py`.

`name_format.py`:
- `missing`: basis official, surfaces `("open-spec","upload")`, with `data.name_source == "folder"`.
- `not-a-string`, decided by YAML 1.1 resolution.
- `length`: under 1 or over 64 characters.
- `charset`: anything outside `[a-z0-9-]`.
- `hyphen`: a leading, trailing or consecutive hyphen.
- `folder-mismatch`: compared against `ctx.folder_name`.
  - All of these use surfaces `("open-spec","upload")`.
- `refused-character`, surfaces `("claude-code",)`, for any of:
  - `<` or `>`;
  - `unicodedata.category` in `Cc`, `Cf`, `Co` or `Cn`;
  - a `Zs` character other than U+0020;
  - two spaces in a row;
  - a leading or trailing space.
- `data` holds `name`, `length`, `folder_name` and `matches_folder`.

`name_plain.py`:
- `quoted`, `block-scalar`, `multi-line`: basis `convention`, empty surfaces.
- `anchor-alias-tag`: basis `convention`, empty surfaces.
- `yaml11-type`: when `yaml11_tag` is int, float or timestamp. Booleans and null belong to `frontmatter.plain-values`. Basis `inference`, surfaces `("upload",)`.

`reserved_names.py`:
- It runs even without frontmatter; its name rule then uses the folder name.
- `reserved-word`: `anthropic` or `claude` in the name, case-insensitive, or in the folder name when `name` is absent. Surfaces `("upload",)`, basis official.
- `synced-folder`: the folder name, lowercased, is `synced` and the origin is in {personal, project, managed}. With origin `unknown` the same finding carries `condition: "in a personal, project or managed location"`. Surfaces `("claude-code",)`.
- `anthropic-skills-name`: the folder is `anthropic-skills` or starts with `anthropic-skills:` and the origin is not `plugin`. With `unknown` it carries the condition `"outside a plugin"`.
- Command files are out of scope, because these scripts audit `SKILL.md`.

- [ ] **Step 1: Write the failing tests.**
  - For `name_format.py`:
    - `name: demo-skill` in the folder `demo-skill` gives `[]`;
    - `name: Other_Name-claude-` in the folder `x` gives `charset`, `hyphen` and `folder-mismatch`;
    - a 65-character name gives `length`;
    - `a--b` gives `hyphen`;
    - `name: "a​b"` gives `refused-character` and `charset`;
    - `name: "<x>"` gives `refused-character`;
    - `name: "a b"` gives `refused-character`;
    - no name gives `missing`;
    - `name: 12` gives `not-a-string`;
    - a name with an emoji gives `data.length` in code points.
  - For `name_plain.py`:
    - `name: demo` gives `[]`;
    - `name: "demo"` gives `quoted`;
    - `name: |\n  demo` gives `block-scalar`;
    - `name: &a demo` gives `anchor-alias-tag`;
    - `name: 2026-11-17` gives `yaml11-type`;
    - `name: 1e3` gives `yaml11-type`;
    - `name: on` gives `[]` from this script.
  - For `reserved_names.py`:
    - `name: claude-helper` gives `reserved-word`;
    - the folder `Synced` with `--origin personal` gives `synced-folder`, and with `--origin plugin` gives `[]`;
    - the folder `anthropic-skills` with `--origin project` gives `anthropic-skills-name`, and with `--origin unknown` the same finding with its condition;
    - no frontmatter and the folder `claude-x` give `reserved-word` with `status == "ran"`.
- [ ] **Step 2:** Run the tests. Expected: they fail.
- [ ] **Step 3:** Implement the three scripts and set their executable bit.
- [ ] **Step 4:** Run the tests, `ruff` and `basedpyright`. Expected: pass and 0 findings.
- [ ] **Step 5:** Commit: `git commit -m "Add the name, plain-name and reserved-name frontmatter checks"`.

### Task 5: Text limits, FM-7 (`frontmatter.description`), FM-8 (`frontmatter.listing-cap`) and FM-9 (`frontmatter.compatibility`)

**Files:** Create `frontmatter/description.py`, `listing_cap.py` and `compatibility.py`. Tests: `tests/test_frontmatter_text_limits.py`.

Every length is `len()` in code points. `data` also carries `utf16_length`, because Claude Code's own counting unit is unverified.

`description.py`:
- `missing`: surfaces `("open-spec","upload")`, with `data.claude_code_fallback = "first non-empty body line"`.
- `not-a-string`, `empty` (whitespace only).
- `too-long`: over 1,024 characters, surfaces `("open-spec","upload")`.
- `angle-bracket`: any `<` or `>`. Surfaces `("upload","claude-code")`, with the message noting that upload rejects it and that Claude Code shows `&lt;`/`&gt;`, plus `data.xml_tags` from the regex `<[A-Za-z/!?][^<>]*>`.

`listing_cap.py`:
- Option `--cap N`, default 1536.
- Combined text = `description` + `when_to_use`, with the separator from Task 0.
- `over-cap` fires when the combined length is over the cap. `data` holds:
  - `description_length`, `when_to_use_length`, `combined_length`, `cap`;
  - `first_lost_field`, `first_lost_offset` (0-based in that field), `around_cut` (`text.snippet`);
  - `line`, filled only when that field is a single-line plain or single-quoted scalar.
- Surfaces `("claude-code",)`, basis official.
- `data.cap_setting = "skillListingMaxDescChars"`.

`compatibility.py`:
- Absent gives `[]`.
- `not-a-string`, `empty`, and `too-long` over 500 characters.
- Surfaces `("open-spec","upload")`.

- [ ] **Step 1: Write the failing tests.**
  - For `description.py`:
    - 1,024 characters give `[]`, 1,025 give `too-long`;
    - `<tag>` gives `angle-bracket` with `data.xml_tags == ["<tag>"]`;
    - `a > b` gives `angle-bracket`;
    - no description gives `missing`;
    - `description: 5` gives `not-a-string`;
    - `"  "` gives `empty`;
    - 1,000 emoji give `[]` with `data.utf16_length == 2000`.
  - For `listing_cap.py`:
    - a description of 1,000 and a `when_to_use` of 600 give `over-cap` with `first_lost_field == "when_to_use"` and `first_lost_offset == 536`;
    - a combined 1,536 gives `[]`;
    - `--cap 100` with a 150-character description gives `first_lost_offset == 100`;
    - a description alone of 1,600 gives `first_lost_field == "description"`, offset 1536.
  - For `compatibility.py`:
    - 500 characters give `[]`;
    - 501 give `too-long`;
    - `""` gives `empty`;
    - `compatibility: 7` gives `not-a-string`.
- [ ] **Step 2:** Run the tests. Expected: they fail.
- [ ] **Step 3:** Implement the three scripts and set their executable bit.
- [ ] **Step 4:** Run the tests, `ruff` and `basedpyright`. Expected: pass and 0 findings.
- [ ] **Step 5:** Commit: `git commit -m "Add the description, listing-cap and compatibility frontmatter checks"`.

### Task 6: Fields, FM-10 (`frontmatter.metadata`), FM-11 (`frontmatter.field-names`) and FM-12 (`frontmatter.field-values`)

**Files:** Create `frontmatter/metadata.py`, `field_names.py` and `field_values.py`. Tests: `tests/test_frontmatter_fields.py`.

`metadata.py`:
- Values use YAML 1.1 resolution, which is what upload sees.
- `not-a-map`: surfaces `("claude-code","open-spec","upload")`, with the message "Claude Code drops a value that isn't a map".
- `non-string-key` and `non-string-value`: surfaces `("open-spec","upload")`.
- `reused-field-name`: a key in `CLAUDE_CODE_FIELDS`, surfaces `("claude-code",)`, basis official.

`field_names.py`:
- `unknown-field`: a key not in `CLAUDE_CODE_FIELDS`. The message adds "did you mean `x`" from `difflib.get_close_matches(cutoff=0.75)`. Surfaces `("claude-code",)`.
- `outside-spec`: a key not in `SPEC_FIELDS`, surfaces `("upload",)`. The condition depends on `--origin`:
  - `account`: none;
  - `personal`: `"when the skill is enabled on claude.ai, which uploads it"`;
  - `plugin`: as Task 0 decided;
  - other origins: `"if the skill is uploaded, sent to the Skills API or packaged"`.
- `data.keys`: `[{key, line}]` in file order.

`field_values.py`:
- `boolean-form`, for the fields in `BOOLEAN_FIELDS`:
  - a plain value outside `BOOLEAN_FORMS` gives the finding with basis official;
  - a quoted value gives the finding with basis inference and the message "quoted: unverified whether Claude Code reads it as a boolean".
- `context-value`: anything other than `fork`.
- `effort-value`: a value outside `EFFORT_LEVELS`.
- `shell-value`: a value outside `SHELLS`.
- `string-or-list`, for `allowed-tools`, `disallowed-tools`, `paths` and `arguments`: the value is a string scalar, or a sequence of string scalars, under YAML 1.1 resolution.
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
    - `metadata:\n  version: "1.0"` gives `[]`;
    - `metadata:\n  version: 1.0` gives `non-string-value`.
  - For `field_names.py`:
    - `bogus-key: 1` gives `unknown-field`;
    - `disable_model_invocation: true` gives `unknown-field` with `disable-model-invocation` in the message;
    - `argument-hint: x` with `--origin account` gives `outside-spec` with `condition is None`, and with `--origin personal` the same finding with its condition;
    - the six spec fields alone give `[]`.
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
    - `effort:` (null) gives `empty-value`.
- [ ] **Step 2:** Run the tests. Expected: they fail.
- [ ] **Step 3:** Implement the three scripts and set their executable bit.
- [ ] **Step 4:** Run the tests, `ruff` and `basedpyright`. Expected: pass and 0 findings.
- [ ] **Step 5:** Commit: `git commit -m "Add the metadata, field-name and field-value frontmatter checks"`.

### Task 7: FM-13 (`frontmatter.field-combinations`) and FM-14 (`frontmatter.allowed-tools`)

**Files:** Create `frontmatter/field_combinations.py` and `allowed_tools.py`. Tests: `tests/test_frontmatter_combinations_tools.py`.

`field_combinations.py`:
- Booleans are read through `BOOLEAN_FORMS`.
- `uninvocable`: `disable-model-invocation` true together with `user-invocable` false. Basis inference.
- `paths-ignored`: `paths` set while `disable-model-invocation` is true. Basis inference.
- `fork-only-field`: `agent` or `background` set without `context: fork`. Basis official.
- Surfaces `("claude-code",)`.

`allowed_tools.py`:
- Entries are split on whitespace and commas outside parentheses. Each sequence item counts as one entry.
- `list-form`: the value is a sequence. Surfaces `("open-spec","upload")`, condition `"for a skill meant to work outside Claude Code"`, basis official (spec: "A space-separated string").
- `unscoped-bash`: an entry that, with spaces removed, is `Bash`, `Bash(*)` or `Bash(:*)`. Surfaces `("claude-code",)`, with the basis Task 0 decided.
- Unbalanced parentheses give `data.unparsed_entries` and no crash.
- `data.entries` lists the parsed entries.

- [ ] **Step 1: Write the failing tests.**
  - For `field_combinations.py`:
    - `disable-model-invocation: true` with `user-invocable: false` gives `uninvocable`;
    - `paths: "*.py"` with `disable-model-invocation: yes` gives `paths-ignored`;
    - `agent: Explore` without `context` gives `fork-only-field`;
    - `agent: Explore` with `context: fork` gives `[]`;
    - `background: false` with `context: fork` gives `[]`.
  - For `allowed_tools.py`:
    - `allowed-tools: [Read, Grep]` gives `list-form`;
    - `allowed-tools: Bash` gives `unscoped-bash`;
    - `allowed-tools: Read Bash(git diff:*)` gives `[]` with two entries;
    - `allowed-tools: "Read, Bash(*)"` gives `unscoped-bash`;
    - `allowed-tools: "Bash(git"` gives `[]` with `data.unparsed_entries == ["Bash(git"]`.
- [ ] **Step 2:** Run the tests. Expected: they fail.
- [ ] **Step 3:** Implement the two scripts and set their executable bit.
- [ ] **Step 4:** Run the tests, `ruff` and `basedpyright`. Expected: pass and 0 findings.
- [ ] **Step 5:** Commit: `git commit -m "Add the field-combination and allowed-tools frontmatter checks"`.

### Task 8: Release verification

- [ ] **Step 1:** Run `npm run test:plugins` and `uv run python -m unittest discover -s plugins/skills-engineering/tests -p 'test_frontmatter_*.py' -v`. Expected: every test passes on both interpreters. Show the raw output.
- [ ] **Step 2: Corpus run.** Run all 14 scripts on every `SKILL.md` in `plugins/*/skills/*/` and in the synced skills under `/root/.claude/`. Expected:
  - exit 0 on every file;
  - no traceback on stderr;
  - each file finishes in under 1 s.

  Show a table of findings per rule. Read every finding on this plugin's own `auditing-skills`, and confirm each one by hand against the file.
- [ ] **Step 3: Differential check.** A throwaway scratchpad script compares the composed values with ruamel.yaml 0.19.1 (YAML 1.2) on the same corpus, and lists each divergence with the YAML 1.1 rule that explains it. A divergence that no YAML 1.1 versus 1.2 rule explains is a bug: return to the task that owns it.
- [ ] **Step 4: Cross-check against Claude Code.** For every spec case marked "validate passed/rejected" in Coverage, run `claude plugin validate --json` on the fixture. Confirm the scripts find what validate misses and agree where validate reports.
- [ ] **Step 5:** Run `ruff check`, `ruff format --check` and `basedpyright --outputjson` over `plugins/skills-engineering`, and `claude plugin validate --strict plugins/skills-engineering`. Expected: 0 findings and `valid`.
- [ ] **Step 6: Independent review.** One fresh reviewer on the most capable model reviews the whole branch diff against this plan and the spec. Fix every confirmed finding and rerun Steps 1 to 5.
- [ ] **Step 7:** Commit any fixes, then report to Nery with the raw outputs. No push.

## Out of scope (next plans)

- The entry script `collect.py`, `routing.json`, the wiring in step 3 of `SKILL.md` and its `allowed-tools`.
- The rule's sync point for `common/fields.py` and the CHANGELOG entry.
- The other data domains (body, size, files, hooks, code, plugin, session, environment).

## Appendix: Task 0 results

To be filled by Task 0.
