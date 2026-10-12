---
name: test-install
description: Tests a Claude Code plugin the way its users receive it — installs a copy from a commit into a throwaway Claude Code configuration, checks that every file arrived and that it loads, runs its eval suite or real requests against that copy, then cleans up; can also package it for a Claude app upload. Use when the user wants to test or smoke-test a plugin as an end user would install it, before publishing or releasing it, or asks if it works outside their own setup. Not for reviewing eval cases.
argument-hint: "[plugin folder or name]"
---

# Test the installed plugin

Plugin: `$ARGUMENTS` (a folder, or a plugin name to find in the current repository; if empty, the plugin in the current directory). When a name matches more than one `.claude-plugin/plugin.json`, list their paths and ask which one.

This skill runs `claude` and `git` in a terminal. In a conversation with no shell, such as one in the Claude app, say so and stop.

**Never touch the user's own Claude Code configuration or project.** Every `claude` command below runs with `CLAUDE_CONFIG_DIR=<cfg>`, and every session runs in `<target>`, both throwaway folders outside the repository. Never copy credentials from the user's real configuration.

**Every run that calls the model counts against the user's plan or API bill.** Step 7 is where paid work is agreed: nothing paid runs, and no sign-in happens, before the user's go-ahead there.

## Why a copy

`claude --plugin-dir` and a local marketplace with a relative-path source load the plugin in place, from your working folder. Users get a copy in their plugin cache instead, and files outside the plugin folder or left out of git don't travel with it (docs: <https://code.claude.com/docs/en/plugins/loading#in-place-and-copied-plugins>). A `git-subdir` or `url` source over `file://` makes Claude Code copy the plugin from a commit, as it does for users.

The copy comes from a commit. If `git status --porcelain -- <plugin folder>` prints anything, tell the user the test covers the last commit only, and commit first only if they ask. If the plugin is not in a git repository, read `references/not-in-git.md`.

## Steps

1. **Check the tools.** Report what is missing and stop when `claude --version` is older than 2.1.293 (older releases refuse eval runs that grant Bash on Macs with Docker Desktop), when `git` is missing, or when the plugin has an eval suite (`evals/`, or the `experimental.evals` path in its `plugin.json`) and `git --version` is older than 2.31 (`claude plugin eval` refuses older git). If `CLAUDE_CODE_PLUGIN_CACHE_DIR` or `CLAUDE_CODE_PLUGIN_SEED_DIR` is set, start every `claude` command below with `env -u CLAUDE_CODE_PLUGIN_CACHE_DIR -u CLAUDE_CODE_PLUGIN_SEED_DIR`: the first moves the plugins folder out of `<cfg>`, the second brings other plugins into the test.
2. **Find the plugin.** It has `.claude-plugin/plugin.json`. Record its `name` and `version` ("none" when absent), the repository root (`git rev-parse --show-toplevel`), the plugin's path from that root (`.` when it is the root), and `git rev-parse HEAD`.
3. **Throwaway folders.** Run `mktemp -d` three times: `<cfg>` (configuration), `<mkt>` (marketplace), `<target>` (project). Before any `claude` command, write `<cfg>/settings.json` so a claude.ai sign-in brings none of the user's synced plugins, skills or connectors into the test (docs: <https://code.claude.com/docs/en/settings-reference>):

   ```json
   {
     "syncClaudeAiPlugins": false,
     "syncClaudeAiSkills": false,
     "disableClaudeAiConnectors": true
   }
   ```

4. **Marketplace.** Write `<mkt>/.claude-plugin/marketplace.json`. Use a `git-subdir` source when the plugin is a subfolder of the repository; when it is the repository root, use `{"source": "url", "url": "file://<absolute repo root>", "sha": "<HEAD>"}` instead.

   ```json
   {
     "name": "test-bench-local",
     "owner": { "name": "Plugin Test Bench" },
     "plugins": [
       {
         "name": "<plugin name>",
         "source": {
           "source": "git-subdir",
           "url": "file://<absolute repo root>",
           "path": "<plugin path from the repo root>",
           "sha": "<HEAD>"
         }
       }
     ]
   }
   ```

5. **Install and compare.**
   - `CLAUDE_CONFIG_DIR=<cfg> claude plugin marketplace add <mkt>`
   - `CLAUDE_CONFIG_DIR=<cfg> claude plugin install <name>@test-bench-local`
   - `<installPath>` is the `installPath` recorded for `<name>@test-bench-local` in `<cfg>/plugins/installed_plugins.json`. Compare its file list with `git ls-tree -r --name-only HEAD -- <plugin path>` and with the files on disk in the plugin folder. Call a file the copy lacks **needed** when one of the plugin's files names it (a skill, agent, command, hook, MCP or LSP config, script or the manifest), and **unreferenced** otherwise. A path the plugin's files reference outside its own folder is needed and never travels with the copy.
   - `CLAUDE_CONFIG_DIR=<cfg> claude plugin validate <installPath>`
   - If `marketplace add`, `install` or `validate` fails, report the error and go to step 11.
6. **Load check**, free: Claude Code reports what it loaded before it checks the login, so run it with no credentials and it never calls the model.
   - An Anthropic profile lives outside `<cfg>`: if `~/.config/anthropic` (`%APPDATA%\Anthropic` on Windows) holds an `active_config` file or a `default` profile, this run would sign in with it and be billed. Say so and ask before running it.
   - `cd <target> && env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u CLAUDE_CODE_OAUTH_TOKEN -u ANTHROPIC_PROFILE -u ANTHROPIC_FEDERATION_RULE_ID -u CLAUDE_CODE_USE_BEDROCK -u CLAUDE_CODE_USE_VERTEX -u CLAUDE_CODE_USE_FOUNDRY -u CLAUDE_CODE_USE_ANTHROPIC_AWS -u CLAUDE_CODE_USE_MANTLE CLAUDE_CONFIG_DIR=<cfg> claude -p --output-format stream-json --verbose "Reply OK."`
   - Read the `system/init` event; the "Not logged in" error after it is expected. The load passes when the plugin appears under `plugins` with a `path` that is `<installPath>` once both go through `realpath` (macOS reports `/var/folders/…` as `/private/var/folders/…`), and `plugin_errors` is absent (docs: <https://code.claude.com/docs/en/headless>). Otherwise report the error and go to step 11.
7. **Agree on the paid steps.**
   - Grants: the tools the plugin needs beyond reading, such as `Bash`, `Write`, `Edit`, `WebFetch(domain:<host>)` for each site it fetches, and its MCP tools. Take them from its skills, agents, README and eval cases. A skill's own `allowed-tools` can't widen an eval run's grants.
   - An eval run grants `Bash` only inside the OS sandbox: on Linux, `command -v bwrap socat` must find both; native Windows has none (use WSL2). Without it, drop `Bash` from the eval grants and say which cases will fail.
   - Paid steps: with an eval suite, the smoke test in step 9, one run per case (a case is a folder holding `case.yaml` or `prompt.md` under the eval directory), and real requests as an extra. Without one, real requests: take them from the plugin's README usage examples, or propose one to three from its skills' descriptions, two runs each; also suggest `claude plugin eval init` to draft a suite and the `review-evals` skill to check it.
   - When cases have a `scaffold_script`, ask whether the user wrote or trusts the suite: scaffold scripts run on this machine as the user, so step 9 adds `--scaffold` only on a yes.
   - Who pays: `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN` or a cloud provider's variables set in the shell authenticate the paid runs; otherwise the login of step 8.
   - Show the grants, the requests, the run counts and who pays, and wait. If the user declines everything paid, go to step 11.
8. **Sign in.** A new configuration has no login (docs: <https://code.claude.com/docs/en/authentication>). If step 7 found a credential in the shell, it authenticates the runs. Otherwise ask the user to run `CLAUDE_CONFIG_DIR=<cfg> claude auth login` in a separate terminal, and wait until `CLAUDE_CONFIG_DIR=<cfg> claude auth status` shows a login.
9. **Eval suite on the installed copy**, when agreed in step 7. The suite is `evals/`, or the `experimental.evals` path in `plugin.json`.
   - `cd <target> && CLAUDE_CONFIG_DIR=<cfg> claude plugin eval <name>@test-bench-local --runs 1 --ablation none --no-publish --keep-temp --allow-tools <grants>`. The target comes before `--allow-tools`; each grant is its own argument, quoted when it holds parentheses or `*`, as in `--allow-tools Write "Bash(npm test *)" "WebFetch(domain:example.com)"`. With no grants, leave out `--allow-tools`.
   - Add `--scaffold` when the user said yes in step 7. Without it, cases with a `scaffold_script` run without their fixtures: leave them out of the passed count and list them under Not tested. An installed plugin named as the target needs no trust prompt.
   - Results land in `<target>/evals/results/`. Report each case's score and failing graders; a case passes when its score meets the threshold, 1.0 by default. When a case fails, read `out/trace.jsonl` in the kept folder the eval printed: it is readable as is. Don't run git inside a kept folder: the eval's own notice warns against it.
   - A full run (both arms, 3 runs each by default) is `cases × 6` runs plus three judge calls per `llm` or `baseline` grader per run; offer it only as a follow-up.
10. **Real requests**, when agreed in step 7: read `references/manual-session.md`.
11. **Clean up**, even after a failure. First, if the plugin's README says it works in the Claude app, ask whether to build a zip to try it there; on a yes, read `references/claude-app.md`. Then, in this order:
    - `CLAUDE_CONFIG_DIR=<cfg> claude auth logout`, when step 8 signed in: on macOS the login is a Keychain entry keyed to `<cfg>`, which deleting the folder leaves behind.
    - Each kept eval folder `<kept>` is read-only, with a `sealed/` folder at mode 000: `chmod 700 <kept> <kept>/sealed && chmod -R u+rwX <kept> && rm -rf <kept>`.
    - Delete `<cfg>`, `<mkt>` and `<target>`, and the snapshot folder from `references/not-in-git.md` if there is one.

## Report

```markdown
## Install test: <name> <version or "no version"> @ <short sha>

**Verdict:** works as installed | works with warnings | fails as installed

- Copy: <installPath> — <n> files; missing from the copy: <needed and unreferenced files, or "none">
- Validate: <result>
- Load: <`plugins` entry from the init event, or the `plugin_errors` entry>
- Eval smoke test: <passed>/<cases> — <per failing case: grader and why>, or "not run: <why>"
- Requests: <per request: what ran, denials, result>, or "not run: <why>"
- Usage: <cost estimates Claude Code printed>
- Not tested: <uncommitted changes, other operating systems, the Claude app, anything skipped>
```

The verdict is the first rule that matches:

1. **fails as installed**: `marketplace add`, `install` or `validate` failed, the plugin is not under `plugins` in the init event or its `path` is not `<installPath>`, `plugin_errors` is present, or a needed file is missing from the copy.
2. **works with warnings**: `validate` reported warnings, an eval case failed, a request hit a permission denial, an unreferenced file is missing from the copy, or no eval case and no request ran.
3. **works as installed**: otherwise. Other operating systems and the Claude app go under Not tested and never change the verdict.

## Beyond this machine

- The eval run gives each case a temporary home and configuration with only the plugin loaded, but it uses this machine's `PATH` and installed programs: it proves independence from the user's setup, not from their machine. Other operating systems need CI or another machine.
- Not used: `--bare`, which skips installed plugins and the subscription login (docs: <https://code.claude.com/docs/en/headless>).
