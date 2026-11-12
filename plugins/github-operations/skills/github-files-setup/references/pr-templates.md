# PR templates

1. Choose from the four models in `<skill-dir>/assets/PULL_REQUEST_TEMPLATE/` (`standard`, `bug-fix`, `hotfix`, `maintenance`) the ones the repository's kinds of change need. A small repository may need only `standard`.
2. Fill the checks from what step 1 found, so no template asks for checks the repository doesn't have:
   - Replace every `Project checks:` hint with the exact commands from its `CLAUDE.md`, `package.json` scripts, `Makefile`, `justfile` or CI files.
   - Fit the **Before merge** checks line to where the checks run. Keep the CI line when pull requests run CI checks. When the checks are local only, write that the project checks above pass locally, with their output in the pull request. When it has both, keep both. When it has none, remove the line and say so to the user.
3. Write each chosen template to `.github/PULL_REQUEST_TEMPLATE/<kind>.md`.
4. Write the default template to `.github/pull_request_template.md` too. GitHub has no chooser for PR templates: it opens this file, and another template only through a link that names it.
5. When a template changes later, change the default copy with it.
6. After the merge, open `https://github.com/<owner>/<repo>/compare/<default branch>...<branch>?quick_pull=1` on a test branch, then the same link with `&template=<kind>.md`, and confirm each template loads. Give the user those links, so contributors can reach the other templates: GitHub returns 404 for a link with a wrong parameter.

Lookup: GitHub reads a single template named `pull_request_template.md` or `.txt`, in any case, from `.github/`, the root or `docs/`, and a `PULL_REQUEST_TEMPLATE/` folder in the same places. When the repository already has one, update it where it is instead of adding a second copy elsewhere.
