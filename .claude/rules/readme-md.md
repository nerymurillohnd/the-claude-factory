---
paths:
  - "README.md"
  - "**/README.md"
---

# README.md files

A `README.md` in this repository is one of four kinds, and each kind has its own owner, template, rules and checks. Identify the kind before you edit, then load what it names.

## Which README this is

| File | What it is | Scope | Load |
| :-- | :-- | :-- | :-- |
| `README.md` at the repository root | The marketplace's front page for users | Maintainer: no pull request | The `maintaining-user-docs` skill |
| `plugins/<name>/README.md` | One plugin's user guide | Plugin: every change goes through a pull request | The `building-plugins` skill; for a plugin that is or contains a mod, also `building-mods` |
| `.claude/templates/plugin/README.md` | The older plugin README template, frozen until DEBT-011 closes | Maintainer | The plugin template section below |
| Any other, such as `scripts/tests/<plugin>/…/README.md` | A maintainer note, never shipped to users | Maintainer | Nothing more: keep it accurate |

## Root README

- **Template:** `.claude/skills/maintaining-user-docs/assets/root-readme-template.md` sets the order of sections and what never goes in; `references/root-readme.md` there says how to use and change it.
- **Generated blocks:** never edit the `<!-- catalog:* -->` and `<!-- plugin-count:* -->` blocks by hand; run `npm run generate`. The catalog's version column is the only plugin version the root README shows.
- **Plugin details:** none beyond the catalog row; they belong in each plugin's README.
- **Compatibility:** "Where plugins work" must match `docs/compatibility.md`.
- **Checks:** both generators with `--check`, and opening every relative link and `#anchor` you touched. No script reads this file's prose.

## Plugin README

- **Template:** the one `building-plugins` sets, `assets/README-template.md`. Never start from another plugin's README. The skill's scaffold writes the README from it. Until DEBT-011 closes, `check-repo.mjs` still follows the older `.claude/templates/plugin/README.md`, whose sections differ.
- **Rules:** `.claude/CLAUDE.md` → Plugin Documentation and Changelogs → Templates and README holds the required sections, the badges, the Compatibility rows and the one version number allowed. `building-plugins` → `references/readme-style.md` holds the template's use and the style.
- **A plugin with a mod:** the README also carries what `building-mods` section 5 lists: where the mod runs, what turns it off, the organization caveat, what it reaches, and the "Tested with Claude Code X.Y.Z" line.
- **A `README.md`-only change:** a pull request, no version bump and no CHANGELOG entry. GitHub shows it once it is merged, but the copy a user already installed keeps its old README until the plugin's next version.
- **Checks:** `node scripts/check-repo.mjs` covers the sections, leftover `TODO` and `TEMPLATE` comments, the "works in" badge and one Compatibility row per component type. `plugin-versions-consistency.py` covers the Version badge. Neither reads the text of the cells or the prose: compare those yourself.

## The plugin template

- The plugin templates are `building-plugins`' assets; `references/templates.md` there says how to fill and change them.
- `.claude/templates/plugin/README.md` is the older template, kept frozen because `check-repo.mjs` and the repository's tests still read it until DEBT-011 closes. Never edit it and never build a README from it.

## Every README

- English, written for users. Never mention this repository's maintenance, `.claude/`, scripts or CI. A user's own `.claude/settings.json` may be mentioned.
- Check every command, flag, UI path and minimum version against the live official docs and the release notes before you write it. When they differ, the release notes win.
- One fact has one value everywhere. `docs/compatibility.md` is the single source of the component × surface matrix, and the marketplace is `nerymurillohnd/the-claude-factory` with the suffix `@the-claude-factory`.
- Write no version number by hand, except the ones the rules above allow.
- Disclose every network call, hook and file the plugin writes, and every prerequisite with how to install it.
