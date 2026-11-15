---
paths:
  - ".github/**"
  - "/.claude-plugin/marketplace.json"
---

# GitHub

## Files

- Pin each action in a workflow by commit SHA, with a `# vX.Y.Z` comment on the same line, until `.github/workflows/actions.lock` replaces the pins (DEBT-007). `gh actions-lock` needs an authenticated `gh` with API access to the action repositories, which a cloud session doesn't have, so generate the lockfile only on Nery's machine.
- Start every `run:` script that runs more than one command with `set -euo pipefail`: a step with no `shell:` runs as `bash -e {0}`, without `pipefail`, and `shell: bash` as `bash --noprofile --norc -eo pipefail {0}`, without `-u`.
- Bump `CLAUDE_CODE_VERSION` in `.github/actions/setup/action.yml` to the `claude --version` the maintainers run, as an exact build of Anthropic's signed apt repository.
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
- Reproduce a review finding, from any reviewer, before changing code for it, and answer it with the result: fix what holds, and say with the evidence what doesn't. Reply on the finding's own thread; when it has none on GitHub, ask the owner where to answer.

## Checks before a commit and a merge

| When | Run |
| :-- | :-- |
| Locally, before each commit | `npm run lint` and `npm run typecheck`; `npm run test:scripts` when `scripts/` changed; the plugin checks of `.claude/rules/plugins.md` and `.claude/rules/plugins/testing.md` for each changed plugin; `npm run check:consistency -- --offline` |
| Before each merge, in Validate (`.github/workflows/validate.yml`) | its `Checks` job, which includes `npm run check:install -- --from local <plugin>` for each changed plugin outside DEBT-003; evals as `.claude/rules/plugins/evals.md` sets |

- Run a merge-only check locally only when no pull-request workflow exists, or to reproduce a CI failure.
- Merge only when the merge checks pass.
