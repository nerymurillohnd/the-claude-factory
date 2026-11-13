---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Check every skill with skill-lint, an own deterministic maintainer linter

## Scope

`scripts/validators/skill-lint.py`, the package `scripts/validators/skill_lint/`, its tests in `scripts/testers/skill_lint/`, and the `lint:skills` and `test:scripts` npm scripts. It checks the skills matched by `plugins/*/skills/*/SKILL.md` and `.claude/skills/*/SKILL.md`. Maintainer scope: it never writes to a plugin. Out of scope: when and by whom it runs (not wired into `lint`, `check`, Git hooks or CI), and checks against files outside a skill folder.

## Context and problem statement

No official tool mechanically checks what breaks a skill on a third party's machine. `claude plugin validate --strict` (Claude Code 2.1.322) checks only that skill frontmatter parses: it passed github-operations, prompt-writer and instruction-engineering while they held a name with a reserved word, a script without a shebang or an executable bit, and frontmatter fields that claude.ai uploads reject. `quick_validate.py` (skill-creator) checks only the six spec fields, the lengths and `compatibility`, and lets reserved words through. `/doctor prompt-audit` is model-based, not deterministic. The rule catalog, its sources and the architecture are in `.claude/maintainer/specs/skill-lint-spec.md`.

## Decision drivers

- Catch mechanical defects before a skill reaches users, with evidence and a rule id per finding.
- The repository cannot depend on a plugin it distributes, and the maintainer and plugin scopes stay separate (CLAUDE.md, Project scopes).
- One owner per check, so no check is duplicated or left without an owner.
- Every finding reaches the owner, who decides what is fixed and when.

## Considered options

- **Own maintainer code in `scripts/validators/`, independent of the `skill-diagnostics` plugin, with skill-diagnostics used once as a test oracle**: chosen.
- **Run the skill-diagnostics plugin's scripts as the linter**: rejected because the repository would depend on a plugin it distributes, which mixes the two scopes.
- **Rely on `claude plugin validate`, `quick_validate.py` and `/doctor prompt-audit`**: rejected because none checks the mechanical defects above deterministically.

## Decision outcome

Chosen option: **own maintainer code**, because it covers what no official tool checks, keeps the scopes apart and gives a deterministic, repeatable result.

The owner set these terms on 2026-11-12:

- **One owner per check:** structure, `claude plugin validate`; behavior, `claude plugin eval`; semantics, agents or `/doctor prompt-audit`; mechanical checks nothing official covers, skill-lint. Python syntax at the 3.12 floor stays with ruff (`per-file-target-version` `py312`).
- **Severity:** ✗ means the skill breaks, is rejected, or violates an official limit the project enforces, and exits 1. ⚠ is a lead that needs judgment and exits 0. `--strict` turns ⚠ into failures. A usage error exits 2.
- **Reserved words** (`anthropic`, `claude`) in a name give ⚠ (PO-07); a rename goes in a plugin pull request with a major version bump.
- **Reading scope:** only the files inside each skill folder, plus their git index modes. Every finding in every skill is reported, project skills included.
- **PO-05 withdrawn:** relative, `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}` script paths are all valid; no rule judges the form, and the id is not reused.
- **Each run:** Claude reports each defect to the owner, one question per rule id, and fixes it or records it as debt only after the owner decides.
- **How it runs:** `npm run lint:skills`, which runs `uv run python scripts/validators/skill-lint.py` under ADR_2026-11-12_maintainer-scripts-run-through-uv-run.

### Consequences

- Good, because a run at commit 61f139f (2026-11-13) reported 26 skills, 83 errors and 98 warnings that no official tool reported.
- Good, because the code has 184 unittest tests with fixture skills built in temporary directories, so no broken skill is committed.
- Bad, because the rules follow documentation that changes; each rule cites its source URL and must be re-checked against it.
- Bad, because the findings are not yet compared with the oracle, so some may be false positives.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The tests pass and the code has no suppressions | `npm run test:scripts`, `npm run lint:python`, `npm run typecheck:python` | 184 tests OK, 0 errors (2026-11-13) | Every change under `scripts/` |
| CO-01 agrees with Claude Code's parser | Compare with `claude plugin validate` on the 26 skills; label each ruamel-only failure | pending | Before the first owner review of findings |
| The overlapping rules agree with skill-diagnostics | Compare verdicts on the 26 skills and explain each difference | pending | Before the first owner review of findings |

## More information

- Spec: `.claude/maintainer/specs/skill-lint-spec.md`. Plans: `.claude/maintainer/plans/2026-11-12-skill-lint.md` and `.claude/maintainer/plans/2026-11-12-skill-lint-review-fixes.md`.
- The owner made the decision on 2026-11-12; it was implemented on branch `claude/repo-refactor-redesign-feqwzk` and pushed on 2026-11-13.
- Related: ADR_2026-11-13_skill-lint-skips-vendored-folders, ADR_2026-11-13_skill-lint-reads-html-comments-as-prose, ADR_2026-11-13_local-stubs-type-ruamel-yaml.
