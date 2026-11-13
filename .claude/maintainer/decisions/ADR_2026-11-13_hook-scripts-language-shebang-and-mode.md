---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Hook scripts pick Bash, Python or Node by complexity, start with an env shebang and are executable

## Scope

Every script a Claude Code `command` hook runs, in a plugin (`plugins/*/hooks/`, inline hooks in `plugin.json`) or in this project (`.claude/hooks/`, `.claude/settings.json`, `.claude/agents/`). Out of scope: mod modules named under `"modules"` in a `hooks/hooks.json` and the files they import, which Claude Code loads in its own process; skill scripts; Git hooks.

## Context and problem statement

The repository ships command hooks in three languages with no written convention: Bash (`skill-diagnostics`, `typescript6/7-lsp-intelligence`, `project-maintainer`, `block-no-verify`), Python (`python-lsp-intelligence/hooks/check.py`) and Node (`bash-lsp-intelligence/hooks/check.mjs`). On 2026-11-13 all 13 had an env shebang and git mode 100755, but `approve-own-scripts.sh` used `set -uo pipefail` and `block-no-verify.sh` `set -E -o pipefail`, and nothing said when each language fits or how a hook is wired. The official hooks page recommends exec form (`args`) for commands holding `${CLAUDE_PLUGIN_ROOT}`, and substitutes `${user_config.*}` in exec form only (code.claude.com/docs/en/hooks, "Exec form and shell form", read 2026-11-13).

## Decision drivers

- Every hook script behaves the same on a user's machine, whoever wrote it.
- The language matches the hook's complexity.
- Plugin hooks run with no dependency the plugin does not declare.

## Considered options

- **Language by complexity (Bash for direct hooks, Python for complex or dynamic ones, Node as `.mjs` for JavaScript), `#!/usr/bin/env bash|python3|node` and mode 100755 on every script, `set -euo pipefail` in Bash with justified exceptions, plugin Python on the standard library at the 3.12 floor, and the invocation form chosen per hook by the official criteria**: chosen.
- **One fixed invocation form for every hook**: rejected by the owner; the form depends on how each hook is wired.
- **Shebang and mode on mod modules too**: rejected because Claude Code imports them as ES modules and never executes them.
- **Node hooks in `.ts`**: rejected because `node` does not run TypeScript on every Node version a user may have.

## Decision outcome

Chosen option: **language by complexity with a fixed start for every script**, because it makes every hook script predictable and runnable on its own for testing, and keeps plugin hooks free of undeclared dependencies. The rule is `.claude/rules/hook-scripts.md`.

### Consequences

- Good, because the 13 existing command-hook scripts already have the shebang and mode, so the rule describes them and guides new ones.
- Good, because a Python hook in a plugin needs nothing beyond Python 3.12, which ruff and basedpyright already check under ADR_2026-11-12_basedpyright-checks-plugins-at-python-3-12.
- Bad, because the two Bash hooks without `-e` need a justifying comment on their `set` line, and changing them is a plugin change that needs a pull request.
- Neutral, because ADR_2026-11-12_uv-project-pins-maintainer-python-tools keeps PEP 723 metadata for plugin scripts; no plugin hook uses PEP 723 today, and this decision applies it to no hook.

## More information

- The owner decided this on 2026-11-13: the three shebangs, `chmod +x` on all, Bash for simple direct hooks with `set -euo pipefail` and its known exceptions, Python for complex hooks, Node for JavaScript; mods excluded and Node hooks as `.mjs`; the invocation form per hook; plugin Python hooks on the standard library at the 3.12 floor.
- Sources: code.claude.com/docs/en/hooks ("Exec form and shell form", "Exit code output", "Things to know about hooks in plugins" in the public-marketplace-dev copy checked to 2.1.319) and code.claude.com/docs/en/plugins/mods/reference ("The hooks module… An ES module"), read 2026-11-13.
