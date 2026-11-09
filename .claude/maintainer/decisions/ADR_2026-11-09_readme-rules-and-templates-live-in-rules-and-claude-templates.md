---
status: accepted
date: 2026-11-09
decision-makers:
  - "Nery Samuel Murillo"
supersedes:
  - ADR_2026-10-25_templates-live-in-their-skills-assets
  - ADR_2026-10-25_plugin-readme-rules-live-in-building-plugins
superseded-by: none
---

# README rules live in path-scoped rules, and README templates in `.claude/templates/`

## Scope

How the root `README.md` and each `plugins/<plugin>/README.md` are written: their templates, the instructions for using them, and the project-wide README requirements. Out of scope: the other templates (`building-plugins`' plugin manifest, changelog, license and notice assets, and `testing-plugins`' eval CI template), which stay in their skills' `assets/`; and the marketplace's other documents (`docs/`, the root policy files), which stay in `maintaining-user-docs`.

## Context and problem statement

The README instructions were spread over four places: `.claude/rules/readme-md.md`, which only pointed elsewhere; `building-plugins` (`assets/README-template.md`, `references/templates.md`, `references/readme-style.md`, part of `references/public-readiness.md`); `maintaining-user-docs` (`assets/root-readme-template.md`, `references/root-readme.md`); and `.claude/CLAUDE.md` (README content requirements). A skill loads only when its description matches the task, and an edit to a published README did not reach the template or the style rules. On 2026-11-09 two published READMEs were found carrying rename history and a false migration claim; nothing in the README instructions said a README describes only what exists now. Where should the README instructions and templates live?

## Decision drivers

- Instructions about a file load when that file is edited, without depending on a skill's description.
- One source per instruction: no README rule repeated across a rule, a skill and `CLAUDE.md`.
- A rule says how to write the file; when to change it lives in `CLAUDE.md`, because a path-scoped rule loads only once the file is touched.

## Considered options

- **Two path-scoped rules, the templates in `.claude/templates/`, the generalities in `CLAUDE.md`**: chosen.
- **Keep the README instructions in the two skills' references and assets**: rejected, because they load only with the skill and were not consulted when a published README was edited.
- **One rule for every README**: rejected; the root README and plugin READMEs have different readers, templates and checks.

## Decision outcome

Chosen option, as Nery ordered on 2026-11-09:
- `.claude/rules/maintainer/root-readme.md` (`paths: README.md`) consolidates `readme-md.md`'s root section and `maintaining-user-docs/references/root-readme.md`, and names `.claude/templates/root-readme-template.md`.
- `.claude/rules/plugins/plugin-readme.md` (`paths: plugins/*/README.md`) consolidates `readme-md.md`'s plugin section, `building-plugins/references/readme-style.md`, the README parts of `references/templates.md` and `references/public-readiness.md`, and `CLAUDE.md`'s list of what a plugin README declares; it names `.claude/templates/plugin-readme-template.md`.
- `.claude/CLAUDE.md` → "README files" holds the generalities: a README describes what exists now and history goes to the CHANGELOG, the kinds of README with their rule and template, and when a README changes. "Repository Layout" lists `.claude/rules/` and `.claude/templates/`.
- Deleted: `.claude/rules/readme-md.md`, `building-plugins/references/readme-style.md`, `maintaining-user-docs/references/root-readme.md`, and both skills' README template assets. `scaffold-plugin.py`, `check-readme-placeholders.py`, `scripts/check-repo.mjs` and its test read the plugin template from its new path; `biome.jsonc` excludes `.claude/templates`.

### Consequences

- Good, because the instructions for a README load whenever Claude edits it, and each instruction has one home.
- Good, because the scaffold and the checks keep one template, at a path no skill owns.
- Bad, because rules do not load in the project's cloud threads: there the project instructions must list the two new rules in place of `readme-md.md`.
- Bad, because a rule loads only after the README is touched; a plan that needs the template's shape earlier must open the rule or the template on purpose.

## More information

This reverses part of earlier decisions: ADR_2026-10-25_plugin-readme-rules-live-in-building-plugins had moved plugin README rules from the rule `user-docs.md` into the skill, and ADR_2026-10-25_templates-live-in-their-skills-assets had moved templates out of an earlier `.claude/templates/`. Both are superseded for README files only; their other outcomes stay. Related: ADR_2026-10-26_plugin-readme-template-takes-the-published-shape.
