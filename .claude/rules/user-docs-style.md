---
paths:
  - "README.md"
  - "docs/**"
  - "plugins/*/README.md"
  - "SECURITY.md"
  - "SUPPORT.md"
  - "CONTRIBUTING.md"
  - ".claude/templates/**"
---

# User-facing documentation style

## Purpose

READMEs sell: lead with the outcome and why to install, then teach. Never mention maintenance, `.claude/`, internal scripts, CI internals or how we work.

## Voice

- English, second person, active voice, present tense. Short sentences.
- Benefit first, mechanics second.
- No hype words without substance ("revolutionary", "magic").

## Formatting kit

- Emoji-prefixed `##` headings, one emoji per heading, consistent across docs (📥 install, 🔧 manage, 🧭 compatibility, 🩺 troubleshooting, ❓ FAQ, 🔄 update, 🗑️ uninstall, 📝 changelog, 📄 license).
- Badges in the hero only: shields.io, brand color `D97757`.
- Tables for comparisons, commands per surface, requirements and options.
- GitHub alerts (`> [!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`) — never two alerts back to back without text between.
- `<details>` for per-surface instructions and FAQs; the most common option `open`.
- **Bold** for UI labels exactly as shown in the app (`/plugin` → **Installed** → **Update now**). *Italics* for emphasis or terms.
- Code blocks always have a language (`bash`, `text`, `json`).
- Relative links inside the repo; absolute `https://` links outside.

## Accuracy

- Every command, flag, version and UI path is verified against current official docs before publishing.
- Version-gated features state the minimum version (e.g. "v2.1.292+").
- Install commands always use `<plugin>@the-claude-factory` and source `nerymurillohnd/the-claude-factory`.

## Structure

- Root README section order is defined in `.claude/templates/root-readme.md`.
- Plugin README section order comes from `.claude/templates/plugin/README.md`; required sections are enforced by `check-repo.mjs`.
- `docs/` pages end with prev/next navigation in `<sub>`.

## Lint

`npx --yes markdownlint-cli2@0.23.3` must pass. Heading anchors with emoji start with `-` (e.g. `#-catalog`).
