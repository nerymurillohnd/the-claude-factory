---
paths:
  - ".github/**"
---

# GitHub governance

The files GitHub reads from this repository.

## Where a new file goes
- Put GitHub Actions workflows in `workflows/`, each action pinned by commit SHA with a `# vX.Y.Z` comment on the same line, which Dependabot updates together.
- Put one issue form per issue kind in `ISSUE_TEMPLATE/`, with its labels and its default issue type (`type:`). Keep blank issues off and the contact links in `ISSUE_TEMPLATE/config.yml`.
- Keep the private vulnerability report form in `VULNERABILITY_REPORT.yml`, in issue-form syntax; GitHub shows its default form when it cannot parse this one.
- Put pull request templates in `PULL_REQUEST_TEMPLATE/`, and keep `pull_request_template.md`, the default template, identical to `PULL_REQUEST_TEMPLATE/standard.md`.
- Define the fixed labels in `labels.json`. Leave out the `plugin: <name>` labels: `sync-labels.py` generates them from `.claude-plugin/marketplace.json`.
- Configure updates for GitHub Actions, npm and uv in `dependabot.yml`. Bump the uv tools in the `tools:install` npm script by hand, because Dependabot does not read it.
- Record each zizmor finding accepted on purpose in `zizmor.yml`, with its reason; any other finding fails `npm run lint:workflows`.
- Keep code ownership in `CODEOWNERS`.

## Working here
- Keep every "plugin" dropdown, in the issue forms and in `VULNERABILITY_REPORT.yml`, equal to the plugins of `marketplace.json` in catalog order. Apply only labels that `labels.json` defines or that are generated `plugin: <name>` labels: GitHub skips a missing label silently.
- After changing `labels.json` or the catalog, run `npm run labels:sync` (a dry run) and review its output. Run `npm run labels:sync -- --apply` only with the owner's approval, because it changes GitHub.
- Keep the contact links in `ISSUE_TEMPLATE/config.yml` consistent with `SUPPORT.md` and the Support section of the root `README.md`: all three send readers to the same places.
- Run `npm run lint:github` after changing a form, `config.yml` or `dependabot.yml`, and `npm run lint:workflows` after changing a workflow or `zizmor.yml`.
