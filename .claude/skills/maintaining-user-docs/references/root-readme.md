# Root README: how to use its template

`../assets/root-readme-template.md` is the template of the root `README.md`: the order of its sections, what each one is for, its rules, and what never goes in. The root README already exists and is never rebuilt from scratch, so the template is not filled once and copied: every edit to the README follows it.

## Use it

1. Read the template before you edit `README.md`, and find the row of each section you touch.
2. Keep the sections in the template's order, under their emoji headings. A new section goes where its intent fits, and needs a row in the template first.
3. Write each section to its row's intent and rules, from the primary sources the skill's "Files and their job" table names.
4. Never hand-edit the generated `<!-- catalog:* -->` and `<!-- plugin-count:* -->` blocks: run `npm run generate`. Section 3 (Catalog) and the plugin-count badge come only from it.
5. Keep "Where plugins work" equal to `docs/compatibility.md`.
6. Check what the template's "Never include" list forbids: no maintenance workflow, `.claude/`, scripts, CI internals, release mechanics, roadmap dates, or plugin details beyond the catalog row.
7. Run both generators with `--check`, and open every relative link and `#anchor` you touched.

## Change it

- Edit the template only when the front page itself should change shape: a section added, removed, moved or given a new rule. Then bring `README.md` in line in the same change.
