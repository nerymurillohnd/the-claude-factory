---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Every template lives in its skill's assets, with its usage in references

## Scope

Every template of this repository that a skill creates or edits files from: the plugin files of `building-plugins`, the root README template of `maintaining-user-docs`, and the eval CI workflow of `testing-plugins`. Out of scope: `.github/ISSUE_TEMPLATE/` and `pull_request_template.md`, which are the live files GitHub reads, and the frozen copies in `.claude/templates/` kept until DEBT-011 closes.

## Context and problem statement

The plugin templates already sat in `building-plugins/assets/` with `references/templates.md` saying how to use them. The root README template lived only as a reference of `maintaining-user-docs`, and the eval CI template of `testing-plugins` carried its instructions only in its own header comment. Where does each template live, and where does its usage live?

## Decision drivers

- A skill holds what it creates from, beside the procedure that uses it.
- An agent that loads the skill finds how to use and fill each template without reading the template itself.

## Considered options

- **Template in the skill's `assets/`, usage in its `references/`**: chosen.
- **Templates in `.claude/templates/`**: rejected because they would sit apart from the skill that uses them; those copies stay frozen only until DEBT-011 closes.

## Decision outcome

Chosen option: **Template in the skill's `assets/`, usage in its `references/`**, as Nery ordered: "todo template, agregarlo como assets/ en su skill respectiva + el como utilizarlo y llenarlo en su respectivo references/".

### Consequences

- Good, because each skill is complete: the template and the instructions to fill it load together.
- Bad, because until DEBT-011 closes the plugin and root README templates also exist as frozen copies.

## More information

Applied on 2026-10-25: `maintaining-user-docs/assets/root-readme-template.md` with `references/root-readme.md` (commit `dba682a`), and "The CI template" in `testing-plugins/references/eval-policy.md` (commit `3d183ac`). Related: ADR_2026-10-25_plugin-scaffold-belongs-to-building-plugins.
