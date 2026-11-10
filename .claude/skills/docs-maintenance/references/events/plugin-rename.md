# A plugin is renamed

This file is part of the docs-maintenance skill. Follow `references/governance.md` for briefing, checking and the rules that apply to every event, and `references/commands.md` for what each command named here tells you. "Stage 1, 2, 3" means order; subagents named in the same stage run in parallel, launched in one message, and a stage starts only when the previous one has returned.

A rename makes it a different plugin to every existing install, so users must install the new name.

1. You: update `plugin.json` and the `marketplace.json` entry, then run `claude plugin validate plugins/<new-name> --strict` and `claude plugin validate . --strict`. Check that the old name is not still listed as a plugin.
2. Stage 1: `changelog-writer` records the rename as a breaking change in the plugin's changelog, and `plugin-readme-writer` updates every command and name in the README.
3. Stage 2: `marketplace-readme-writer` updates the catalog, and `changelog-writer` records the rename in the root `CHANGELOG.md`.
