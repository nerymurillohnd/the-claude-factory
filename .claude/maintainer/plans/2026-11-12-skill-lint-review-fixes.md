# Fix the 15 code-review findings in skill-lint (subagent-written modules)

## Context

`/code-review xhigh` on the modules subagents wrote (Tasks 1–4: `markdown.py`, `discover.py`,
`frontmatter.py`, `refs.py`, `script_refs.py`) reported 15 findings: 11 correctness, 1
conventions, 2 efficiency, 1 altitude. Four were confirmed by probes. The owner asked for a fix
plan, with python-lsp-intelligence mandatory. Outcome: every finding fixed (or ruled out with
evidence), each behind a failing test, then ReportFindings re-sent with outcomes.

The previous content of this file (the skill-lint design) is saved in
`.claude/maintainer/specs/skill-lint-spec.md`.

## Ground rules (from CLAUDE.md, `.claude/rules/skill-lint.md`, the skill)

- Code changes only with Edit/Write. Checks only through npm: `npm run test:scripts`,
  `npm run lint:python`, `npm run typecheck:python` (project rule wins over the skill's bare
  `ruff`/`basedpyright` commands; same tools, same config).
- python-lsp-intelligence: the impact-analysis checklist applies; the `LSP` tool is not
  available in cloud sessions, so it runs through the owner-approved equivalent (see Owner
  decisions).
- Failing test first for each correctness finding; confirm it fails before the fix.
- No `noqa`, `pyright: ignore` or new `cast()`.
- `markdown.py` (252 lines) must be split before it grows (rule: ~250); update
  `.claude/rules/skill-lint.md` in the same commit.
- Spec changes go into `skill-lint-spec.md` in the same commit as the rule change.
- Commit by topic; no push without authorization.

## Owner decisions (2026-11-12)

- **LSP:** the owner chose to restart the session so the basedpyright LSP loads. After the
  worker restart the `LSP` tool is still absent, and the official docs explain why
  (code.claude.com/docs/en/tools-reference#lsp-tool-behavior, read 2026-11-12): "In cloud
  sessions, Claude Code doesn't start plugin language servers, so the LSP tool stays inactive
  there." A restart cannot fix it in this environment. **Owner decision:** use the cloud
  equivalent. Before each signature change or deletion, Grep every caller and blind spot (spec,
  plan, rule file, tests), read each calling file, and after the change run
  `npm run typecheck:python` (basedpyright over all of `scripts/`, so every caller is
  re-checked). The final report states that the LSP tool was unavailable and this was used
  instead.
- **Vendored folders:** prune `node_modules/` and `.venv/` (and `.git/`) from the file
  listing, and add them to the CO-12 exemptions in the spec.
- **HTML comments:** no links, headings, anchors or fences come from comment content; the
  text stays in prose, so CO-11 still checks it.

## Callers found (Grep; re-checked by reading each caller before its change)

- `parse_markdown`: discover.py:126, refs.py:170, rules_content_files.py:62,
  rules_portability.py:61, rules_scripts.py:77, rules_capabilities.py:117, test_markdown.py.
- `resolve` (module function): rules_content_files.py:90, rules_scripts.py:87,146, test_refs.py.
- `reference_graph`: rules_content_files.py:127, test_refs.py. `imported_or_sourced`:
  rules_scripts.py:91, test_refs.py.
- `is_shell`: refs.py:151, commands.py:162. `sourced_paths`: refs.py:152.
- `git_modes` / `ModeReader`: discover.py default, test_discover.py, test_rules_scripts.py,
  helpers.load.

## Fixes, grouped into commits

### Commit 1 — Markdown parser (findings 1, 2, 3, 7) + split

Split first, no behavior change: `markdown_model.py` (dataclasses, `github_slug`, `_plain`,
`_target`, `_Builder`) and `markdown.py` (line scanner, `parse_markdown`). Callers that import
types (`discover.py` MarkdownDoc, `rules_capabilities.py` BangCommand) move to `markdown_model`.

1. **HTML comments (markdown.py:154).** Track `<!-- … -->` across lines outside fences and
   inline code. Comment content yields no links, headings, anchors or fences; it stays in
   `prose` (Claude reads the raw file, so CO-11 still sees it).
   Tests: `<!-- [old](gone.md) -->` → no link; multi-line comment hiding `# Title` and a fence;
   `` `<!--` `` in inline code does not open a comment.
2. **Schemes (markdown.py:24).** Skip any RFC 3986 scheme of 2+ chars
   (`^[A-Za-z][A-Za-z0-9+.-]+:`) and protocol-relative `//`. One-letter `C:` stays a path so
   PO-02 still sees `C:\x`. Tests: `ftp:`, `vscode:`, `//host/x`, `C:\x` kept.
3. **Unclosed indented fence (markdown.py:235).** A fence opened with indent > 0 that never
   closes ends at the first non-blank line indented less than its opener (container end);
   an unindented one still runs to EOF (CommonMark). Indented code blocks (4+ spaces after a
   blank line, last block not a list item) become `CodeSnippet`s. Tests: probe case keeps later
   headings and links; list-item fence still works; 4-space block after a paragraph's blank
   line is code; 4-space list continuation stays prose.
7. **Slugs (markdown.py:84).** First fetch the current `github-slugger` source and GitHub's
   anchor behavior, cite them; then `html.unescape` text outside code spans before slugging and
   align the drop set with the slugger's regex (emoji, combining marks). Tests: `A &amp; B` →
   `a--b`; emoji heading; combining mark. If a case already matches, that part is
   `no_change_needed` with the evidence.

### Commit 2 — Script references (findings 5, 6, 12)

5. **`.` as source (script_refs.py:14).** Match `source`/`.` only in command position: line
   start or after `;`, `&`, `|`, `(`, `{`, `&&`, `||`, `then`, `do`, `else`. Tests:
   `find . -name x`, `git add . lib.sh` → nothing; `. ./lib.sh`, `x && source lib.sh` → found.
6. **Sourced path base (refs.py:153).** Resolve sourced paths like other tokens (script folder,
   then skill root: `link=False`). Test: `scripts/run.sh` with `source scripts/lib.sh` → lib.sh
   reached, no CO-12, not an SC entry point.
12. **`is_shell` (script_refs.py:52).** Compare the shebang interpreter (last path part, or the
   word after `env`/`env -S`) against `{sh, bash, zsh, dash, ksh}`. Tests: `#!/usr/bin/env fish`
   → False; `#!/bin/sh`, `#!/usr/bin/env -S bash -e` → True.

### Commit 3 — Discovery (findings 4, 8a, 9, 11, 15)

4 + 8a. **`_identify` (discover.py:84).** `load_skill` resolves `skill_md` first; `_identify`
   uses a `match folder.parts[-4:]` pattern (`("plugins", p, "skills", _)`,
   `(_, ".claude", "skills", _)`), which removes the magic number and the `noqa`. Test: relative
   `.claude/skills/x/SKILL.md` under `contextlib.chdir` → project; `discover(Path("."))`.
9. **Misleading message (discover.py:116).** `_read_text` also returns why each file was not
   read (outside folder / OSError text / not UTF-8); `_frontmatter` reports the real reason.
   Tests: SKILL.md symlink to outside; unreadable SKILL.md (chmod 000, skipped as root).
11. **Silent git failure (discover.py:116).** `git_modes` returns `GitModes(modes, error)`:
   no git or not a repository → `error=None` (genuinely untracked); any other failure → the
   git message. `Skill` keeps `modes_error`; SC-02 says "git failed: <msg>; filesystem mode"
   instead of "untracked". `ModeReader`, `helpers.load` and the two tests update.
15. **rglob / binaries (discover.py:92).** Walk with `os.walk`, pruning `.git`, `node_modules`
   and `.venv`; `_read_text` skips files over 1 MiB without reading them. The spec's CO-12
   exemptions gain `node_modules/` and `.venv/` in the same commit. Test: a skill with
   `node_modules/x/index.js` and `.venv/lib/y.py` lists neither.

### Commit 4 — Frontmatter (findings 8b, 10)

8b. **Two `pyright: ignore` (frontmatter.py:66,78).** First list exactly what basedpyright
   reports untyped in ruamel.yaml 0.19.1. Fix with local stubs for the three modules used
   (`ruamel.yaml`, `.comments`, `.error`) under `scripts/typings/` (basedpyright's default
   `stubPath` for `-p scripts`), which also removes the existing `cast()` calls. If stubs
   cannot express it, report the evidence and stop for the owner's decision.
10. **Key collisions (frontmatter.py:76).** When two keys give the same `str(key)` (`1` and
   `"1"`), fail CO-01 as a duplicate key, as Claude Code's JavaScript object would merge them.
   Test: `1: a` + `"1": b` → error naming both.

### Commit 5 — Efficiency and altitude (findings 13, 14)

14. `Skill` gets `markdown: Mapping[str, MarkdownDoc]` built once in `load_skill` (SKILL.md →
   `body`); the five `skill.body if rel == SKILL_MD else parse_markdown(text)` call sites read
   it.
13. `_Resolver` becomes public `Resolver`; `rules_content_files` and `rules_scripts` build one
   per check and reuse it; the module-level `resolve()` wrapper is removed after
   `findReferences` + Grep confirm only tests and those rules use it; tests move to
   `Resolver(skill).resolve`.

## Verification

1. Per finding: the new test fails before the fix, passes after; mutation check (revert the fix
   → test fails).
2. After each commit: `npm run test:scripts`, `npm run lint:python`, `npm run typecheck:python`,
   raw output shown, zero suppressions (`grep -rn "noqa\|pyright: ignore" scripts/validators`).
3. `npm run lint:skills` on the 26 skills before and after; explain every changed finding.
4. ReportFindings re-sent with an outcome per finding, then one line per finding to the owner.
5. Commits by topic on `claude/repo-refactor-redesign-feqwzk`; no push until authorized.
