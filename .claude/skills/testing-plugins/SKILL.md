---
name: testing-plugins
description: Use to build or run the eval suite of any plugin, mods included, when evals are requested for it, to run the live checks of a ready plugin's MCP servers and MCP hooks, and to diagnose install, load or marketplace errors of plugins from a public GitHub marketplace. Not for a mod's own tests and troubleshooting, unit tests, type checks, linters or validate runs.
---

# GitHub plugin QA

Tests plugins that are published, or about to be published, in a **public GitHub marketplace**, and diagnoses the errors those plugins and marketplaces produce. Three jobs: (A) evals with a light local pilot and smoke and a full CI suite, (B) troubleshooting, (C) live checks of a ready plugin's MCP servers.

## Scope

In scope: Claude Code plugins whose marketplace is a public GitHub repo (`owner/repo` or an `https://github.com/...` URL) added with `claude plugin marketplace add`.

Out of scope. Say so in one sentence and stop; do not improvise a fix:
- **A mod's own tests and troubleshooting** (`claude plugin test`, a hooks module that does not load or a skipped hook): `testing-mods`. A mod's eval suite is in scope here, as for any plugin: `/en/plugin-evals` excludes no kind of plugin.
- Unit tests, type checks, linters and `claude plugin validate` runs: they belong to whoever writes the code.
- Local-path marketplaces, GitHub Enterprise Server, `claudeai-*` (claude.ai) marketplaces, `skills-dir` plugins.
- Anything blocked by organization policy (`blocked by enterprise policy`, `strictKnownMarketplaces`, `disableSideloadFlags`...): the fix belongs to an administrator.

## When to act

Only when asked. Never add evals to a plugin, or run them, on your own initiative.

- **New plugin, evals requested:** build or complete its suite, run the local pilot, hand the full run to CI.
- **Existing plugin without evals, edited, and nobody asked for evals:** do nothing about evals. At most mention in one line that it has no suite.
- **A user pastes an install, load or marketplace error:** go to part B.
- **Nery says a plugin with an MCP server, or with a hook that matches or calls MCP tools, is ready:** go to part C. Never before: while the plugin is being shaped, its build runs static checks only.

## Ground truth first

Plugin evals and plugin loading change with every Claude Code release, and docs and changelog sometimes disagree (the changelog wins; say which one you used).

1. `claude --version`, then `claude plugin eval --help` as separate plain commands. The CLI is the authority for flags.
2. The references here were checked against the docs (eval policy on 2026-10-26, troubleshooting on 2026-10-25), against `claude` v2.1.310 `--help`, and against every `plugin eval` and marketplace entry of the changelog from v2.1.269, when `plugin eval` was added, to v2.1.310. If the installed version is newer, check the changelog for `plugin eval` and `marketplace` from v2.1.310 on before relying on a flag or message.
3. The official docs win over this skill, this repository's rules and its records. When they disagree, follow the docs, say so, and correct the project text.
4. Mark anything you could not verify as unverified and say what it affects.

## A. Evals: pilot and smoke locally, full suite in CI

Read [references/eval-policy.md](references/eval-policy.md) before running anything.

1. **Gate.** Confirm the plugin is in scope and has (or is getting) `evals/`. For a new suite, use `claude plugin eval init` (interactive) or `claude plugin eval init --bare <case>`. Cases still need: one grader on the result, one on the steps, at least four should-trigger prompts in users' words plus one or two near misses.
2. **Pilot (local, light).** `claude plugin eval . --runs 1 --ablation none --no-publish`, narrowed with `--case <glob>` to the cases the edit can affect; the smoke is the same command with `--tag smoke`. Target first, flags after. Add `--scaffold` when a case has a `scaffold_script`: the docs allow it for "suites you or your organization wrote", which a suite of this repository is. State the cost estimate (cases × 1 run × 1 arm, plus judge calls for `llm` graders) and get a yes before running. For a suite or plugin someone else wrote, `--trust-plugin` and `--scaffold` need the user's go-ahead by name; `--allow-real-servers` and `--mocks off` always do, because they call real services.
3. **Report the pilot honestly.** It shows that cases load, run and grade. It has no baseline, so there is no Δ, and one run is noisy. Never call a pilot "the suite passed".
4. **Full suite = CI, only for a new plugin or an existing plugin with evals whose components or dependencies changed.** Otherwise CI skips it. Use the repo's existing eval workflow if there is one and audit it with the checklist in the reference; otherwise adapt [assets/evals-ci.yml](assets/evals-ci.yml), which uses [scripts/changed-eval-plugins.sh](scripts/changed-eval-plugins.sh) to pick targets, as the reference's "The CI template" says. Do not push, open a PR or spend CI money without the user's approval.

## B. Troubleshooting

Read [references/troubleshooting.md](references/troubleshooting.md).

1. Get the **exact message** and the command that produced it. Search the reference by message text: it is grouped by the stage that emits the message, which is not always the command that was run.
2. If the message is not in the reference, or is out of scope, say so. Do not guess from similar messages.
3. Separate repo problems from local state: reproduce in a throwaway configuration that leaves your own settings and plugins untouched, as a user without a GitHub SSH key would: `env -u CLAUDE_CODE_PLUGIN_DIRS CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1 CLAUDE_CONFIG_DIR="$T/config" CLAUDE_CODE_PLUGIN_CACHE_DIR="$T/plugins" claude plugin marketplace add <owner/repo>`, then `... claude plugin install <plugin>@<marketplace>` with the same prefix, where `T` is a `mktemp -d` folder. Works there but not on the user's machine means local state (settings, cache, `installed_plugins.json`, git credentials). Fails in both means the marketplace repo or the plugin entry.
4. Apply one fix, then check the success signal the reference lists for that entry (for example `Successfully added marketplace: <name>`).

## C. Live MCP checks

Read [references/mcp-live-checks.md](references/mcp-live-checks.md) and work through it: load with the option unset, set it and reload, call a tool from the main conversation and from an agent, the Claude app steps, and the cases of hooks that match or call MCP tools. They start the plugin's servers and call real tools, so they run only after the static checks pass and only on Nery's word that the plugin is ready.

## Answer format

Lead with the command or file change, ready to copy, target first in every `claude plugin eval` command. Then the evidence: what you ran or read (`--help`, doc page, changelog entry, command output) and what remains unverified. After a pilot, add what was run, what it showed, and what is left to CI. Keep explanation short.
