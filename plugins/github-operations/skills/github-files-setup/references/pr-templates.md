# PR templates

1. Choose the models for the kinds of change the repository takes:

   | Model | Use it for |
   | :-- | :-- |
   | `assets/PULL_REQUEST_TEMPLATE/standard.md` | Every repository: features, refactors and any change without a more specific template. It is the default |
   | `assets/PULL_REQUEST_TEMPLATE/bug-fix.md` | Repositories that take bug reports |
   | `assets/PULL_REQUEST_TEMPLATE/maintenance.md` | Docs, tests, dependencies and tooling with no runtime effect |
   | `assets/PULL_REQUEST_TEMPLATE/hotfix.md` | Repositories that run in production |

   A small repository may need only `standard`.
2. Fit each template to the repository:
   - In every template, replace the hint that follows **Project checks** (an HTML comment asking for the exact commands) with the exact commands from its `CLAUDE.md`, `package.json` scripts, `Makefile`, `justfile` or CI files.
   - Fit the checks line under **Before merge**, the one that names "CI and the project checks above", to where the checks run: keep both when pull requests run CI and local checks; name only "CI" or only "the project checks above, run locally" when only one applies; when the repository has neither, remove the line and say so to the user.
   - Remove the sections that never apply to the repository, such as **Quality surfaces** and **Screenshots** in a command-line tool, or **Data and migrations** without a database. Keep the ones that apply to some changes, which contributors mark N/A.
3. Write each chosen template to `.github/PULL_REQUEST_TEMPLATE/<template>.md`.
4. Write the default template, `standard`, or the only one chosen, to `.github/pull_request_template.md` too. GitHub has no chooser for PR templates: it opens this file, and another template only through a link that names it.
5. When a template changes later, change the default copy with it.
6. After the merge, open `https://github.com/<owner>/<repo>/compare/<default branch>...<branch>?quick_pull=1` on a test branch, then the same link with `&template=<template>.md`, and confirm each template loads. Give the user those links, so contributors can reach the other templates: GitHub returns 404 for a link with a wrong parameter.

Lookup: GitHub reads a single template named `pull_request_template.md` or `.txt`, in any case, from `.github/`, the root or `docs/`, and a `PULL_REQUEST_TEMPLATE/` folder in the same places. When the repository already has one, update it where it is instead of adding a second copy elsewhere.
