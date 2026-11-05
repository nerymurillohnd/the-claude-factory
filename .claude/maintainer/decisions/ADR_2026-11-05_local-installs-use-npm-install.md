---
status: accepted
date: 2026-11-05
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# Local installs use npm install; CI keeps npm ci

## Scope

The rule in `.claude/CLAUDE.md` (Maintainer Tooling) on how the maintainer's clone and worktrees install their npm dependencies. CI's installs in `.github/workflows/validate.yml` are out of scope and stay on `npm ci`.

## Context and problem statement

`.claude/CLAUDE.md` required `npm ci` in every fresh clone and new worktree. `npm ci` deletes `node_modules` and reinstalls it every time, which Nery found slow in his sessions. The session-start hook `.claude/hooks/repo-setup.sh` already runs `npm install` in the clone and in each plugin with a lockfile, so the rule and the hook disagreed. No other local rule, hook or script requires `npm ci` (`git grep 'npm ci'`, 2026-11-05: only CLAUDE.md, ADR context, specs and CI). Which install should local work use?

## Decision drivers

- Fast session starts and installs.
- The lockfile stays the source of the versions everyone runs.
- One rule, the same as what the hook does.

## Considered options

- **`npm install` locally, `npm ci` in CI**: chosen.
- **Keep `npm ci` everywhere**: rejected by Nery as needless friction; it reinstalls everything on each run.
- **`npm install` in CI too**: rejected, because CI's `npm ci` is what fails when the lockfile and `package.json` disagree.

## Decision outcome

Chosen option: **`npm install` locally, `npm ci` in CI**. CLAUDE.md now says to install with `npm install` under the `.nvmrc` Node, names the hook that runs it, and allows a `package-lock.json` change in a commit only together with the dependency change that caused it.

### Consequences

- Good, because an install with `node_modules` already in place changes only what differs from the lockfile, and the rule matches the hook.
- Good, because CI still catches a lockfile out of step with `package.json`.
- Bad, because `npm install` can rewrite `package-lock.json` under another Node or npm, as a Node 22 container did on 2026-11-04. The `devEngines` pin (ADR_2026-11-04_node-pinned-in-package-json-through-devengines) stops a wrong Node, and the commit rule keeps an unintended rewrite out of the history.

## More information

Decided by Nery on 2026-11-05, after he asked why `npm ci` was required and confirmed that only CLAUDE.md imposed it locally.
