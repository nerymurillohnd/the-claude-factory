---
paths:
  - ".github/**"
  - "/.claude-plugin/marketplace.json"
---

# GitHub

## Files

- Pin each action in a workflow by commit SHA, with a `# vX.Y.Z` comment on the same line.
- Give each issue form its labels and default issue type (`type:`), and keep blank issues off.
- Keep `pull_request_template.md` identical to `PULL_REQUEST_TEMPLATE/standard.md`.
- Define the fixed labels in `labels.json`, never the `plugin: <name>` labels, which `sync-labels.py` generates.
- Bump the uv tools in the `tools:install` npm script by hand: Dependabot does not read it.
- Record each zizmor finding accepted on purpose in `zizmor.yml`, with its reason.
- Keep every "plugin" dropdown equal to the plugins of `marketplace.json`, in catalog order.
- Keep the contact links in `ISSUE_TEMPLATE/config.yml`, `SUPPORT.md` and the root README's Support section the same.
- Run `npm run lint:github` after changing a form, `config.yml` or `dependabot.yml`, and `npm run lint:workflows` after changing a workflow or `zizmor.yml`.
- Run `npm run labels:sync` after changing `labels.json` or the catalog, and add `-- --apply` only with the owner's approval.

## Pull requests

- Send every change inside `plugins/` through a pull request, skill, agent and command files included, except a documentation-only change that alters neither behavior nor what users installed.
- Open a pull request for a change outside `plugins/`, or a documentation-only plugin change, only when the owner asks for one.

## Checks before a commit and a merge

| When | Run |
| :-- | :-- |
| Locally, before each commit | `npm run lint` and `npm run typecheck`; `npm run test:scripts` when `scripts/` changed; the plugin checks of `.claude/rules/plugins.md` and `.claude/rules/plugins/testing.md` for each changed plugin; `npm run check:consistency -- --offline` |
| Before each merge: in the pull-request workflow, or locally while there is none | `npm run check`; `npm run check:install` for each changed plugin; evals as `.claude/rules/plugins/evals.md` sets |

- Run a merge-only check locally only when no pull-request workflow exists, or to reproduce a CI failure.
- Merge only when the merge checks pass.
