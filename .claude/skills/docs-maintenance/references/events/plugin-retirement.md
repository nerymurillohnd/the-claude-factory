# A plugin is retired

This file is part of the docs-maintenance skill. Follow `references/governance.md` for briefing, checking and the rules that apply to every event, and `references/commands.md` for what each command named here tells you. "Stage 1, 2, 3" means order; subagents named in the same stage run in parallel, launched in one message, and a stage starts only when the previous one has returned.

1. You: remove its entry from `marketplace.json`, as the owner decides, then run `claude plugin validate . --strict`.
2. Stage 1: `marketplace-readme-writer` removes it from the catalog, `changelog-writer` records the retirement in the root `CHANGELOG.md`, and `privacy-writer` removes what the policy says about it.
3. Leave the plugin's own directory and documents to the owner's decision: retiring it from the catalog does not delete them.
