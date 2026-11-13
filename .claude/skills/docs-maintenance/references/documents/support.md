# Support resources

How to create `SUPPORT.md` from `assets/SUPPORT-template.md`.

## Produces

`SUPPORT.md` (all caps) at the repository root. GitHub links it from "Helpful resources" when someone opens an issue. Precedence: `.github/`, then the root, then `docs/`.

## When

- When the repository becomes public.
- When a guide in `docs/`, an issue form or a support channel is added, renamed or removed.

## Sources

Read 2026-11-10 (`github/docs` at `f309096`):

- "Adding support resources to your project": type `SUPPORT.md` (with all caps) and "add information about how people can get support for your project"; link it from other places, such as the README.
- The live `SUPPORT.md` for the structure.

## Placeholders

| Value | Meaning | True value from |
| :-- | :-- | :-- |
| `{{guideTitle}}`, `{{guideFile}}`, `{{guideSummary}}` | One row per user guide | `docs/` |
| `{{perComponentDocs}}` | Where the rest of the docs live | For example, each plugin's README |
| `{{owner}}`, `{{repo}}` | Repository | The repository |
| `{{bugReportForm}}`, `{{featureRequestForm}}`, `{{questionForm}}` | Issue form file names | `.github/ISSUE_TEMPLATE/` |
| `{{responseExpectations}}` | What gets the fastest answer | The information the issue forms ask for |
| `{{upstreamSupport}}` | Where platform problems go | The platform's own tracker |

## Procedure

1. Copy the template to `SUPPORT.md`; delete its header comment.
2. List every user guide in `docs/` that answers common questions.
3. Keep one row per issue form that exists; delete the rest.
4. Fill the upstream line with the platform's own tracker.
5. Run the checks.

## Rules

Official:

- List only channels that exist and are answered.

This repository:

- The issue rows also cover `plugin_idea.yml` and `docs_issue.yml`.
- `SUPPORT.md`, the README Support section and `.github/ISSUE_TEMPLATE/config.yml` send readers to the same places. Edit only `SUPPORT.md` here, and report each disagreement in the other two with the change it needs.
- `SUPPORT.md` holds no policy of its own on security reports or response times; it points to `SECURITY.md`.
- Platform problems go to `anthropics/claude-code` issues.

## Checks

- Every link opens (`ls docs/ .github/ISSUE_TEMPLATE/`).
- `grep -n '{{\|<!--' SUPPORT.md` returns nothing.

## Never

- Never promise a response time.
- Never send security reports to public issues.
