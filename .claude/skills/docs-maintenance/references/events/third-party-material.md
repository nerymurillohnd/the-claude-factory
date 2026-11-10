# Third-party material changes

This file is part of the docs-maintenance skill. Follow `references/governance.md` for briefing, checking and the rules that apply to every event, and `references/commands.md` for what each command named here tells you. "Stage 1, 2, 3" means order; subagents named in the same stage run in parallel, launched in one message, and a stage starts only when the previous one has returned.

Material from another author is added to a plugin, updated to another version or removed.

1. Stage 1: `notice-writer` creates or updates the plugin's `NOTICE.txt`. Pass the source, its exact version and its license for each work. A source with no license cannot be redistributed: tell the owner before anything is written.
2. Stage 2: `plugin-readme-writer` updates the credits and license notes.
