# Repository foundation

This file is part of the docs-maintenance skill. Follow `references/governance.md` for briefing, checking and the rules that apply to every event, and `references/commands.md` for what each command named here tells you. "Stage 1, 2, 3" means order; subagents named in the same stage run in parallel, launched in one message, and a stage starts only when the previous one has returned.

The repository's own documents are created or rebuilt, for example when the marketplace is set up or restructured.

1. Stage 1: `license-writer` (root `LICENSE`), `code-of-conduct-writer`, `security-writer`, `privacy-writer`.
2. Stage 2: `contributing-writer` and `support-writer`. They link to the code of conduct and the security policy, so those must exist first.
3. Stage 3: `marketplace-readme-writer`. The front page links to every policy and lists the catalog.
4. Stage 4: `changelog-writer` for the root `CHANGELOG.md`. It takes the marketplace display name from the root README's title.

Gather all owner values before stage 1: the copyright line, the reporting channels, the security policy, the effective date of the privacy policy, the marketplace display name.
