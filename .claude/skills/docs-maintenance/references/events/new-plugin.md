# New plugin

This file is part of the docs-maintenance skill. Follow `references/governance.md` for briefing, checking and the rules that apply to every event, and `references/commands.md` for what each command named here tells you. "Stage 1, 2, 3" means order; subagents named in the same stage run in parallel, launched in one message, and a stage starts only when the previous one has returned.

A directory appears under `plugins/` with its `plugin.json`, and is listed in `marketplace.json`.

Before stage 1, run `claude plugin validate plugins/<plugin> --strict` and `claude plugin validate . --strict`, and fix what they report. After stage 2, run `claude plugin validate plugins/<plugin> --strict --profile directory`.

1. Stage 1: `license-writer` (the plugin's `LICENSE`), `changelog-writer` (the plugin's `CHANGELOG.md`), and `notice-writer` only if the plugin contains third-party material.
2. Stage 2: `plugin-readme-writer`. The README states the license and links the changelog.
3. Stage 3: `marketplace-readme-writer` adds the plugin to the catalog, `changelog-writer` records the launch in the root `CHANGELOG.md` once the plugin's first version is dated, and `privacy-writer` adds the plugin to `PRIVACY.md`, the single policy that covers every plugin.

A plugin that is not released yet gets its changelog with "Initial release." under `## [Unreleased]` and no dated version. The root changelog entry waits for the release.
