---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-13_hook-scripts-language-shebang-and-mode
superseded-by: none
---

# Bash scripts start strict, and a command hook maps every unexpected failure to the exit code it means

## Scope

Every standalone Bash script in the repository, maintainer and plugin alike, through `.claude/rules/code-quality/shell.md` (`**/*.sh`); and the `run:` scripts of GitHub Actions workflows, through `.claude/rules/architecture/github.md`. Out of scope: Python and Node hooks, and mods.

## Context and problem statement

ADR_2026-11-13_hook-scripts-language-shebang-and-mode chose a language by complexity, an env shebang, `chmod +x` and `set -euo pipefail` for hook scripts. It kept them in `.claude/rules/hook-scripts.md`, which was removed at the owner's request on 2026-11-14 (commit 52417b7). Since then no rule said how a Bash script starts.

On 2026-11-15 the owner shared a general shell-safety policy and asked whether it helps. It recommends `#!/usr/bin/env bash` and `set -euo pipefail`. It misses what matters most for Claude Code hooks: under `set -e` a script exits with the failing command's own code. Checked here:
- `grep` on an unreadable file exits 2;
- `jq` 1.7 exits 2 on a usage or system error.

Exit 2 blocks on `PreToolUse`, `Stop`, `SubagentStop` and the other blocking events (code.claude.com/docs/en/hooks, "Exit code 2 behavior per event", read 2026-11-15).

## Decision drivers

- A hook must never block, or keep Claude from stopping, because of an unexpected failure.
- Plugin scripts run on users' macOS machines, where the plugins state Bash 3.2 as their floor.
- Rules hold only what changes Claude's behavior, within 50 lines.

## Considered options

- **Five lines in the shell rule:**
  - the shebang and strict mode, with any dropped option justified on its `set` line;
  - the exit-code mapping for command hooks (a `trap 'exit 1' ERR` or an `EXIT` trap; 2 for a guard that fails closed);
  - the Bash 3.2 floor;
  - `jq -e`'s exit codes;
  - no `set -x` in hooks or CI.

  Plus one line in the GitHub rule on the shells Actions runs: chosen.
- **Adopt the shared policy as written**: rejected. It runs to about 150 lines, mostly what Claude already does, and leaves out the exit-2 behavior of hooks.
- **Restore `hook-scripts.md`**: rejected, because the owner removed it.

## Decision outcome

Chosen option: **the five shell lines and one GitHub line**, because they fix the failure modes this repository actually has. Verified facts behind them:
- Bash's NEWS gives `mapfile`/`readarray` and `${v,,}`/`${v^^}` to bash-4.0, and `inherit_errexit` to bash-4.4.
- The jq manual says `-e` exits 4 when no valid result is produced and 1 when the last one is `false` or `null`. Checked here with jq 1.7: no output 4, `null` 1, parse error 5, usage error 2.
- GitHub's workflow syntax gives a step with no `shell:` as `bash -e {0}` and `shell: bash` as `bash --noprofile --norc -eo pipefail {0}`.

The earlier ADR's other choices were not re-adopted here: language by complexity, `chmod +x`, Node hooks as `.mjs`, and Python hooks on the standard library at a 3.12 floor. They have had no rule since 2026-11-14.

### Consequences

- Good, because a failing `grep` or `jq` can no longer block a user's tool call or keep Claude from stopping.
- Good, because the existing hooks already conform. `skill-diagnostics`' `Stop` and `SubagentStop` hooks map every failure to 1 with an `EXIT` trap. `block-no-verify` and `approve-own-scripts` run without `-e`.
- Bad, because `plugins/block-no-verify/hooks/block-no-verify.sh` drops `-e` and `-u` with no reason on its `set` line; fixing it is a plugin change with a version bump.

## More information

- Decided by the owner on 2026-11-15 ("sí, hazlo así").
- Whether an empty array under `set -u` fails on Bash 3.2 was not verified, so the rule doesn't state it.
