---
name: testing-plugins
description: Use to build or run the eval suite of a plugin that has no mods, when evals are requested for it or a plugin that has evals was edited, and to diagnose install, load or marketplace errors of plugins from a public GitHub marketplace. Not for mods, and not for tests other than evals.
---

# GitHub plugin QA

Tests plugins that are published, or about to be published, in a **public GitHub marketplace**, and diagnoses the errors those plugins and marketplaces produce. Two jobs: (A) evals with a light local pilot and a full CI suite, (B) troubleshooting.

## Scope

In scope: Claude Code plugins whose marketplace is a public GitHub repo (`owner/repo` or an `https://github.com/...` URL) added with `claude plugin marketplace add`.

Out of scope. Say so in one sentence and stop; do not improvise a fix:
- **Mods**: plugins whose `hooks/hooks.json` lists a hooks module under `modules`, whatever their category.
- Tests other than evals: unit tests, type checks, linters and `claude plugin validate` runs.
- Local-path marketplaces, GitHub Enterprise Server, `claudeai-*` (claude.ai) marketplaces, `skills-dir` plugins.
- Anything blocked by organization policy (`blocked by enterprise policy`, `strictKnownMarketplaces`, `disableSideloadFlags`...): the fix belongs to an administrator.

## When to act

Only when asked. Never add evals to a plugin, or run them, on your own initiative.

- **New plugin, evals requested:** build or complete its suite, run the local pilot, hand the full run to CI.
- **Existing plugin that has `evals/` and was edited:** run the local pilot on the affected cases, make sure CI will run the full suite.
- **Existing plugin without evals, edited, and nobody asked for evals:** do nothing about evals. At most mention in one line that it has no suite.
- **A user pastes an install, load or marketplace error:** go to part B.

## Ground truth first

Plugin evals and plugin loading change with every Claude Code release, and docs and changelog sometimes disagree (the changelog wins; say which one you used).

1. `claude --version`, then `claude plugin eval --help` as separate plain commands. The CLI is the authority for flags.
2. The references here were checked on 2026-10-25 against the docs, against `claude` v2.1.310 `--help`, and against every `plugin eval` and marketplace entry of the changelog from v2.1.269, when `plugin eval` was added, to v2.1.310. If the installed version is newer, check the changelog for `plugin eval` and `marketplace` from v2.1.310 on before relying on a flag or message.
3. Mark anything you could not verify as unverified and say what it affects.

## A. Evals: pilot locally, full suite in CI

Read [references/eval-policy.md](references/eval-policy.md) before running anything.

1. **Gate.** Confirm the plugin is in scope and has (or is getting) `evals/`. For a new suite, use `claude plugin eval init` (interactive) or `claude plugin eval init --bare <case>`. Cases still need: one grader on the result, one on the steps, at least four should-trigger prompts in users' words plus one or two near misses.
2. **Pilot (local, light).** `claude plugin eval . --runs 1 --ablation none --no-publish`, narrowed with `--case <glob>` to the cases the edit can affect. Target first, flags after. State the cost estimate (cases × 1 run × 1 arm, plus judge calls for `llm` graders) and get a yes before running. Never add `--trust-plugin`, `--scaffold`, `--allow-real-servers` or `--mocks off` unless the user's go-ahead names that flag.
3. **Report the pilot honestly.** It shows that cases load, run and grade. It has no baseline, so there is no Δ, and one run is noisy. Never call a pilot "the suite passed".
4. **Full suite = CI, only for plugins with evals that are new or edited.** An unedited plugin with evals is skipped. Use the repo's existing eval workflow if there is one and audit it with the checklist in the reference; otherwise adapt [assets/evals-ci.yml](assets/evals-ci.yml), which uses [scripts/changed-eval-plugins.sh](scripts/changed-eval-plugins.sh) to pick targets. Do not push, open a PR or spend CI money without the user's approval.

## B. Troubleshooting

Read [references/troubleshooting.md](references/troubleshooting.md).

1. Get the **exact message** and the command that produced it. Search the reference by message text: it is grouped by the stage that emits the message, which is not always the command that was run.
2. If the message is not in the reference, or is out of scope, say so. Do not guess from similar messages.
3. Separate repo problems from local state: reproduce in a throwaway configuration that leaves your own settings and plugins untouched, as a user without a GitHub SSH key would: `env -u CLAUDE_CODE_PLUGIN_DIRS CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1 CLAUDE_CONFIG_DIR="$T/config" CLAUDE_CODE_PLUGIN_CACHE_DIR="$T/plugins" claude plugin marketplace add <owner/repo>`, then `... claude plugin install <plugin>@<marketplace>` with the same prefix, where `T` is a `mktemp -d` folder. Works there but not on the user's machine means local state (settings, cache, `installed_plugins.json`, git credentials). Fails in both means the marketplace repo or the plugin entry.
4. Apply one fix, then check the success signal the reference lists for that entry (for example `Successfully added marketplace: <name>`).

## Answer format

Lead with the command or file change, ready to copy, target first in every `claude plugin eval` command. Then the evidence: what you ran or read (`--help`, doc page, changelog entry, command output) and what remains unverified. After a pilot, add what was run, what it showed, and what is left to CI. Keep explanation short.
