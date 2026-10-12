---
name: install-test
description: Tests a plugin of The Claude Factory as a third party receives it — a copied install from a git-sourced local marketplace in a throwaway Claude Code config, the plugin's eval suite against the installed copy (temporary home, nothing personal loaded), an optional manual session, a Cowork test zip, then full cleanup. Use only when Nery explicitly asks to test, try or smoke-test a plugin as users install it, or before a release.
argument-hint: "<plugin-name>"
---

# Install test

Plugin: `$ARGUMENTS`. Never test in Nery's real `~/.claude` or inside the repository: every command below runs with `CLAUDE_CONFIG_DIR=<cfg>`, and sessions run in `<target>`.

## What each test proves

- **Copied install** (steps 2–3): users get a copy in the plugin cache; `--plugin-dir` and a local marketplace with a relative-path `source` load in place (docs: plugins/loading, In-place and copied plugins). A `git-subdir` source over `file://` makes Claude Code copy it, as for users.
- **Eval suite** (step 5): the main proof. Each run gets a temporary home, working directory and Claude Code configuration, with only the plugin loaded; no user settings, hooks, `CLAUDE.md`, memory, skills or other plugins (docs: plugin-evals, How runs are isolated). It still runs on this machine with this shell's `PATH`, so it proves independence from Nery's setup, not from that machine.
- **Other machines**: CI proves it. `validate.yml` runs the plugin's scripts by path on Linux, macOS and Windows with Python 3.9 and 3.13; `evals.yml` runs the full eval suite on an Ubuntu runner. The docs name a container or CI runner as the isolated environment for plugin code (docs: plugin-evals, Trust the plugin directory).
- **Cowork** (step 7): only a claude.ai upload reaches it.
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
5. **Eval suite on the installed copy.** For a plugin with `evals/`, run a smoke test as `.claude/rules/evals.md` says, with the tool grants for the plugin in `.github/scripts/evals-config.json`:
   - `cd <target> && CLAUDE_CONFIG_DIR=<cfg> claude plugin eval <name>@factory-install-test --runs 1 --ablation none --model sonnet --judge-model opus --scaffold --no-publish --allow-tools <grants>`
   - Ask Nery before running it, with the case count and the estimated cost.
6. **Manual session (optional).** Run when Nery wants to watch a real conversation; it isolates the config, not the home folder. In `<target>`, add the fixture the plugin needs (for `skill-diagnostics`, a small skill folder), then run each realistic prompt from the plugin README's Usage section, as the slash command and as a natural request:
   - `cd <target> && CLAUDE_CONFIG_DIR=<cfg> claude -p --output-format json "<prompt>"`
   - Report per prompt: the result text, `permission_denials`, `total_cost_usd`, and whether the plugin's components ran (skill, agents, hooks).
   - Ask Nery before the first paid run, with the number of runs and an estimate.
7. **Cowork.** Cowork reads plugins from the claude.ai account, not from `<cfg>`. Build a zip of the committed plugin with `git archive`, stamp `version` as `<version>-test.<short sha>`, put it in `~/Downloads`, and tell Nery to upload it in **Customize** → **Plugins** and run the same prompts in a Cowork task.
8. **Clean up.**
   - `CLAUDE_CONFIG_DIR=<cfg> claude auth logout` - Run first: on macOS the login lives in a Keychain entry keyed to `<cfg>`, which deleting the folder leaves behind (docs: authentication, Credential management).
   - `CLAUDE_CONFIG_DIR=<cfg> claude purge <target> --yes`
   - Delete `<cfg>`, `<mkt>` and `<target>`.

## Report

- What was installed: plugin, version, commit SHA, cache path.
- Per eval case and per prompt: pass or fail, with raw output.
- Every permission prompt or denial, and every component that did not run.
- Total cost, and what was not tested: other machines until CI runs, Cowork until Nery reports back.
