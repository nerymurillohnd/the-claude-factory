# Data handling changes

This file is part of the docs-maintenance skill. Follow `references/governance.md` for briefing, checking and the rules that apply to every event, and `references/commands.md` for what each command named here tells you. "Stage 1, 2, 3" means order; subagents named in the same stage run in parallel, launched in one message, and a stage starts only when the previous one has returned.

A plugin starts or stops calling a remote service, collecting data or keeping files on the user's machine.

1. Stage 1: `privacy-writer` updates `PRIVACY.md`, and `plugin-readme-writer` updates the plugin's "What this plugin runs and sends" section. Both read the plugin's files; tell them what changed.
