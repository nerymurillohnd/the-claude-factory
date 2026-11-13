---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Type ruamel.yaml in the maintainer scripts with local stubs

## Scope

`scripts/typings/ruamel/yaml/` (`__init__.pyi`, `main.pyi`, `comments.pyi`, `error.pyi`) and the maintainer scripts that import ruamel.yaml (`scripts/validators/skill_lint/frontmatter.py`, `scripts/check-github-files.py`). Maintainer scope; plugin scripts are out of scope.

## Context and problem statement

`frontmatter.py` silenced two basedpyright findings with `# pyright: ignore[reportUnknownMemberType]` and cast six values, against `.claude/rules/skill-lint.md` ("fix every finding without suppressing it"). The cause is in ruamel.yaml 0.19.1: it ships `py.typed`, but annotates `YAML.load` with `StreamTextType`, defined only under `if False:` in `ruamel/yaml/compat.py`, and `CommentedBase.lc` as `Any`, so basedpyright sees these members as unknown.

## Decision drivers

- No suppressions and no casts used to silence a checker.
- Types that describe what ruamel.yaml returns at runtime.

## Considered options

- **Local stubs for the members the scripts use, under `scripts/typings/`, basedpyright's default `stubPath` for `-p scripts`**: chosen.
- **A typed Protocol, as `check-github-files.py` does for `YAML.load`**: rejected for `frontmatter.py` because `CommentedBase.lc` is typed `Any`, so a Protocol still needs a cast.
- **Keep the ignores and casts**: rejected because the rule forbids suppressions.

## Decision outcome

Chosen option: **local stubs**, because they remove every ignore and cast in `frontmatter.py` and type the real API once for every maintainer script.

### Consequences

- Good, because basedpyright reports 0 errors with no suppression, and flagged the old casts as unnecessary once the stubs existed (2026-11-13, commit fb70b21).
- Bad, because the stubs must be kept in step with ruamel.yaml: a member a script starts using must be added, and a version bump in `uv.lock` means checking them against the installed package.
- Neutral, because the `YamlLoader` Protocol in `check-github-files.py` and its comment that ruamel.yaml has no type stubs are now redundant; they still type-check.

## More information

- The rule `.claude/rules/skill-lint.md` says to keep the stubs current.
- Implemented in this session on 2026-11-12 and 2026-11-13, under the review-fix plan the owner approved, `.claude/maintainer/plans/2026-11-12-skill-lint-review-fixes.md`.
