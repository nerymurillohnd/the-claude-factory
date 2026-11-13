---
paths:
  - ".github/**"
---

# GitHub governance (`.github/`)

What GitHub reads from this repository: workflows, forms, templates, labels and Dependabot.

## What each file is for
- `workflows/`: GitHub Actions. Today only `release.yml`, which tags and publishes plugin releases. Pin every action by commit SHA with a `# vX.Y.Z` comment on the same line; Dependabot updates both.
- `ISSUE_TEMPLATE/*.yml`: one issue form per issue kind. Each form sets its labels and a default issue type (`type:`). `config.yml` turns blank issues off and holds the contact links.
- `VULNERABILITY_REPORT.yml`: GitHub's custom form for private vulnerability reports, in issue-form syntax. If GitHub cannot parse it, reporters get the default form.
- `PULL_REQUEST_TEMPLATE/`: `standard.md`, `bug-fix.md`, `maintenance.md`. `pull_request_template.md` is the default template and stays identical to `standard.md`.
- `labels.json`: the fixed labels. The `plugin: <name>` labels are generated from `.claude-plugin/marketplace.json` and are not listed here.
- `dependabot.yml`: updates for GitHub Actions, npm and uv, with a cooldown and grouped minor and patch updates. It does not read the uv tools pinned in the `tools:install` npm script; bump those by hand.
- `zizmor.yml`: the zizmor findings accepted on purpose, each with its reason. Any other finding fails `npm run lint:workflows`.
- `CODEOWNERS`: `@nerymurillohnd` owns every path.

## Working here
- Every "plugin" dropdown, in the issue forms and in `VULNERABILITY_REPORT.yml`, lists exactly the plugins of `marketplace.json` in catalog order. Every label a form or `dependabot.yml` applies exists in `labels.json` or is a generated `plugin: <name>` label.
- After changing `labels.json` or the catalog, run `npm run labels:sync` (a dry run) and review it. Apply it with `npm run labels:sync -- --apply` only with the owner's approval, because it changes GitHub.
- Run `npm run lint:github` after changing a form, `config.yml` or `dependabot.yml`, and `npm run lint:workflows` after changing a workflow or `zizmor.yml`.
