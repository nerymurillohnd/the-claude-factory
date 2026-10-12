---
name: release
description: Releases a plugin or the marketplace of The Claude Factory — SemVer level, changelog, version bump, root changelog, catalog, verification and commit. Use only when Nery explicitly asks to release, publish, ship or bump a plugin or the marketplace.
argument-hint: "<plugin-name|marketplace> [major|minor|patch]"
---

# Release

Target: `$ARGUMENTS`. Rules: `.claude/rules/versioning-and-releases.md`.

## 1. Decide the level

1. Diff since the last tag: `git diff <name>--v<current>..HEAD -- plugins/<name>/` (or `marketplace--v<current>` for the catalog).
2. Classify every change as major / minor / patch; the highest wins. If a level was given, confirm it matches the diff — push back if it doesn't.

## 2. Changelog

- Make sure `## [Unreleased]` in `plugins/<name>/CHANGELOG.md` lists every user-visible change, grouped (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`), with issue refs `(#n)`.
- If it's empty, write it from the diff first.

## 3. Bump

```bash
node .github/scripts/bump-version.mjs <name> <level>
```

## 4. Marketplace record

1. Root `CHANGELOG.md` → `[Unreleased]`: `- **<name>** <new-version> — <one-line summary>.` under the right group.
2. Bump the marketplace per the table in the rules (minor for a plugin major/minor, patch for a plugin patch):

   ```bash
   node .github/scripts/bump-version.mjs marketplace <level>
   ```

## 5. Verify and commit

1. Run the `verify` skill — all ✔. Confirm the release passed `/test-installed-plugin` and was exercised in the Claude app (per `.claude/rules/cross-surface-compatibility.md`).
2. Commit: `chore(release): <name> <new-version>` (body: changelog bullets, `Closes #n` for fixed issues).
3. After Nery pushes to `main`, `release.yml` creates the `<name>--v<version>` tag and GitHub Release. Never tag by hand.

## 6. Close the loop

- For each fixed issue: comment with the release link using the *Released* reply in `.claude/templates/issue-replies.md`, label `status: released`, close.
