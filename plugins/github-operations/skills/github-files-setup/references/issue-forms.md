# Issue forms

## Contents

- Choose the forms
- Pair each form with a PR template
- Write each form
- Validate
- After the merge
- Limits

## Choose the forms

Choose from who files issues and what they report. Ask the user when it is unclear who files issues.

| Model in `<skill-dir>/assets/ISSUE_TEMPLATE/` | Public repository (outside users) | Internal repository (one team) |
| :-- | :-: | :-: |
| `bug_report.yml` | yes | yes |
| `feature_request.yml` | yes | yes |
| `docs_issue.yml` | when it has user docs | when it has docs |
| `idea.yml` | yes | no |
| `question.yml` | when Discussions are off | no |
| `maintenance.yml` | no | yes |
| `incident.yml` | no | when it runs in production |
| `config.yml` | yes | yes |

## Pair each form with a PR template

Each form leads to a kind of change, and that change has its PR template. Keep the pairs consistent, so an issue and the pull request that closes it ask for the same facts:

| Form | Signal it serves | PR template it leads to |
| :-- | :-- | :-- |
| `bug_report` | Something breaks or differs from the docs | `bug-fix` |
| `incident` | Production is broken now | `hotfix` |
| `feature_request` | Improve something that exists | `standard` |
| `idea` | Propose something brand new | `standard` |
| `maintenance` | Planned upkeep or debt, no user-facing defect | `maintenance` |
| `docs_issue` | A doc is wrong, unclear or missing | `maintenance` |
| `question` | "How do I…?" | none |

When the repository has no template of a pair, map its forms to a template it kept.

## Write each form

Write each chosen form to `.github/ISSUE_TEMPLATE/`:

1. Keep the model's `name`, `description`, `title` prefix and the order of its fields, unless the repository's convention differs.
2. Replace generic options with the repository's own: components or packages as dropdown options, supported versions, operating systems and runtimes it targets, its environments.
3. Ask for the evidence its maintainers use: the command that reproduces the problem, the log file it writes, the version command it has.
4. Mark a field `required: true` only when a report is useless without it. Offer `N/A` in the description when a field may not apply.
5. Set `labels:` to the repository's labels: the type label for the form and its triage label. The labels step creates the missing ones.
6. Remove fields that do not apply, such as a browser field in a command-line tool.
7. Write field labels that read well as headings: GitHub writes a submitted form as one `### <field label>` heading per field, in order.
8. In `config.yml`, keep `blank_issues_enabled: false`, and add contact links only to places the repository really uses, such as its Discussions, docs or security policy.

## Validate

1. Run, from the repository's root:
   - `<skill-dir>/scripts/check-forms.py --kind issue .github/ISSUE_TEMPLATE/<form>.yml ...` on every form but `config.yml`;
   - `<skill-dir>/scripts/check-forms.py --kind issue-config .github/ISSUE_TEMPLATE/config.yml`.
2. Fix every finding and run both again. Move on only when both exit 0.
3. Check by reading what the script cannot: `name` is unique across the forms, input labels are unique and not near-identical, and no label holds a blocked word such as "Password".

## After the merge

Confirm GitHub read `config.yml` with `gh api graphql -f query='query { repository(owner:"<owner>", name:"<repo>") { contactLinks { name url } } }'`, and ask the user to open `https://github.com/<owner>/<repo>/issues/new/choose` signed in.

## Limits

- `required: true` is enforced only in public repositories.
- The GraphQL field `issueTemplates` does not list YAML forms: never use it to verify forms.
- `isBlankIssuesEnabled` describes the viewer: an admin sees `true` even when `config.yml` disables blank issues.
- A form's `type:` key needs issue types defined at organization level.
- Issues opened through the API or `gh` skip the form: only issues filed on GitHub get its layout and labels. Tell the user.
