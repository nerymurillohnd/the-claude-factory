---
status: accepted
date: 2026-10-29
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-25_release-tags-are-created-unsigned-by-ci
superseded-by: none
---

# Release tags stay unsigned to keep the signing key local

## Scope

The `<plugin>--v<version>` tags and GitHub Releases that `.github/workflows/release.yml` creates. Commits, and tags created on Nery's machine, stay SSH-signed.

## Context and problem statement

ADR_2026-10-25_release-tags-are-created-unsigned-by-ci kept CI tags unsigned, and its first driver was "No user fetches a tag". That is wrong: a plugin's `dependencies` version range installs "the highest git tag that satisfies this range" (`/en/plugins/dependencies`), so users' Claude Code reads these tags whenever such a range exists. `.claude/CLAUDE.md` repeated the wrong reason. Does the corrected fact change the decision?

## Decision drivers

- The signing key must not leave Nery's machine.
- Claude Code resolves version ranges by tag name and does not verify tag signatures, so a signature would not change what users install.
- Releases stay automatic.

## Considered options

- **Keep CI tags unsigned and state the correct reason**: chosen.
- **Sign tags, redesigning key custody**: rejected, because it puts the key in a GitHub secret or adds a manual step per release, for a signature no install checks.

## Decision outcome

Chosen option: **Keep CI tags unsigned and state the correct reason**, because the key stays local and the signature would protect no install. The rest of the earlier record stands, including the rejection of `claude plugin tag` in `release.yml` and its revisit trigger.

### Consequences

- Good, because the record and `.claude/CLAUDE.md` now state a true reason.
- Bad, because once a plugin declares a version range, an unsigned tag that someone moves changes what users install; a tag ruleset (DEBT-008) remains the protection.

## More information

Decided by Nery on 2026-10-29, after the live-sources audit `.claude/maintainer/audits/2026-10-29-plugins-and-mods-live-sources-audit.md` (F3.6, F4.5). `.claude/CLAUDE.md` → Change Control was corrected in commit `a736011`.
