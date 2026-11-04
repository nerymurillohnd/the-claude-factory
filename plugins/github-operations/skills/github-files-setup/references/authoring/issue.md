# Issue forms: design them for the repository

Write the content of each issue form you chose in `setup/templates.md`, section 2, from its model in `<skill-dir>/assets/ISSUE_TEMPLATE/`, so it asks this repository's reporters for what its maintainers need.

## 1. Pair each form with a PR template

Each issue form leads to a kind of change, and that change has its PR template. Keep the pairs consistent, so an issue and the pull request that closes it ask for the same facts:

| Form | Signal it serves | PR template it leads to |
| :-- | :-- | :-- |
| `bug_report` | Something breaks or differs from the docs | `bug-fix` |
| `incident` | Production is broken now | `hotfix` |
| `feature_request` | Improve something that exists | `standard` |
| `idea` | Propose something brand new | `standard` |
| `maintenance` | Planned upkeep or debt, no user-facing defect | `maintenance` |
| `docs_issue` | A doc is wrong, unclear or missing | `maintenance` |
| `question` | "How do I…?" | none |

When you leave out a PR template, map its forms to the one you kept.

## 2. Adapt the fields

1. Keep the model's `name`, `description`, `title` prefix and the order of its fields, unless the repository's convention differs.
2. Replace generic options with the repository's own: components or packages as dropdown options, supported versions, operating systems and runtimes it targets, its environments.
3. Ask for the evidence its maintainers use: the command that reproduces the problem, the log file it writes, the version command it has.
4. Mark a field `required: true` only when a report is useless without it. Offer `N/A` in the description when a field may not apply.
5. Set `labels:` to the repository's labels: the type label for the form and its triage label. Section 4 of `setup/templates.md` creates the missing ones.
6. Remove fields that do not apply, such as a browser field in a command-line tool.

## 3. How a submitted form reads

GitHub writes a submitted form as one `### <field label>` heading per field, in order, each followed by the answer. Write field labels that read well as headings, because they become the structure of every issue filed with the form.

Issues opened through the API or `gh` skip the form. Tell the user that only issues filed on GitHub get its layout and labels.
