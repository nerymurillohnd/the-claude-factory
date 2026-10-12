---
name: test-installed-plugin
description: Tests a plugin of The Claude Factory as a third party receives it — a copied install from a git-sourced local marketplace in a throwaway Claude Code config, a load check, the eval suite against the installed copy (temporary home, nothing personal loaded), an optional manual session, a Claude app test zip, then full cleanup. Use only when Nery explicitly asks to test, try or smoke-test a plugin as users install it, including before a release.
argument-hint: "<plugin-name>"
---

# Test the installed plugin

Plugin: `$ARGUMENTS`. Never test in Nery's real `~/.claude` or inside the repository: every command below runs with `CLAUDE_CONFIG_DIR=<cfg>`, and sessions run in `<target>`.

## What each test proves

- **Copied install** (steps 2–4): users get a copy in the plugin cache. `--plugin-dir` and a local marketplace with a relative-path `source` load in place (docs: plugins/loading, In-place and copied plugins); use them only to iterate while developing. A `git-subdir` source over `file://` makes Claude Code copy the plugin, as for users.
- **Eval suite** (step 6): the main proof. Each run gets a temporary home, working directory and Claude Code configuration, with only the plugin loaded (docs: plugin-evals, How runs are isolated). It shares this machine's `PATH` and system, so it proves independence from Nery's setup, not from this machine.
- **Other machines**: CI. `validate.yml` runs each plugin's scripts by path (`.github/scripts/tests/<plugin>/by_path.sh`) on Linux, macOS and Windows with Python 3.9 and 3.13; `evals.yml` runs the full suite on an Ubuntu runner. No official page gives a recipe for testing a plugin inside a container; only seeding is documented (docs: plugins/org, Seed containers and CI).
- **Claude app** (step 8): only a claude.ai install reaches it. A conversation runs as a Cowork session when it can and as a chat conversation otherwise, where agents, hooks and local MCP servers don't run. Which interpreters the app provides is not documented.
- **Not used**: `--bare`. It loads the plugin in place, sends no skill listing, gives Claude only Bash, file read and file edit tools, and needs an API key (`ANTHROPIC_API_KEY` or `apiKeyHelper`), never a subscription login (docs: headless, Start faster with bare mode).
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
   - Confirm the copy: `ls <cfg>/plugins/cache/factory-install-test/<name>/`.
4. **Sign in, then check the load.** A new config has no login (docs: authentication). Ask Nery to run `! CLAUDE_CONFIG_DIR=<cfg> claude auth login` once; never copy credentials from the real config. Then:
   - `cd <target> && CLAUDE_CONFIG_DIR=<cfg> claude -p --output-format stream-json --verbose "Reply OK."`
   - In the `init` event, the plugin is listed under `plugins` with its `path` under `<cfg>/plugins/cache/factory-install-test/`, and `plugin_errors` is absent (docs: plugins/org, Confirm the rollout). Stop and report otherwise.
5. **Grants.** Take the plugin's `allow_tools` from `.github/scripts/evals-config.json`. In a `-p` run with no host, anything that would prompt is denied (docs: headless, Turn off permission prompts in unattended runs), and a run with no mode set can start in auto mode, which drops a bare `Bash` grant (docs: headless, Auto-approve tools); so the manual session pins `--permission-mode dontAsk`.
6. **Eval suite on the installed copy.** For a plugin with `evals/`, run a smoke test as `.claude/rules/evals.md` says:
   - `cd <target> && CLAUDE_CONFIG_DIR=<cfg> claude plugin eval <name>@factory-install-test --runs 1 --ablation none --model sonnet --judge-model opus --scaffold --no-publish --keep-temp --allow-tools <grants>`
   - An installed plugin named as the target skips the trust prompt (docs: plugin-evals, Trust the plugin directory), so no `--trust-plugin`.
   - Results go to `<target>/evals/results/`: report them, with the kept sandbox paths, before step 9 deletes `<target>`.
   - Ask Nery before running it, with the case count: it uses Nery's plan, and Claude Code reports a list-price estimate of that usage.
7. **Manual session (optional).** Run when Nery wants to watch a real conversation; it isolates the config, not the home folder. In `<target>`, add the fixture the plugin needs (for `skill-diagnostics`, a small skill folder), then run each realistic prompt from the plugin README's Usage section, as the slash command and as a natural request:
   - `cd <target> && CLAUDE_CONFIG_DIR=<cfg> claude -p --output-format json --permission-mode dontAsk --allowedTools <grants> "<prompt>"`
   - Report per prompt: the result text, `permission_denials`, `total_cost_usd`, and whether the plugin's components ran (skill, agents, hooks).
   - Ask Nery before the first run, with the number of runs: each one uses Nery's plan.
8. **Claude app.** Build a zip of the committed plugin with `git archive`, stamp `version` as `<version>-test.<short sha>`, put it in `~/Downloads`, and tell Nery to upload it in **Customize** → **Plugins** → **Add** → **Upload plugin** and run the same prompts in a Cowork session and, when the plugin ships agents or hooks, in a chat conversation too.
9. **Clean up.**
   - `CLAUDE_CONFIG_DIR=<cfg> claude auth logout` - Run first: on macOS the login lives in a Keychain entry keyed to `<cfg>`, which deleting the folder leaves behind (docs: authentication, Credential management).
   - `CLAUDE_CONFIG_DIR=<cfg> claude purge <target> --yes`
   - Delete `<cfg>`, `<mkt>` and `<target>`.

## Report

- What was installed: plugin, version, commit SHA, cache path, and the `init` event's `plugins` entry.
- Per eval case and per prompt: pass or fail, with raw output.
- Every permission denial, and every component that did not run.
- Usage (the list-price estimate Claude Code reports), and what was not tested: other machines until CI runs, the Claude app until Nery reports back.
