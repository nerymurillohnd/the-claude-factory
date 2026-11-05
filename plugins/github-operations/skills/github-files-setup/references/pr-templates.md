# PR templates

1. Choose from the four models in `<skill-dir>/assets/PULL_REQUEST_TEMPLATE/` (`standard`, `bug-fix`, `hotfix`, `maintenance`) the ones the repository's kinds of change need. A small repository may need only `standard`.
2. Write each chosen template to `.github/PULL_REQUEST_TEMPLATE/`, with the repository's real checks in place of every `Project checks:` hint: the exact commands from its `CLAUDE.md`, `package.json` scripts, `Makefile` or CI files.
3. Write the default template to `.github/pull_request_template.md` too: that is the one GitHub opens, and a folder alone shows no chooser.
4. When a template changes later, change the default copy with it.
5. After the merge, open `https://github.com/<owner>/<repo>/compare` on a test branch, and again with `?template=<file>.md`, and confirm each template loads.
