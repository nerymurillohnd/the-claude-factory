# Plugin README: template and style

How a plugin's `README.md` is written in this repository, and how its template is kept. It applies to every `plugins/<name>/README.md` and to everything under `.claude/templates/plugin/`. What the README must contain for any public plugin is in `public-readiness.md`; this file adds this repository's template and style.

## Start from the template

- Every plugin README starts from `.claude/templates/plugin/README.md`, which `node scripts/new-plugin.mjs` renders for a new plugin. `check-repo.mjs` requires that template's sections, so never start from another plugin's README or from any other template.
- Resolve every `{{…}}` placeholder and `<!-- TODO -->` comment of the template. Delete rows and sections that do not apply, but keep every required section.
- Keep exactly one Compatibility row per component type the plugin ships.
- Open with an outcome-first TL;DR.
- The Version badge reads `version` from `plugin.json`. Never hardcode a version in it.

## Keep the template

- Edit `.claude/templates/plugin/` itself only to change what every plugin README gets, and keep its `{{…}}` placeholders and `<!-- TODO -->` comments: they are what a new README resolves.
- A change to the template brings every plugin README built from it in line in the same change; those READMEs are plugin files, so that part goes through a pull request.

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
