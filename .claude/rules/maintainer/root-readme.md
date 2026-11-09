---
paths:
  - "README.md"
---

# Root README

The root `README.md` is the marketplace's front page. Its template is `.claude/templates/root-readme-template.md`: the order of the sections, each one's intent and rules, and what never goes in. The README already exists and is never rebuilt, so every edit follows the template.

## Edit it from the template

1. Find the template row of each section you touch, and write the section to that row's intent and rules. Trust & safety follows `/en/plugins/security` → Review a plugin before you install.
2. Keep the sections in the template's order, under their emoji headings. A new section goes where its intent fits, and gets its row in the template first.
3. Never hand-edit the `<!-- catalog:* -->` and `<!-- plugin-count:* -->` blocks: run `npm run generate`. The catalog's version column is the only plugin version the README shows, and no plugin detail goes beyond its catalog row.
4. Change each pair below together, in the same commit:
   - Where plugins work ↔ `docs/compatibility.md`
   - Quick start and Manage your plugins ↔ `docs/installation.md`, `docs/managing-plugins.md`, `docs/troubleshooting.md`
   - Documentation ↔ the marketplace guides in `docs/`
   - Support ↔ `SUPPORT.md`, `CONTRIBUTING.md`, `docs/faq.md` and the issue forms
5. Run `npm run generate:check` and `python3 scripts/validators/readme-catalog-consistency.py`, then open every relative link and `#anchor` you touched. No script reads the prose.

## Style

- Benefit first, mechanics second.
- `##` headings with one emoji each, as the template names them.
- Badges only in the hero, from shields.io, brand color `D97757`.
- Tables for comparisons, commands per surface, requirements and options.
- `<details>` for per-surface instructions and FAQs, with the most common option `open`.

## Change the template

- Change `.claude/templates/root-readme-template.md` only when the front page changes shape: a section added, removed, moved or given a new rule. Bring `README.md` in line in the same change.
