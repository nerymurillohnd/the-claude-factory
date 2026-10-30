---
status: accepted
date: 2026-10-29
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Mods commit no tsconfig.json

## Scope

The root `tsconfig.json` of every mod under `plugins/<mod>/`: today file-tree-pane, macos-grep-guard, model-trace, project-maintainer, tool-ledger and turn-meter. A mod's `types/index.d.ts` contract is out of scope and stays committed.

## Context and problem statement

When a mod has no `tsconfig.json`, Claude Code adds one at its root that extends the generated `.claude-plugin/types/tsconfig.json` (`/en/plugins/mods/create`, "Get type definitions for your version"). Six mods committed that file. Everything committed under `plugins/<plugin>/` reaches every user's plugin cache, while `.claude-plugin/types/` is git-ignored, so users receive a tsconfig that extends a file they never have. Should mods keep committing it?

## Decision drivers

- Ship to users only what the plugin needs to run; a mod needs no TypeScript, no build step and no tsconfig (`/en/plugins/mods/create`).
- No gate uses the file since ADR_2026-10-29_remove-the-mod-tsc-gate.
- Anthropic's own mods carry no per-mod tsconfig (`anthropics/claude-code` `mods/`).

## Considered options

- **Remove the six files in one pull request with a patch bump each, git-ignore `plugins/*/tsconfig.json`, and reject a committed one in `check-repo`**: chosen.
- **Remove them later, logged as debt**: rejected, because each release until then keeps shipping a broken file.

## Decision outcome

Chosen option: **Remove the six files in one pull request, git-ignore the pattern and add the check**, because the file serves no user and the check keeps it from coming back.

### Consequences

- Good, because users' caches no longer hold a tsconfig that points at a missing file.
- Good, because the editor still gets one: Claude Code writes it, git-ignored, in a `--plugin-dir` session.
- Bad, because six plugins take a patch release for a file removal.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| No `plugins/*/tsconfig.json` is tracked | `git ls-files 'plugins/*/tsconfig.json'` prints nothing | pending | After the pull request merges |
| A committed one fails the repository check | `check-repo` test in `scripts/testers/` | pending | After the pull request merges |

## More information

Decided by Nery on 2026-10-29, after the live-sources audit `.claude/maintainer/audits/2026-10-29-plugins-and-mods-live-sources-audit.md` (F3.3, F8.3, F8.4, F8.7). The premise of ADR_2026-10-27_biome-checks-every-tsconfig-with-auto-expand about the plugins' tsconfig files lapses once they are removed.
