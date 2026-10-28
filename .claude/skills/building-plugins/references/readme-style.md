# Plugin README: template and style

How a plugin's `README.md` is written in this repository. It applies to every `plugins/<name>/README.md`. What the README must contain for any public plugin is in `public-readiness.md`, and how the templates are used and kept is in `templates.md`; this file adds this repository's style.

## Write it from the template

- Start a plugin README from `../assets/README-template.md`, never from another plugin's README.
- Replace every `<…>` placeholder of the template, then run `check-readme-placeholders.py <name>` to confirm none is left, in any case. Delete a row or section only as `templates.md` says.
- Keep exactly one Compatibility row per component type the plugin ships.
- Open with an outcome-first TL;DR.

## Badges and the facts they show

`plugin.json` is the only source of the plugin's name, version, description and category; the README follows it.

- Never write the plugin's version in its README: the Version badge shows it. The only version numbers written by hand are Claude Code versions: the minimum (the Claude Code badge, Prerequisites and each version-gated feature); and the minimum version of an external tool in Prerequisites, such as `python3` 3.12 or later for a plugin that runs Python, as `.claude/CLAUDE.md` → Plugin Tooling requires.
- The badges sit in the hero only, from shields.io in the flat style, in this order and color. Each shows a value that lives in another file:
  - **Version** (`D97757`, the brand color): a dynamic badge that reads `$.version` from this plugin's `plugin.json` on `main`, so a bump shows once it is merged; links to `./CHANGELOG.md`. `scripts/validators/plugin-versions-consistency.py` fails on a hardcoded version.
  - **Works in** (`2563EB`): `Claude Code · Claude app` or `Claude Code only`, matching `metadata.surfaces` in `plugin.json`; links to `#-compatibility`.
  - **Category** (`6B7280`): the title in `scripts/categories.json` of the plugin's `metadata.category`; links to `../../README.md#-catalog`.
  - **Claude Code** (`D97757`, with `logo=claude&logoColor=white`): the minimum Claude Code version, the same one Prerequisites states; links to `https://code.claude.com/docs/en/plugins/install`.
  - **License** (`22C55E`): links to the plugin's `LICENSE`.
- When the surfaces, the category or the minimum Claude Code version change, update the badge and the README text that states it in the same change; step 5 of `SKILL.md` then regenerates the catalog.

## Style

- READMEs sell: lead with the outcome and why to install, then teach. Never mention maintenance, `.claude/`, internal scripts, CI internals or how we work.
- English, second person, active voice, present tense, short sentences. Benefit first, mechanics second.
- Emoji-prefixed `##` headings, one emoji per heading, consistent across docs (📋 prerequisites, 📥 install, 🔧 manage, 🧭 compatibility, 🩺 troubleshooting, ❓ FAQ, 🔄 update, 🗑️ uninstall, 📝 changelog, 📄 license).
- Tables for comparisons, the Prerequisites summary and options.
- Every command the user runs goes in a fenced code block, never inside a sentence, so GitHub gives it a copy button.
- GitHub alerts (`> [!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`), never two back to back without text between.
- `<details>` for each install method of a prerequisite (its `<summary>` names the method and platforms, its body holds only the command) and for FAQs; never to hide prose.
- **Bold** for UI labels exactly as shown in the app (`/plugin` → **Installed** → **Update now**); _italics_ for emphasis or terms.
- Relative links inside the repo; absolute `https://` links outside.
- State the minimum version of every version-gated feature (e.g. "v2.1.292+").
