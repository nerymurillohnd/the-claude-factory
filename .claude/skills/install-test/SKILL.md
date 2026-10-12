---
name: install-test
description: Tests a plugin of The Claude Factory as a third party receives it — a copied install from a git-sourced local marketplace in a throwaway Claude Code config, a real session in a throwaway project, the plugin's eval suite against the installed copy, then full cleanup. Use only when Nery explicitly asks to test, try or smoke-test a plugin as users install it, or before a release.
argument-hint: "<plugin-name>"
---

# Install test

Plugin: `$ARGUMENTS`. Never test in Nery's real `~/.claude` or inside the repository: every command below runs with `CLAUDE_CONFIG_DIR=<cfg>`, and sessions run in `<target>`.

## Why this setup

- `--plugin-dir` and a local marketplace with a relative-path `source` load the plugin in place; users get a copy in the plugin cache (docs: plugins/loading, In-place and copied plugins). A `git-subdir` source over `file://` makes Claude Code copy it, as for users.
- The copy comes from a commit, not the working tree. If `git status --porcelain plugins/<name>` prints anything, tell Nery the test covers `HEAD` only, and commit first only if Nery asks.

## Steps

1. **Throwaway folders.** Run `mktemp -d` three times, outside the repository: `<cfg>` (config), `<mkt>` (marketplace), `<target>` (project).
2. **Marketplace.** Write `<mkt>/.claude-plugin/marketplace.json`:

   ```json
   {
     "name": "factory-install-test",
     "owner": { "name": "Nery Murillo" },
     "plugins": [
       {
         "name": "<name>",
         "source": {
           "source": "git-subdir",
           "url": "file://<absolute repo path>",
           "path": "plugins/<name>",
           "sha": "<output of git rev-parse HEAD>"
         }
       }
     ]
   }
   ```

3. **Install.**
   - `CLAUDE_CONFIG_DIR=<cfg> claude plugin marketplace add <mkt>`
   - `CLAUDE_CONFIG_DIR=<cfg> claude plugin install <name>@factory-install-test`
   - Confirm the copy: `ls <cfg>/plugins/cache/factory-install-test/<name>/`, and `CLAUDE_CONFIG_DIR=<cfg> claude plugin list`.
4. **Sign in.** A new config has no login (docs: authentication). Ask Nery to run `! CLAUDE_CONFIG_DIR=<cfg> claude auth login` once. Never copy credentials from the real config.
5. **Session test.** In `<target>`, add the fixture the plugin needs (for `skill-diagnostics`, a small skill folder). Run each realistic prompt from the plugin README's Usage section, both as the slash command and as a natural request:
   - `cd <target> && CLAUDE_CONFIG_DIR=<cfg> claude -p --output-format json "<prompt>"`
   - Report per prompt: the result text, `permission_denials`, `total_cost_usd`, and whether the plugin's components ran (skill, agents, hooks).
   - Ask Nery before the first paid run, with the number of runs and an estimate.
6. **Eval suite.** For a plugin with `evals/`, run it against the installed copy, as `.claude/rules/evals.md` says for a local smoke test:
   - `cd <target> && CLAUDE_CONFIG_DIR=<cfg> claude plugin eval <name>@factory-install-test --runs 1 --ablation none --model sonnet --judge-model opus --no-publish --trust-plugin`
   - Ask Nery before running it, with the case count and the estimated cost.
7. **Cowork.** Cowork reads plugins from the claude.ai account, not from `<cfg>`. Build a zip of the committed plugin with `git archive`, stamp `version` as `<version>-test.<short sha>`, put it in `~/Downloads`, and tell Nery to upload it in **Customize** → **Plugins** and run the same prompts in a Cowork task.
8. **Clean up.**
   - `CLAUDE_CONFIG_DIR=<cfg> claude auth logout` - Run first: on macOS the login lives in a Keychain entry keyed to `<cfg>`, which deleting the folder leaves behind (docs: authentication, Credential management).
   - `CLAUDE_CONFIG_DIR=<cfg> claude purge <target> --yes`
   - Delete `<cfg>`, `<mkt>` and `<target>`.

## Report

- What was installed: plugin, version, commit SHA, cache path.
- Per prompt and per eval case: pass or fail, with raw output.
- Every permission prompt or denial, and every component that did not run.
- Total cost, and what was not tested (Cowork until Nery reports back).
