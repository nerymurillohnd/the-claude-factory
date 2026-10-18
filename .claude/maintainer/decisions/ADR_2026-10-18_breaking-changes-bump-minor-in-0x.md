---
status: accepted
date: 2026-10-18
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Breaking changes bump the minor version while a plugin is in 0.x

## Scope

Versioning of every plugin in the marketplace while its version is `0.y.z`: the SemVer table in `.claude/rules/stages/versioning-and-releases.md` and the level passed to `.github/scripts/bump-version.mjs`. Plugins at `1.0.0` or later keep the plain table: breaking means major.

## Context and problem statement

The SemVer table says a breaking change is major, and a removed skill is breaking. The same rule file says plugins stay on `0.x` while they are new. The two clash: a literal major bump from `0.x` would jump to `1.0.0`, which declares the interface stable.

`github-operations` 0.2.0 already shipped a breaking change as a minor bump. That change replaced `GITHUB_PAT` with the `github_token` option, in PR #19. The 2026-10-18 handoff left the 0.x rule open for Nery to decide.

PR #20 removes the internal `pr-diagnostics` skill and folds it into the `pr-tracker` agent. That forced the decision.

## Decision drivers

- `1.0.0` should mean the interface is stable, not that one breaking change happened.
- Users must still see breaking changes. The changelog marks each one `**Breaking:**`.
- The rule has to match what already shipped (0.2.0).
- SemVer 2.0.0 item 4 says major version zero is for initial development and anything may change.

## Considered options

- **Minor for breaking changes in 0.x (0.3.0)**: chosen.
- **Patch (0.2.1)**: rejected. The removed skill could not be invoked by users, so behavior stays the same, but a listed component disappears. Calling that a patch hides a structural change.
- **Major (1.0.0)**: rejected. The literal rule would declare `github-operations` stable right after its token interface changed in 0.2.0.

## Decision outcome

Chosen option: **minor for breaking changes in 0.x**. It keeps `1.0.0` for a declared-stable interface, still signals the break in the version and the changelog, and matches 0.2.0.

The rule: while a plugin is `0.y.z`, a breaking change bumps to `0.(y+1).0`, and its changelog entry keeps the leading `**Breaking:**`. A plugin moves to `1.0.0` only when Nery declares its interface stable. From then on, breaking means major.

### Consequences

- Good, because 0.2.0 and 0.3.0 now follow a written rule instead of an exception.
- Good, because users read breaking changes in the changelog regardless of the bump level.
- Bad, because in 0.x a minor bump no longer guarantees backward compatibility. Users have to read the changelog.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The SemVer table states the 0.x exception | Read `.claude/rules/stages/versioning-and-releases.md` | Updated in the same change as this record | When the versioning rule changes |
| `github-operations` releases as 0.3.0 | `gh release view github-operations--v0.3.0` after PR #20 merges | pending | After the PR #20 release |

## More information

- PR #19 (0.2.0) and PR #20 (0.3.0) in `nerymurillohnd/the-claude-factory`.
- Related: ADR_2026-10-18_fold-pr-diagnostics-into-pr-tracker.
- [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html), item 4.
