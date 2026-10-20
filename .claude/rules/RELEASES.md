# Releases

- Release right after a plugin PR that carries a version change merges. There is no separate release commit.
- The plugin PR holds the bump: the level from the diff, the notes under `[Unreleased]`, `node .github/scripts/bump-version.mjs <plugin> <level>` and the root `CHANGELOG.md` line.
- Reference fixed issues with `Refs #n`. Never write `Closes #n`: issues close in the release step.

## After the Merge

1. `gh run list --workflow release.yml --branch main --limit 1` - Run to read the release run that follows the merge.
2. `gh release view <plugin>--v<version>` - Run to confirm the tag and the GitHub Release exist.
3. `gh workflow run release.yml` - Run only when Validate passed and no release run exists.
4. For each fixed issue: comment that the fix is released, label it `status: released` and close it.

- If Validate failed, fix the cause first. Release only after it passes.
- Never tag by hand.
