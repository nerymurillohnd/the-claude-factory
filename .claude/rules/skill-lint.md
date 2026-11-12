---
paths:
  - "scripts/**/*.py"
---
# skill-lint (maintainer scripts)

The spec is `.claude/maintainer/specs/skill-lint-spec.md`; it holds the rule catalog (CO, PO, SC, CA) and the severity model.

## Execution chain

- `npm run lint:skills` runs `uv run python scripts/validators/skill-lint.py`, the project's Python 3.15 from `.venv`.
- `scripts/validators/skill-lint.py` is a shim. It puts `scripts/` on the import path and runs `validators.skill_lint.cli` with `runpy`, so the package has one name. Its `#!/usr/bin/env python3` line is not the interpreter that runs it.
- `cli.py` loads the named skills or discovers all of them, runs the four `check` functions (content, portability, scripts, capabilities), filters with `--only`, prints through `report.py` and returns 0, 1 or 2.
- `npm run test:scripts` runs `unittest discover` on `scripts/testers/` with `-t scripts`, so tests import `validators.skill_lint.<module>`.

## Modules (`scripts/validators/skill_lint/`)

| Module | Job |
| :-- | :-- |
| `model.py` | `Finding`, `Severity` (error or warning), `Family` (CO, PO, SC, CA), `SkillKind` |
| `discover.py` | `discover()` and `load_skill()`: the two skill globs, files, UTF-8 text, git modes, `Skill` |
| `frontmatter.py` | Strict YAML frontmatter with ruamel.yaml: duplicate keys, key lines, `body_start` |
| `markdown.py` | `parse_markdown()`: links, headings and GitHub slugs, code, `!` commands, prose |
| `refs.py` | `resolve()`, `escapes()`, `reference_graph()`, `depths()`: which file references which |
| `script_refs.py` | Python imports and shell `source` lines between a skill's scripts |
| `commands.py` | What the Markdown runs (`run_contexts`) and what scripts call (`script_commands`) |
| `rules_content.py` | CO-01 to CO-06 (frontmatter values, body length); calls `rules_content_files.py` |
| `rules_content_files.py` | CO-07 to CO-12 (links, depth, tables of contents, dated text, orphans) |
| `rules_portability.py` | PO rules |
| `rules_scripts.py` | SC rules; `entry_points()` |
| `rules_capabilities.py` | CA rules; `inventory()` of `!` commands, hooks and allowed-tools |
| `report.py` | Summary, table, details, manifest and JSON |
| `cli.py` | Arguments, the run and the exit code |

## Conventions

- Import package modules absolutely (`from validators.skill_lint.model import Finding`): `ruff.toml` bans relative imports. Never import bare `skill_lint`, which fails at runtime.
- Give each rule module a `SOURCES` map from rule id to the spec's source URL, and build every `Finding` from it.
- Read only files inside the skill folder, and never write to a skill.
- Build test skills in a `tempfile.TemporaryDirectory` with `build_skill()` and `load()` from `scripts/testers/skill_lint/helpers.py`; never commit fixture skills.
- Keep each module under about 250 lines; split by responsibility as `rules_content_files.py` and `commands.py` do.
