# CI/CD for a public plugin marketplace

How a public marketplace's GitHub Actions workflows check every change and release every new version, and how to harden them. Facts come from the Claude Code docs and GitHub Docs, read on 2026-11-16 and checked against Claude Code 2.1.325. A line marked **(pattern)** is a design that follows from those facts but that no official page prescribes. A line marked **(observed)** was seen in a working marketplace's CI but isn't stated in the docs.

## Contents

- [What CI is for](#what-ci-is-for)
- [Install Claude Code on the runner](#install-claude-code-on-the-runner)
- [The validate workflow](#the-validate-workflow)
- [The release workflow](#the-release-workflow)
- [Harden every workflow](#harden-every-workflow)
- [Make the checks gate the merge](#make-the-checks-gate-the-merge)
- [Done when](#done-when)
- [Documentation References](#documentation-references)

## What CI is for

Every push to the default branch reaches users at their next update, because the catalog users add is that branch. Local checks run only when someone remembers them. CI has two jobs:

- **Validate** each pull request and each push, so a broken manifest, a mismatched version or an entry pointing at a missing folder never reaches the branch users read.
- **Release** each new version (a tag and, if wanted, a GitHub Release) only after validation passes, so a tag always names a version that passed.

When a marketplace has one maintainer and no CI, these checks still have to happen. Run them by hand before each push, and say in the report that nothing enforces them.

## Install Claude Code on the runner

`claude plugin validate`, `claude plugin tag` and `claude plugin test` run from the `claude` binary. Pin the version, so a Claude Code release can't change what passes without a commit in the repository. Each route is in "Advanced installation options" on https://code.claude.com/docs/en/setup:

- **Native installer, pinned**: `curl -fsSL https://claude.ai/install.sh | bash -s <version>`. It also accepts `stable` or `latest`.
- **npm**: `npm install -g @anthropic-ai/claude-code@<version>`. The package needs Node.js 22 or later. When `npm --version` starts with `12`, the setup page sends you to "Fix an npm 12 install" instead. Don't install with `sudo`.
- **Signed apt, dnf or apk repository**: each repository has a `stable` and a `latest` channel, is signed with the Claude Code release signing key, and never updates on its own. Verify the key as the setup page's tab shows.

Follow the install with a step that runs `claude --version` and fails when the version isn't the pinned one, so a changed install route can't slip a different binary in.

`claude plugin validate`, `claude plugin tag` and `claude plugin test` ran with no sign-in in this marketplace's own CI on 2.1.325 **(observed)**. The docs state "Needs no session, sign-in or network" only for `claude plugin test`. `claude plugin eval` needs credentials, such as `ANTHROPIC_API_KEY` stored as a repository secret ("Run evals in CI", https://code.claude.com/docs/en/plugin-evals#run-evals-in-ci).

## The validate workflow

Trigger it on `pull_request` and on `push` to the default branch.

1. Check out the repository with `persist-credentials: false`, because this job pushes nothing.
2. Install Claude Code, pinned, as above.
3. Run `claude plugin validate --strict .` at the repository root. With a `.claude-plugin/marketplace.json` there, it validates the catalog.
4. Run `claude plugin validate --strict <plugin-dir>` for every plugin directory. A marketplace run doesn't open the listed plugins' skill, agent, command, hook or MCP files (`cli-commands-guide`, `plugin validate`).
5. Fail the job on the exit code. Exit `1` means errors, or warnings under `--strict`; exit `2` means the validator itself failed. Scripts read the exit code or `--json`, never the output symbols, which change when there is no TTY.

A plugin that leaves `version` out to track commits gets a missing-`version` warning, which `--strict` turns into a failure. "Prepare your plugin for release" (https://code.claude.com/docs/en/plugins/publish#prepare-your-plugin-for-release) says to drop `--strict` in that case. Validate such a plugin without `--strict`, and make the job fail on its errors. Its other warnings then don't fail the job, so read them in the run's log.

Add these checks when the repository needs them:

- **Mods**: `claude plugin test <dir>` exits `1` when a test fails, "so it works in CI" (https://code.claude.com/docs/en/plugins/mods/test).
- **Evals**: every run is a real model call on the account that owns the key. Run them in CI only with the owner's agreement on cost. Use the flags "Run evals in CI" gives (`--trust-plugin`, `--json`, pinned `--model` and `--judge-model`, `--no-publish`, `--max-cost-usd`), and run only the suites of plugins the pull request changed **(pattern)**.
- **The repository's own linters** for any scripts the plugins ship.

## The release workflow

**(pattern)** This applies only to plugins that set `version`. With the commit-SHA model, every push to the default branch is already the release, and there is nothing to tag.

1. Run it after validation passes on a push to the default branch: as a job with `needs:` on the validate job, or as a workflow called from it.
2. Check out with `fetch-depth: 0`, so the existing tags are visible.
3. For each plugin whose current version has no `<name>--v<version>` tag, run `claude plugin tag <plugin-dir>`. It creates that annotated tag after checking that `plugin.json` and the marketplace entry agree on the version. It refuses a dirty working tree, a tag that already exists, and a plugin with no `version`.
4. Push the tag (`--push`, or `git push` with the job's token). Optionally create a GitHub Release for it from that version's CHANGELOG section.
5. Give only this job `permissions: contents: write`.

Never move or recreate a tag that users may already have fetched. To fix a bad release, ship a new version.

## Harden every workflow

From "Secure use reference" (https://docs.github.com/en/actions/reference/security/secure-use):

- **Least privilege**: "set the default permission for the `GITHUB_TOKEN` to read access only for repository contents", then raise it per job. A workflow-level `permissions: {}` with per-job grants does this.
- **Pin actions to a full-length commit SHA**: this "helps mitigate the risk of a bad actor adding a backdoor to the action's repository". Take the SHA from the action's own repository, not a fork, and keep the version tag in a comment beside it.
- **Untrusted input**: never put `${{ github.event.* }}` text, such as a pull request title, straight into a `run:` script. Pass it through an environment variable ("Use an intermediate environment variable").
- **Privileged triggers**: `pull_request_target` and `workflow_run`, combined with a checkout of an untrusted pull request, "can be exploited to take over a repository". A public marketplace receives pull requests from strangers, so use `pull_request` for validation.
- **Keep pins current**: a `.github/dependabot.yml` with `package-ecosystem: "github-actions"`, `directory: "/"` and a `schedule.interval` raises pull requests for outdated actions (https://docs.github.com/en/code-security/dependabot/working-with-dependabot/keeping-your-actions-up-to-date-with-dependabot). Dependabot "will not create alerts for actions pinned to SHA values", so the version updates are what keep pinned actions current.

Check each workflow with `actionlint`, and with `zizmor` for security findings, when they are available **(pattern)**.

## Make the checks gate the merge

A workflow that fails but doesn't block the merge only reports. A ruleset on the default branch makes it a gate ("Available rules for rulesets", https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets):

- **Require status checks to pass before merging**: name the validate job. Without it, "collaborators can merge the branch at any time".
- **Require a pull request before merging**: changes reach the branch users read only through a pull request.
- **Block force pushes** and **Restrict deletions**: a force push can rewrite the commit a user's install points at.

A ruleset is a repository setting, not a file. It takes effect on GitHub as soon as it is saved, so it needs the owner's yes. The owner creates it in the repository settings, or approves the API call that creates it.

## Done when

- `actionlint` passes on every workflow, or the report says the check couldn't run.
- Every action is pinned to a full SHA with its version in a comment, and every job declares its own `permissions`.
- The first run on GitHub after the push is green, and a deliberately broken manifest in a test pull request fails it. Seeing those runs needs the push, so until the owner pushes, report this check as waiting on them.

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/publish#prepare-your-plugin-for-release
- https://code.claude.com/docs/en/setup.md — install routes and version pinning ("Advanced installation options")
- https://code.claude.com/docs/en/plugins/cli-reference.md — `plugin validate`, `plugin tag`, `plugin test`
- https://code.claude.com/docs/en/plugin-evals.md — "Run evals in CI"
- https://code.claude.com/docs/en/plugins/mods/test.md — mod tests in CI
- https://docs.github.com/en/actions/reference/security/secure-use — token permissions, SHA pinning, script injection, privileged triggers
- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax — workflow keys (`on`, `permissions`, `concurrency`, `needs`)
- https://docs.github.com/en/code-security/dependabot/working-with-dependabot/keeping-your-actions-up-to-date-with-dependabot — Dependabot for actions
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets — rules that gate the merge
