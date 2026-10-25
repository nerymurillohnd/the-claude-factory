---
paths:
  - "README.md"
  - "plugins/*/README.md"
  - "docs/**"
  - "SECURITY.md"
  - "SUPPORT.md"
  - "CONTRIBUTING.md"
  - ".claude/templates/plugin/**"
  - ".claude/templates/root-readme.md"
---

# User Docs Rules

Apply to the root `README.md`, `docs/`, every plugin `README.md`, `SECURITY.md`, `SUPPORT.md`, `CONTRIBUTING.md` and the plugin and root README templates.

- READMEs sell: lead with the outcome and why to install, then teach. Never mention maintenance, `.claude/`, internal scripts, CI internals or how we work.
- In a plugin README, resolve every `{{…}}` and `<!-- TODO -->` of the template, delete rows and sections that do not apply but keep every required section, keep exactly one Compatibility row per component type the plugin ships, and give an outcome-first TL;DR with real usage examples.
- The Version badge reads `version` from `plugin.json`. Never hardcode a version in it.
- List every prerequisite with how to install it and its alternatives, and every network call the plugin makes.
- English, second person, active voice, present tense, short sentences. Benefit first, mechanics second.
- Emoji-prefixed `##` headings, one emoji per heading, consistent across docs (📥 install, 🔧 manage, 🧭 compatibility, 🩺 troubleshooting, ❓ FAQ, 🔄 update, 🗑️ uninstall, 📝 changelog, 📄 license).
- Badges in the hero only: shields.io, brand color `D97757`.
- Tables for comparisons, commands per surface, requirements and options.
- GitHub alerts (`> [!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`), never two back to back without text between.
- `<details>` for per-surface instructions and FAQs, with the most common option `open`.
- **Bold** for UI labels exactly as shown in the app (`/plugin` → **Installed** → **Update now**); *italics* for emphasis or terms.
- Relative links inside the repo; absolute `https://` links outside.
- State the minimum version of every version-gated feature (e.g. "v2.1.292+").
