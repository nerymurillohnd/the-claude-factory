# Issue forms

## Contents

- Choose the forms
- Pair each form with a PR template
- Write each form
- Labels by component
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

When the owner's `.github` repository holds issue templates or a `config.yml`, the repository inherits them until it has one valid template or `config.yml` of its own; from then on none of the inherited ones show. Tell the user before writing the first one.

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

1. Keep the model's `name`, `description`, `title` prefix and the order of its fields, unless the repository's convention differs. A `name` of 3 characters or fewer hides the form.
2. Replace generic options with the repository's own: components or packages as dropdown options, supported versions, operating systems and runtimes it targets, its environments. A dropdown takes `multiple: true` for several answers, and `default: <index>` to preselect one; with a default, no option may be "None" or "n/a".
3. Ask for the evidence its maintainers use: the command that reproduces the problem, the log file it writes, the version command it has. An `upload` field takes files, with `validations.accept` limiting the extensions.
4. Mark a field `required: true` only when a report is useless without it, and add `min_length` to a text field that needs a real answer. Offer `N/A` in the description when a field may not apply.
5. Set `labels:` to the repository's labels: the type label for the form and its triage label. The labels step creates the missing ones.
6. When the repository's owner is an organization with issue types (step 1), set `type:` to the matching type instead of a type label. Add `projects:` (`<owner>/<number>`) only when every reporter can write to that project.
7. Give each field a stable `id`: links can prefill a field by its id (`issues/new?template=<file>&<id>=<text>`), so renaming an id breaks those links.
8. Replace every placeholder in angle brackets, such as `<OWNER>` or `<DEFAULT_BRANCH>`, and keep a link only when its target exists and is on: the private advisory link needs private vulnerability reporting, a Discussions link needs Discussions, a docs link needs that page on the default branch.
9. Remove fields that do not apply, such as a browser field in a command-line tool.
10. Write field labels that read well as headings: GitHub writes a submitted form as one `### <field label>` heading per field, in order.
11. In `config.yml`, keep `blank_issues_enabled: false`, and add contact links only to places the repository really uses, such as its Discussions, docs or security policy.

The chooser lists forms in alphanumeric order of file name, YAML forms before Markdown templates. To set the order, prefix the file names (`01-bug_report.yml`, `02-feature_request.yml`), and update every link that names a form file.

## Labels by component

A form applies only the labels in its top-level `labels:`. A dropdown answer, such as the component a reporter picks, goes into the issue's body as text and applies no label. To label issues by component, offer the user one of:

- **Triage by hand:** the maintainers read the answer and apply the label. Nothing to add.
- **One form per component:** each form names its component label in `labels:`. Fits two or three components, not more.
- **A workflow that labels from the form:** a GitHub Actions workflow on `issues: opened` reads the answer under its `### <field label>` heading and adds the label with `gh issue edit "$NUMBER" --add-label "<label>"`. Every label it applies must exist. The workflow runs on untrusted input from any reporter: write it only when the user wants it, and audit it with `github-operations:claude-github-actions` before the pull request.

## Validate

1. Run, from the repository's root:
   - `python3 <skill-dir>/scripts/check-forms.py --kind issue .github/ISSUE_TEMPLATE/<form>.yml ...` on every form but `config.yml`;
   - `python3 <skill-dir>/scripts/check-forms.py --kind issue-config .github/ISSUE_TEMPLATE/config.yml`.
2. Fix every finding and run both again. Move on only when both exit 0.
3. When the script exits 2 because ruamel.yaml or check-jsonschema is missing and uv is not installed, tell the user what it printed, then check each form by reading it against this page and GitHub's form syntax, and say in the report that the script did not run.

## After the merge

Ask the user to open `https://github.com/<owner>/<repo>/issues/new/choose` signed in and confirm that the forms and contact links appear. A user with write access also sees a blank issue, marked **Maintainers only**: that is expected.

## Limits

- `required: true` is enforced only in public repositories.
- Forms must be `.yml` files in `.github/ISSUE_TEMPLATE/` on the default branch.
- A form's `type:` needs issue types defined for the owner; `projects:` needs the reporter's write access to the project.
- Issues opened through the API or `gh` skip the form: only issues filed on GitHub get its layout and labels. Tell the user.
