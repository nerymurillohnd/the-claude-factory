# Release pipeline baseline: which checks pass on the work branch

Measured on 2026-11-15 on `ccr-7fcd6ef3-rku7l1` at 005f47d, with Claude Code 2.1.325, Node 26.13.1, npm 12.2.1, uv 0.13.7 and Python 3.15.2, after `npm ci`, `npm run tools:install`, `uv sync` and `npm ci` in `plugins/tailwind-development/`. It decides which checks block in `validate.yml` and which run in its non-blocking `debt` job ([plan](2026-11-15-release-pipeline.md), Task 1).

## Results

| Check | Exit | Job |
| --- | --- | --- |
| `lint:python` | 0 | checks |
| `lint:shell` | 0 | checks |
| `lint:workflows` | 0 | checks |
| `lint:github` | 0 | checks |
| `lint:js` | 1 | debt (DEBT-006) |
| `lint:frontmatter` | 1 (16 findings) | debt (DEBT-005) |
| `lint:skills` | 1 (31 skills, 91 errors, 106 warnings) | none: never part of `check`; each rule id goes to the owner first |
| `typecheck:ts` | 0 | checks |
| `typecheck:python` | 0 | checks |
| `check:consistency` | 1 (PC-04 only, 10 findings) | checks, after the PC-04 pending rule (Task 2) |
| `claude plugin validate --strict` on 17 plugins and on `.` | 0 | checks |
| `claude plugin validate --strict` on file-tree-pane, model-trace, project-maintainer, tool-ledger, turn-meter | 1 | debt (DEBT-003) |
| `validate:claude` | 0 | checks |
| `validate:mods` | 0 | checks |
| `validate:portable` | 1 (the same five plugins) | debt (DEBT-003) |
| `validate:hooks-catch` | 1 (four hooks in project-maintainer and turn-meter) | debt (DEBT-003) |
| `test:scripts` | 0 | checks |

## Findings beyond the records

- Plain `--strict` now also fails on `file-tree-pane` and `project-maintainer`, with `error TS5097: An import path can only end with a '.ts' extension when 'allowImportingTsExtensions' is enabled`. DEBT-003 recorded plain `--strict` failing only on model-trace, tool-ledger and turn-meter; it gets this evidence.
- `tool-ledger` and `turn-meter` fail plain `--strict` with `TS2741: Property 'isCollapsed' is missing`, the cause DEBT-003 recorded for `validate:portable`.
- The PC-04 findings are the nine untagged current versions plus `skill-diagnostics` 0.4.0.

## skill-diagnostics 0.4.0

- `ced195b` (2026-11-13) is the last commit on `main` where `plugin.json` says 0.4.0; `39b0110` moved it to 0.4.1.
- At `ced195b` the 0.4.0 notes are still under `## [Unreleased]`, so `release-notes.py skill-diagnostics` exits 1 there: "CHANGELOG.md has no ## [0.4.0] section with notes". A backfill therefore reads the notes from the current changelog and only targets `ced195b`.
