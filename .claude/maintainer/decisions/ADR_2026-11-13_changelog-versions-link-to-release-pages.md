---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Each plugin changelog version links to its release page

## Scope

These files are in scope:

- The link references at the bottom of every `plugins/<plugin>/CHANGELOG.md`.
- Step 5 of `.claude/skills/docs-maintenance/references/documents/changelog.md`.
- Step 4 of the `plugin-releases` skill.
- `scripts/release/release_tools/changelog.py` (`npm run release:changelog`).

The link before the first release, `[Unreleased]` → `commits/main/plugins/<name>` in the CHANGELOG template, is out of scope and stays as it is.

## Context and problem statement

Step 5 of the changelog procedure said that "each version compares its tag with the previous one", and `release-changelog.py` wrote links in that form. On 2026-11-13 none of the 22 plugin CHANGELOGs had a compare link for a version. Each version linked to `releases/tag/<plugin>--v<version>`, for example `[0.1.5]` in `plugins/block-no-verify/CHANGELOG.md`.

The next release would have left that file with mixed formats, which DEBT-004 recorded. Which format should every version use?

## Decision drivers

- Keep one format in each file and across all 22 plugins.
- Avoid a version bump for every plugin. Under the `plugin-versioning` skill, a change to `CHANGELOG.md` takes a bump.
- Point users to the release they read about.

## Considered options

- **Each version links to its release page, `releases/tag/<plugin>--v<version>`**: chosen.
- **Each version links to a compare with the previous tag, as the procedure said**: rejected. Converting the 22 CHANGELOGs would change every plugin's `CHANGELOG.md`, which means 22 version bumps under the project's own rule.

## Decision outcome

Chosen option: **the release page**. The owner chose it on 2026-11-13. It matches the 22 existing files, so only maintainer files change.

`[Unreleased]` still links to `compare/<plugin>--v<newest>...HEAD`.

### Consequences

- Good, because the files, the procedure and the script now agree. A trial on a copy of `block-no-verify`, bumped to 0.1.6, wrote `[0.1.6]: …/releases/tag/block-no-verify--v0.1.6`.
- Good, because no plugin needs a bump for this.
- Bad, because a version's link no longer shows the diff from the previous version. The release page shows the notes. The diff is one step further, on GitHub's compare view.

## More information

The change is commit d3aef8e. It closes DEBT-004.
