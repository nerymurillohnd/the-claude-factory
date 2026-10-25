---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Release tags are created unsigned by CI

## Scope

The `<plugin>--v<version>` tags and GitHub Releases that `.github/workflows/release.yml` creates after Validate succeeds on `main`. Commits, and tags created on Nery's machine, are out of scope: they stay SSH-signed.

## Context and problem statement

`~/.claude/CLAUDE.md` required every commit and tag to be SSH-signed with `~/.ssh/id_ed25519_signing`, and a project may tighten that rule, never relax it. `release.yml` creates each tag with `gh release create`, which makes a lightweight, unsigned tag (`git cat-file -t turn-meter--v0.1.1` prints `commit`). Should release tags be signed, and how?

In this marketplace, a GitHub repository whose plugins are relative-path entries, users clone `main` and Claude Code takes the version from `plugin.json` (`/en/plugins/loading`, "How Claude Code computes the version"). A tag serves only plugin dependency ranges, which resolve against tags in the marketplace repository (`/en/plugins/dependencies`, "Release a plugin that others depend on"), and anchors the GitHub Release. No plugin declares `dependencies` today.

## Decision drivers

- No user fetches a tag, so a signature on it protects no install.
- The signing key must not leave Nery's machine.
- Nery runs the marketplace alone: releases stay automatic, with no manual step per merge.
- The exemption must not weaken the signing rule for any other repository.

## Considered options

- **CI creates the tags unsigned, under a narrow exemption in both CLAUDE.md files**: chosen.
- **Sign in CI with the signing key stored as a GitHub secret**: rejected, because anyone who can change a workflow could sign as Nery, and a leaked key must be rotated in every repository.
- **Create the annotated tag with `claude plugin tag` in `release.yml`**: rejected for now, because its checks (versions agree, clean tree, tag absent) are already covered here and it adds a Claude Code install to the release path; it still would not sign.
- **Nery creates signed tags locally after each merge**: rejected, because it adds a manual step that must land on the right commit after Validate, against the goal of automating recurring work, and it protects no user.

## Decision outcome

Chosen option: **CI creates the tags unsigned, under a narrow exemption**, because the tag carries no install, the key stays local and releases stay automatic.

- `~/.claude/CLAUDE.md` → Git & GitHub allows the exemption only in a public, git-hosted Claude Code plugin marketplace, when the project's CLAUDE.md says so.
- `.claude/CLAUDE.md` → Versioning and Releases states it for this repository (commit `89abb3b`).

### Consequences

- Good, because releases stay automatic and the signing key never reaches GitHub.
- Good, because every other repository keeps the full signing rule.
- Bad, because a release tag carries no proof of who made it until a tag ruleset stops anyone from moving or deleting it (DEBT-008).

## More information

Decided by Nery on 2026-10-25, after reviewing the options in this session. Revisit when a plugin declares a version range on another plugin of this marketplace: tags then decide what users install, and `claude plugin tag` becomes worth its cost.
