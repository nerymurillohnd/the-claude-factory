# Root README

How to edit the root `README.md`, the marketplace's front page, against `assets/root-readme-template.md`. This procedure replaces the former path-scoped rule `.claude/rules/maintainer/root-readme.md`.

## Produces

`README.md` at the repository root. GitHub shows the first README it finds in `.github/`, then the root, then `docs/`; keep only the root one.

## When

- The README already exists and is never rebuilt: every edit follows the blueprint.
- When a section's facts change: a plugin added, renamed or removed (through the generator), a change in `docs/`, `SUPPORT.md`, `CONTRIBUTING.md`, the issue forms or the compatibility matrix.

## Sources

Read 2026-11-10:

- GitHub Docs, "About the repository README file" (`github/docs` at `f309096`): README precedence, relative links, truncation past 500 KiB.
- GitHub Docs, "Basic writing and formatting syntax": alerts, `<details>`, anchors.
- Claude Code docs `plugins/security` → Review a plugin before you install (the Trust & safety section).
- claude.com `/docs/plugins/platform-support`, through `docs/compatibility.md`.

## Placeholders

The blueprint is a section table, not a file to copy. Its values name this repository's facts:

| Value | This repository |
| :-- | :-- |
| `{{generatedBlocks}}` | The `<!-- catalog:* -->` and `<!-- plugin-count:* -->` blocks |
| `{{generateCommand}}` | `npm run generate` |
| `{{marketplaceDisplayName}}` | The Claude Factory |
| `{{ciBadges}}` | The `validate.yml` status badge |
| `{{compatibilityPage}}` | `docs/compatibility.md` |
| `{{securityPolicy}}` | `SECURITY.md` |
| `{{contributionPolicy}}` | No pull requests; issues welcome |
| `{{license}}` | MIT |
| Section 1 value table | Focused, Validated, Versioned, Documented, Open |

## Procedure

1. Find the blueprint row of each section you touch, and write the section to that row's intent and rules. Trust & safety follows the official "Review a plugin before you install" guidance.
2. Keep the sections in the blueprint's order, under their emoji headings. A new section goes where its intent fits, and gets its row in the blueprint first.
3. Never hand-edit the generated blocks: run `npm run generate`. The catalog's version column is the only plugin version the README shows, and no plugin detail goes beyond its catalog row.
4. Change each pair below together, in the same commit:
   - Where plugins work ↔ `docs/compatibility.md`
   - Quick start and Manage your plugins ↔ `docs/installation.md`, `docs/managing-plugins.md`, `docs/troubleshooting.md`
   - Documentation ↔ the marketplace guides in `docs/`
   - Support ↔ `SUPPORT.md`, `CONTRIBUTING.md`, `docs/faq.md` and the issue forms
5. Run the checks.

## Rules

Official (GitHub):

- Relative links inside the repository; absolute `https://` links outside it.
- GitHub alerts only "when they are crucial for user success", "one or two per article", never consecutive and never nested (GitHub Docs, Basic writing and formatting syntax → Alerts).

This repository:

- English, for users: second person, active voice, present tense, short sentences. Benefit first, mechanics second.
- Never the maintenance workflow, `.claude/` contents, scripts, CI internals, release mechanics, roadmap dates or promises, or plugin details beyond the catalog row.
- Name the two surfaces **Claude Code** and **Claude**; the marketplace is `nerymurillohnd/the-claude-factory` with the suffix `@the-claude-factory`.
- `##` headings with one emoji each, as the blueprint names them.
- Badges only in the hero, from shields.io, brand color `D97757`.
- Tables for comparisons, commands per surface, requirements and options.
- `<details>` for per-surface instructions and FAQs, with the most common option `open`.
- **Bold** for UI labels exactly as the app shows them; _italics_ for emphasis or terms.
- The catalog lists exactly the plugins of `.claude-plugin/marketplace.json`, grouped by category, none missing and none extra. `marketplace.json` and each `plugin.json` are read-only here; report a disagreement and use `plugin.json`.
- Surfaces come from each plugin's `metadata.surfaces` (`claude-code`, `claude-app`), this project's own convention: the docs define `metadata` as a free-form object Claude Code doesn't read. Write them as **Claude Code** and **Claude**.
- Manage your plugins: auto-update is off by default for this marketplace and is turned on per user under **Marketplaces** in `/plugin`; an update needs `/reload-plugins` or the next session; `claude plugin marketplace update` refreshes listings only. In Claude, plugins are managed in **Customize > Plugins** (**Disable plugin**, **Remove**, **Check for updates**). Removing a marketplace uninstalls every plugin installed from it: that is the one alert this section may carry.

## Checks

- The catalog's plugin names equal `jq -r '.plugins[].name' .claude-plugin/marketplace.json` (no script checks this yet: DEBT-001).
- Open every relative link and `#anchor` you touched. No script reads the prose.

## Change the blueprint

- Change `assets/root-readme-template.md` only when the front page changes shape: a section added, removed, moved or given a new rule. Bring `README.md` in line in the same change.

## Never

- Never rebuild the README from the blueprint; edit the section you change.
- Never hand-edit a generated block.
