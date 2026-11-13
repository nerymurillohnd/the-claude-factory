# Contributing guidelines

How to create `CONTRIBUTING.md` from `assets/CONTRIBUTING-template.md`.

## Produces

`CONTRIBUTING.md` at the repository root. GitHub links it when someone opens an issue or a pull request, and shows a Contributing tab and a sidebar link. Precedence: `.github/`, then the root, then `docs/`; the file name is not case sensitive.

## When

- When the repository becomes public.
- When the contribution model, the issue forms or the labels change.

## Sources

Read 2026-11-10 (`github/docs` at `f309096`):

- "Setting guidelines for repository contributors": guidelines "could include: steps for creating good issues or pull requests; links to external documentation, mailing lists, or a code of conduct; community and behavioral expectations."
- "Creating a default community health file": precedence and the account-wide default.
- The live `CONTRIBUTING.md` for the structure (ways to contribute, what happens after an issue). Every issue starts from a form, each form names the labels it applies, and questions, vulnerabilities and platform bugs each have their own place.

## Placeholders

| Value | Meaning | True value from |
| :-- | :-- | :-- |
| `{{projectDisplayName}}` | Project name | The root README |
| `{{contributionModel}}` | Who builds and releases, and what outsiders can do | The maintainer's decision |
| `{{owner}}`, `{{repo}}` | Repository | The repository |
| `{{bugReportForm}}`, `{{featureRequestForm}}`, `{{docsIssueForm}}` | Issue form file names | `.github/ISSUE_TEMPLATE/` |
| `{{needsInfoLabel}}` | Label that asks for details | `.github/labels.json` |

## Procedure

1. Copy the template to `CONTRIBUTING.md`; delete its header comment.
2. Choose the contribution-model paragraph that is true; with pull requests accepted, add a section with the branch, commit, check and review steps.
3. Keep one table row per issue form that exists, with its exact file name; delete the rest.
4. Use label names that exist in the repository.
5. Run the checks.

## Rules

Official (GitHub):

- `https://github.com/<owner>/<repo>/issues/new?template=<file name>` opens the issue form stored under `.github/ISSUE_TEMPLATE/`; the value is the file name with its extension. A link to a form that doesn't exist opens a 404 page, so link only forms that exist.
- A form's `labels` apply when the issue is created, and a label that doesn't exist in the repository is not added.
- Link the code of conduct and the documentation contributors need.

This repository:

- Pull requests are not accepted; users contribute only by opening issues. README Support, `CONTRIBUTING.md` and `docs/faq.md` say the same.
- The table also has a "Plugin idea" row (`plugin_idea.yml`).
- Optional GitHub files not used here: `FUNDING.yml` (sponsor button) and `ACCESSIBILITY.md`.

## Checks

- Every issue form link opens a form (`ls .github/ISSUE_TEMPLATE/`).
- Every label named exists: `gh api repos/{owner}/{repo}/labels --paginate --jq '.[].name'` (`gh label list` uses GraphQL, which cloud sessions block).
- `grep -n '{{\|<!--' CONTRIBUTING.md` returns nothing.

## Never

- Never promise a review or a response time the maintainer does not keep.
