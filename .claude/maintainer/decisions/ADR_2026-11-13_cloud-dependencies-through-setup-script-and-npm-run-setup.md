---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Install the repository's dependencies in cloud sessions through the setup script and npm run setup

## Scope

The `setup` npm script in the root `package.json`, and step 5 of the `the-claude-factory` cloud environment's setup script, which also serves the owner's Claude Projects threads. Maintainer scope. The owner's own machine is out of scope: there `node_modules/` and `.venv/` persist and the owner runs `npm ci` or `npm run setup` by hand.

## Context and problem statement

`node_modules/` and `.venv/` are git-ignored, so a clone never brings them, and the maintainer checks need both: Biome and TypeScript come from `node_modules`, and `basedpyright -p scripts` reads `.venv` directly (without it, 5 unresolved-import errors on 2026-11-13). The owner reported that cloud sessions started without `node_modules`, which broke tools and plugins.

The docs at code.claude.com/docs/en/cloud-environments (read 2026-11-13) say the setup script runs once, Anthropic snapshots the filesystem, and later sessions skip the script until it, the allowed hosts or a seven-day expiry change. They also recommend a SessionStart hook for project dependencies. In this session the snapshot did keep `node_modules`: `plugins/tailwind-development/node_modules` dated 2026-11-12, older than the container's start on 2026-11-13.

Before this change the setup script ran `npm ci` and `npm run tools:install` separately, never ran `uv sync`, and installed plugin dependencies with `npm install`, which can rewrite a plugin's lockfile.

## Decision drivers

- Every cloud session, plain or a Projects thread, starts with `node_modules/` and `.venv/` present.
- Nothing runs on the owner's machine that was meant only for the cloud.
- One command prepares a checkout, through npm as the single entry point (ADR_2026-11-12_npm-scripts-are-the-single-entry-point).
- No lockfile changes as a side effect of setup.

## Considered options

- **`npm run setup` (`npm ci && uv sync --locked && npm run tools:install`), called from the setup script, with plugins installed by `npm ci --ignore-scripts`**: chosen.
- **A SessionStart hook in `.claude/settings.json` that exits unless `CLAUDE_CODE_REMOTE` is `true`, the documented pattern**: rejected by the owner, because the setup script already runs only in the cloud and before Claude starts, so a hook adds a second script and environment detection. The docs also say repository hooks don't run in Projects threads or in sessions with several repositories.
- **A hook that runs both locally and in the cloud**: rejected, because it would reinstall on the owner's machine on its own and needs a script portable to macOS.
- **A `postinstall` script that runs `uv sync`**: rejected, because it fires on every `npm install` of a package instead of when someone asks for it.

## Decision outcome

Chosen option: **the setup script calls `npm run setup`**, because it runs only in the cloud, before Claude starts, also in Projects threads, and gives the owner's machine and the cloud the same one-step command.

### Consequences

- Good, because a fresh checkout is ready in one command: from an empty `node_modules/` and `.venv/`, `npm run setup` exited 0 and `npm run typecheck` reported 0 errors (2026-11-13).
- Good, because `npm ci` and `uv sync --locked` never rewrite `package-lock.json` or `uv.lock`; the setup script run left `git status` clean (2026-11-13).
- Bad, because the snapshot keeps the dependencies of the day it was built. After `package-lock.json` or `uv.lock` changes, a session runs `npm run setup` itself until the snapshot is rebuilt.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The setup script prepares the checkout | Run it from the checkout's parent with `node_modules/` and `.venv/` deleted | Exit 0 in 25 seconds; `node_modules`, `.venv` and the plugin's `node_modules` present; no `failed` line (2026-11-13) | Each change to the setup script |
| A fresh session gets both folders | Start a new cloud session on the environment and check the `[setup]` lines | Pending | First fresh session after 2026-11-13 |
| A Projects thread gets both folders | Start a thread in the owner's project and run `ls -d node_modules .venv` | Pending | First thread after 2026-11-13 |

## More information

- The setup script is stored on the cloud environment, not in the repository; its replacement was approved on 2026-11-13.
- The overview draft `.claude/architecture/CLAUDE.draft.md` (Cloud sessions) tells a session to run `npm run setup` when a folder is missing or a lockfile changed.
- The owner decided this in this session, on 2026-11-13.
