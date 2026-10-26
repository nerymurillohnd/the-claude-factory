---
status: accepted
date: 2026-10-26
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# `main` and the release tags stay without GitHub protection

## Scope

Applies to the GitHub settings of `nerymurillohnd/the-claude-factory`: branch protection or rulesets on `main`, and a tag ruleset on `*--v*`. The local hooks, `validate.yml` and `release.yml` are out of scope.

## Context and problem statement

DEBT-008 recorded that `main` has no branch protection and the repository has no rulesets (`gh api …/branches/main/protection` returned `Branch not protected`, HTTP 404, and `…/rulesets` returned nothing, on 2026-10-25 and again on 2026-10-26). Users clone `main`, so a merge is the release, and `release.yml` creates the `<plugin>--v<version>` tags unsigned (ADR_2026-10-25_release-tags-are-created-unsigned-by-ci). The debt proposed a ruleset on `main` requiring the Validate checks and pull requests, with Nery as bypass actor, and a tag ruleset blocking update and deletion of `*--v*`. Should the repository add that protection?

## Decision drivers

- Nery and Claude Code are the only parties who work on this repository; users take part only through issues (`.claude/CLAUDE.md` → Responsibility).
- Changes outside `plugins/` do not require a pull request (`.claude/CLAUDE.md` → Change Control).
- No friction without a third party to protect against.

## Considered options

- **Leave `main` and the release tags without GitHub protection**: chosen.
- **Rulesets on `main` and on `*--v*`, with Nery as bypass actor**: rejected because the repository has a sole maintainer and no external contributor to guard against, and a ruleset requiring pull requests clashes with the rule that changes outside `plugins/` go straight to `main`.

## Decision outcome

Chosen option: **leave them without GitHub protection**, because only Nery and Claude Code push to the repository, so a ruleset would add friction to every maintainer commit without stopping anyone it was meant for.

### Consequences

- Good, because maintainer and documentation commits keep going straight to `main`, as Change Control allows.
- Bad, because the CI gate before users stays voluntary: nothing refuses a push to `main` that fails Validate.
- Bad, because nothing refuses an unsigned commit on `main`: on 2026-10-26 the three commits of [PR #51](https://github.com/nerymurillohnd/the-claude-factory/pull/51), made by the GitHub app, reached `main` unsigned.
- Bad, because a `*--v*` release tag can be moved or deleted, which would change what a plugin dependency range resolves to.

## More information

Decided by Nery on 2026-10-26, closing DEBT-008 as accepted. ADR_2026-10-25_release-tags-are-created-unsigned-by-ci names a tag ruleset as what would stop a tag from being moved or deleted; this decision leaves that consequence in place.
