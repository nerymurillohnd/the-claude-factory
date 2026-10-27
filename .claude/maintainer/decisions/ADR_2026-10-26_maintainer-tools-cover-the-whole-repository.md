---
status: accepted
date: 2026-10-26
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Every maintainer tool covers the whole repository except node_modules, .github and the never-format files

## Scope

- In scope: the ShellCheck, shfmt, Ruff, Basedpyright and Biome gates of `scripts/gates.mjs`; `biome.json`, `ruff.toml`, `.editorconfig`, the new root `pyrightconfig.json` and `.claude/skills/pyrightconfig.json`; the Maintainer Tooling list of `.claude/CLAUDE.md`.
- Out of scope: the plugin gates of `scripts/gates.mjs`, which already run over `plugins/`; `tsc`, whose projects (`scripts/`, `.claude/hooks/`, each plugin) already cover every JavaScript and TypeScript file; actionlint, which checks `.github/workflows/`.

## Context and problem statement

The maintainer gates checked shell and Python only under `scripts/`: the three `.claude/hooks/*.sh`, the three skill shell scripts and the 19 skill Python scripts under `.claude/skills/` had no gate. Biome ran over `.github/` while the other tools did not. Run at the root, each tool reached a different set of files. Nery ordered that Ruff, shfmt, ShellCheck, tsc, Biome and Basedpyright run over the whole repository, except `node_modules/`, `.github/` and the files he defined as never linted or formatted. How should each tool get that scope?

## Decision drivers

- One scope for every tool, set in the tool's own config, so a bare run at the root and the gates agree.
- No file outside the exceptions left without a check.
- Basedpyright always adds `**/.*` to its excludes, and the defaults win over `include` ([config docs](https://docs.basedpyright.com/latest/configuration/config-files/)); on 1.40.2 it skipped files under `.claude/` even when named on the command line ("No source files found", 2026-10-26).

## Considered options

- **Set the exceptions in each tool's config, widen the maintainer gates to every tracked file outside `plugins/` and `.github/`, and give `.claude/skills/` its own Basedpyright config**: chosen.
- **Widen only the gates' file lists**: rejected because a bare run at the root would still reach a different set of files than the gates.
- **Check `.claude/` Python from a temporary copy outside the dot folder**: rejected because a config rooted inside `.claude/skills/` does the same with no copy (19 source files found, 0 errors).

## Decision outcome

Chosen option: **the scope lives in each tool's config, and the gates cover every tracked file outside `plugins/` and `.github/`**, because the bare runs and the gates then check the same files.

- `biome.json` excludes `.github`; `ruff.toml` sets `extend-exclude = [".github"]`; `.editorconfig` sets `ignore = true` for `node_modules`, `.github`, `.superpowers` and `.claude/worktrees`, which shfmt reads; the root `pyrightconfig.json` excludes `.github` and the PEP 723 Python that `scripts/basedpyright-maintainer.mjs` checks against its own environment.
- The gates `shellcheck-maintainer`, `shfmt-maintainer`, `ruff-check-maintainer`, `ruff-format-maintainer` and `basedpyright-maintainer-other` replace the `*-scripts` gates; `basedpyright-skills` runs `basedpyright -p .claude/skills/pyrightconfig.json`.
- The never-format Markdown files stay excluded in `biome.json`, the only tool that reads Markdown.

### Consequences

- Good, because the 25 shell and Python files under `.claude/` now have gates; all passed on 2026-10-26 with no change.
- Good, because a bare `biome ci .`, `ruff check .`, `ruff format --check .`, `shfmt -d .` and `basedpyright` at the root reach the same files as the gates.
- Bad, because a bare `basedpyright` at the root still cannot see `.claude/`: the skills' Python needs `-p .claude/skills/pyrightconfig.json`, which `.claude/CLAUDE.md` states.
- Neutral, because `.github/` keeps only actionlint, and its JSON and Markdown are no longer linted.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Bare runs at the root pass and reach `.claude/` | `ruff check . --show-files`, `shfmt -f .`, `biome ci .`, `basedpyright -p .claude/skills/pyrightconfig.json` | Passed on 2026-10-26: Ruff 19 of 37 files in `.claude/`, shfmt 6 of 29, Biome flagged a planted bad JSON in `.claude/hooks/`, Basedpyright 19 files and 0 errors | When a tool's major version changes |
| The gate list is right | `node --test scripts/tests/gates.test.mjs` | Passed on 2026-10-26, 14 of 14 | Each change to `scripts/gates.mjs` |
| Basedpyright still skips dot folders | `basedpyright --verbose` prints `Auto-excluding **/.*` | Observed on basedpyright 1.40.2 | When basedpyright changes its default excludes |

## More information

- Decided by Nery on 2026-10-26: "Haz que ruff, shfmt, shellcheck, tsc, biome, basedpyright, etc sean ejecutables en todo el repo, exceptuando node_modules, .github, y las carpetas/archivos que he definido nunca deben lintearse ni formatearse".
- Related: ADR_2026-10-21_gates-run-from-one-script, ADR_2026-10-26_biome-formats-and-lints-maintainer-markdown.
