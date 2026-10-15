---
name: release
description: Releases a plugin of The Claude Factory — SemVer level, changelog, version bump, root changelog line, catalog, verification and commit. Use only when Nery explicitly asks to release, publish, ship or bump a plugin. The marketplace has no version to release.
argument-hint: "<plugin-name> [major|minor|patch]"
---

# Release

Target: `$ARGUMENTS`. Rules: `.claude/rules/stages/versioning-and-releases.md`.

## 1. Decide the level

1. Diff since the last tag: `git diff <name>--v<current>..HEAD -- plugins/<name>/`.
2. Classify every change as major / minor / patch; the highest wins. If a level was given, confirm it matches the diff — push back if it doesn't.

## 2. Changelog

- Make sure `## [Unreleased]` in `plugins/<name>/CHANGELOG.md` lists every user-visible change, grouped (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`), with issue refs `(#n)`.
- If it's empty, write it from the diff first.

## 3. Bump

```bash
node .github/scripts/bump-version.mjs <name> <level>
```

## 4. Marketplace record

- Root `CHANGELOG.md`: add `- **<name>** <new-version> — <one-line summary>.` under today's `## YYYY-MM-DD` heading and the right group. Create the heading when it is missing.
- Do not bump the marketplace. It has no version.

## 5. Verify and commit

1. Run the `verify` skill — all ✔. Confirm the release passed `/test-installed-plugin` and was exercised in the Claude app (`.claude/CLAUDE.md`, **Done**).
2. Commit: `chore(release): <name> <new-version>` (body: changelog bullets, `Closes #n` for fixed issues).
3. After Nery pushes to `main`, `release.yml` creates the `<name>--v<version>` tag and GitHub Release. Never tag by hand.

## 6. Close the loop

- For each fixed issue: comment with the release link using the *Released* reply in `.claude/templates/issue-replies.md`, label `status: released`, close.
