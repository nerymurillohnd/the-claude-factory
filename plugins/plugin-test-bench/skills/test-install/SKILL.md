---
name: test-install
description: Tests a Claude Code plugin the way its users receive it — installs a copy from a throwaway local marketplace in a separate Claude Code configuration, checks that it loads and that every file arrived, runs its eval suite against the installed copy, optionally runs real prompts, then cleans everything up. Use when the user wants to test, smoke-test or try a plugin as an end user would install it, before publishing or releasing it, or asks whether a plugin works outside their own setup.
argument-hint: "[plugin folder or name]"
---

# Test the installed plugin

Plugin: `$ARGUMENTS` (a folder, or a name to find in the current repository; if empty, the plugin in the current directory).

**Never touch the user's own Claude Code configuration or project.** Every `claude` command below runs with `CLAUDE_CONFIG_DIR=<cfg>`, and every session runs in `<target>`, both throwaway folders outside the repository. Never copy credentials from the user's real configuration.

**Every run that calls the model counts against the user's plan or API bill.** Before each paid step (eval suite, prompts), say how many runs it starts and wait for the user's go-ahead.

## Why a copy

`claude --plugin-dir` and a local marketplace with a relative-path source load the plugin in place, from your working folder. Users get a copy in their plugin cache instead, and files outside the plugin folder or left out of git don't travel with it (docs: <https://code.claude.com/docs/en/plugins/loading#in-place-and-copied-plugins>). A `git-subdir` or `url` source over `file://` makes Claude Code copy the plugin from a commit, as it does for users.

The copy comes from a commit. If `git status --porcelain -- <plugin folder>` prints anything, tell the user the test covers the last commit only, and commit first only if they ask. If the plugin is not in a git repository, read `references/not-in-git.md`.

## Steps

1. **Check the tools.** `claude --version` is 2.1.288 or later (`claude purge`) and, when the plugin has an eval suite, `git --version` is 2.31 or later (`claude plugin eval` refuses older git). Report what is missing and stop.
2. **Find the plugin.** It has `.claude-plugin/plugin.json`. Record its `name` and `version`, the repository root (`git rev-parse --show-toplevel`), the plugin's path from that root, and `git rev-parse HEAD`.
3. **Throwaway folders.** Run `mktemp -d` three times: `<cfg>` (configuration), `<mkt>` (marketplace), `<target>` (project).
4. **Marketplace.** Write `<mkt>/.claude-plugin/marketplace.json`. Use a `git-subdir` source when the plugin is a subfolder of the repository; when it is the repository root, use `{"source": "url", "url": "file://<repo root>", "sha": "<HEAD>"}` instead.

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
   - The copy lives in `<cfg>/plugins/cache/test-bench-local/<name>/<version>/`. Compare its file list with `git ls-tree -r --name-only HEAD -- <plugin path>` and with the files on disk in the plugin folder: report every file the user has locally that the copy lacks (ignored by git, untracked, or outside the plugin folder), and every path the plugin's files reference outside its own folder.
   - `CLAUDE_CONFIG_DIR=<cfg> claude plugin validate <cache path>`
6. **Sign in.** A new configuration has no login (docs: <https://code.claude.com/docs/en/authentication>). If `ANTHROPIC_API_KEY` or a cloud provider's variables are set in the shell, they authenticate the runs. Otherwise ask the user to type `! CLAUDE_CONFIG_DIR=<cfg> claude auth login` and wait until `CLAUDE_CONFIG_DIR=<cfg> claude auth status` shows a login.
7. **Load check.**
   - `cd <target> && CLAUDE_CONFIG_DIR=<cfg> claude -p --output-format stream-json --verbose "Reply OK."`
   - In the `system/init` event, the plugin must appear under `plugins` with a `path` inside `<cfg>/plugins/cache/test-bench-local/`, and `plugin_errors` must be absent (docs: <https://code.claude.com/docs/en/headless>). Otherwise report the error and go to step 11.
8. **Grants.** List the tools the plugin needs beyond reading: `Bash`, `Write`, `Edit`, `WebFetch(domain:…)` for each site it fetches, its MCP tools. Take them from its skills, agents, README and eval cases, and confirm the list with the user. A skill's own `allowed-tools` can't widen an eval run's grants.
9. **Eval suite on the installed copy.** If the plugin has an eval directory (`evals/`, or the `experimental.evals` path in `plugin.json`), run a smoke test: one arm, one run per case. Say the case count first.
   - `cd <target> && CLAUDE_CONFIG_DIR=<cfg> claude plugin eval <name>@test-bench-local --runs 1 --ablation none --no-publish --keep-temp --allow-tools <grants>`
   - Add `--scaffold` when cases use a `scaffold_script`: it runs on the user's machine as the user, so only for a suite they wrote. An installed plugin named as the target needs no trust prompt.
   - Results land in `<target>/evals/results/`. Report each case's score and failing graders, and read `out/trace.jsonl` in a kept run folder when a case fails, before step 11 deletes them.
   - A full run (both arms, 3 runs each) is `cases × 6` runs plus judge calls; offer it only as a follow-up.
   - No eval suite: say so, and suggest `claude plugin eval init` to draft one and the `review-evals` skill to check it.
10. **Real prompts (optional).** Read `references/manual-session.md` when the user wants to watch the plugin answer real requests, or when it has no eval suite.
11. **Clean up**, even after a failure, in this order:
    - `CLAUDE_CONFIG_DIR=<cfg> claude auth logout`, when step 6 signed in: on macOS the login is a Keychain entry keyed to `<cfg>`, which deleting the folder leaves behind.
    - `CLAUDE_CONFIG_DIR=<cfg> claude purge <target> --yes`
    - Delete `<cfg>`, `<mkt>` and `<target>`, and any `--keep-temp` folders the eval printed.

## Report

```markdown
## Install test: <name> <version> @ <short sha>

**Verdict:** works as installed | works with warnings | fails as installed

- Copy: <cache path> — <n> files; missing from the copy: <files or "none">
- Validate: <result>
- Load: <`plugins` entry from the init event, or the `plugin_errors` entry>
- Eval smoke test: <passed>/<cases> — <per failing case: grader and why>
- Prompts: <per prompt: what ran, denials, result>
- Usage: <cost estimates Claude Code printed>
- Not tested: <uncommitted changes, other operating systems, the Claude app, anything skipped>
```

"Fails as installed" when the plugin did not load or a file it needs is missing from the copy; "with warnings" for failing eval cases, permission denials, or untested parts.

## Beyond this machine

- The eval run gives each case a temporary home and configuration with only the plugin loaded, but it uses this machine's `PATH` and installed programs: it proves independence from the user's setup, not from their machine. Other operating systems need CI or another machine.
- For the Claude app (web and desktop), read `references/claude-app.md` when the plugin is meant to work there too.
- Not used: `--bare`, which loads plugins in place and needs an API key (docs: <https://code.claude.com/docs/en/headless>).
