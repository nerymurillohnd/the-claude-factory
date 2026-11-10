# A released plugin changes

This file is part of the docs-maintenance skill. Follow `references/governance.md` for briefing, checking and the rules that apply to every event, and `references/commands.md` for what each command named here tells you. "Stage 1, 2, 3" means order; subagents named in the same stage run in parallel, launched in one message, and a stage starts only when the previous one has returned.

Its components, commands, configuration, prerequisites or behavior change, before a version bump.

1. Stage 1: `changelog-writer`: record each change under `## [Unreleased]`. Give it each change in user terms, its type (Added, Changed, Deprecated, Removed, Fixed or Security) and whether it is breaking.
2. Stage 2: `plugin-readme-writer`, if the change alters anything the README describes. Run `claude --plugin-dir plugins/<plugin> plugin details <name>` first when components were added or removed, so your brief matches the real inventory.
3. Add the events "Third-party material changes" or "Data handling changes" when they apply.

A change limited to formatting, tests or internal refactoring with no effect for users needs no changelog entry.
