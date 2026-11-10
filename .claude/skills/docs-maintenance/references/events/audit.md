# Audit or review

This file is part of the docs-maintenance skill. Follow `references/governance.md` for briefing, checking and the rules that apply to every event, and `references/commands.md` for what each command named here tells you. "Stage 1, 2, 3" means order; subagents named in the same stage run in parallel, launched in one message, and a stage starts only when the previous one has returned.

Someone asks whether the documentation is correct, or you suspect drift.

1. Launch the owner of each document in scope with the audit scenario and an explicit "report only, do not fix". For a whole plugin, that is `plugin-readme-writer`, `changelog-writer`, `license-writer` and `notice-writer` (if the plugin has a notice). For the whole repository, all ten, in parallel: an audit writes nothing.
2. Show the owner the findings, grouped by file.
3. Fix what the owner approves: launch the same subagents again with the findings to fix and "fix these findings".
