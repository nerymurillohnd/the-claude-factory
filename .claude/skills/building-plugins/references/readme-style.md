# Plugin README: template and style

How a plugin's `README.md` is written in this repository. It applies to every `plugins/<name>/README.md`. What the README must contain for any public plugin is in `public-readiness.md`, and how the templates are used and kept is in `templates.md`; this file adds this repository's style.

## Write it from the template

- Start a plugin README from `../assets/README-template.md`, never from another plugin's README.
- Replace every `<…>` placeholder of the template, then search the README for `<` to confirm none is left. Delete a row or section only as `templates.md` says.
- Keep exactly one Compatibility row per component type the plugin ships.
- Open with an outcome-first TL;DR.
- The Version badge reads `version` from `plugin.json`. Never hardcode a version in it.

## Style

- READMEs sell: lead with the outcome and why to install, then teach. Never mention maintenance, `.claude/`, internal scripts, CI internals or how we work.
- English, second person, active voice, present tense, short sentences. Benefit first, mechanics second.
- Emoji-prefixed `##` headings, one emoji per heading, consistent across docs (📥 install, 🔧 manage, 🧭 compatibility, 🩺 troubleshooting, ❓ FAQ, 🔄 update, 🗑️ uninstall, 📝 changelog, 📄 license).
- Badges in the hero only: shields.io, brand color `D97757`.
- Tables for comparisons, commands per surface, requirements and options.
- GitHub alerts (`> [!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`), never two back to back without text between.
- `<details>` for per-surface instructions and FAQs, with the most common option `open`.
- **Bold** for UI labels exactly as shown in the app (`/plugin` → **Installed** → **Update now**); *italics* for emphasis or terms.
- Relative links inside the repo; absolute `https://` links outside.
- State the minimum version of every version-gated feature (e.g. "v2.1.292+").
