---
paths:
  - "scripts/**/*.py"
  - "scripts/**/*.pyi"
---
# skill-lint (maintainer scripts)

## Run

- Launch skill-lint only through `npm run lint:skills`, which runs `uv run python scripts/validators/skill-lint.py` on Python 3.15 from `.venv`, and its tests only through `npm run test:scripts`; never run a file under `scripts/validators/` or `scripts/testers/` as `./<file>.py`, because its `#!/usr/bin/env python3` line would pick the machine's OS Python.
- Run `npm run test:scripts` after every change under `scripts/validators/` or `scripts/testers/`; it runs `unittest discover` on `scripts/testers/` with `-t scripts`.
- Run `npm run lint:python` and `npm run typecheck:python` before each commit, and fix every finding without suppressing it.

## Edit

- Edit `skill_lint/cli.py` to change arguments, the order of the checks or the exit codes; keep `scripts/validators/skill-lint.py` a shim that only puts `scripts/` on the import path and runs `validators.skill_lint.cli` with `runpy`.
- Edit `discover.py` to change which skills are found or what a `Skill` loads; keep the two globs `plugins/*/skills/*/SKILL.md` and `.claude/skills/*/SKILL.md`.
- Keep `PRUNED_DIRS` in `discover.py` equal to the folders the spec's Discovery section lists, and let `git_modes` return no modes only when git is missing or the folder is not in a repository; raise `GitError` for any other git failure, so SC-02 names it.
- Edit `frontmatter.py` for YAML parsing, `markdown.py` for the line scan (fences, indented code, HTML comments, headings), `markdown_model.py` for the `MarkdownDoc` parts, slugs, links, inline code and `!` commands, `refs.py` for path resolution and the reference graph, `script_refs.py` for Python imports and shell `source` lines, and `commands.py` for the commands Markdown runs and scripts call.
- Add or change a rule in its family's module:
  - CO-01 to CO-06: `rules_content.py`.
  - CO-07 to CO-12: `rules_content_files.py`.
  - PO: `rules_portability.py`.
  - SC: `rules_scripts.py`.
  - CA: `rules_capabilities.py`.
- Edit `report.py` to change the table, the details, the manifest or the JSON.
- Check the rule against `.claude/maintainer/specs/skill-lint-spec.md` before changing it, and update the spec in the same commit.

## Write the code

- Type ruamel.yaml through the local stubs in `scripts/typings/ruamel/yaml/`: add each new ruamel member a script uses to them, and check them against the installed version when `uv.lock` bumps ruamel.yaml.
- Start every new `.py` file under `scripts/validators/` and `scripts/testers/` with `#!/usr/bin/env python3` and give it mode 100755 (`chmod +x`, then `git add`), as every existing one has; ruff's EXE rules fail a file whose shebang and mode disagree.
- Import package modules absolutely (`from validators.skill_lint.model import Finding`): `ruff.toml` bans relative imports, and a bare `import skill_lint` fails at runtime.
- Build every `Finding` from the module's `SOURCES` map, which maps each rule id to the spec's source URL.
- Read only files inside the skill folder; never write to a skill.
- Read parsed Markdown from `skill.markdown`, never call `parse_markdown` in a rule module, and build one `Resolver` per check, not one per token.
- Build test skills in a `tempfile.TemporaryDirectory` with `build_skill()` and `load()` from `scripts/testers/skill_lint/helpers.py`; never commit fixture skills.
- Write the failing test first, then the code; confirm the test fails with the rule disabled.
- Split a module that grows past about 250 lines by responsibility, as `rules_content_files.py`, `commands.py` and `markdown_model.py` split from their parents, and update this rule in the same commit.
