# A plugin gets a new version

This file is part of the docs-maintenance skill. Follow `references/governance.md` for briefing, checking and the rules that apply to every event, and `references/commands.md` for what each command named here tells you. "Stage 1, 2, 3" means order; subagents named in the same stage run in parallel, launched in one message, and a stage starts only when the previous one has returned.

You have set the new `version` in `plugin.json`, and the release (tag and GitHub Release) happens now.

Before stage 1, run `claude plugin tag plugins/<plugin> --dry-run`: it must exit `0` and show the version you set. A mismatch with the marketplace entry is yours to fix first.

1. Stage 1: `changelog-writer`: turn `## [Unreleased]` into the version's section. Pass the version and the release date: the UTC day the tag and GitHub Release are created, never the day the bump was prepared.
2. Stage 2: `plugin-readme-writer`, to bring version-dependent content in line (badges, minimum versions, update notes).
3. Stage 3: `changelog-writer` records the release in the root `CHANGELOG.md`, and `marketplace-readme-writer` updates the catalog row if it shows the version.

If `## [Unreleased]` is empty, the release has nothing to record: stop and ask the owner what the version changes.

Once the documents are committed, the owner decides when to create and push the tag and the GitHub Release. Do it the same UTC day as the date written in the changelog.
