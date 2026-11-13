# New plugin

This file is part of the docs-maintenance skill. Follow `../governance.md` for the owner's values, the checks and the conventions, and write each document from its procedure in `../documents/`. Numbered steps run in order.

A directory appears under `plugins/` with its `plugin.json`, and is listed in `marketplace.json`. Its first version is set by the `plugin-versioning` skill.

Before step 1, run `claude plugin validate plugins/<plugin> --strict` and `claude plugin validate . --strict`, and fix what they report.

1. The plugin's `LICENSE`, its `CHANGELOG.md` with "Initial release." under `## [Unreleased]` and no dated version, and its `NOTICE.txt` only if it contains third-party material.
2. The plugin's `README.md`, written in full by the `plugin-readme-writer` subagent (see `../governance.md`). It states the license and links the changelog. Then run `claude plugin validate plugins/<plugin> --strict --profile directory`.
3. The plugin's row in the root `README.md` catalog, and the plugin in `PRIVACY.md`, the single policy for every plugin. Its line in the root `CHANGELOG.md` waits for its release (`plugin-releases` skill).
